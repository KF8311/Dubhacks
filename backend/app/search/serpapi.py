from __future__ import annotations

import asyncio
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

import httpx

from app.core.config import get_settings
from app.core.ids import listing_id
from app.core.timeouts import MAX_LISTINGS, SEARCH_S
from app.domain.models import Listing, SearchSpec

SERPAPI_URL = "https://serpapi.com/search.json"
GOOGLE_HOSTS = frozenset(
    {
        "google.com",
        "www.google.com",
        "shopping.google.com",
        "googleusercontent.com",
    }
)

# Google Shopping often omits a store URL and only names the seller in `source`.
KNOWN_SOURCES = {
    "amazon": "amazon.com",
    "asos": "asos.com",
    "best buy": "bestbuy.com",
    "bestbuy": "bestbuy.com",
    "costco": "costco.com",
    "custom ink": "customink.com",
    "cvs": "cvs.com",
    "ebay": "ebay.com",
    "gap": "gap.com",
    "h&m": "hm.com",
    "hy-vee": "hy-vee.com",
    "hyvee": "hy-vee.com",
    "instacart": "instacart.com",
    "kroger": "kroger.com",
    "macys": "macys.com",
    "macy's": "macys.com",
    "nike": "nike.com",
    "nordstrom": "nordstrom.com",
    "old navy": "oldnavy.gap.com",
    "sams club": "samsclub.com",
    "sam's club": "samsclub.com",
    "target": "target.com",
    "uniqlo": "uniqlo.com",
    "walgreens": "walgreens.com",
    "walmart": "walmart.com",
    "whole foods": "wholefoodsmarket.com",
    "zara": "zara.com",
}


def merchant_host(url: str) -> str:
    if not url:
        return ""
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _product_url(item: dict) -> str:
    for key in ("product_link", "link"):
        value = str(item.get(key) or "").strip()
        host = merchant_host(value)
        if host and host not in GOOGLE_HOSTS:
            return value
    return ""


def domain_from_source(source: str) -> str:
    raw = (source or "").strip().lower()
    if not raw:
        return ""
    if " " not in raw and "." in raw:
        host = merchant_host(f"https://{raw}")
        if host and host not in GOOGLE_HOSTS:
            return host
    head = raw.split("-", 1)[0].strip()
    if head in KNOWN_SOURCES:
        return KNOWN_SOURCES[head]
    for name, domain in KNOWN_SOURCES.items():
        if raw.startswith(name) or f" {name} " in f" {raw} ":
            return domain
    return ""


def _price_cents(item: dict) -> int | None:
    raw = item.get("extracted_price")
    if raw is None:
        return None
    try:
        cents = int((Decimal(str(raw)) * 100).quantize(Decimal("1")))
    except (InvalidOperation, ValueError):
        return None
    return cents if cents > 0 else None


def listing_from_shopping_result(item: dict) -> Listing | None:
    product_url = _product_url(item)
    domain = merchant_host(product_url)
    if not domain or domain in GOOGLE_HOSTS:
        domain = domain_from_source(str(item.get("source") or ""))
        if not domain:
            return None
        product_id = str(item.get("product_id") or item.get("title") or "item")
        product_url = f"https://{domain}/item/{listing_id(product_id)}"
    price_cents = _price_cents(item)
    if price_cents is None:
        return None
    title = str(item.get("title") or "").strip() or "Untitled listing"
    merchant_name = str(item.get("source") or domain).strip() or domain
    thumbs = item.get("serpapi_thumbnails") or []
    image_url = str(item.get("thumbnail") or (thumbs[0] if thumbs else "") or "")
    return Listing(
        id=listing_id(product_url),
        title=title,
        price_cents=price_cents,
        merchant_name=merchant_name,
        merchant_domain=domain,
        image_url=image_url,
        product_url=product_url,
        source="serpapi",
    )


