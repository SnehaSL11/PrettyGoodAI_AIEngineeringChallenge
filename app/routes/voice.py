"""Twilio voice webhook routes and media stream WebSocket."""

from __future__ import annotations

import json
import logging
from urllib.parse import unquote

from fastapi import APIRouter, Form, Request, Response, WebSocket

from app.session_registry import registry
from config import get_settings
from telephony.twilio_client import download_recording
from voice.media_bridge import handle_twilio_media_stream
from voice.realtime_bridge import handle_realtime_media_stream, load_scenario_for_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["voice"])


def _twiml(content: str) -> Response:
    return Response(content=content, media_type="application/xml")


@router.api_route("/voice/outbound", methods=["GET", "POST"])
async def voice_outbound(
    request: Request,
    call_id: str = "",
    scenario_path: str = "",
    bridge_mode: str = "silent",
) -> Response:
    """Return TwiML to connect Twilio Media Stream when outbound call is answered."""
    settings = get_settings()

    if not call_id:
        call_id = request.query_params.get("call_id", "unknown")
    if not scenario_path:
        scenario_path = request.query_params.get("scenario_path", "")
    bridge_mode = request.query_params.get("bridge_mode", bridge_mode or "realtime")

    scenario_path = unquote(scenario_path)
    registry.get_or_create(call_id, scenario_path, bridge_mode=bridge_mode)

    stream_url = settings.media_stream_url(call_id)
    logger.info("Outbound TwiML for %s stream=%s mode=%s", call_id, stream_url, bridge_mode)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{stream_url}" />
    </Connect>
</Response>"""
    return _twiml(twiml)


@router.post("/voice/status")
async def voice_status(
    call_id: str = "",
    bridge_mode: str = "realtime",
    CallSid: str = Form(default=""),
    CallStatus: str = Form(default=""),
) -> dict:
    """Receive Twilio call lifecycle updates."""
    session = registry.get(call_id) if call_id else None
    if not session and call_id:
        settings = get_settings()
        scenario_resolved = settings.resolve_scenario_path(call_id)
        scenario_path = str(scenario_resolved.resolve()) if scenario_resolved else ""
        session = registry.get_or_create(call_id, scenario_path, bridge_mode=bridge_mode)
    if session:
        session.twilio_call_sid = CallSid or session.twilio_call_sid
        session.twilio_status = CallStatus
        session.log_event("status_callback", call_sid=CallSid, status=CallStatus)
        session.mark_completed(CallStatus)
        logger.info("Status %s for %s: %s", CallSid, call_id, CallStatus)
        if CallStatus in {"completed", "failed", "busy", "no-answer", "canceled"}:
            settings = get_settings()
            settings.ensure_call_dir(call_id)
            log_path = settings.call_paths(call_id)["events"]
            log_path.write_text(json.dumps(session.events, indent=2), encoding="utf-8")
    else:
        logger.warning("Status callback for unknown call_id=%s", call_id)
    return {"ok": True}


@router.post("/voice/recording")
async def voice_recording(
    call_id: str = "",
    RecordingUrl: str = Form(default=""),
    RecordingSid: str = Form(default=""),
    CallSid: str = Form(default=""),
    RecordingStatus: str = Form(default=""),
) -> dict:
    """Download recording when Twilio notifies us it is ready."""
    settings = get_settings()
    session = registry.get(call_id) if call_id else None

    if session:
        session.recording_url = RecordingUrl
        session.log_event(
            "recording_callback",
            recording_sid=RecordingSid,
            call_sid=CallSid,
            status=RecordingStatus,
        )

    if RecordingUrl and call_id and RecordingStatus == "completed":
        settings.ensure_call_dir(call_id)
        destination = settings.call_paths(call_id)["recording"]
        try:
            download_recording(settings, RecordingUrl, destination)
            if session:
                session.recording_path = str(destination)
            logger.info("Recording stored for %s at %s", call_id, destination)
        except Exception as exc:
            logger.exception("Failed to download recording for %s: %s", call_id, exc)
            return {"ok": False, "error": str(exc)}

    return {"ok": True}


@router.websocket("/media/{call_id}")
async def media_stream(websocket: WebSocket, call_id: str) -> None:
    """Bidirectional audio WebSocket from Twilio Media Streams."""
    session = registry.get(call_id)
    if not session:
        settings = get_settings()
        scenario_resolved = settings.resolve_scenario_path(call_id)
        scenario_path = str(scenario_resolved) if scenario_resolved else ""
        session = registry.create(call_id, scenario_path, bridge_mode="realtime")

    if session.bridge_mode == "realtime":
        scenario = load_scenario_for_session(session)
        await handle_realtime_media_stream(websocket, session, scenario)
    else:
        await handle_twilio_media_stream(websocket, session)
