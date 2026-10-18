from app.checks.base import CheckTarget
from app.checks.safe_browsing import SafeBrowsingCheck
from app.domain.enums import CheckId, TrustStatus


def target(url="https://scam.example/p", domain="scam.example"):
    return CheckTarget("lst_1", url, domain, "m", 100, None)


def threats(*types):
    async def lookup(url):
        return list(types)

    return lookup


async def test_threat_match_fails(monkeypatch):
    monkeypatch.setattr("app.checks.safe_browsing.lookup", threats("MALWARE"))

    result = await SafeBrowsingCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.FAILED
    assert result.severity == 1.0
    assert "MALWARE" in result.summary


async def test_clean_passes(monkeypatch):
    monkeypatch.setattr("app.checks.safe_browsing.lookup", threats())

    result = await SafeBrowsingCheck().run(target("https://bestbuy.com/p"), ctx=None)

    assert result.status == TrustStatus.PASSED


async def test_a_lookup_error_is_skipped_not_passed(monkeypatch):
    async def broken(url):
        raise RuntimeError("no key")

    monkeypatch.setattr("app.checks.safe_browsing.lookup", broken)

    result = await SafeBrowsingCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.SKIPPED
    assert result.source == "unavailable"


async def test_the_villain_matches_the_local_denylist():
    """With no API key, the offline threat list still catches the demo villain."""

    result = await SafeBrowsingCheck().run(
        target(
            "https://premium-audio-deals.shop/p/1", "premium-audio-deals.shop"
        ),
        ctx=None,
    )

    assert result.status == TrustStatus.FAILED
    assert result.severity == 1.0


async def test_a_denylisted_subdomain_matches(monkeypatch):
    from app.checks import safe_browsing

    monkeypatch.setattr(
        safe_browsing, "_denylist", lambda: frozenset({"premium-audio-deals.shop"})
    )

    result = await safe_browsing.SafeBrowsingCheck().run(
        target("https://www.premium-audio-deals.shop/p", "www.premium-audio-deals.shop"),
        ctx=None,
    )

    assert result.status == TrustStatus.FAILED


async def test_a_lookalike_domain_does_not_match(monkeypatch):
    from app.checks import safe_browsing

    monkeypatch.setattr(
        safe_browsing, "_denylist", lambda: frozenset({"premium-audio-deals.shop"})
    )

    result = await safe_browsing.SafeBrowsingCheck().run(
        target(
            "https://premium-audio-deals.shop.evil.test/p",
            "premium-audio-deals.shop.evil.test",
        ),
        ctx=None,
    )

    assert result.status == TrustStatus.PASSED


def test_check_identity():
    check = SafeBrowsingCheck()

    assert check.id == CheckId.SAFE_BROWSING
    assert check.display_name == "Safe Browsing"
    assert check.timeout_s > 0
