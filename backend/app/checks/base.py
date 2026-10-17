"""The protocol every trust check implements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from app.domain.enums import CheckId
from app.domain.models import TrustCheckResult


@dataclass(frozen=True)
class CheckTarget:
    """What a check is asked to investigate."""

    listing_id: str
    product_url: str
    merchant_domain: str
    merchant_name: str
    price_cents: int
    category: str | None = None


@dataclass
class CheckContext:
    """Shared dependencies handed to every check.

    Fields are annotated ``Any`` and default to ``None`` so a check can be
    unit-tested without standing up HTTP, a cache, or settings. The concrete
    types are ``httpx.AsyncClient``, ``Cache``, ``Allowlist``, and ``Settings``.
    """

    http: Any = None
    cache: Any = None
    allowlist: Any = None
    config: Any = None


class TrustCheck(Protocol):
    """A single trust check.

    ``run`` must return a ``TrustCheckResult`` and must not raise for expected
    failures — the runner converts exceptions and timeouts into ``SKIPPED``.
    """

    id: CheckId
    display_name: str
    timeout_s: float

    async def run(
        self, target: CheckTarget, ctx: CheckContext
    ) -> TrustCheckResult: ...
