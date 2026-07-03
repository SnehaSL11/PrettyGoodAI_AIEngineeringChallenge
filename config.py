"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _sanitize_ssl_env() -> None:
    """Drop SSLKEYLOGFILE when missing — broken path breaks Twilio/OpenAI HTTPS."""
    keylog = os.environ.get("SSLKEYLOGFILE")
    if keylog and not Path(keylog).is_file():
        os.environ.pop("SSLKEYLOGFILE", None)


_sanitize_ssl_env()


def call_slug(call_id: str) -> str:
    """Map call-01 → call01 for per-call output folders."""
    if call_id.startswith("call-"):
        suffix = call_id[5:]
        if suffix.isdigit():
            return f"call{int(suffix):02d}"
    return call_id.replace("-", "")


def call_id_from_slug(slug: str) -> str:
    """Map call01 → call-01."""
    if slug.startswith("call") and len(slug) > 4 and slug[4:].isdigit():
        return f"call-{int(slug[4:]):02d}"
    return slug


class Settings(BaseSettings):
    """Central config — all secrets and tunables come from .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Twilio
    twilio_account_sid: str = Field(..., description="Twilio Account SID")
    twilio_auth_token: str = Field(..., description="Twilio Auth Token")
    twilio_phone_number: str = Field(..., description="Outbound caller ID (E.164)")

    # OpenAI
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Target
    target_phone_number: str = Field(
        default="+18054398008",
        description="Pretty Good AI test line",
    )

    # Server
    public_base_url: str = Field(..., description="Public URL for Twilio webhooks")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Realtime patient agent
    openai_realtime_model: str = Field(default="gpt-realtime-2")
    openai_realtime_voice: str = Field(default="shimmer")

    # Chat models (planning + evaluation)
    openai_planning_model: str = Field(default="gpt-4o")
    openai_eval_model: str = Field(default="gpt-4o")

    # Whisper
    whisper_model: str = Field(default="whisper-1")

    # Call behavior
    max_call_duration_seconds: int = Field(default=180)
    response_delay_ms: int = Field(default=400)
    call_ring_timeout_seconds: int = Field(default=30)
    vad_silence_duration_ms: int = Field(
        default=1200,
        description="Wait this long after agent stops before patient may respond",
    )
    agent_turn_cooldown_ms: int = Field(
        default=600,
        description="Extra pause after agent speech before patient audio plays",
    )
    patient_playback_hold_ms: int = Field(
        default=800,
        description="After patient audio is sent, wait this long for phone playback to finish",
    )

    # Paths
    output_dir: Path = Field(default=Path("outputs"))

    @property
    def call_history_path(self) -> Path:
        return self.output_dir / "call_history.json"

    @property
    def bug_report_path(self) -> Path:
        return self.output_dir / "bug_report.md"

    def call_dir(self, call_id: str) -> Path:
        """Per-call folder, e.g. outputs/call01/."""
        return self.output_dir / call_slug(call_id)

    def ensure_call_dir(self, call_id: str) -> Path:
        """Create and return the per-call output folder."""
        directory = self.call_dir(call_id)
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def call_paths(self, call_id: str) -> dict[str, Path]:
        """Standard artifact paths for one call inside its folder."""
        slug = call_slug(call_id)
        call_dir = self.call_dir(call_id)
        return {
            "call_dir": call_dir,
            "scenario": call_dir / f"{slug}-scenario.json",
            "recording": call_dir / f"{slug}-recording.mp3",
            "events": call_dir / f"{slug}-events.json",
            "session": call_dir / f"{slug}-session.json",
            "transcript_txt": call_dir / f"{slug}-transcript.txt",
            "transcript_json": call_dir / f"{slug}-transcript-full.json",
            "bugs": call_dir / f"{slug}-bugs.md",
        }

    def call_scenario_path(self, call_id: str) -> Path:
        return self.call_paths(call_id)["scenario"]

    def resolve_scenario_path(self, call_id: str) -> Path | None:
        """Scenario JSON for a call (new layout, then legacy flat layout)."""
        paths = self.call_paths(call_id)
        if paths["scenario"].exists():
            return paths["scenario"]
        legacy = self.output_dir / "scenarios" / f"{call_id}.json"
        if legacy.exists():
            return legacy
        return None

    def resolve_recording_path(self, call_id: str) -> Path | None:
        paths = self.call_paths(call_id)
        if paths["recording"].exists():
            return paths["recording"]
        legacy = self.output_dir / "recordings" / f"{call_id}.mp3"
        if legacy.exists():
            return legacy
        return None

    def ensure_output_dirs(self) -> None:
        """Create the top-level output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def media_stream_url(self, call_id: str) -> str:
        """WebSocket URL Twilio Media Streams connects to."""
        base = self.public_base_url.rstrip("/")
        ws_base = base.replace("https://", "wss://").replace("http://", "ws://")
        return f"{ws_base}/media/{call_id}"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    settings = Settings()
    settings.ensure_output_dirs()
    return settings
