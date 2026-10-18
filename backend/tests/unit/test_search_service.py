import pytest

from app.domain.models import Listing, SearchSpec
from app.search.catalog import load_catalog
from app.search.service import search

SPEC = SearchSpec(query="headphones")


def _listing(listing_id: str, price_cents: int) -> Listing:
    return Listing(
        id=listing_id,
        title=f"Item {listing_id}",
        price_cents=price_cents,
        merchant_name="Example",
        merchant_domain="example.com",
        image_url="https://img.example/x.jpg",
        product_url=f"https://example.com/{listing_id}",
    )


class StubProvider:
    name = "stub"

    def __init__(self, listings: list[Listing] | None = None, error: Exception | None = None):
        self._listings = listings or []
        self._error = error
        self.calls = 0

    async def search(self, spec: SearchSpec, limit: int) -> list[Listing]:
        self.calls += 1
        if self._error is not None:
            raise self._error
        return self._listings[:limit]


async def test_uses_provider_results_when_available():
    provided = [_listing("lst_a", 1000), _listing("lst_b", 2000)]

    listings, source = await search(
        SPEC, limit=8, provider=StubProvider(provided), catalog=load_catalog()
    )

    assert source == "serpapi"
    assert [item.id for item in listings] == ["lst_a", "lst_b"]


async def test_falls_back_to_catalog_when_provider_raises():
    provider = StubProvider(error=RuntimeError("SERPAPI_KEY unset"))

    listings, source = await search(SPEC, limit=8, provider=provider, catalog=load_catalog())

    assert provider.calls == 1
    assert source == "catalog"
    assert len(listings) == 8


async def test_falls_back_to_catalog_when_provider_returns_nothing():
    listings, source = await search(
        SPEC, limit=8, provider=StubProvider([]), catalog=load_catalog()
    )

    assert source == "catalog"
    assert len(listings) == 8


async def test_catalog_fallback_stays_labelled_catalog():
    listings, _ = await search(
        SPEC, limit=3, provider=StubProvider(error=TimeoutError()), catalog=load_catalog()
    )

    assert {item.source for item in listings} == {"catalog"}


async def test_budget_filters_out_pricier_listings():
    catalog = [_listing("lst_cheap", 9000), _listing("lst_mid", 15000), _listing("lst_dear", 40000)]

    listings, _ = await search(
        SearchSpec(query="headphones", budget_max_cents=15000),
        limit=8,
        provider=StubProvider(error=RuntimeError("down")),
        catalog=catalog,
    )

    assert [item.id for item in listings] == ["lst_cheap", "lst_mid"]


async def test_budget_range_drops_listings_outside_the_band():
    provided = [
        _listing("lst_cheap", 20000),
        _listing("lst_ok", 110000),
        _listing("lst_dear", 200000),
    ]

    listings, source = await search(
        SearchSpec(query="computers", budget_min_cents=100_000, budget_max_cents=120_000),
        limit=8,
        provider=StubProvider(provided),
        catalog=load_catalog(),
    )

    assert source == "serpapi"
    assert [item.id for item in listings] == ["lst_ok"]


async def test_empty_live_search_does_not_swap_computers_for_headphones():
    listings, source = await search(
        SearchSpec(query="computers"),
        limit=8,
        provider=StubProvider([]),
        catalog=load_catalog(),
    )
    assert listings == []
    assert source == "serpapi"


async def test_typed_range_miss_does_not_swap_in_the_headphone_catalog():
    listings, source = await search(
        SearchSpec(query="computers", budget_min_cents=100_000, budget_max_cents=120_000),
        limit=8,
        provider=StubProvider([]),
        catalog=load_catalog(),
    )
    assert listings == []
    assert source == "serpapi"


async def test_budget_that_matches_nothing_keeps_the_catalog():
    catalog = [_listing("lst_cheap", 9000), _listing("lst_dear", 40000)]

    listings, source = await search(
        SearchSpec(query="headphones", budget_max_cents=500),
        limit=8,
        provider=StubProvider(error=RuntimeError("down")),
        catalog=catalog,
    )

    assert source == "catalog"
    assert [item.id for item in listings] == ["lst_cheap", "lst_dear"]


async def test_respects_limit_on_provider_results():
    provided = [_listing(f"lst_{index}", 1000 + index) for index in range(5)]

    listings, _ = await search(
        SPEC, limit=2, provider=StubProvider(provided), catalog=load_catalog()
    )

    assert len(listings) == 2


async def test_the_default_limit_keeps_the_whole_demo_catalog():
    """The demo needs all 8 trusted listings *and* the villain to be present."""

    catalog = load_catalog()

    listings, source = await search(SPEC, provider=StubProvider(), catalog=catalog)

    assert source == "catalog"
    assert len(listings) == len(catalog)
    assert "lst_vln_xm5" in {item.id for item in listings}


async def test_live_mode_reports_unavailable_instead_of_the_catalog():
    listings, source = await search(
        SPEC,
        limit=8,
        provider=StubProvider(error=TimeoutError()),
        catalog=load_catalog(),
        allow_catalog_fallback=False,
    )

    assert listings == []
    assert source == "unavailable"


async def test_live_mode_reports_unavailable_when_the_provider_is_empty():
    listings, source = await search(
        SPEC,
        limit=8,
        provider=StubProvider([]),
        catalog=load_catalog(),
        allow_catalog_fallback=False,
    )

    assert listings == []
    assert source == "unavailable"


async def test_live_mode_keeps_a_typed_range_empty_result():
    """A live query that matches nothing in a typed range is a real answer."""

    listings, source = await search(
        SearchSpec(query="computers", budget_min_cents=100_000, budget_max_cents=120_000),
        limit=8,
        provider=StubProvider([]),
        catalog=load_catalog(),
        allow_catalog_fallback=False,
    )

    assert listings == []
    assert source == "serpapi"


@pytest.mark.parametrize("limit", [0, -1])
async def test_rejects_non_positive_limit(limit: int):
    with pytest.raises(ValueError):
        await search(SPEC, limit=limit, provider=StubProvider(), catalog=load_catalog())


@pytest.mark.asyncio
async def test_quota_exhaustion_is_not_swallowed_by_the_catalog_fallback():
    """The orchestrator needs to tell "out of searches" apart from a timeout."""
    from app.search.provider import SearchQuotaExhausted

    provider = StubProvider(error=SearchQuotaExhausted("Your account has run out of searches."))
    with pytest.raises(SearchQuotaExhausted):
        await search(SPEC, provider=provider)
