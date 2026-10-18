from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone

from app.checks.base import CheckContext, CheckTarget, TrustCheck
from app.checks.registry import get_checks
from app.checks.runner import run_checks
from app.core.config import get_settings
from app.core.ids import new_id
from app.core.timeouts import CHECK_CONCURRENCY, INVESTIGATION_BUDGET_S, MAX_LISTINGS, SEARCH_S
from app.domain.enums import SessionStage, TrustStatus, Verdict
from app.domain.models import Investigation, Listing, Session, SessionStats, TrustCheckResult
from app.search.catalog import load_catalog
from app.search.service import search as default_search
from app.services.llm import narrate
from app.sessions.events import EventBus
from app.sessions.store import SessionRegistry
from app.trust.allowlist import Allowlist, load_allowlist
from app.trust.recommendation import recommend
from app.trust.scoring import score_investigation


def _load_allowlist() -> Allowlist:
    try:
        return load_allowlist()
    except Exception:  # noqa: BLE001 — missing data file must not kill the session
        return Allowlist(frozenset())


class SessionOrchestrator:
    def __init__(
        self,
        store: SessionRegistry,
        bus: EventBus,
        checks: list[TrustCheck] | None = None,
        search=default_search,
        config=None,
    ) -> None:
        self.store = store
        self.bus = bus
        self.checks = checks
        self.search = search
        self.config = config

    def _search_timeout(self) -> float:
        # Shopping + immersive store lookups need more than SEARCH_S or
        # wait_for cancels a live result and the grid goes empty.
        return 12.0 if os.environ.get("VERCEL") else max(SEARCH_S, 8.0)

    async def _search_with_retry(
        self, session_id: str, spec
    ) -> tuple[list[Listing], str] | None:
        """Live search with one retry. Never substitutes the curated catalog.

        A longer wait is better than unrelated products in the grid: two attempts
        at the live provider, then an honest failure the user can retry.
        """
        empty = False
        for _attempt in range(2):
            try:
                listings, source = await asyncio.wait_for(
                    self.search(spec, MAX_LISTINGS, allow_catalog_fallback=False),
                    timeout=self._search_timeout(),
                )
            except Exception:  # noqa: BLE001 — retry once, then fail
                continue
            # An empty live result is worth one retry; a provider still running
            # after the budget is not worth a second wait.
            if source == "serpapi" and listings:
                return listings, source
            if source == "serpapi":
                empty = True
        if empty:
            return [], "serpapi"
        self.bus.publish(
            session_id,
            "session.error",
            {
                "code": "SEARCH_UNAVAILABLE",
                "message": (
                    "Live search is taking too long. We did not substitute "
                    "unrelated products — start over to try again."
                ),
                "recoverable": False,
            },
        )
        return None

    def _fail_session(self, session_id: str, session: Session) -> None:
        session.stage = SessionStage.FAILED
        session.updated_at = datetime.now(timezone.utc)
        self.store.update(session)
        self.bus.publish(session_id, "session.stage", {"stage": session.stage.value})
        self.bus.close(session_id)

    def _active_checks(self) -> list[TrustCheck]:
        if self.checks is None:
            return get_checks()
        return list(self.checks)

    async def start(self, session: Session) -> None:
        # Vercel freezes the isolate when the HTTP handler returns, so the
        # background task never finishes. Await the run there; locally keep
        # fire-and-forget so SSE can stream while POST /answers returns 202.
        if os.environ.get("VERCEL"):
            await self._run(session.id)
            return
        asyncio.create_task(self._run(session.id), name=f"orch-{session.id}")

    async def _run(self, session_id: str) -> None:
        session = self.store.get(session_id)
        if session is None:
            return
        started = time.monotonic()
        session.stage = SessionStage.SEARCHING
        self.store.update(session)
        self.bus.publish(session_id, "session.stage", {"stage": session.stage.value})
        settings = self.config or get_settings()
        self.bus.publish(
            session_id,
            "search.started",
            {
                "query": session.search_spec.query,
                "providers": ["catalog"] if getattr(settings, "offline", False) else ["serpapi"],
            },
        )
        if getattr(settings, "offline", False):
            # Replay and refusal tests must stay on the curated catalog even
            # when a search key is present in the environment.
            listings, source = load_catalog()[:MAX_LISTINGS], "catalog"
        else:
            outcome = await self._search_with_retry(session_id, session.search_spec)
            if outcome is None:
                self._fail_session(session_id, session)
                return
            listings, source = outcome

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

        allowlist = _load_allowlist()
        checks = self._active_checks()
        ctx = CheckContext(allowlist=allowlist, config=self.config or get_settings())
        sem = asyncio.Semaphore(CHECK_CONCURRENCY)

        async def investigate(listing: Listing) -> None:
            async with sem:
                await self._investigate_listing(session_id, listing, checks, ctx, allowlist)

        if listings:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*(investigate(item) for item in listings)),
                    timeout=INVESTIGATION_BUDGET_S,
                )
            except TimeoutError:
                self.bus.publish(
                    session_id,
                    "session.error",
                    {
                        "code": "INVESTIGATION_TIMEOUT",
                        "message": "Investigation hit the 14s budget.",
                        "recoverable": True,
                    },
                )

        pairs = []
        for listing in listings:
            inv = self.store.investigation_for(session_id, listing.id)
            if inv is not None:
                pairs.append((listing, inv.score))

        rec = recommend(pairs)
        session.recommended_listing_id = rec.recommended_listing_id
        story = await narrate(rec)
        payload = {
            "recommended_listing_id": rec.recommended_listing_id,
            "median_trusted_cents": rec.median_trusted_cents,
            "savings_cents": rec.savings_cents,
            "eligible_ids": rec.eligible_ids,
            "reason": rec.reason,
            "no_trusted_option": rec.no_trusted_option,
            "narrative": story,
        }
        self.store.set_recommendation(session_id, payload)
        self.bus.publish(session_id, "recommendation.ready", payload)

        duration_ms = int((time.monotonic() - started) * 1000)
        trusted = caution = danger = 0
        for _, score in pairs:
            if score.verdict == Verdict.TRUSTED:
                trusted += 1
            elif score.verdict == Verdict.CAUTION:
                caution += 1
            else:
                danger += 1
        session.stats = SessionStats(
            listings=len(listings),
            trusted=trusted,
            caution=caution,
            danger=danger,
            duration_ms=duration_ms,
        )
        if rec.no_trusted_option or not listings:
            session.stage = SessionStage.NO_TRUSTED_OPTION
        else:
            session.stage = SessionStage.READY
        session.updated_at = datetime.now(timezone.utc)
        self.store.update(session)
        self.bus.publish(session_id, "session.stage", {"stage": session.stage.value})
        self.bus.publish(
            session_id,
            "investigation.complete",
            {"stats": session.stats.model_dump(), "duration_ms": duration_ms},
        )
        self.bus.close(session_id)

    async def _investigate_listing(
        self,
        session_id: str,
        listing: Listing,
        checks: list[TrustCheck],
        ctx: CheckContext,
        allowlist: Allowlist,
    ) -> None:
        started = time.monotonic()
        allowlisted = allowlist.matches(listing.merchant_domain)
        target = CheckTarget(
            listing_id=listing.id,
            product_url=listing.product_url,
            merchant_domain=listing.merchant_domain,
            merchant_name=listing.merchant_name,
            price_cents=listing.price_cents,
            category=listing.category,
        )
        results: list[TrustCheckResult] = []
        for index, check in enumerate(checks):
            self.bus.publish(
                session_id,
                "check.started",
                {
                    "listing_id": listing.id,
                    "check_id": check.id.value,
                    "name": check.display_name,
                    "index": index,
                },
            )

        if allowlisted:
            for check in checks:
                result = TrustCheckResult(
                    id=check.id,
                    name=check.display_name,
                    status=TrustStatus.SKIPPED,
                    severity=0,
                    summary="Allowlisted merchant; checks skipped.",
                    source="allowlist",
                )
                results.append(result)
                self.bus.publish(
                    session_id,
                    "check.completed",
                    {"listing_id": listing.id, "check": result.model_dump(mode="json")},
                )
        elif checks:
            async for result in run_checks(target, checks, ctx=ctx, timeout_s=6.0):
                results.append(result)
                self.bus.publish(
                    session_id,
                    "check.completed",
                    {"listing_id": listing.id, "check": result.model_dump(mode="json")},
                )

        score = score_investigation(results, allowlisted=allowlisted)
        inv = Investigation(
            id=new_id("inv"),
            listing_id=listing.id,
            session_id=session_id,
            checks=results,
            score=score,
            allowlisted=allowlisted,
            duration_ms=int((time.monotonic() - started) * 1000),
            created_at=datetime.now(timezone.utc),
        )
        self.store.attach_investigation(session_id, inv)
        self.bus.publish(
            session_id,
            "listing.scored",
            {
                "listing_id": listing.id,
                "score": score.score,
                "verdict": score.verdict.value,
                "confidence": score.confidence,
                "top_reason": score.top_reason,
                "allowlisted": score.allowlisted,
                "penalties": [p.model_dump(mode="json") for p in score.penalties],
            },
        )
