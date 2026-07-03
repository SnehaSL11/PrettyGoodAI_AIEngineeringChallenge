"""Merge Whisper transcript with realtime session event logs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_events(events_path: Path) -> list[dict[str, Any]]:
    if not events_path.exists():
        return []
    data = json.loads(events_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return []


def _extract_turns(events: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Pull patient/agent utterances logged during the realtime call."""
    turns: list[dict[str, str]] = []
    for event in events:
        name = event.get("event")
        text = (event.get("text") or "").strip()
        if not text:
            continue
        if name == "patient_said":
            turns.append({"speaker": "patient", "text": text, "t": event.get("t", "")})
        elif name == "agent_said":
            turns.append({"speaker": "agent", "text": text, "t": event.get("t", "")})
    return turns


def build_full_transcript(
    *,
    call_id: str,
    scenario_path: str,
    recording_path: str,
    whisper_text: str,
    events_path: Path,
    session_log_path: Path | None = None,
) -> dict[str, Any]:
    """Build structured transcript JSON for a call."""
    events = _load_events(events_path)
    turns = _extract_turns(events)

    session_meta: dict[str, Any] = {}
    if session_log_path and session_log_path.exists():
        session_meta = json.loads(session_log_path.read_text(encoding="utf-8"))

    return {
        "call_id": call_id,
        "scenario_path": scenario_path,
        "recording_path": recording_path,
        "whisper_transcript": whisper_text,
        "turns": turns,
        "turn_count": len(turns),
        "session": session_meta,
        "notes": (
            "whisper_transcript is the full mixed recording; "
            "turns are speaker-labeled excerpts from the realtime session log when available."
        ),
    }


def format_readable_transcript(full: dict[str, Any]) -> str:
    """Plain-text transcript for submission (turns + full whisper fallback)."""
    lines: list[str] = [
        f"Call: {full['call_id']}",
        f"Recording: {full['recording_path']}",
        f"Scenario: {full['scenario_path']}",
        "",
    ]

    turns = full.get("turns") or []
    if turns:
        lines.append("=== Speaker-labeled turns (from session log) ===")
        for index, turn in enumerate(turns, start=1):
            speaker = turn.get("speaker", "unknown").upper()
            text = turn.get("text", "")
            timestamp = turn.get("t", "")
            prefix = f"[{timestamp}] " if timestamp else f"[{index}] "
            lines.append(f"{prefix}{speaker}: {text}")
        lines.append("")

    lines.append("=== Full recording transcript (Whisper) ===")
    lines.append(full.get("whisper_transcript", "").strip())
    return "\n".join(lines).strip() + "\n"
