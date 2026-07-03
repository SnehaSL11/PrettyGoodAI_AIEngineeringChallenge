"""Twilio mulaw audio helpers for Media Streams."""

from __future__ import annotations

import base64

try:
    import audioop
except ImportError:  # Python 3.13+
    import audioop_lts as audioop  # type: ignore[no-redef]

# 20 ms of mulaw silence at 8 kHz (160 samples)
MULAW_SILENCE_FRAME = base64.b64encode(audioop.lin2ulaw(b"\x00" * 160, 2)).decode("ascii")


def decode_mulaw_payload(payload_b64: str) -> bytes:
    """Decode base64 mulaw payload from Twilio into PCM16 bytes."""
    mulaw_bytes = base64.b64decode(payload_b64)
    return audioop.ulaw2lin(mulaw_bytes, 2)


def encode_mulaw_payload(pcm16: bytes) -> str:
    """Encode PCM16 bytes to base64 mulaw for Twilio Media Streams."""
    mulaw_bytes = audioop.lin2ulaw(pcm16, 2)
    return base64.b64encode(mulaw_bytes).decode("ascii")


def silence_payload() -> str:
    """Return a base64 mulaw silence frame for keepalive playback."""
    return MULAW_SILENCE_FRAME


TWILIO_SAMPLE_RATE = 8000
OPENAI_SAMPLE_RATE = 24000


def resample_pcm16(pcm16: bytes, from_rate: int, to_rate: int) -> bytes:
    """Resample mono PCM16 audio between sample rates."""
    if from_rate == to_rate:
        return pcm16
    converted, _ = audioop.ratecv(pcm16, 2, 1, from_rate, to_rate, None)
    return converted


def twilio_mulaw_b64_to_openai_pcm16_b64(payload_b64: str) -> str:
    """Twilio inbound frame → OpenAI Realtime input_audio_buffer format."""
    pcm_8k = decode_mulaw_payload(payload_b64)
    pcm_24k = resample_pcm16(pcm_8k, TWILIO_SAMPLE_RATE, OPENAI_SAMPLE_RATE)
    return base64.b64encode(pcm_24k).decode("ascii")


def openai_pcm16_b64_to_twilio_mulaw_b64(payload_b64: str) -> str:
    """OpenAI Realtime audio delta → Twilio outbound media frame."""
    pcm_24k = base64.b64decode(payload_b64)
    pcm_8k = resample_pcm16(pcm_24k, OPENAI_SAMPLE_RATE, TWILIO_SAMPLE_RATE)
    return encode_mulaw_payload(pcm_8k)
