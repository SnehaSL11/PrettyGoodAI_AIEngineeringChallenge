"""FastAPI application — Twilio webhooks and health checks."""

from fastapi import FastAPI

from config import get_settings

app = FastAPI(
    title="Patient Voice Bot",
    description="Automated patient simulator for Pretty Good AI challenge",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict:
    """Verify the server is running. Use before starting ngrok."""
    settings = get_settings()
    return {
        "status": "ok",
        "target_phone": settings.target_phone_number,
        "public_base_url": settings.public_base_url,
    }
