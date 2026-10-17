"""Deterministic trust scoring (D-005). The LLM never computes a score."""

from __future__ import annotations

from app.domain.enums import CheckId, TrustStatus, Verdict
from app.domain.models import Penalty, ScoreResult, TrustCheckResult

FAIL_DEDUCTION = 40
WARNING_DEDUCTION = 15
TRUSTED_THRESHOLD = 70
CAUTION_THRESHOLD = 40
MIN_COMPLETED_CHECKS = 3
COVERAGE_CAP = 69  # not payable
TOTAL_CHECKS = len(CheckId)

ALLOWLIST_REASON = "Allowlisted merchant."
ALL_PASSED_REASON = "All checks passed."


def _dedupe(checks: list[TrustCheckResult]) -> dict[CheckId, TrustCheckResult]:
    """One result per CheckId, keeping the highest severity."""
    kept: dict[CheckId, TrustCheckResult] = {}
    for check in checks:
        current = kept.get(check.id)
        if current is None or check.severity > current.severity:
            kept[check.id] = check
    return kept


def _points(check: TrustCheckResult) -> int:
    if check.status == TrustStatus.FAILED:
        return round(check.severity * FAIL_DEDUCTION)
    if check.status == TrustStatus.WARNING:
        return round(check.severity * WARNING_DEDUCTION)
    return 0


def _verdict(score: int) -> Verdict:
    if score >= TRUSTED_THRESHOLD:
        return Verdict.TRUSTED
    if score >= CAUTION_THRESHOLD:
        return Verdict.CAUTION
    return Verdict.DANGER


def score_investigation(
    checks: list[TrustCheckResult],
    *,
    allowlisted: bool,
    scoring_version: str = "1.0",
) -> ScoreResult:
    if allowlisted:
        return ScoreResult(
            score=0,
            verdict=Verdict.TRUSTED,
            confidence=1.0,
            penalties=[],
            fatal_flags=[],
            top_reason=ALLOWLIST_REASON,
            scoring_version=scoring_version,
            allowlisted=True,
        )

    by_id = _dedupe(checks)
    completed = sum(1 for check in by_id.values() if check.status != TrustStatus.SKIPPED)
    confidence = completed / TOTAL_CHECKS

    penalties = [
        Penalty(check_id=check.id, points=points, reason=check.summary)
        for check in by_id.values()
        if (points := _points(check)) > 0
    ]

    score = max(0, min(100, 100 - sum(penalty.points for penalty in penalties)))
    fatal_flags: list[str] = []

    safe_browsing = by_id.get(CheckId.SAFE_BROWSING)
    domain_age = by_id.get(CheckId.DOMAIN_AGE)
    page_flags = by_id.get(CheckId.PAGE_FLAGS)

    if safe_browsing is not None and safe_browsing.status == TrustStatus.FAILED:
        score, fatal_flags = 0, ["safe_browsing"]
    elif (
        page_flags is not None
        and page_flags.status == TrustStatus.FAILED
        and domain_age is not None
        and domain_age.status == TrustStatus.FAILED
    ):
        score, fatal_flags = 0, ["page_flags+domain_age"]
    elif domain_age is not None and domain_age.status == TrustStatus.FAILED and domain_age.severity >= 0.85:
        score, fatal_flags = 5, ["domain_age"]

    # Insufficient evidence is not trust.
    if completed < MIN_COMPLETED_CHECKS:
        score = min(score, COVERAGE_CAP)

    top_reason = (
        max(penalties, key=lambda penalty: penalty.points).reason
        if penalties
        else ALL_PASSED_REASON
    )

    return ScoreResult(
        score=score,
        verdict=_verdict(score),
        confidence=confidence,
        penalties=penalties,
        fatal_flags=fatal_flags,
        top_reason=top_reason,
        scoring_version=scoring_version,
        allowlisted=False,
    )
