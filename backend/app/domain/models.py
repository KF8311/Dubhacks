from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.enums import CheckId, CheckoutStage, SessionStage, TrustStatus, Verdict


class Evidence(BaseModel):
    label: str
    value: str
    url: str | None = None


class QuestionOption(BaseModel):
    id: str
    label: str


class Question(BaseModel):
    id: str
    prompt: str
    kind: Literal["single_select", "multi_select", "free_text"] = "single_select"
    options: list[QuestionOption] = Field(default_factory=list)
    allow_free_text: bool = False


class TrustCheckResult(BaseModel):
    id: CheckId
    name: str
    status: TrustStatus
    severity: float = Field(ge=0, le=1)
    summary: str
    evidence: list[Evidence] = Field(default_factory=list)
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


class Penalty(BaseModel):
    check_id: CheckId
    points: int
    reason: str


class ScoreResult(BaseModel):
    score: int = Field(ge=0, le=100)
    verdict: Verdict
    confidence: float = Field(ge=0, le=1)
    penalties: list[Penalty] = Field(default_factory=list)
    fatal_flags: list[str] = Field(default_factory=list)
    top_reason: str
    scoring_version: str = "1.0"
    # Allowlisted listings score 0 by design, so downstream payability and
    # recommendation rules cannot recover this from the score alone.
    allowlisted: bool = False


class Recommendation(BaseModel):
    recommended_listing_id: str | None = None
    median_trusted_cents: int | None = None
    savings_cents: int | None = None
    eligible_ids: list[str] = Field(default_factory=list)
    reason: str
    no_trusted_option: bool = False


class Investigation(BaseModel):
    id: str
    listing_id: str
    session_id: str
    checks: list[TrustCheckResult]
    score: ScoreResult
    allowlisted: bool
    duration_ms: int
    created_at: datetime


class Answer(BaseModel):
    question_id: str
    option_id: str | None = None
    text: str | None = None


class SearchSpec(BaseModel):
    query: str
    budget_max_cents: int | None = None
    budget_min_cents: int | None = None
    category: str | None = None
    merchants_preferred: list[str] = Field(default_factory=list)


class SessionStats(BaseModel):
    listings: int = 0
    trusted: int = 0
    caution: int = 0
    danger: int = 0
    duration_ms: int = 0


class Session(BaseModel):
    id: str
    client_id: str
    query: str
    stage: SessionStage
    answers: list[Answer] = Field(default_factory=list)
    search_spec: SearchSpec
    listing_ids: list[str] = Field(default_factory=list)
    recommended_listing_id: str | None = None
    stats: SessionStats = Field(default_factory=SessionStats)
    created_at: datetime
    updated_at: datetime
    expires_at: datetime


class Mandate(BaseModel):
    id: str
    session_id: str
    listing_id: str
    investigation_id: str
    merchant_domain: str
    max_amount_cents: int = Field(gt=0)
    currency: str = "USD"
    expires_at: datetime
    status: Literal["active", "consumed", "expired"] = "active"


class Checkout(BaseModel):
    id: str
    session_id: str
    listing_id: str
    investigation_id: str
    mandate_id: str
    amount_cents: int
    currency: str = "USD"
    stage: CheckoutStage = CheckoutStage.AWAITING_PASSKEY
    idempotency_key: str | None = None
    token_id: str | None = None
    created_at: datetime
    expires_at: datetime


class Transaction(BaseModel):
    id: str
    checkout_id: str
    status: Literal["approved", "declined"]
    amount_cents: int
    currency: str
    token_last4: str
    processor: Literal["mock-vic"] = "mock-vic"
    mode: Literal["sandbox"] = "sandbox"
    auth_code: str
    created_at: datetime


class Receipt(BaseModel):
    id: str
    share_id: str
    checkout_id: str
    transaction_id: str
    listing: Listing
    investigation_snapshot: Investigation
    amount_cents: int
    currency: str
    token_last4: str
    verified: list[str]
    unverified: list[str]
    issued_at: datetime
    signature: str
