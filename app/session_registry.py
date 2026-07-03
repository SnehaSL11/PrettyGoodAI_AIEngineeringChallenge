"""In-memory registry of active phone call sessions."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ActiveCallSession:
    """Runtime state for one outbound call (lives in FastAPI process memory)."""

    call_id: str
    scenario_path: str
    twilio_call_sid: str | None = None
    stream_sid: str | None = None
    twilio_status: str = "init"
    stream_connected: bool = False
    frames_received: int = 0
    frames_sent: int = 0
    recording_url: str | None = None
    recording_path: str | None = None
    bridge_mode: str = "silent"
    events: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_event: asyncio.Event = field(default_factory=asyncio.Event)

    def log_event(self, name: str, **payload: Any) -> None:
        self.events.append(
            {
                "t": datetime.now(timezone.utc).isoformat(),
                "event": name,
                **payload,
            }
        )

    def mark_completed(self, status: str) -> None:
        self.twilio_status = status
        if status in {"completed", "failed", "busy", "no-answer", "canceled"}:
            self.completed_event.set()


class SessionRegistry:
    """Thread-safe enough for single-process FastAPI (one worker)."""

    def __init__(self) -> None:
        self._sessions: dict[str, ActiveCallSession] = {}

    def create(
        self,
        call_id: str,
        scenario_path: str,
        *,
        bridge_mode: str = "silent",
    ) -> ActiveCallSession:
        session = ActiveCallSession(
            call_id=call_id,
            scenario_path=scenario_path,
            bridge_mode=bridge_mode,
        )
        self._sessions[call_id] = session
        return session

    def get(self, call_id: str) -> ActiveCallSession | None:
        return self._sessions.get(call_id)

    def get_or_create(
        self,
        call_id: str,
        scenario_path: str,
        *,
        bridge_mode: str = "silent",
    ) -> ActiveCallSession:
        existing = self.get(call_id)
        if existing:
            return existing
        return self.create(call_id, scenario_path, bridge_mode=bridge_mode)

    def remove(self, call_id: str) -> None:
        self._sessions.pop(call_id, None)


registry = SessionRegistry()
