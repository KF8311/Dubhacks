import pytest

from app.domain.enums import CheckId, TrustStatus
from app.domain.models import SearchSpec, TrustCheckResult
from app.sessions.events import EventBus
from app.sessions.orchestrator import SessionOrchestrator
from app.sessions.store import SessionRegistry


class FakeCheck:
    timeout_s = 1.0

    def __init__(self, id):
        self.id, self.display_name = id, id.value

    async def run(self, target, ctx):
        return TrustCheckResult(
            id=self.id,
            name=self.display_name,
            status=TrustStatus.PASSED,
            severity=0,
            summary="ok",
            source="live",
        )


@pytest.mark.asyncio
async def test_full_investigation_emits_score_and_recommendation():
    store, bus = SessionRegistry(), EventBus()
    checks = [FakeCheck(i) for i in CheckId]
    orch = SessionOrchestrator(store, bus, checks=checks)
    s = store.create("c1", "headphones")
    s.search_spec = SearchSpec(query="headphones")
    await orch._run(s.id)
    events = [e async for e in bus.subscribe(s.id)]
    types = [e.type for e in events]
    assert "listing.scored" in types
    assert "recommendation.ready" in types
    assert types[-1] == "investigation.complete"
