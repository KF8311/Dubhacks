from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from app.domain.enums import CheckoutStage, TrustStatus, Verdict
from app.domain.models import Checkout, Investigation, Listing, Mandate
from app.trust.scoring import MIN_COMPLETED_CHECKS, TRUSTED_THRESHOLD

STALE_AFTER = timedelta(minutes=30)
MIN_CONFIDENCE = 0.6


class PayabilityCode(str, Enum):
    MERCHANT_NOT_TRUSTED = "MERCHANT_NOT_TRUSTED"
    SCORE_TOO_LOW = "SCORE_TOO_LOW"
    COVERAGE_TOO_LOW = "COVERAGE_TOO_LOW"
    MERCHANT_MISMATCH = "MERCHANT_MISMATCH"
    AMOUNT_EXCEEDS_CAP = "AMOUNT_EXCEEDS_CAP"
    MANDATE_EXPIRED = "MANDATE_EXPIRED"
    ALREADY_PAID = "ALREADY_PAID"
    INVESTIGATION_STALE = "INVESTIGATION_STALE"


@dataclass(frozen=True)
class MandateDraft:
    merchant_domain: str
    max_amount_cents: int
    currency: str = "USD"


class PayabilityError(Exception):
    def __init__(self, code: PayabilityCode, details: dict | None = None) -> None:
        self.code = code
        self.status_code = 409
        self.details = details or {}
        super().__init__(code.value)


def _completed_count(investigation: Investigation) -> int:
    return sum(1 for check in investigation.checks if check.status != TrustStatus.SKIPPED)


def assert_payable(
    investigation: Investigation,
    listing: Listing,
    mandate: MandateDraft | Mandate,
    *,
    now: datetime,
    checkout: Checkout | None = None,
) -> None:
    if investigation is None:
        raise PayabilityError(PayabilityCode.INVESTIGATION_STALE, {"reason": "missing"})

    if investigation.created_at.tzinfo is None:
        created = investigation.created_at.replace(tzinfo=now.tzinfo)
    else:
        created = investigation.created_at
    if now - created > STALE_AFTER:
        raise PayabilityError(PayabilityCode.INVESTIGATION_STALE)

    if investigation.score.verdict != Verdict.TRUSTED:
        raise PayabilityError(
            PayabilityCode.MERCHANT_NOT_TRUSTED,
            {"verdict": investigation.score.verdict.value},
        )

    if not investigation.allowlisted and investigation.score.score < TRUSTED_THRESHOLD:
        raise PayabilityError(
            PayabilityCode.SCORE_TOO_LOW,
            {"score": investigation.score.score},
        )

    if not investigation.allowlisted:
        completed = _completed_count(investigation)
        if investigation.score.confidence < MIN_CONFIDENCE or completed < MIN_COMPLETED_CHECKS:
            raise PayabilityError(
                PayabilityCode.COVERAGE_TOO_LOW,
                {"completed": completed, "confidence": investigation.score.confidence},
            )

    if listing.merchant_domain != mandate.merchant_domain:
        raise PayabilityError(
            PayabilityCode.MERCHANT_MISMATCH,
            {
                "listing": listing.merchant_domain,
                "mandate": mandate.merchant_domain,
            },
        )

    if listing.price_cents > mandate.max_amount_cents:
        raise PayabilityError(
            PayabilityCode.AMOUNT_EXCEEDS_CAP,
            {"price_cents": listing.price_cents, "cap": mandate.max_amount_cents},
        )

    listing_currency = listing.currency
    mandate_currency = mandate.currency
    if listing_currency != mandate_currency:
        raise PayabilityError(
            PayabilityCode.MERCHANT_MISMATCH,
            {"reason": "currency", "listing": listing_currency, "mandate": mandate_currency},
        )

    if isinstance(mandate, Mandate):
        if mandate.status == "consumed":
            raise PayabilityError(PayabilityCode.ALREADY_PAID)
        if mandate.status != "active" or mandate.expires_at <= now:
            raise PayabilityError(PayabilityCode.MANDATE_EXPIRED)

    if checkout is not None and checkout.stage == CheckoutStage.CAPTURED:
        raise PayabilityError(PayabilityCode.ALREADY_PAID)