def listings_from_payload(
    payload: dict,
    spec: SearchSpec,
    limit: int = MAX_LISTINGS,
) -> list[Listing]:
    del spec  # reserved for token/budget filtering in Task 4
    out: list[Listing] = []
    seen: set[str] = set()
    for item in payload.get("shopping_results") or []:
        listing = listing_from_shopping_result(item if isinstance(item, dict) else {})
        if listing is None or listing.product_url in seen:
            continue
        seen.add(listing.product_url)
        out.append(listing)
        if len(out) >= limit:
            break
    return out


def _cents(raw: object) -> int | None:
    if raw is None:
        return None
    try:
        cents = int((Decimal(str(raw)) * 100).quantize(Decimal("1")))
    except (InvalidOperation, ValueError):
        return None
    return cents if cents > 0 else None


def listing_from_immersive(
    payload: dict,
    *,
    fallback_title: str,
    image_url: str,
) -> Listing | None:
    """Use the first immersive store whose link is a real merchant site."""
    results = payload.get("product_results") if isinstance(payload, dict) else None
    if not isinstance(results, dict):
        return None
    title = str(results.get("title") or fallback_title).strip() or "Untitled listing"
    stores = results.get("stores") or []
    for store in stores:
        if not isinstance(store, dict):
            continue
        product_url = str(store.get("link") or "").strip()
        domain = merchant_host(product_url)
        if not domain or domain in GOOGLE_HOSTS or domain.endswith(".google.com"):
            continue
        price_cents = _cents(store.get("extracted_price"))
        if price_cents is None:
            continue
        merchant_name = str(store.get("name") or domain).strip() or domain
        return Listing(
            id=listing_id(product_url),
            title=title,
            price_cents=price_cents,
            merchant_name=merchant_name,
            merchant_domain=domain,
            image_url=image_url,
            product_url=product_url,
            source="serpapi",
        )
    return None


def _with_api_key(url: str, api_key: str) -> str:
    """Append the key. Re-encoding the existing query drops the page token."""
    joiner = "&" if urlparse(url).query else "?"
    return f"{url}{joiner}api_key={api_key}"


class SerpAPIProvider:
    name = "serpapi"

    def __init__(self, api_key: str | None = None, timeout_s: float = SEARCH_S - 1.0) -> None:
        self.api_key = api_key if api_key is not None else get_settings().serpapi_key
        self.timeout_s = timeout_s

    async def search(self, spec: SearchSpec, limit: int = MAX_LISTINGS) -> list[Listing]:
        if not self.api_key:
            raise RuntimeError("SERPAPI_KEY unset")
        params = {
            "engine": "google_shopping",
            "q": spec.query,
            "api_key": self.api_key,
            "num": limit,
        }
        async with httpx.AsyncClient(timeout=2.5) as client:
            response = await client.get(SERPAPI_URL, params=params)
            response.raise_for_status()
            payload = response.json()
            direct = listings_from_payload(payload, spec, limit=limit)
            if direct:
                return direct
            return await self._from_immersive(client, payload, limit)

    async def _from_immersive(
        self,
        client: httpx.AsyncClient,
        payload: dict,
        limit: int,
    ) -> list[Listing]:
        # Four lookups stay inside the 5s search budget. A slow one must not
        # discard the stores that already came back.
        items = [
            item
            for item in (payload.get("shopping_results") or [])
            if isinstance(item, dict) and item.get("serpapi_immersive_product_api")
        ][: min(limit, 4)]

        async def one(item: dict) -> Listing | None:
            url = _with_api_key(str(item["serpapi_immersive_product_api"]), self.api_key or "")
            try:
                response = await client.get(url)
                response.raise_for_status()
                body = response.json()
            except Exception:
                return None
            return listing_from_immersive(
                body,
                fallback_title=str(item.get("title") or ""),
                image_url=str(item.get("thumbnail") or ""),
            )

        found_tasks = [asyncio.create_task(one(item)) for item in items]
        done, pending = await asyncio.wait(found_tasks, timeout=2.0)
        for task in pending:
            task.cancel()
        listings: list[Listing] = []
        seen: set[str] = set()
        for task in done:
            listing = task.result()
            if listing is None or listing.product_url in seen:
                continue
            seen.add(listing.product_url)
            listings.append(listing)
        return listings
