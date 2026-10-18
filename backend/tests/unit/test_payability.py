from datetime import UTC, datetime, timedelta

import pytest

from app.domain.enums import CheckId, TrustStatus, Verdict
from app.domain.models import (
    Investigation,
    Listing,
    Mandate,
    ScoreResult,
    TrustCheckResult,
)
from app.payments.mandates import create_mandate
from app.payments.payability import PayabilityCode, PayabilityError, assert_payable

NOW = datetime(2026, 10, 17, 19, 0, tzinfo=UTC)


def listing(cents=10000, domain="bestbuy.com", currency="USD"):
    return Listing(
        id="lst_1",
        title="x",
        price_cents=cents,
        currency=currency,
        merchant_name="m",
        merchant_domain=domain,
        image_url="",
        product_url="",
    )


def inv(verdict=Verdict.TRUSTED, score=92, confidence=0.9, minutes_ago=1, completed=5, allowlisted=False):
    checks = [
        TrustCheckResult(
            id=cid,
            name=cid.value,
            status=TrustStatus.PASSED,
            severity=0,
            summary="ok",
            source="live",
        )
        for cid in list(CheckId)[:completed]
    ]
    return Investigation(
        id="inv_1",
        listing_id="lst_1",
        session_id="ses_1",
        checks=checks,
        score=ScoreResult(
            score=score,
            verdict=verdict,
            confidence=confidence,
            top_reason="x",
            scoring_version="1.0",
        ),
        allowlisted=allowlisted,
        duration_ms=1,
        created_at=NOW - timedelta(minutes=minutes_ago),
    )


def mandate(cents=30000, domain="bestbuy.com", expires=NOW + timedelta(minutes=10), status="active"):
    return Mandate(
        id="man_1",
        session_id="ses_1",
        listing_id="lst_1",
        investigation_id="inv_1",
        merchant_domain=domain,
        max_amount_cents=cents,
        expires_at=expires,
        status=status,
    )


def test_trusted_is_payable():
    assert_payable(inv(), listing(), mandate(), now=NOW)


def test_mandate_below_price_raises():
    with pytest.raises(ValueError):
        create_mandate(listing(10000), max_amount_cents=5000, now=NOW)


def test_danger_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(Verdict.DANGER, 0), listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.MERCHANT_NOT_TRUSTED
    assert e.value.details["verdict"] == "danger"


def test_low_confidence_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(confidence=0.5), listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.COVERAGE_TOO_LOW
    assert e.value.details["confidence"] == 0.5


def test_a_missing_investigation_is_stale_not_payable():
    with pytest.raises(PayabilityError) as e:
        assert_payable(None, listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.INVESTIGATION_STALE


def test_an_allowlisted_merchant_pays_at_score_zero():
    """D-015: the allowlist exempts a merchant from the score and coverage floor."""
    assert_payable(
        inv(Verdict.TRUSTED, score=0, confidence=1.0, completed=0, allowlisted=True),
        listing(),
        mandate(),
        now=NOW,
    )


def test_currency_mismatch_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(), listing(currency="EUR"), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.MERCHANT_MISMATCH
    assert e.value.details["reason"] == "currency"


def test_exactly_thirty_minutes_is_not_stale():
    assert_payable(inv(minutes_ago=30), listing(), mandate(), now=NOW)


def test_the_payability_constants_are_frozen():
    from app.payments.payability import MIN_CONFIDENCE, STALE_AFTER
    from app.trust.scoring import MIN_COMPLETED_CHECKS, TRUSTED_THRESHOLD

    assert STALE_AFTER == timedelta(minutes=30)
    assert MIN_CONFIDENCE == 0.6
    assert TRUSTED_THRESHOLD == 70
    assert MIN_COMPLETED_CHECKS == 3


def test_caution_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(Verdict.CAUTION, 50), listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.MERCHANT_NOT_TRUSTED


def test_low_coverage_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(completed=2), listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.COVERAGE_TOO_LOW


def test_amount_over_cap_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(), listing(40000), mandate(30000), now=NOW)
    assert e.value.code == PayabilityCode.AMOUNT_EXCEEDS_CAP


def test_stale_investigation_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(minutes_ago=45), listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.INVESTIGATION_STALE


def test_score_too_low_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(Verdict.TRUSTED, score=65, confidence=0.9), listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.SCORE_TOO_LOW


def test_merchant_mismatch_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(), listing(domain="bestbuy.com"), mandate(domain="amazon.com"), now=NOW)
    assert e.value.code == PayabilityCode.MERCHANT_MISMATCH


def test_mandate_expired_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(
            inv(),
            listing(),
            mandate(expires=NOW - timedelta(minutes=1)),
            now=NOW,
        )
    assert e.value.code == PayabilityCode.MANDATE_EXPIRED


def test_already_paid_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(), listing(), mandate(status="consumed"), now=NOW)
    assert e.value.code == PayabilityCode.ALREADY_PAID
