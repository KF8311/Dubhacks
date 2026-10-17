import time

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.errors import AppError
from app.sessions.events import bus
from app.sessions.store import registry

router = APIRouter()
_started_at = time.monotonic()


@router.get("/")
def root() -> dict:
    return {
        "service": "sniff-visa",
        "health": "/api/health",
        "sessions": "POST /api/sessions",
        "docs": "/docs",
    }


@router.get("/api/health")
def health() -> dict:
    settings = get_settings()
    db = "ok" if settings.mongodb_uri else "unavailable"
    status = "ok" if db == "ok" else "degraded"
    return {
        "status": status,
        "db": db,
        "version": settings.version,
        "demo_mode": settings.demo_mode,
        "uptime_s": int(time.monotonic() - _started_at),
    }


@router.post("/api/demo/reset")
def demo_reset() -> dict:
    settings = get_settings()
    if not settings.demo_mode:
        raise AppError(
            "DEMO_RESET_DISABLED",
            "Demo reset is only available when DEMO_MODE is on.",
            status_code=403,
        )
    registry.clear()
    bus.reset()
    return {"ok": True, "cleared": ["sessions", "investigations", "checkouts", "receipts"]}
