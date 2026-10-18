from __future__ import annotations

import asyncio
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs, quote, urlparse

import httpx

from app.core.config import get_settings
from app.core.ids import listing_id
from app.core.timeouts import IMMERSIVE_STORE_S, MAX_LISTINGS, SEARCH_S
from app.domain.models import Listing, SearchSpec
from app.search.provider import SearchQuotaExhausted

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
    "office depot": "officedepot.com",
    "old navy": "oldnavy.gap.com",
    "sams club": "samsclub.com",
    "sam's club": "samsclub.com",
    "staples": "staples.com",
    "target": "target.com",
    "jetpens": "jetpens.com",
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


def _clean_url(value: str) -> str:
    """SerpAPI returns links with literal spaces; a URL must not contain them.

    Tapping a link in a text message stops at the first space, so an encoded
    URL is the difference between "works" and "404".
    """
    return value.strip().replace(" ", "%20")


def _product_url(item: dict) -> str:
    for key in ("product_link", "link"):
        value = _clean_url(str(item.get(key) or ""))
        host = merchant_host(value)
        if host and host not in GOOGLE_HOSTS:
            return value
    return ""


def _google_product_url(item: dict) -> str:
    """Point a Google-hosted result at its Google Shopping results page.

    Google's shopping engine often returns only `google.com/search?ibp=oshop…`
    links, with the retailer named in `source`. The `prds` catalog token in
    those links can resolve to a different listing than the one we priced, so
    drop it and keep the query. `ibp=oshop` is the legacy form and now opens an
    empty page; `udm=28` is the shopping vertical Google redirects to. An
    invented `https://<retailer>/item/<id>` is not acceptable — it 404s.
    """
    for key in ("product_link", "link"):
        value = _clean_url(str(item.get(key) or ""))
        if value and merchant_host(value) in GOOGLE_HOSTS:
            query = parse_qs(urlparse(value).query).get("q", [""])[0].strip()
            if query:
                return f"https://www.google.com/search?udm=28&q={quote(query)}"
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
        # Never invent a merchant path: link to the Google Shopping results page.
        product_url = _google_product_url(item)
    price_cents = _price_cents(item)
    if price_cents is None:
        return None
    title = str(item.get("title") or "").strip() or "Untitled listing"
    merchant_name = str(item.get("source") or domain).strip() or domain
    thumbs = item.get("serpapi_thumbnails") or []
    image_url = str(item.get("thumbnail") or (thumbs[0] if thumbs else "") or "")
    # A shared (or empty) product_url must not collapse listings onto one id:
    # every Google result for a query now points at the same results page.
    identity = f"{product_url}|{domain}|{item.get('product_id') or title}"
    return Listing(
        id=listing_id(identity),
        title=title,
        price_cents=price_cents,
        merchant_name=merchant_name,
        merchant_domain=domain,
        image_url=image_url,
        product_url=product_url,
        source="serpapi",
    )


def listing_pairs_from_payload(
    payload: dict,
    limit: int = MAX_LISTINGS,
) -> list[tuple[Listing, dict]]:
    """Pair each listing with the shopping result it came from.

    The raw item carries the immersive lookup URL that turns a Google-hosted
    result into the merchant's own product page.
    """
    out: list[tuple[Listing, dict]] = []
    seen: set[str] = set()
    for item in payload.get("shopping_results") or []:
        if not isinstance(item, dict):
            continue
        listing = listing_from_shopping_result(item)
        if listing is None or listing.id in seen:
            continue
        seen.add(listing.id)
        out.append((listing, item))
        if len(out) >= limit:
            break
    return out


def listings_from_payload(
    payload: dict,
    spec: SearchSpec,
    limit: int = MAX_LISTINGS,
) -> list[Listing]:
    del spec  # reserved for token/budget filtering in Task 4
    return [listing for listing, _item in listing_pairs_from_payload(payload, limit)]


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
        product_url = _clean_url(str(store.get("link") or ""))
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


def store_url_for_listing(payload: dict, listing: Listing) -> str:
    """Return the store URL that belongs to this listing's merchant.

    The immersive response lists every store that sells the product, often
    including Google itself and marketplaces like DoorDash that resell another
    merchant's catalog. Taking the first store would relabel a Walmart result
    as whatever merchant came first, and a fuzzy name match would send an
    Office Depot listing to doordash.com. Only an exact merchant host is
    accepted; anything else keeps the Google Shopping link.
    """
    results = payload.get("product_results") if isinstance(payload, dict) else None
    if not isinstance(results, dict):
        return ""
    for store in results.get("stores") or []:
        if not isinstance(store, dict):
            continue
        link = _clean_url(str(store.get("link") or ""))
        host = merchant_host(link)
        if not host or host in GOOGLE_HOSTS or host.endswith(".google.com"):
            continue
        if host == listing.merchant_domain:
            return link
    return ""


# Every immersive lookup is a SerpAPI search. A listing that already resolved
# keeps its merchant page for the life of the process, so re-running the demo
# query costs one search instead of ten. Misses are not cached: a later lookup
# may still find the store.
_STORE_URL_CACHE: dict[str, str] = {}
_STORE_URL_CACHE_MAX = 1024


