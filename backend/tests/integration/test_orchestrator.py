import pytest

from app.domain.models import Listing, SearchSpec
from app.sessions.events import EventBus
from app.sessions.orchestrator import SessionOrchestrator
from app.sessions.store import SessionRegistry


@pytest.mark.asyncio
async def test_orchestrator_start_finishes_before_return_on_vercel(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")

    async def search(_spec, _limit):
        return [
            Listing(
                id="lst_phone",
                title="Pixel 9",
                price_cents=79900,
                currency="USD",
                merchant_name="Best Buy",
                merchant_domain="bestbuy.com",
                image_url="",
                product_url="https://bestbuy.com/pixel",
                source="serpapi",
            )
        ], "serpapi"

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[], search=search)
    session = store.create("c1", "phone")
    session.search_spec = SearchSpec(query="phone")
    store.update(session)
    await orch.start(session)
    assert store.get(session.id).stage.value in {"ready", "no_trusted_option"}
    assert [item.title for item in store.listings(session.id)] == ["Pixel 9"]


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


@pytest.mark.asyncio
async def test_orchestrator_falls_back_to_catalog_when_search_times_out():
    async def boom(_spec, _limit):
        raise TimeoutError("search budget")

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[], search=boom)
    session = store.create("c1", "purple t shirt")
    session.search_spec = SearchSpec(query="purple t shirt")
    store.update(session)
    await orch._run(session.id)
    found = [event for event in [e async for e in bus.subscribe(session.id)] if event.type == "listing.found"]
    assert found, "timed-out SerpAPI must still show catalog listings"


@pytest.mark.asyncio
async def test_orchestrator_uses_llm_narrative(monkeypatch):
    async def fake_narrate(_recommendation):
        return "LLM pick story"

    monkeypatch.setattr("app.sessions.orchestrator.narrate", fake_narrate)
    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[])
    session = store.create("c1", "headphones")
    session.search_spec = SearchSpec(query="headphones")
    store.update(session)
    await orch._run(session.id)
    ready = [event for event in [e async for e in bus.subscribe(session.id)] if event.type == "recommendation.ready"]
    assert ready
    assert ready[0].payload["narrative"] == "LLM pick story"
