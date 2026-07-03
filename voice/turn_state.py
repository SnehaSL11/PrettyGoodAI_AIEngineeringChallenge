"""Shared turn-taking state for the Realtime ↔ Twilio bridge."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

# Twilio Media Streams mulaw frames are ~20 ms at 8 kHz.
TWILIO_FRAME_SECONDS = 0.02


@dataclass
class TurnState:
    """Coordinates when patient audio may be sent to the phone."""

    agent_speaking: bool = False
    patient_generating: bool = False
    response_allowed_after: float = field(default_factory=time.monotonic)
    patient_playback_until: float = 0.0
    response_frames_sent: int = 0

    def mark_agent_started(self, *, cooldown_seconds: float) -> bool:
        """Agent started speaking. Returns True if OpenAI generation is active."""
        self.agent_speaking = True
        self.response_allowed_after = max(
            self.response_allowed_after,
            time.monotonic() + cooldown_seconds,
        )
        return self.patient_generating

    def mark_agent_stopped(self, *, cooldown_seconds: float) -> None:
        """Agent stopped speaking — wait before starting the next patient turn."""
        self.agent_speaking = False
        self.response_allowed_after = max(
            self.response_allowed_after,
            time.monotonic() + cooldown_seconds,
            self.patient_playback_until,
        )

    def mark_patient_response_started(self) -> None:
        self.patient_generating = True
        self.response_frames_sent = 0

    def mark_patient_frame_sent(self) -> None:
        self.response_frames_sent += 1

    def mark_patient_audio_complete(self, *, playback_hold_seconds: float) -> None:
        """All audio for this response was sent — wait for Twilio/phone playback."""
        self.patient_generating = False
        playback_seconds = (self.response_frames_sent * TWILIO_FRAME_SECONDS) + playback_hold_seconds
        self.patient_playback_until = max(
            self.patient_playback_until,
            time.monotonic() + playback_seconds,
        )
        self.response_allowed_after = max(
            self.response_allowed_after,
            self.patient_playback_until,
        )

    def is_patient_on_line(self) -> bool:
        """Patient audio is generating or still playing on the phone."""
        if self.patient_generating:
            return True
        return time.monotonic() < self.patient_playback_until

    def may_send_patient_audio(self) -> bool:
        """Never drop in-flight patient audio — always flush the current response."""
        if self.patient_generating:
            return True
        if self.is_patient_on_line():
            return False
        if self.agent_speaking:
            return False
        return time.monotonic() >= self.response_allowed_after

    def may_accept_agent_audio(self) -> bool:
        """Block agent audio from reaching OpenAI while patient is on the line."""
        return not self.is_patient_on_line()

    def may_start_patient_response(self) -> bool:
        if self.agent_speaking or self.is_patient_on_line():
            return False
        return time.monotonic() >= self.response_allowed_after
