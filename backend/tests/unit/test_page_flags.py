from app.checks.base import CheckTarget
from app.checks.page_flags import PageFlagsCheck
from app.domain.enums import CheckId, TrustStatus

CLEAN_PAGE = """
<html><body>
  <h1>Sony WH-1000XM5</h1>
  <p>In stock. Free shipping and returns within 30 days.</p>
  <p>Contact our support team at support@example.test.</p>
</body></html>
"""


def target(url="https://scam.shop/p/1", domain="scam.shop"):
    return CheckTarget("lst_1", url, domain, "m", 100, None)


def fake_html(html):
    async def fetch(url, ctx):
        return html

    return fetch


async def test_urgency_and_advance_payment_fail(monkeypatch):
    villain = (
        "<html><body>"
        "<div>FLASH SALE — TODAY ONLY — ENDS IN 00:14:59</div>"
        "<p>ONLY 3 LEFT IN STOCK</p>"
        "<p>Send payment first, then message us with your transaction ID.</p>"
        "<p>All sales final. No refunds.</p>"
        "<script>setInterval(function () { remaining -= 1; }, 1000);</script>"
        "</body></html>"
    )
    monkeypatch.setattr("app.checks.page_flags.fetch_html", fake_html(villain))

    result = await PageFlagsCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.FAILED
    assert result.severity >= 0.4


async def test_a_clean_page_passes(monkeypatch):
    monkeypatch.setattr("app.checks.page_flags.fetch_html", fake_html(CLEAN_PAGE))

    result = await PageFlagsCheck().run(target("https://shop.example/p/1"), ctx=None)

    assert result.status == TrustStatus.PASSED
    assert result.severity == 0.0


async def test_one_flag_warns(monkeypatch):
    page = "<html><body><p>All sales final. No refunds.</p></body></html>"
    monkeypatch.setattr("app.checks.page_flags.fetch_html", fake_html(page))

    result = await PageFlagsCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.WARNING
    assert result.severity == 0.4


async def test_a_non_https_product_url_is_critical(monkeypatch):
    monkeypatch.setattr("app.checks.page_flags.fetch_html", fake_html(CLEAN_PAGE))

    result = await PageFlagsCheck().run(target("http://scam.shop/p/1"), ctx=None)

    assert result.status == TrustStatus.FAILED
    assert result.severity == 0.85


async def test_fetch_failure_is_skipped_not_passed(monkeypatch):
    monkeypatch.setattr("app.checks.page_flags.fetch_html", fake_html(None))

    result = await PageFlagsCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.SKIPPED
    assert result.source == "unavailable"


async def test_villain_fixture_needs_no_network():
    result = await PageFlagsCheck().run(
        target("https://premium-audio-deals.shop/p/1", "premium-audio-deals.shop"),
        ctx=None,
    )

    assert result.status == TrustStatus.FAILED
    assert result.source == "fixture"
    assert len(result.evidence) >= 2


def test_check_identity():
    check = PageFlagsCheck()

    assert check.id == CheckId.PAGE_FLAGS
    assert check.display_name == "Page flags"
    assert check.timeout_s > 0