def _remember_store_url(listing_id_value: str, url: str) -> None:
    if not url:
        return
    if len(_STORE_URL_CACHE) >= _STORE_URL_CACHE_MAX:
        _STORE_URL_CACHE.clear()
    _STORE_URL_CACHE[listing_id_value] = url


QUOTA_MARKERS = ("out of searches", "quota", "no searches left")


def _is_quota_exhausted(response: httpx.Response) -> bool:
    """SerpAPI answers an empty plan with 429 and a plain error string.

    A 429 can also mean a rate limit, which is worth retrying; only the plan
    message is permanent. The body is read defensively because a proxy or a
    test double may not return JSON.
    """
    if getattr(response, "status_code", 200) != 429:
        return False
    try:
        message = str((response.json() or {}).get("error") or "")
    except Exception:  # noqa: BLE001 — an unreadable body is not a quota signal
        message = str(getattr(response, "text", "") or "")
    lowered = message.lower()
    return any(marker in lowered for marker in QUOTA_MARKERS)


def _with_api_key(url: str, api_key: str) -> str:
    """Append the key. Re-encoding the existing query drops the page token."""
    joiner = "&" if urlparse(url).query else "?"
    return f"{url}{joiner}api_key={api_key}"


def _shopping_query(spec: SearchSpec) -> str:
    query = spec.query
    lo, hi = spec.budget_min_cents, spec.budget_max_cents
    if lo is not None and hi is not None:
        return f"{query} ${lo // 100}-{hi // 100}"
    if hi is not None:
        return f"{query} under ${hi // 100}"
    return query


class SerpAPIProvider:
    name = "serpapi"

    def __init__(self, api_key: str | None = None, timeout_s: float = SEARCH_S - 1.0) -> None:
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.serpapi_key
        self.timeout_s = timeout_s
        self.location = (settings.serpapi_location or "").strip()
        self.gl = settings.serpapi_gl
        self.hl = settings.serpapi_hl

    async def search(self, spec: SearchSpec, limit: int = MAX_LISTINGS) -> list[Listing]:
        if not self.api_key:
            raise RuntimeError("SERPAPI_KEY unset")
        params = {
            "engine": "google_shopping",
            "q": _shopping_query(spec),
            "api_key": self.api_key,
            "num": limit,
        }
        if spec.budget_min_cents is not None:
            params["min_price"] = spec.budget_min_cents // 100
        if spec.budget_max_cents is not None:
            params["max_price"] = spec.budget_max_cents // 100
        # Localize by market rather than by appending a city to `q`, which
        # would change what Google matches instead of where it looks.
        if self.location:
            params["location"] = self.location
        params["gl"] = self.gl
        params["hl"] = self.hl
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            response = await client.get(SERPAPI_URL, params=params)
            if _is_quota_exhausted(response):
                raise SearchQuotaExhausted("Your account has run out of searches.")
            response.raise_for_status()
            payload = response.json()
            pairs = listing_pairs_from_payload(payload, limit=limit)
            if pairs:
                return await self._enrich(client, pairs)
            return await self._from_immersive(client, payload, limit)

    async def _enrich(
        self,
        client: httpx.AsyncClient,
        pairs: list[tuple[Listing, dict]],
    ) -> list[Listing]:
        """Swap Google-hosted links for the merchant's own product page.

        Google Shopping returns only `google.com/search?…` links for most
        results. The listing carries an immersive lookup URL that names every
        store selling it; matching the store back to the listing's merchant
        yields a link that actually loads. Lookups run concurrently and stop at
        the immersion budget — a slow one keeps its Google link rather than
        delaying the grid.
        """

        async def one(listing: Listing, item: dict) -> str:
            cached = _STORE_URL_CACHE.get(listing.id)
            if cached:
                return cached
            url = str(item.get("serpapi_immersive_product_api") or "")
            if not url:
                return ""
            try:
                response = await client.get(_with_api_key(url, self.api_key or ""))
                response.raise_for_status()
                payload = response.json()
            except Exception:  # noqa: BLE001 — a lost lookup is not a lost listing
                return ""
            found = store_url_for_listing(payload, listing)
            _remember_store_url(listing.id, found)
            return found

        tasks = {
            listing.id: asyncio.create_task(one(listing, item))
            for listing, item in pairs
            if item.get("serpapi_immersive_product_api")
        }
        if tasks:
            _done, pending = await asyncio.wait(tasks.values(), timeout=IMMERSIVE_STORE_S)
            for task in pending:
                task.cancel()
        enriched: list[Listing] = []
        for listing, _item in pairs:
            task = tasks.get(listing.id)
            if task is None or task.cancelled():
                enriched.append(listing)
                continue
            try:
                product_url = task.result()
            except Exception:  # noqa: BLE001
                product_url = ""
            if product_url and product_url != listing.product_url:
                listing = listing.model_copy(update={"product_url": product_url})
            enriched.append(listing)
        return enriched

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
