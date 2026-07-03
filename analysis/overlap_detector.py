"""Detect likely voice overlap from session turn timestamps and bridge events."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


# Gaps shorter than this between speaker turns suggest simultaneous speech.
TIGHT_TURN_GAP_MS = 800
# Back-to-back lines from the same speaker this close often mean a double reply.
DUPLICATE_SPEAKER_GAP_MS = 1500
# Patient lines within this window are treated as duplicate responses.
DUPLICATE_PATIENT_GAP_MS = 250


def _parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _gap_ms(previous: str, current: str) -> float | None:
    prev_t = _parse_timestamp(previous)
    curr_t = _parse_timestamp(current)
    if not prev_t or not curr_t:
        return None
    return (curr_t - prev_t).total_seconds() * 1000


def _looks_truncated(text: str) -> bool:
    """Heuristic: utterance starts mid-sentence (common when overlap cuts audio)."""
    stripped = text.strip()
    if len(stripped) < 12:
        return False
    first = stripped[0]
    if first.islower():
        return True
    starters = (
        "and ",
        "but ",
        "or ",
        "so ",
        "then ",
        "please ",
        "thanks ",
        "thank you",
        "yes ",
        "no ",
    )
    lowered = stripped.lower()
    return any(lowered.startswith(prefix) for prefix in starters)


def detect_turn_overlap_signals(turns: list[dict[str, Any]]) -> list[str]:
    """Return human-readable overlap signals from speaker-labeled turns."""
    signals: list[str] = []

    for index in range(1, len(turns)):
        previous = turns[index - 1]
        current = turns[index]
        gap = _gap_ms(previous.get("t", ""), current.get("t", ""))
        if gap is None:
            continue

        prev_speaker = previous.get("speaker", "")
        curr_speaker = current.get("speaker", "")
        prev_text = (previous.get("text") or "").strip()
        curr_text = (current.get("text") or "").strip()
        timestamp = current.get("t", "")

        if gap < TIGHT_TURN_GAP_MS and prev_speaker != curr_speaker:
            signals.append(
                f"Tight turn gap ({gap:.0f}ms) at {timestamp}: "
                f"{prev_speaker.upper()} then {curr_speaker.upper()} — likely simultaneous speech."
            )

        if (
            prev_speaker == "patient"
            and curr_speaker == "patient"
            and gap < DUPLICATE_PATIENT_GAP_MS
        ):
            signals.append(
                f"Duplicate patient replies ({gap:.0f}ms apart) at {timestamp}: "
                f"\"{prev_text[:60]}\" / \"{curr_text[:60]}\"."
            )

        if (
            prev_speaker == curr_speaker
            and gap < DUPLICATE_SPEAKER_GAP_MS
            and gap >= DUPLICATE_PATIENT_GAP_MS
        ):
            signals.append(
                f"Back-to-back {curr_speaker} turns ({gap:.0f}ms apart) at {timestamp}."
            )

        if curr_speaker == "agent" and _looks_truncated(curr_text):
            signals.append(
                f"Possible truncated agent utterance at {timestamp}: \"{curr_text[:80]}\"."
            )

    return signals


def detect_event_overlap_signals(events_path: Path) -> list[str]:
    """Return overlap signals from realtime bridge session events."""
    if not events_path.exists():
        return []

    events = json.loads(events_path.read_text(encoding="utf-8"))
    if not isinstance(events, list):
        return []

    signals: list[str] = []
    for event in events:
        name = event.get("event")
        timestamp = event.get("t", "")

        if name == "agent_speech_started" and event.get("patient_on_line"):
            signals.append(
                f"Agent speech started while patient audio was still active at {timestamp}."
            )

        if name == "agent_speech_started" and event.get("cancel_patient"):
            signals.append(
                f"Bridge attempted to cancel patient speech at {timestamp}."
            )

        if name == "patient_response_deferred":
            signals.append(
                f"Patient reply deferred until playback finished at {timestamp}."
            )

    return signals


def build_overlap_context(
    turns: list[dict[str, Any]],
    events_path: Path | None = None,
) -> str:
    """Format overlap signals for the evaluator prompt."""
    signals = detect_turn_overlap_signals(turns)
    if events_path:
        signals.extend(detect_event_overlap_signals(events_path))

    if not signals:
        return "No strong overlap signals detected from turn timestamps or bridge events."

    lines = ["Automated overlap / turn-timing signals:"]
    for index, signal in enumerate(signals, start=1):
        lines.append(f"{index}. {signal}")
    return "\n".join(lines)
