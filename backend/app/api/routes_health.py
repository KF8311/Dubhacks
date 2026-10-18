import os
import time

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.paths import _candidates, data_dir
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
    resolved = data_dir()
    return {
        "status": status,
        "db": db,
        "version": settings.version,
        "demo_mode": settings.demo_mode,
        "uptime_s": int(time.monotonic() - _started_at),
        "build": os.environ.get("VERCEL_GIT_COMMIT_SHA", "")[:7],
        # Which search path will run. Both answers show the catalog, so this is
        # the only way to tell "deliberately offline" from "the key is missing".
        "search": {
            "offline": settings.offline,
            "serpapi_key": bool(settings.serpapi_key),
        },
        # The answers route 500s when the function ships without its data bundle.
        # Report the resolved directory and every candidate so a deploy can be
        # diagnosed from outside, without dashboard logs.
        "data": {
            "dir": str(resolved),
            "catalog_exists": (resolved / "catalog.json").is_file(),
            "candidates": [
                {"path": str(path), "exists": (path / "catalog.json").is_file()}
                for path in _candidates()
            ],
        },
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
