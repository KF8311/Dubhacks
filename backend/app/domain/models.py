"""Core domain models shared by the API, the trust engine, and the UI.

STOPGAP — read before editing.
Task 1 (owner: A) creates this file. Person B added only the two models that
Task 3 and Task 4 depend on, so trust/data work could start before the platform
scaffold landed. When A's version arrives, merge it into this file: A's copy is
authoritative for everything beyond ``Listing`` and ``SearchSpec``.

Shapes are copied verbatim from
``docs/superpowers/plans/2026-10-17-sniff-visa.md`` (Task 1 model list).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.enums import CheckId, TrustStatus


class Evidence(BaseModel):
    label: str
    value: str
    url: str | None = None


class TrustCheckResult(BaseModel):
    id: CheckId
    name: str
    status: TrustStatus
    severity: float = Field(ge=0, le=1)
    summary: str
    evidence: list[Evidence] = []
    source: Literal["live", "cache", "allowlist", "fixture", "timeout", "unavailable"]
    duration_ms: int = 0


class Listing(BaseModel):
    id: str
    title: str
    price_cents: int = Field(gt=0)
    currency: str = "USD"
    merchant_name: str
    merchant_domain: str
    image_url: str
    product_url: str
    category: str | None = None
    source: Literal["serpapi", "catalog", "fixture"] = "catalog"


class SearchSpec(BaseModel):
    query: str
    budget_max_cents: int | None = None
    category: str | None = None
    merchants_preferred: list[str] = []
