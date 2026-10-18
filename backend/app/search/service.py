"""Product search with a curated-catalog fallback (D-004, D-011)."""

from __future__ import annotations

from app.core.timeouts import MAX_LISTINGS
from app.domain.models import Listing, SearchSpec
from app.search.catalog import catalog_covers, load_catalog
from app.search.provider import SearchProvider
from app.search.serpapi import SerpAPIProvider


def _within_budget(listings: list[Listing], spec: SearchSpec) -> list[Listing]:
    lo, hi = spec.budget_min_cents, spec.budget_max_cents
    if lo is None and hi is None:
        return listings

    def in_band(item: Listing) -> bool:
        if lo is not None and item.price_cents < lo:
            return False
        if hi is not None and item.price_cents > hi:
            return False
        return True

    matched = [item for item in listings if in_band(item)]
    if matched:
        return matched
    # D-022: a ceiling-only grocery-scale cap vs the headphone catalog.
    # A typed range must not fall back to $200 junk (D-024).
    if lo is None:
        return listings
    return matched


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
        matched = _within_budget(listings, spec)
        if matched or spec.budget_min_cents is not None:
            return matched[:limit], source
        return listings[:limit], source

    if spec.budget_min_cents is not None:
        return [], "serpapi"

    if not catalog_covers(spec.query):
        return [], "serpapi"

    listings = catalog if catalog is not None else load_catalog()
    return _within_budget(listings, spec)[:limit], "catalog"
