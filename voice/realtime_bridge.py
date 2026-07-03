"""Twilio Media Stream ↔ OpenAI Realtime bridge (Phase 4 patient voice)."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from websockets.asyncio.client import connect as ws_connect

from app.session_registry import ActiveCallSession
from config import Settings, get_settings
from patient.models import Scenario
from patient.prompt_builder import build_session_config
from voice.audio_utils import (
    openai_pcm16_b64_to_twilio_mulaw_b64,
    twilio_mulaw_b64_to_openai_pcm16_b64,
)
from voice.turn_state import TurnState

logger = logging.getLogger(__name__)

OPENAI_REALTIME_URL = "wss://api.openai.com/v1/realtime"


async def handle_realtime_media_stream(
    websocket: WebSocket,
    session: ActiveCallSession,
    scenario: Scenario,
) -> None:
    """Connect Twilio audio to OpenAI Realtime patient agent."""
    settings = get_settings()
    await websocket.accept()
    session.stream_connected = True
    session.log_event("stream_connected", mode="realtime", scenario=scenario.id)
    logger.info("Realtime bridge starting for %s scenario=%s", session.call_id, scenario.name)

    stream_sid_holder: dict[str, str | None] = {"sid": None}
    stop_event = asyncio.Event()
    turn_state = TurnState()
    cooldown_seconds = settings.agent_turn_cooldown_ms / 1000.0
    playback_hold_seconds = settings.patient_playback_hold_ms / 1000.0

    try:
        model = settings.openai_realtime_model
        url = f"{OPENAI_REALTIME_URL}?model={model}"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
        }

        async with ws_connect(url, additional_headers=headers) as openai_ws:
            await _configure_openai_session(openai_ws, scenario, settings)
            session.log_event("openai_session_configured", model=model)

            timeout_task = asyncio.create_task(
                _max_duration_guard(stop_event, settings.max_call_duration_seconds, session.call_id)
            )
            pending_holder: dict[str, Any] = {
                "task": None,
                "after_playback": False,
                "playback_wait_task": None,
            }

            openai_task = asyncio.create_task(
                _forward_openai_to_twilio(
                    openai_ws,
                    websocket,
                    session,
                    stream_sid_holder,
                    stop_event,
                    settings,
                    turn_state,
                    cooldown_seconds,
                    playback_hold_seconds,
                    pending_holder,
                )
            )

            try:
                await _forward_twilio_to_openai(
                    websocket,
                    openai_ws,
                    session,
                    stream_sid_holder,
                    stop_event,
                    turn_state,
                )
            finally:
                stop_event.set()
                await _cancel_pending_response(pending_holder)
                openai_task.cancel()
                timeout_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await openai_task
                    await timeout_task

    except WebSocketDisconnect:
        session.log_event("twilio_disconnected")
        logger.info("Twilio disconnected for %s", session.call_id)
    except Exception as exc:
        session.log_event("realtime_bridge_error", error=str(exc))
        logger.exception("Realtime bridge failed for %s: %s", session.call_id, exc)
        raise
    finally:
        session.stream_connected = False
        logger.info(
            "Realtime bridge ended for %s (rx=%s tx=%s)",
            session.call_id,
            session.frames_received,
            session.frames_sent,
        )


async def _configure_openai_session(
    openai_ws: Any,
    scenario: Scenario,
    settings: Settings,
) -> None:
    session_config = build_session_config(
        scenario,
        voice=settings.openai_realtime_voice,
        model=settings.openai_realtime_model,
        caller_phone=settings.twilio_phone_number,
        vad_silence_duration_ms=settings.vad_silence_duration_ms,
    )

    first = await asyncio.wait_for(openai_ws.recv(), timeout=5.0)
    first_event = json.loads(first)
    if first_event.get("type") == "error":
        raise RuntimeError(f"OpenAI Realtime error: {first_event}")

    await openai_ws.send(
        json.dumps({"type": "session.update", "session": session_config})
    )

    for _ in range(10):
        raw = await asyncio.wait_for(openai_ws.recv(), timeout=5.0)
        event = json.loads(raw)
        if event.get("type") == "session.updated":
            return
        if event.get("type") == "error":
            raise RuntimeError(f"OpenAI session.update failed: {event}")


async def _max_duration_guard(stop_event: asyncio.Event, max_seconds: int, call_id: str) -> None:
    await asyncio.sleep(max_seconds)
    logger.info("Max call duration reached for %s (%ss)", call_id, max_seconds)
    stop_event.set()


async def _cancel_pending_response(
    pending_holder: dict[str, Any],
) -> None:
    task = pending_holder.get("task")
    if task and not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
    pending_holder["task"] = None

    playback_wait = pending_holder.get("playback_wait_task")
    if playback_wait and not playback_wait.done():
        playback_wait.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await playback_wait
    pending_holder["playback_wait_task"] = None


async def _schedule_patient_response(
    openai_ws: Any,
    turn_state: TurnState,
    cooldown_seconds: float,
    pending_holder: dict[str, Any],
    call_id: str,
) -> None:
    task = pending_holder.get("task")
    if task and not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
    pending_holder["task"] = None

    async def _create_after_cooldown() -> None:
        try:
            await asyncio.sleep(cooldown_seconds)
            deadline = time.monotonic() + 30.0
            while time.monotonic() < deadline:
                if turn_state.may_start_patient_response():
                    break
                await asyncio.sleep(0.05)
            else:
                return
            if not turn_state.may_start_patient_response():
                return
            await openai_ws.send(json.dumps({"type": "response.create"}))
            logger.debug("Scheduled patient response for %s", call_id)
        except asyncio.CancelledError:
            raise

    pending_holder["task"] = asyncio.create_task(_create_after_cooldown())


async def _wait_for_playback_then_respond(
    openai_ws: Any,
    turn_state: TurnState,
    cooldown_seconds: float,
    pending_holder: dict[str, Any],
    session: ActiveCallSession,
) -> None:
    if not pending_holder.get("after_playback"):
        return

    existing = pending_holder.get("playback_wait_task")
    if existing and not existing.done():
        return

    async def _run() -> None:
        try:
            deadline = time.monotonic() + 45.0
            while turn_state.is_patient_on_line() and time.monotonic() < deadline:
                wait = turn_state.patient_playback_until - time.monotonic()
                await asyncio.sleep(max(wait, 0.05))
            if not pending_holder.get("after_playback") or turn_state.agent_speaking:
                return
            pending_holder["after_playback"] = False
            session.log_event("patient_response_scheduled_after_playback")
            await _schedule_patient_response(
                openai_ws,
                turn_state,
                cooldown_seconds,
                pending_holder,
                session.call_id,
            )
        except asyncio.CancelledError:
            raise

    pending_holder["playback_wait_task"] = asyncio.create_task(_run())


async def _forward_twilio_to_openai(
    twilio_ws: WebSocket,
    openai_ws: Any,
    session: ActiveCallSession,
    stream_sid_holder: dict[str, str | None],
    stop_event: asyncio.Event,
    turn_state: TurnState,
) -> None:
    while not stop_event.is_set():
        try:
            message = await asyncio.wait_for(twilio_ws.receive_text(), timeout=1.0)
        except asyncio.TimeoutError:
            continue

        data = json.loads(message)
        event = data.get("event")

        if event == "connected":
            session.log_event("twilio_connected")
            continue

        if event == "start":
            stream_sid_holder["sid"] = data.get("start", {}).get("streamSid")
            session.stream_sid = stream_sid_holder["sid"]
            session.log_event("stream_started", stream_sid=session.stream_sid)
            continue

        if event == "media":
            payload = data.get("media", {}).get("payload")
            if not payload:
                continue
            session.frames_received += 1
            if not turn_state.may_accept_agent_audio():
                continue
            openai_audio = twilio_mulaw_b64_to_openai_pcm16_b64(payload)
            await openai_ws.send(
                json.dumps({"type": "input_audio_buffer.append", "audio": openai_audio})
            )
            continue

        if event == "stop":
            session.log_event("stream_stopped")
            stop_event.set()
            break


async def _forward_openai_to_twilio(
    openai_ws: Any,
    twilio_ws: WebSocket,
    session: ActiveCallSession,
    stream_sid_holder: dict[str, str | None],
    stop_event: asyncio.Event,
    settings: Settings,
    turn_state: TurnState,
    cooldown_seconds: float,
    playback_hold_seconds: float,
    pending_holder: dict[str, Any],
) -> None:
    response_delay = settings.response_delay_ms / 1000.0
    dropped_overlap_frames = 0

    while not stop_event.is_set():
        try:
            raw = await asyncio.wait_for(openai_ws.recv(), timeout=1.0)
        except asyncio.TimeoutError:
            continue

        event = json.loads(raw)
        event_type = event.get("type", "")

        if event_type == "input_audio_buffer.speech_started":
            await _cancel_pending_response(pending_holder)
            pending_holder["after_playback"] = False
            should_cancel = turn_state.mark_agent_started(cooldown_seconds=cooldown_seconds)
            session.log_event(
                "agent_speech_started",
                cancel_patient=should_cancel,
                patient_on_line=turn_state.is_patient_on_line(),
            )
            await openai_ws.send(json.dumps({"type": "input_audio_buffer.clear"}))
            continue

        if event_type == "input_audio_buffer.speech_stopped":
            turn_state.mark_agent_stopped(cooldown_seconds=cooldown_seconds)
            session.log_event("agent_speech_stopped")
            if turn_state.is_patient_on_line():
                pending_holder["after_playback"] = True
                session.log_event(
                    "patient_response_deferred",
                    until=turn_state.patient_playback_until,
                )
                await _wait_for_playback_then_respond(
                    openai_ws,
                    turn_state,
                    cooldown_seconds,
                    pending_holder,
                    session,
                )
            else:
                await _schedule_patient_response(
                    openai_ws,
                    turn_state,
                    cooldown_seconds,
                    pending_holder,
                    session.call_id,
                )
            continue

        if event_type in {"response.created", "response.started"}:
            turn_state.mark_patient_response_started()
            continue

        if event_type in {"response.done", "response.completed"}:
            continue

        if event_type in {"response.output_audio.delta", "response.audio.delta"}:
            stream_sid = stream_sid_holder.get("sid")
            delta = event.get("delta")
            if not stream_sid or not delta:
                continue

            if not turn_state.may_send_patient_audio():
                dropped_overlap_frames += 1
                continue

            if response_delay > 0 and turn_state.response_frames_sent == 0:
                await asyncio.sleep(response_delay)

            twilio_payload = openai_pcm16_b64_to_twilio_mulaw_b64(delta)
            await twilio_ws.send_text(
                json.dumps(
                    {
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": twilio_payload},
                    }
                )
            )
            turn_state.mark_patient_frame_sent()
            session.frames_sent += 1
            continue

        if event_type in {
            "response.output_audio.done",
            "response.audio.done",
        }:
            turn_state.mark_patient_audio_complete(
                playback_hold_seconds=playback_hold_seconds,
            )
            session.log_event(
                "patient_playback_hold",
                frames=turn_state.response_frames_sent,
                until=turn_state.patient_playback_until,
            )
            await _wait_for_playback_then_respond(
                openai_ws,
                turn_state,
                cooldown_seconds,
                pending_holder,
                session,
            )
            continue

        if event_type in {
            "response.output_audio_transcript.done",
            "response.audio_transcript.done",
        }:
            session.log_event("patient_said", text=event.get("transcript", ""))
            continue

        if event_type in {
            "conversation.item.input_audio_transcription.completed",
            "conversation.item.input_audio_transcription.done",
        }:
            session.log_event("agent_said", text=event.get("transcript", ""))
            continue

        if event_type == "error":
            session.log_event("openai_error", error=event.get("error"))
            logger.error("OpenAI Realtime error on %s: %s", session.call_id, event)
            continue

    await _cancel_pending_response(pending_holder)

    if dropped_overlap_frames:
        logger.info(
            "Dropped %s patient audio frames during agent speech for %s",
            dropped_overlap_frames,
            session.call_id,
        )


def load_scenario_for_session(session: ActiveCallSession) -> Scenario:
    """Load scenario JSON from the session path."""
    from pathlib import Path

    if not session.scenario_path:
        raise ValueError(f"No scenario_path on session {session.call_id}")
    path = Path(session.scenario_path)
    if not path.exists():
        raise FileNotFoundError(f"Scenario not found: {path}")
    return Scenario.load(path)
