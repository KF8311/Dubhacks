"""Curated product catalog used by search fallback and demo mode."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.paths import data_dir
from app.domain.models import Listing

def load_catalog(path: Path | None = None) -> list[Listing]:
    """Read ``data/catalog.json`` and return listings in file order."""
    source = path or data_dir() / "catalog.json"
    raw = json.loads(source.read_text(encoding="utf-8"))
    items = raw["listings"] if isinstance(raw, dict) else raw
    return [Listing(**item) for item in items]
