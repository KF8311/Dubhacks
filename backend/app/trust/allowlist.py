"""Domain allowlist for merchants we treat as established."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.core.paths import data_dir


def _normalize(domain: str) -> str:
    host = (domain or "").strip().lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


@dataclass(frozen=True)
class Allowlist:
    domains: frozenset[str]

    def matches(self, domain: str) -> bool:
        """True only for the exact host or a dot-boundary subdomain.

        ``bestbuy.com.evil.shop`` does not match ``bestbuy.com``.
        """
        host = _normalize(domain)
        if not host:
            return False
        return any(
            host == entry or host.endswith("." + entry) for entry in self.domains
        )


def load_allowlist(path: Path | None = None) -> Allowlist:
    """Read ``data/allowlist.json`` into a normalized :class:`Allowlist`."""
    source = path or data_dir() / "allowlist.json"
    raw = json.loads(source.read_text(encoding="utf-8"))
    entries = raw["domains"] if isinstance(raw, dict) else raw
    return Allowlist(frozenset(_normalize(d) for d in entries if d))
