"""Twilio REST client — outbound calls, hangup, recording download."""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlencode

import httpx
from twilio.rest import Client

from config import Settings

logger = logging.getLogger(__name__)

ALLOWED_TARGET = "+18054398008"


class TelephonyError(Exception):
    """Raised when telephony operations fail or violate safety rules."""


def _normalize_phone(phone: str) -> str:
    digits = "".join(character for character in phone if character.isdigit())
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    if len(digits) == 10:
        return f"+1{digits}"
    return phone.strip()


def _assert_target_allowed(phone_number: str) -> None:
    if _normalize_phone(phone_number) != ALLOWED_TARGET:
        raise TelephonyError(
            f"Refusing to call {phone_number}. Only {ALLOWED_TARGET} is allowed."
        )


def get_twilio_client(settings: Settings) -> Client:
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)


def webhook_url(settings: Settings, path: str, **query: str) -> str:
    base = settings.public_base_url.rstrip("/")
    if query:
        return f"{base}{path}?{urlencode(query)}"
    return f"{base}{path}"


def media_stream_url(settings: Settings, call_id: str) -> str:
    return settings.media_stream_url(call_id)


def create_outbound_call(
    settings: Settings,
    *,
    call_id: str,
    scenario_path: str,
    bridge_mode: str = "realtime",
) -> str:
    """Place an outbound call to the assessment test line. Returns Twilio Call SID."""
    _assert_target_allowed(settings.target_phone_number)

    client = get_twilio_client(settings)
    outbound_url = webhook_url(
        settings,
        "/voice/outbound",
        call_id=call_id,
        scenario_path=scenario_path,
        bridge_mode=bridge_mode,
    )
    status_url = webhook_url(
        settings,
        "/voice/status",
        call_id=call_id,
        bridge_mode=bridge_mode,
    )
    recording_url = webhook_url(settings, "/voice/recording", call_id=call_id)

    logger.info("Placing outbound call %s → %s", call_id, settings.target_phone_number)
    call = client.calls.create(
        to=settings.target_phone_number,
        from_=settings.twilio_phone_number,
        url=outbound_url,
        method="POST",
        status_callback=status_url,
        status_callback_method="POST",
        status_callback_event=["initiated", "ringing", "answered", "completed"],
        record=True,
        recording_channels="dual",
        recording_status_callback=recording_url,
        recording_status_callback_method="POST",
        timeout=settings.call_ring_timeout_seconds,
    )
    logger.info("Twilio call created: sid=%s status=%s", call.sid, call.status)
    return call.sid


def fetch_call_status(settings: Settings, call_sid: str) -> str:
    client = get_twilio_client(settings)
    call = client.calls(call_sid).fetch()
    return call.status


def hangup_call(settings: Settings, call_sid: str) -> None:
    client = get_twilio_client(settings)
    client.calls(call_sid).update(status="completed")
    logger.info("Hung up call %s", call_sid)


def download_recording(
    settings: Settings,
    recording_url: str,
    destination: Path,
) -> Path:
    """Download Twilio recording MP3 using account credentials."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    mp3_url = f"{recording_url}.mp3" if not recording_url.endswith(".mp3") else recording_url

    with httpx.Client(timeout=60.0) as http:
        response = http.get(
            mp3_url,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
            follow_redirects=True,
        )
        response.raise_for_status()
        destination.write_bytes(response.content)

    logger.info("Recording saved to %s (%s bytes)", destination, destination.stat().st_size)
    return destination
