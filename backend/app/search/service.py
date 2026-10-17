"""Product search with a curated-catalog fallback (D-004, D-011)."""

from __future__ import annotations

from app.core.timeouts import MAX_LISTINGS
from app.domain.models import Listing, SearchSpec
from app.search.catalog import load_catalog
from app.search.provider import SearchProvider
from app.search.serpapi import SerpAPIProvider


def _within_budget(listings: list[Listing], spec: SearchSpec) -> list[Listing]:
    if spec.budget_max_cents is None:
        return listings
    return [item for item in listings if item.price_cents <= spec.budget_max_cents]


async def search(
    spec: SearchSpec,
    limit: int = MAX_LISTINGS,
    *,
    provider: SearchProvider | None = None,
    catalog: list[Listing] | None = None,
) -> tuple[list[Listing], str]:
    """Return ``(listings, source)`` where source is ``serpapi`` or ``catalog``.

    Any provider failure — missing key, timeout, HTTP error, empty payload — falls
    back to the catalog. The demo never shows an empty grid because a third party
    is down.
    """
    if limit <= 0:
        raise ValueError("limit must be positive")

    active = provider if provider is not None else SerpAPIProvider()
    try:
        results = await active.search(spec, limit)
    except Exception:  # noqa: BLE001 — any provider fault must reach the fallback
        results = []

    if results:
        listings, source = list(results), "serpapi"
    else:
        listings = catalog if catalog is not None else load_catalog()
        source = "catalog"

    return _within_budget(listings, spec)[:limit], source
