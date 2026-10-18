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
async def test_orchestrator_retries_search_after_one_timeout():
    calls = {"n": 0}
    drink = Listing(
        id="lst_drink",
        title="Celsius",
        price_cents=2147,
        currency="USD",
        merchant_name="Walmart",
        merchant_domain="walmart.com",
        image_url="",
        product_url="https://walmart.com/celsius",
        source="serpapi",
    )

    async def flaky(_spec, _limit):
        calls["n"] += 1
        if calls["n"] == 1:
            raise TimeoutError("first try")
        return [drink], "serpapi"

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[], search=flaky)
    session = store.create("c1", "energy drinks")
    session.search_spec = SearchSpec(query="energy drinks")
    store.update(session)
    await orch._run(session.id)
    titles = [item.title for item in store.listings(session.id)]
    assert calls["n"] == 2
    assert titles == ["Celsius"]


@pytest.mark.asyncio
async def test_orchestrator_retries_when_first_live_search_is_empty():
    calls = {"n": 0}
    pen = Listing(
        id="lst_pen",
        title="BIC Cristal",
        price_cents=379,
        currency="USD",
        merchant_name="Walmart",
        merchant_domain="walmart.com",
        image_url="",
        product_url="https://walmart.com/bic",
        source="serpapi",
    )

    async def flaky(_spec, _limit):
        calls["n"] += 1
        if calls["n"] == 1:
            return [], "serpapi"
        return [pen], "serpapi"

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[], search=flaky)
    session = store.create("c1", "pens")
    session.search_spec = SearchSpec(query="pens")
    store.update(session)
    await orch._run(session.id)
    titles = [item.title for item in store.listings(session.id)]
    assert calls["n"] == 2
    assert titles == ["BIC Cristal"]


@pytest.mark.asyncio
async def test_orchestrator_retries_when_first_search_returns_catalog():
    calls = {"n": 0}
    drink = Listing(
        id="lst_drink",
        title="Celsius",
        price_cents=2147,
        currency="USD",
        merchant_name="Walmart",
        merchant_domain="walmart.com",
        image_url="",
        product_url="https://walmart.com/celsius",
        source="serpapi",
    )
    headphones = Listing(
        id="lst_sony",
        title="Sony WH-1000XM5",
        price_cents=32800,
        currency="USD",
        merchant_name="Best Buy",
        merchant_domain="bestbuy.com",
        image_url="",
        product_url="https://bestbuy.com/sony",
        source="catalog",
    )

    async def flaky(_spec, _limit):
        calls["n"] += 1
        if calls["n"] == 1:
            return [headphones], "catalog"
        return [drink], "serpapi"

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[], search=flaky)
    session = store.create("c1", "energy drinks")
    session.search_spec = SearchSpec(query="energy drinks")
    store.update(session)
    await orch._run(session.id)
    titles = [item.title for item in store.listings(session.id)]
    assert calls["n"] == 2
    assert titles == ["Celsius"]


@pytest.mark.asyncio
async def test_orchestrator_does_not_show_headphones_when_a_non_audio_search_times_out():
    async def boom(_spec, _limit):
        raise TimeoutError("search budget")

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[], search=boom)
    session = store.create("c1", "purple t shirt")
    session.search_spec = SearchSpec(query="purple t shirt")
    store.update(session)
    await orch._run(session.id)
    found = [event for event in [e async for e in bus.subscribe(session.id)] if event.type == "listing.found"]
    assert found == []
    assert store.get(session.id).stage.value == "no_trusted_option"


@pytest.mark.asyncio
async def test_orchestrator_falls_back_to_catalog_when_headphone_search_times_out():
    async def boom(_spec, _limit):
        raise TimeoutError("search budget")

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[], search=boom)
    session = store.create("c1", "headphones")
    session.search_spec = SearchSpec(query="headphones")
    store.update(session)
    await orch._run(session.id)
    found = [event for event in [e async for e in bus.subscribe(session.id)] if event.type == "listing.found"]
    assert found, "timed-out headphone search may still show the curated catalog"


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
