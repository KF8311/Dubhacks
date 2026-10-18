"""The villain, start to finish, against the real checks and the real engines.

Every other test proves one piece. This one proves the pieces agree: the
fixtures feed the checks, the checks feed the score, the score keeps the
cheapest listing out of the recommendation.
"""

from app.checks.base import CheckContext, CheckTarget
from app.checks.registry import get_checks
from app.checks.runner import run_checks
from app.core.config import Settings
from app.domain.enums import CheckId, TrustStatus, Verdict
from app.domain.models import Listing
from app.trust.recommendation import recommend
from app.trust.scoring import score_investigation

VILLAIN = CheckTarget(
    listing_id="lst_vln_xm5",
    product_url="https://premium-audio-deals.shop/products/xm5",
    merchant_domain="premium-audio-deals.shop",
    merchant_name="Premium Audio Deals",
    price_cents=12049,
    category="audio",
)

VILLAIN_LISTING = Listing(
    id="lst_vln_xm5",
    title="XM5 Wireless Headphones — 70% OFF TODAY ONLY",
    price_cents=12049,
    merchant_name="Premium Audio Deals",
    merchant_domain="premium-audio-deals.shop",
    image_url="https://premium-audio-deals.shop/xm5.png",
    product_url=VILLAIN.product_url,
)

HERO_LISTING = Listing(
    id="lst_tgt_bsp",
    title="Sony WH-1000XM5 Wireless Noise Canceling Headphones",
    price_cents=17999,
    merchant_name="Target",
    merchant_domain="target.com",
    image_url="https://target.scene7.com/xm5.png",
    product_url="https://www.target.com/p/sony-wh-1000xm5/-/A-1",
)


async def villain_checks():
    ctx = CheckContext(config=Settings(offline=True))
    return {
        result.id: result
        async for result in run_checks(VILLAIN, get_checks(), ctx=ctx, timeout_s=6.0)
    }


async def test_every_check_that_can_run_fails_the_villain():
    results = await villain_checks()

    assert results[CheckId.SAFE_BROWSING].status == TrustStatus.FAILED
    assert results[CheckId.DOMAIN_AGE].status == TrustStatus.FAILED
    assert results[CheckId.PAGE_FLAGS].status == TrustStatus.FAILED
    assert results[CheckId.REDDIT].status in {
        TrustStatus.WARNING,
        TrustStatus.FAILED,
    }

    # Offline, SSL cannot be inspected; skipped is not a pass, and the verdict
    # below must not depend on it being one.
    assert results[CheckId.SSL].status in {TrustStatus.SKIPPED, TrustStatus.FAILED}

    fixture_backed = [
        result for result in results.values() if result.source == "fixture"
    ]
    assert fixture_backed, "the villain's evidence must come from fixtures"


async def test_the_villain_scores_danger():
    results = await villain_checks()

    score = score_investigation(list(results.values()), allowlisted=False)

    assert score.verdict == Verdict.DANGER
    assert score.score < 40
    assert score.top_reason


async def test_the_villain_is_excluded_even_when_it_is_cheapest():
    results = await villain_checks()
    villain_score = score_investigation(list(results.values()), allowlisted=False)
    hero_score = score_investigation([], allowlisted=True)

    recommendation = recommend(
        [(VILLAIN_LISTING, villain_score), (HERO_LISTING, hero_score)]
    )

    assert recommendation.recommended_listing_id == HERO_LISTING.id
    assert VILLAIN_LISTING.id not in recommendation.eligible_ids
    assert recommendation.no_trusted_option is False
