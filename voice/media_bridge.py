"""Twilio Media Stream WebSocket handler (Phase 3 — no OpenAI Realtime yet)."""

from __future__ import annotations

import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from app.session_registry import ActiveCallSession
from voice.audio_utils import silence_payload

logger = logging.getLogger(__name__)


async def handle_twilio_media_stream(websocket: WebSocket, session: ActiveCallSession) -> None:
    """Bridge Twilio audio until Phase 4 wires in OpenAI Realtime.

    Modes (session.bridge_mode):
      - silent: send comfort silence back (keeps call alive, agent hears quiet line)
      - echo:   mirror inbound audio (proves bidirectional stream works)
    """
    await websocket.accept()
    session.stream_connected = True
    session.log_event("stream_connected", mode=session.bridge_mode)
    logger.info("Media stream connected for %s (mode=%s)", session.call_id, session.bridge_mode)

    stream_sid: str | None = None

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            event = data.get("event")

            if event == "connected":
                session.log_event("twilio_connected")
                continue

            if event == "start":
                stream_sid = data.get("start", {}).get("streamSid")
                session.stream_sid = stream_sid
                session.log_event("stream_started", stream_sid=stream_sid)
                logger.info("Stream started for %s sid=%s", session.call_id, stream_sid)
                continue

            if event == "media":
                payload = data.get("media", {}).get("payload")
                if not payload or not stream_sid:
                    continue

                session.frames_received += 1

                if session.bridge_mode == "echo":
                    outbound_payload = payload
                else:
                    outbound_payload = silence_payload()

                await websocket.send_text(
                    json.dumps(
                        {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": outbound_payload},
                        }
                    )
                )
                session.frames_sent += 1
                continue

            if event == "stop":
                session.log_event("stream_stopped")
                logger.info(
                    "Stream stopped for %s (rx=%s tx=%s frames)",
                    session.call_id,
                    session.frames_received,
                    session.frames_sent,
                )
                break

            if event == "mark":
                continue

    except WebSocketDisconnect:
        session.log_event("stream_disconnected")
        logger.info("WebSocket disconnected for %s", session.call_id)
    finally:
        session.stream_connected = False
