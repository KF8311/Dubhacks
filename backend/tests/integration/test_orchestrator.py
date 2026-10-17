import pytest

from app.domain.models import SearchSpec
from app.sessions.events import EventBus
from app.sessions.orchestrator import SessionOrchestrator
from app.sessions.store import SessionRegistry


@pytest.mark.asyncio
async def test_orchestrator_emits_listings_and_completes(monkeypatch):
    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[])
    session = store.create("c1", "headphones")
    session.search_spec = SearchSpec(query="headphones")
    store.update(session)
    await orch._run(session.id)
    events = [e async for e in bus.subscribe(session.id)]
    types = [e.type for e in events]
    assert "search.started" in types
    assert "listing.found" in types
    assert types[-1] == "investigation.complete"
