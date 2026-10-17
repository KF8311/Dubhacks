from app.checks.base import CheckTarget
from app.checks.reddit_sentiment import RedditSentimentCheck
from app.domain.enums import CheckId, TrustStatus


def target(domain="scam.shop"):
    return CheckTarget("lst_1", f"https://{domain}/p", domain, "m", 100, None)


def posts(*titles):
    async def search(domain):
        return [
            {"title": title, "permalink": f"https://reddit.com/r/Scams/{index}"}
            for index, title in enumerate(titles)
        ]

    return search


async def test_a_couple_of_scam_mentions_warn(monkeypatch):
    monkeypatch.setattr(
        "app.checks.reddit_sentiment.search",
        posts("scam shop", "fraud alert"),
    )

    result = await RedditSentimentCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.WARNING
    assert result.severity == 0.5


async def test_three_or_more_mentions_fail(monkeypatch):
    monkeypatch.setattr(
        "app.checks.reddit_sentiment.search",
        posts("scam shop", "took my money", "never arrived"),
    )

    result = await RedditSentimentCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.FAILED
    assert result.severity == 0.8


async def test_no_mentions_passes(monkeypatch):
    monkeypatch.setattr("app.checks.reddit_sentiment.search", posts())

    result = await RedditSentimentCheck().run(target("bestbuy.com"), ctx=None)

    assert result.status == TrustStatus.PASSED


async def test_unrelated_mentions_are_not_evidence(monkeypatch):
    monkeypatch.setattr(
        "app.checks.reddit_sentiment.search",
        posts("best deals on headphones", "my new setup"),
    )

    result = await RedditSentimentCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.PASSED


async def test_a_search_error_is_skipped(monkeypatch):
    async def broken(domain):
        raise RuntimeError("429")

    monkeypatch.setattr("app.checks.reddit_sentiment.search", broken)

    result = await RedditSentimentCheck().run(target(), ctx=None)

    assert result.status == TrustStatus.SKIPPED
    assert result.source == "unavailable"


async def test_the_villain_fixture_needs_no_network():
    result = await RedditSentimentCheck().run(
        target("premium-audio-deals.shop"), ctx=None
    )

    assert result.status == TrustStatus.FAILED
    assert result.source == "fixture"
    assert len(result.evidence) == 3


async def test_evidence_carries_only_a_title_and_a_link(monkeypatch):
    monkeypatch.setattr(
        "app.checks.reddit_sentiment.search", posts("this shop is a scam")
    )

    result = await RedditSentimentCheck().run(target(), ctx=None)

    evidence = result.evidence[0]
    assert evidence.label == "Report"
    assert "scam" in evidence.value
    assert evidence.url and evidence.url.startswith("https://reddit.com/")


def test_check_identity():
    check = RedditSentimentCheck()

    assert check.id == CheckId.REDDIT
    assert check.display_name == "Reddit sentiment"
    assert check.timeout_s > 0
