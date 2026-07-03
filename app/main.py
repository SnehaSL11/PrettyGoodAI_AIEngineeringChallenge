"""FastAPI application — Twilio webhooks and health checks."""

from fastapi import FastAPI

from app.routes.voice import router as voice_router
from config import get_settings

app = FastAPI(
    title="Patient Voice Bot",
    description="Automated patient simulator for Pretty Good AI challenge",
    version="0.4.0",
)

app.include_router(voice_router)


@app.get("/health")
async def health() -> dict:
    """Verify the server is running. Use before starting ngrok."""
    settings = get_settings()
    return {
        "status": "ok",
        "target_phone": settings.target_phone_number,
        "public_base_url": settings.public_base_url,
        "phase": 4,
    }
