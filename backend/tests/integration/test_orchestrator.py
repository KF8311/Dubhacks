import pytest

from app.domain.enums import CheckId, TrustStatus
from app.domain.models import Listing, SearchSpec, TrustCheckResult
from app.sessions.events import EventBus
from app.sessions.orchestrator import SessionOrchestrator
from app.sessions.store import SessionRegistry


class _PassingCheck:
    def __init__(self, check_id: CheckId) -> None:
        self.id = check_id
        self.display_name = check_id.value
        self.timeout_s = 1.0
        self.calls = 0

    async def run(self, _target, _ctx):
        self.calls += 1
        return TrustCheckResult(
            id=self.id,
            name=self.display_name,
            status=TrustStatus.PASSED,
            severity=0.0,
            summary="No red flags.",
            source="live",
        )


@pytest.mark.asyncio
async def test_orchestrator_start_finishes_before_return_on_vercel(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")

    async def search(_spec, _limit, **_kwargs):
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
async def test_allowlisted_listing_still_runs_every_check():
    """The allowlist exempts the score floor, not the inspection (D-043)."""
    bestbuy = Listing(
        id="lst_bose",
        title="Bose QuietComfort",
        price_cents=27900,
        currency="USD",
        merchant_name="Best Buy",
        merchant_domain="bestbuy.com",
        image_url="",
        product_url="https://www.bestbuy.com/site/bose",
        source="serpapi",
    )
    checks = [_PassingCheck(check_id) for check_id in CheckId]

    async def search(_spec, _limit, **_kwargs):
        return [bestbuy], "serpapi"

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=checks, search=search)
    session = store.create("c1", "headphones")
    session.search_spec = SearchSpec(query="headphones")
    store.update(session)
    await orch._run(session.id)

    assert all(check.calls == 1 for check in checks)
    investigation = store.investigation_for(session.id, bestbuy.id)
    assert investigation is not None
    assert investigation.allowlisted is True
    assert len(investigation.checks) == len(CheckId)
    assert investigation.score.allowlisted is True
    assert investigation.score.score == 0

    events = [event async for event in bus.subscribe(session.id)]
    completed = [event for event in events if event.type == "check.completed"]
    assert len(completed) == len(CheckId)


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
async def test_orchestrator_persists_listings_and_investigations():
    from app.services.repository import get_repository

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[])
    session = store.create("c1", "headphones")
    session.search_spec = SearchSpec(query="headphones")
    store.update(session)
    await orch._run(session.id)

    listing_ids = [item.id for item in store.listings(session.id)]
    assert listing_ids
    repo = get_repository()
    assert await repo.get_listing(listing_ids[0]) is not None
    inv = store.investigation_for(session.id, listing_ids[0])
    assert inv is not None
    assert await repo.get_investigation_for(session.id, listing_ids[0]) is not None


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

    async def flaky(_spec, _limit, **_kwargs):
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

    async def flaky(_spec, _limit, **_kwargs):
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

    async def flaky(_spec, _limit, **_kwargs):
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
async def test_orchestrator_fails_honestly_instead_of_showing_the_catalog():
    async def boom(_spec, _limit, **_kwargs):
        raise TimeoutError("search budget")

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[], search=boom)
    session = store.create("c1", "purple t shirt")
    session.search_spec = SearchSpec(query="purple t shirt")
    store.update(session)
    await orch._run(session.id)

    events = [event async for event in bus.subscribe(session.id)]
    assert not [event for event in events if event.type == "listing.found"]
    error = [event for event in events if event.type == "session.error"][0]
    assert error.payload["code"] == "SEARCH_UNAVAILABLE"
    assert error.payload["recoverable"] is False
    assert store.get(session.id).stage.value == "failed"
    assert store.listings(session.id) == []


@pytest.mark.asyncio
async def test_orchestrator_survives_a_repository_that_rejects_a_write(monkeypatch):
    """A store failure must not leave the session stuck on "searching"."""
    from app.sessions import orchestrator as module

    class ExplodingRepo:
        async def save_listing(self, _listing):
            raise RuntimeError("E11000 duplicate key error collection: sniff.listings")

        async def save_investigation(self, _inv):
            raise RuntimeError("E11000 duplicate key error collection: sniff.listings")

    monkeypatch.setattr(module, "get_repository", lambda: ExplodingRepo())

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[])
    session = store.create("c1", "headphones")
    session.search_spec = SearchSpec(query="headphones")
    store.update(session)
    await orch._run(session.id)

    assert store.get(session.id).stage.value in {"ready", "no_trusted_option"}
    events = [event async for event in bus.subscribe(session.id)]
    assert events[-1].type == "investigation.complete"
    assert store.listings(session.id)


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


@pytest.mark.asyncio
async def test_an_exhausted_search_quota_fails_once_with_its_own_code():
    """A 429 quota is permanent for the key: retrying only hides the real cause."""
    from app.search.provider import SearchQuotaExhausted

    calls = {"n": 0}

    async def exhausted(_spec, _limit, **_kwargs):
        calls["n"] += 1
        raise SearchQuotaExhausted("Your account has run out of searches.")

    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[], search=exhausted)
    session = store.create("c1", "TUL pens at Office Depot")
    session.search_spec = SearchSpec(query="TUL pens at Office Depot")
    store.update(session)
    await orch._run(session.id)

    events = [event async for event in bus.subscribe(session.id)]
    assert calls["n"] == 1
    error = [event for event in events if event.type == "session.error"][0]
    assert error.payload["code"] == "SEARCH_QUOTA_EXHAUSTED"
    assert "quota" in error.payload["message"].lower()
    assert error.payload["recoverable"] is False
    assert store.get(session.id).stage.value == "failed"
    assert store.listings(session.id) == []
