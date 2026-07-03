"""Whisper transcription of call recordings."""

from __future__ import annotations

import logging
from pathlib import Path

from config import Settings
from planning.llm import get_openai_client

logger = logging.getLogger(__name__)


def transcribe_recording(settings: Settings, recording_path: Path) -> str:
    """Transcribe an MP3 recording with OpenAI Whisper."""
    if not recording_path.exists():
        raise FileNotFoundError(f"Recording not found: {recording_path}")

    client = get_openai_client()
    logger.info("Transcribing %s with model=%s", recording_path.name, settings.whisper_model)

    with recording_path.open("rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
            response_format="text",
        )

    text = response if isinstance(response, str) else str(response)
    return text.strip()
