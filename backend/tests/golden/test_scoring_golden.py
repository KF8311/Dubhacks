"""Pinned demo numbers. Changing these means bumping scoring_version (D-005)."""

from app.domain.enums import CheckId, TrustStatus, Verdict
from app.domain.models import TrustCheckResult
from app.trust.scoring import score_investigation


def result(check_id, status, severity, source="live"):
    return TrustCheckResult(
        id=check_id,
        name=check_id.value,
        status=status,
        severity=severity,
        summary=check_id.value,
        source=source,
    )


def villain():
    return [
        result(CheckId.DOMAIN_AGE, TrustStatus.FAILED, 0.95),
        result(CheckId.SSL, TrustStatus.WARNING, 0.4),
        result(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0.0),
        result(CheckId.REDDIT, TrustStatus.FAILED, 0.8),
        result(CheckId.PAGE_FLAGS, TrustStatus.FAILED, 0.85),
    ]


def hero():
    return [
        result(CheckId.DOMAIN_AGE, TrustStatus.PASSED, 0.0),
        result(CheckId.SSL, TrustStatus.PASSED, 0.0),
        result(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0.0),
        result(CheckId.REDDIT, TrustStatus.PASSED, 0.0),
        result(CheckId.PAGE_FLAGS, TrustStatus.PASSED, 0.0),
    ]


def test_villain_is_danger():
    scored = score_investigation(villain(), allowlisted=False)

    assert scored.verdict == Verdict.DANGER
    assert scored.score <= 31
    assert scored.confidence == 1.0


def test_hero_is_trusted():
    scored = score_investigation(hero(), allowlisted=False)

    assert scored.verdict == Verdict.TRUSTED
    assert scored.score >= 90
    assert scored.fatal_flags == []


def test_villain_cannot_become_payable_through_coverage():
    scored = score_investigation(villain(), allowlisted=False)

    assert scored.score < 70
