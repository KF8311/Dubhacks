from app.domain.enums import CheckId, TrustStatus, Verdict
from app.domain.models import TrustCheckResult
from app.trust.scoring import score_investigation


def check(check_id, status, severity, source="live", summary="x"):
    return TrustCheckResult(
        id=check_id,
        name=check_id.value,
        status=status,
        severity=severity,
        summary=summary,
        source=source,
    )


def test_allowlist_wins():
    result = score_investigation([], allowlisted=True)

    assert (result.score, result.verdict, result.confidence) == (0, Verdict.TRUSTED, 1.0)


def test_allowlisted_is_carried_on_the_result():
    """Downstream rules cannot re-derive allowlisting from a score of 0."""

    assert score_investigation([], allowlisted=True).allowlisted is True
    assert score_investigation([], allowlisted=False).allowlisted is False


def test_safe_browsing_fatal():
    result = score_investigation(
        [check(CheckId.SAFE_BROWSING, TrustStatus.FAILED, 1.0)], allowlisted=False
    )

    assert (result.score, result.verdict) == (0, Verdict.DANGER)
    assert "safe_browsing" in result.fatal_flags


def test_warning_math():
    checks = [
        check(CheckId.DOMAIN_AGE, TrustStatus.WARNING, 0.6),
        check(CheckId.SSL, TrustStatus.PASSED, 0),
        check(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0),
    ]

    assert score_investigation(checks, allowlisted=False).score == 91


def test_failed_math_uses_forty_points():
    checks = [
        check(CheckId.REDDIT, TrustStatus.FAILED, 0.5),
        check(CheckId.SSL, TrustStatus.PASSED, 0),
        check(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0),
    ]

    assert score_investigation(checks, allowlisted=False).score == 80


def test_coverage_caps_at_caution():
    checks = [check(CheckId.SSL, TrustStatus.PASSED, 0)]
    checks += [
        check(CheckId.REDDIT, TrustStatus.SKIPPED, 0, "timeout"),
        check(CheckId.PAGE_FLAGS, TrustStatus.SKIPPED, 0, "timeout"),
        check(CheckId.DOMAIN_AGE, TrustStatus.SKIPPED, 0, "timeout"),
        check(CheckId.SAFE_BROWSING, TrustStatus.SKIPPED, 0, "timeout"),
    ]

    result = score_investigation(checks, allowlisted=False)

    assert result.score == 69
    assert result.verdict == Verdict.CAUTION
    assert result.confidence == 0.2


def test_skipped_checks_do_not_deduct():
    checks = [
        check(CheckId.REDDIT, TrustStatus.SKIPPED, 1.0, "timeout"),
        check(CheckId.SSL, TrustStatus.PASSED, 0),
        check(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0),
        check(CheckId.PAGE_FLAGS, TrustStatus.PASSED, 0),
    ]

    assert score_investigation(checks, allowlisted=False).score == 100


def test_page_flags_with_domain_age_is_fatal():
    checks = [
        check(CheckId.DOMAIN_AGE, TrustStatus.FAILED, 0.95),
        check(CheckId.PAGE_FLAGS, TrustStatus.FAILED, 0.85),
    ]

    result = score_investigation(checks, allowlisted=False)

    assert (result.score, result.verdict) == (0, Verdict.DANGER)
    assert result.fatal_flags == ["page_flags+domain_age"]


def test_domain_age_alone_at_high_severity_is_fatal():
    checks = [
        check(CheckId.DOMAIN_AGE, TrustStatus.FAILED, 0.9),
        check(CheckId.SSL, TrustStatus.PASSED, 0),
        check(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0),
    ]

    result = score_investigation(checks, allowlisted=False)

    assert (result.score, result.verdict) == (5, Verdict.DANGER)
    assert result.fatal_flags == ["domain_age"]


def test_duplicate_check_ids_keep_the_highest_severity():
    checks = [
        check(CheckId.REDDIT, TrustStatus.WARNING, 0.5),
        check(CheckId.REDDIT, TrustStatus.FAILED, 0.8),
        check(CheckId.SSL, TrustStatus.PASSED, 0),
        check(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0),
    ]

    result = score_investigation(checks, allowlisted=False)

    assert result.score == 68
    assert [penalty.points for penalty in result.penalties] == [32]


def test_top_reason_names_the_largest_penalty():
    checks = [
        check(CheckId.REDDIT, TrustStatus.FAILED, 0.4, summary="three scam reports"),
        check(CheckId.SSL, TrustStatus.WARNING, 0.4, summary="free certificate"),
        check(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0),
    ]

    result = score_investigation(checks, allowlisted=False)

    assert result.top_reason == "three scam reports"


def test_top_reason_when_everything_passes():
    checks = [
        check(CheckId.SSL, TrustStatus.PASSED, 0),
        check(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0),
        check(CheckId.PAGE_FLAGS, TrustStatus.PASSED, 0),
    ]

    assert score_investigation(checks, allowlisted=False).top_reason == "All checks passed."


def test_score_clamps_at_zero():
    checks = [
        check(CheckId.REDDIT, TrustStatus.FAILED, 1.0),
        check(CheckId.SSL, TrustStatus.FAILED, 1.0),
        check(CheckId.PAGE_FLAGS, TrustStatus.FAILED, 0.9),
    ]

    assert score_investigation(checks, allowlisted=False).score == 0


def test_scoring_version_is_recorded():
    result = score_investigation([], allowlisted=True)

    assert result.scoring_version == "1.0"
