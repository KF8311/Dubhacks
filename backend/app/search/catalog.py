"""Curated product catalog used by search fallback and demo mode."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.paths import data_dir
from app.domain.models import Listing

# The curated file is the headphone demo. Live searches for other products
# must not fall back to it or the grid looks like every query is headphones.
_CATALOG_QUERY_HINTS = (
    "headphone",
    "headset",
    "earbud",
    "airpod",
    "noise cancell",
    "wh-1000",
    "quietcomfort",
)


def catalog_covers(query: str) -> bool:
    haystack = query.lower()
    return any(hint in haystack for hint in _CATALOG_QUERY_HINTS)


def load_catalog(path: Path | None = None) -> list[Listing]:
    """Read ``data/catalog.json`` and return listings in file order."""
    source = path or data_dir() / "catalog.json"
    raw = json.loads(source.read_text(encoding="utf-8"))
    items = raw["listings"] if isinstance(raw, dict) else raw
    return [Listing(**item) for item in items]
