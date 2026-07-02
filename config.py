"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    openai_realtime_model: str = Field(default="gpt-4o-realtime-preview")
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

    # Paths
    output_dir: Path = Field(default=Path("outputs"))

    @property
    def recordings_dir(self) -> Path:
        return self.output_dir / "recordings"

    @property
    def transcripts_dir(self) -> Path:
        return self.output_dir / "transcripts"

    @property
    def scenarios_dir(self) -> Path:
        return self.output_dir / "scenarios"

    @property
    def logs_dir(self) -> Path:
        return self.output_dir / "logs"

    @property
    def call_history_path(self) -> Path:
        return self.output_dir / "call_history.json"

    @property
    def bug_report_path(self) -> Path:
        return self.output_dir / "bug_report.md"

    def ensure_output_dirs(self) -> None:
        """Create output directories if they don't exist."""
        for directory in (
            self.output_dir,
            self.recordings_dir,
            self.transcripts_dir,
            self.scenarios_dir,
            self.logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    settings = Settings()
    settings.ensure_output_dirs()
    return settings
