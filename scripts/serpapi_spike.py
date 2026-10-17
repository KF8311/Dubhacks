"""Live SerpAPI probe using the real adapter.

Usage (from repo root):
  $env:SERPAPI_KEY="..."
  backend\\.venv\\Scripts\\python.exe scripts\\serpapi_spike.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.domain.models import SearchSpec  # noqa: E402
from app.search.serpapi import SerpAPIProvider  # noqa: E402

QUERY = "noise cancelling headphones"


async def run() -> int:
    provider = SerpAPIProvider()
    if not provider.api_key:
        print("SERPAPI_KEY unset — cannot run live query. Catalog-only until retried.")
        return 2
    try:
        listings = await provider.search(SearchSpec(query=QUERY), limit=8)
    except Exception as exc:  # noqa: BLE001 — spike: any failure is catalog-only
        print(f"SerpAPI request failed ({exc}). Catalog-only until retried.")
        return 2

    print(f"query={QUERY!r} mapped={len(listings)}")
    for listing in listings:
        print(
            f"  {listing.merchant_domain:20} {listing.price_cents:7}  {listing.title[:50]}"
        )

    if not listings:
        print("No merchant domains on product URLs. Decision: catalog only.")
        return 1

    print(json.dumps({"go": True, "merchant_count": len(listings)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
