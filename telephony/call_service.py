"""Sync call workflow used by runner.py CLI."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from config import Settings
from patient.models import CallHistory, CallHistoryEntry, CallStatus, Scenario, utc_now
from planning.history import load_call_history, save_call_history
from telephony.twilio_client import (
    TelephonyError,
    create_outbound_call,
    fetch_call_status,
    hangup_call,
)

logger = logging.getLogger(__name__)

TERMINAL_STATUSES = {"completed", "failed", "busy", "no-answer", "canceled"}


def _update_history_status(
    settings: Settings,
    call_id: str,
    status: CallStatus,
    *,
    notes: str | None = None,
) -> None:
    history = load_call_history(settings.call_history_path)
    for entry in history.entries:
        if entry.call_id == call_id:
            entry.status = status
            if status in {CallStatus.COMPLETED, CallStatus.FAILED}:
                entry.completed_at = utc_now()
            if notes:
                entry.notes = notes
            break
    else:
        logger.warning("No history entry found for call_id=%s", call_id)
    save_call_history(settings.call_history_path, history)


def _write_session_log(settings: Settings, call_id: str, payload: dict) -> Path:
    settings.ensure_call_dir(call_id)
    path = settings.call_paths(call_id)["session"]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def place_call_and_wait(
    settings: Settings,
    *,
    scenario_path: Path,
    bridge_mode: str = "realtime",
    poll_interval_seconds: float = 2.0,
) -> dict:
    """Place outbound Twilio call and poll until it finishes.

    Prerequisites:
      - FastAPI server running (python main.py)
      - PUBLIC_BASE_URL reachable by Twilio (ngrok)
    """
    scenario = Scenario.load(scenario_path)
    call_id = scenario.id
    settings.ensure_call_dir(call_id)
    canonical_scenario = settings.call_scenario_path(call_id)
    if scenario_path.resolve() != canonical_scenario.resolve():
        scenario.save(canonical_scenario)
    scenario_path_str = str(canonical_scenario.resolve())

    history = load_call_history(settings.call_history_path)
    found = False
    for entry in history.entries:
        if entry.call_id == call_id:
            entry.status = CallStatus.IN_PROGRESS
            entry.notes = f"Outbound call started (bridge={bridge_mode})"
            found = True
            break
    if not found:
        history.add(
            CallHistoryEntry(
                call_id=call_id,
                scenario_id=scenario.id,
                category=scenario.category,
                status=CallStatus.IN_PROGRESS,
                scenario_path=scenario_path_str,
                created_at=utc_now(),
                notes=f"Outbound call started (bridge={bridge_mode})",
            )
        )
    save_call_history(settings.call_history_path, history)

    try:
        call_sid = create_outbound_call(
            settings,
            call_id=call_id,
            scenario_path=scenario_path_str,
            bridge_mode=bridge_mode,
        )
    except TelephonyError:
        _update_history_status(settings, call_id, CallStatus.FAILED, notes="Telephony error")
        raise

    deadline = time.time() + settings.max_call_duration_seconds + 60
    last_status = "queued"

    while time.time() < deadline:
        last_status = fetch_call_status(settings, call_sid)
        logger.info("Call %s status: %s", call_id, last_status)
        if last_status in TERMINAL_STATUSES:
            break
        time.sleep(poll_interval_seconds)

    if last_status not in TERMINAL_STATUSES:
        logger.warning("Call %s still %s — hanging up", call_id, last_status)
        hangup_call(settings, call_sid)
        last_status = fetch_call_status(settings, call_sid)

    # Recording callback is async — wait briefly for MP3 download via webhook
    recording_path = settings.call_paths(call_id)["recording"]
    recording_deadline = time.time() + 45
    while not recording_path.exists() and time.time() < recording_deadline:
        time.sleep(poll_interval_seconds)

    recording_ready = recording_path.exists()

    final_status = (
        CallStatus.COMPLETED if last_status == "completed" else CallStatus.FAILED
    )
    _update_history_status(
        settings,
        call_id,
        final_status,
        notes=f"Twilio status={last_status}, recording={'yes' if recording_ready else 'pending'}",
    )

    session_log = _write_session_log(
        settings,
        call_id,
        {
            "call_id": call_id,
            "twilio_call_sid": call_sid,
            "twilio_status": last_status,
            "scenario_path": scenario_path_str,
            "bridge_mode": bridge_mode,
            "recording_path": str(recording_path) if recording_ready else None,
        },
    )

    return {
        "call_id": call_id,
        "twilio_call_sid": call_sid,
        "twilio_status": last_status,
        "recording_path": str(recording_path) if recording_ready else None,
        "session_log": str(session_log),
        "success": last_status == "completed",
    }
