"""Pick the cheapest listing that is safe to pay (D-006, D-015)."""

from __future__ import annotations

from app.domain.enums import Verdict
from app.domain.models import Listing, Recommendation, ScoreResult
from app.trust.scoring import TRUSTED_THRESHOLD

MIN_CONFIDENCE = 0.6
NO_LISTINGS_REASON = "No listings to compare."


def _eligible(score: ScoreResult) -> bool:
    """Allowlisted merchants are scored 0 by design, so the flag is what counts."""
    above_floor = score.score >= TRUSTED_THRESHOLD or score.allowlisted
    return (
        score.verdict == Verdict.TRUSTED
        and above_floor
        and score.confidence >= MIN_CONFIDENCE
    )


def _median_cents(prices: list[int]) -> int:
    ordered = sorted(prices)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def _near_miss_reason(candidates: list[tuple[Listing, ScoreResult]]) -> str:
    if not candidates:
        return NO_LISTINGS_REASON
    listing, score = max(candidates, key=lambda pair: pair[1].score)
    return (
        f"No trusted option. Closest was {listing.id} "
        f"at {score.score} ({score.verdict.value})."
    )


def recommend(candidates: list[tuple[Listing, ScoreResult]]) -> Recommendation:
    eligible = [(listing, score) for listing, score in candidates if _eligible(score)]
    if not eligible:
        return Recommendation(
            eligible_ids=[],
            reason=_near_miss_reason(candidates),
            no_trusted_option=True,
        )

    best_listing, _ = min(
        eligible, key=lambda pair: (pair[0].price_cents, -pair[1].score)
    )
    median = _median_cents([listing.price_cents for listing, _ in eligible])

    return Recommendation(
        recommended_listing_id=best_listing.id,
        median_trusted_cents=median,
        savings_cents=median - best_listing.price_cents,
        eligible_ids=[listing.id for listing, _ in eligible],
        reason=f"Cheapest of {len(eligible)} trusted options.",
        no_trusted_option=False,
    )
