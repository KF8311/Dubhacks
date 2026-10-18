import time

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.errors import AppError
from app.payments.memory import store as payment_store
from app.payments.mock_vic import reset as reset_vic
from app.services.repository import get_db_status, reset_repository
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
    db = get_db_status()
    status = "ok" if db == "ok" else "degraded"
    return {
        "status": status,
        "db": db,
        "version": settings.version,
        "demo_mode": settings.demo_mode,
        # Offline serves the bundled catalog; live mode must not reuse such a
        # backend, or the demo silently shows canned listings.
        "offline": settings.offline,
        "uptime_s": int(time.monotonic() - _started_at),
    }


@router.post("/api/demo/reset")
async def demo_reset() -> dict:
    settings = get_settings()
    if not settings.demo_mode:
        raise AppError(
            "DEMO_RESET_DISABLED",
            "Demo reset is only available when DEMO_MODE is on.",
            status_code=403,
        )
    registry.clear()
    bus.reset()
    payment_store.clear()
    reset_vic()
    await reset_repository()
    return {"ok": True, "cleared": ["sessions", "investigations", "checkouts", "receipts"]}
