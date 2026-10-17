from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone

from app.core.timeouts import MAX_LISTINGS, SEARCH_S
from app.domain.enums import SessionStage
from app.domain.models import Session, SessionStats
from app.search.service import search as default_search
from app.sessions.events import EventBus
from app.sessions.store import SessionRegistry


class SessionOrchestrator:
    def __init__(
        self,
        store: SessionRegistry,
        bus: EventBus,
        checks: list | None = None,
        search=default_search,
    ) -> None:
        self.store = store
        self.bus = bus
        self.checks = checks or []
        self.search = search

    async def start(self, session: Session) -> None:
        asyncio.create_task(self._run(session.id), name=f"orch-{session.id}")

    async def _run(self, session_id: str) -> None:
        session = self.store.get(session_id)
        if session is None:
            return
        started = time.monotonic()
        session.stage = SessionStage.SEARCHING
        self.store.update(session)
        self.bus.publish(session_id, "session.stage", {"stage": session.stage.value})
        self.bus.publish(
            session_id,
            "search.started",
            {"query": session.search_spec.query, "providers": ["catalog"]},
        )
        try:
            listings, source = await asyncio.wait_for(
                self.search(session.search_spec, MAX_LISTINGS),
                timeout=SEARCH_S,
            )
        except Exception:
            listings, source = [], "catalog"
            self.bus.publish(
                session_id,
                "session.error",
                {
                    "code": "SEARCH_FAILED",
                    "message": "Search failed; no listings.",
                    "recoverable": True,
                },
            )

        self.bus.publish(
            session_id,
            "search.completed",
            {"count": len(listings), "source": source},
        )
        session.listing_ids = [item.id for item in listings]
        self.store.replace_listings(session_id, listings)
        session.stage = SessionStage.INVESTIGATING
        self.store.update(session)
        self.bus.publish(session_id, "session.stage", {"stage": session.stage.value})

        for rank, listing in enumerate(listings, start=1):
            self.bus.publish(
                session_id,
                "listing.found",
                {"listing": listing.model_dump(mode="json"), "rank": rank},
            )

        # Task 16 fans out self.checks. Skeleton skips scoring.
        duration_ms = int((time.monotonic() - started) * 1000)
        session.stats = SessionStats(listings=len(listings), duration_ms=duration_ms)
        session.stage = SessionStage.READY if listings else SessionStage.FAILED
        session.updated_at = datetime.now(timezone.utc)
        self.store.update(session)
        self.bus.publish(session_id, "session.stage", {"stage": session.stage.value})
        self.bus.publish(
            session_id,
            "investigation.complete",
            {"stats": session.stats.model_dump(), "duration_ms": duration_ms},
        )
        self.bus.close(session_id)
