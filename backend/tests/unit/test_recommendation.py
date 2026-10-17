from app.domain.enums import Verdict
from app.domain.models import Listing, ScoreResult
from app.trust.recommendation import recommend


def listing(listing_id: str, price_cents: int) -> Listing:
    return Listing(
        id=listing_id,
        title=f"Item {listing_id}",
        price_cents=price_cents,
        merchant_name="Example",
        merchant_domain=f"{listing_id}.example",
        image_url="https://img.example/x.jpg",
        product_url=f"https://example.com/{listing_id}",
    )


def scored(
    score: int,
    verdict: Verdict = Verdict.TRUSTED,
    confidence: float = 1.0,
    allowlisted: bool = False,
) -> ScoreResult:
    return ScoreResult(
        score=score,
        verdict=verdict,
        confidence=confidence,
        top_reason="x",
        allowlisted=allowlisted,
    )


def test_allowlisted_listing_is_eligible_despite_zero_score():
    """The spec scores allowlisted merchants 0 while calling them trusted."""

    pick = listing("lst_storebrand", 20000)

    result = recommend([(pick, scored(0, allowlisted=True))])

    assert result.recommended_listing_id == "lst_storebrand"
    assert result.no_trusted_option is False


def test_picks_the_cheapest_eligible_listing():
    cheap = listing("lst_cheap", 17999)
    dear = listing("lst_dear", 32999)

    result = recommend([(dear, scored(100)), (cheap, scored(100))])

    assert result.recommended_listing_id == "lst_cheap"
    assert sorted(result.eligible_ids) == ["lst_cheap", "lst_dear"]


def test_excludes_danger_even_when_it_is_cheapest():
    villain = listing("lst_villain", 14999)
    hero = listing("lst_hero", 32999)

    result = recommend([(villain, scored(0, Verdict.DANGER)), (hero, scored(100))])

    assert result.recommended_listing_id == "lst_hero"
    assert "lst_villain" not in result.eligible_ids


def test_excludes_low_confidence_trusted_listings():
    thin = listing("lst_thin", 10000)
    solid = listing("lst_solid", 30000)

    result = recommend([(thin, scored(100, confidence=0.4)), (solid, scored(100))])

    assert result.recommended_listing_id == "lst_solid"
    assert result.eligible_ids == ["lst_solid"]


def test_excludes_trusted_but_below_score_floor():
    borderline = listing("lst_border", 10000)
    good = listing("lst_good", 30000)

    result = recommend([(borderline, scored(55)), (good, scored(100))])

    assert result.recommended_listing_id == "lst_good"


def test_median_and_savings_use_only_eligible_listings():
    picked = listing("lst_a", 10000)
    middle = listing("lst_b", 20000)
    priciest = listing("lst_c", 30000)
    rejected = listing("lst_d", 5000)

    result = recommend(
        [
            (picked, scored(100)),
            (middle, scored(100)),
            (priciest, scored(100)),
            (rejected, scored(0, Verdict.DANGER)),
        ]
    )

    assert result.recommended_listing_id == "lst_a"
    assert result.median_trusted_cents == 20000
    assert result.savings_cents == 10000


def test_tie_on_price_prefers_the_higher_score():
    low = listing("lst_low", 20000)
    high = listing("lst_high", 20000)

    result = recommend([(low, scored(80)), (high, scored(95))])

    assert result.recommended_listing_id == "lst_high"


def test_no_trusted_option_names_the_best_near_miss():
    worse = listing("lst_worse", 10000)
    closer = listing("lst_closer", 20000)

    result = recommend(
        [(worse, scored(20, Verdict.DANGER)), (closer, scored(65, Verdict.CAUTION))]
    )

    assert result.recommended_listing_id is None
    assert result.no_trusted_option is True
    assert result.median_trusted_cents is None
    assert "lst_closer" in result.reason


def test_empty_candidates_returns_no_trusted_option():
    result = recommend([])

    assert result.recommended_listing_id is None
    assert result.no_trusted_option is True
    assert result.eligible_ids == []
