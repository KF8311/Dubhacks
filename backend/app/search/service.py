from __future__ import annotations

import asyncio

from app.core.ids import listing_id
from app.core.timeouts import MAX_LISTINGS, SEARCH_S
from app.domain.models import Listing, SearchSpec


def _stub_listings() -> list[Listing]:
    hero_url = "https://www.bestbuy.com/site/sony-wh-1000xm5/6505727.p"
    villain_url = "https://premium-audio-deals.shop/sony-wh-1000xm5"
    return [
        Listing(
            id=listing_id(hero_url),
            title="Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
            price_cents=32800,
            merchant_name="Best Buy",
            merchant_domain="bestbuy.com",
            image_url="",
            product_url=hero_url,
            category="audio",
            source="catalog",
        ),
        Listing(
            id=listing_id(villain_url),
            title="Sony WH-1000XM5 — Warehouse Deal",
            price_cents=8900,
            merchant_name="Premium Audio Deals",
            merchant_domain="premium-audio-deals.shop",
            image_url="",
            product_url=villain_url,
            category="audio",
            source="catalog",
        ),
    ]


async def _provider_search(spec: SearchSpec, limit: int) -> list[Listing]:
    del spec, limit
    raise RuntimeError("serpapi not wired")


async def search(spec: SearchSpec, limit: int = MAX_LISTINGS) -> tuple[list[Listing], str]:
    try:
        listings = await asyncio.wait_for(_provider_search(spec, limit), timeout=SEARCH_S)
        source = "serpapi"
        if not listings:
            raise RuntimeError("empty serpapi")
    except Exception:
        listings = _stub_listings()
        source = "catalog"
    if spec.budget_max_cents:
        in_budget = [item for item in listings if item.price_cents <= spec.budget_max_cents]
        if in_budget:
            listings = in_budget
    return listings[:limit], source
