from app.domain.enums import Verdict
from app.domain.models import Listing, ScoreResult
from app.trust.recommendation import recommend


def listing(id, cents):
    return Listing(
        id=id,
        title="x",
        price_cents=cents,
        merchant_name="m",
        merchant_domain="d.com",
        image_url="",
        product_url="",
    )


def score(verdict, n=90, confidence=0.9):
    return ScoreResult(
        score=n,
        verdict=verdict,
        confidence=confidence,
        top_reason="x",
        scoring_version="1.0",
    )


def test_cheapest_trusted_wins():
    pairs = [
        (listing("a", 12000), score(Verdict.TRUSTED, 95)),
        (listing("b", 10000), score(Verdict.TRUSTED, 90)),
        (listing("c", 8000), score(Verdict.DANGER, 5)),
    ]
    r = recommend(pairs)
    assert r.recommended_listing_id == "b"
    assert r.savings_cents == 1000  # median trusted 11000 - 10000


def test_no_trusted_option():
    pairs = [(listing("a", 10000), score(Verdict.CAUTION, 50))]
    r = recommend(pairs)
    assert r.recommended_listing_id is None
    assert r.no_trusted_option is True
