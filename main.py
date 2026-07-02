"""Uvicorn entry point.

Run with:
    python main.py
    # or
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import uvicorn

from config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
