"""Run one session end to end in-process, for a terminal demo or a smoke check.

No HTTP server, no database, no network: the orchestrator, the allowlist, the
fixtures, and the scoring all run exactly as they do in the app.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass

from app.core.config import Settings
from app.domain.models import SearchSpec
from app.sessions.events import EventBus
from app.sessions.orchestrator import SessionOrchestrator
from app.sessions.store import SessionRegistry


@dataclass(frozen=True)
class ReplayReport:
    session_id: str
    stage: str
    listings: int
    trusted: int
    caution: int
    danger: int
    danger_ids: list[str]
    picked_id: str | None
    median_cents: int | None
    savings_cents: int | None
    events: dict[str, int]

    def as_dict(self) -> dict:
        """The report without the random session id, so two runs compare equal."""
        payload = asdict(self)
        payload.pop("session_id")
        return payload


async def replay(query: str = "noise cancelling headphones") -> ReplayReport:
    store, bus = SessionRegistry(), EventBus()
    # Offline on purpose: the demo must produce the same numbers with no network.
    orchestrator = SessionOrchestrator(store, bus, config=Settings(offline=True))
    session = store.create("replay", query)
    session.search_spec = SearchSpec(query=query)

    await orchestrator._run(session.id)

    final = store.get(session.id)
    assert final is not None

    events = list(bus._log[session.id])
    scores = {
        inv.listing_id: inv.score
        for inv in store._investigations.get(session.id, [])
    }
    recommendation = store._recommendations.get(session.id, {})

    return ReplayReport(
        session_id=session.id,
        stage=final.stage.value,
        listings=final.stats.listings,
        trusted=final.stats.trusted,
        caution=final.stats.caution,
        danger=final.stats.danger,
        danger_ids=sorted(
            listing_id
            for listing_id, score in scores.items()
            if score.verdict.value == "danger"
        ),
        picked_id=recommendation.get("recommended_listing_id"),
        median_cents=recommendation.get("median_trusted_cents"),
        savings_cents=recommendation.get("savings_cents"),
        events=dict(sorted(Counter(event.type for event in events).items())),
    )
