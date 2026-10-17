"""Cheapest trusted listing. Never recommend caution or danger."""

from __future__ import annotations

from statistics import median

from pydantic import BaseModel, Field

from app.domain.enums import Verdict
from app.domain.models import Listing, ScoreResult
from app.trust.scoring import ALLOWLIST_REASON, TRUSTED_THRESHOLD

MIN_CONFIDENCE = 0.6


class Recommendation(BaseModel):
    recommended_listing_id: str | None
    median_trusted_cents: int | None
    savings_cents: int | None
    eligible_ids: list[str] = Field(default_factory=list)
    reason: str
    no_trusted_option: bool


def _eligible(score: ScoreResult) -> bool:
    if score.verdict != Verdict.TRUSTED:
        return False
    if score.top_reason == ALLOWLIST_REASON:
        return True
    return score.score >= TRUSTED_THRESHOLD and score.confidence >= MIN_CONFIDENCE


def recommend(pairs: list[tuple[Listing, ScoreResult]]) -> Recommendation:
    eligible = [(listing, score) for listing, score in pairs if _eligible(score)]
    eligible.sort(key=lambda pair: (pair[0].price_cents, -pair[1].score))
    ids = [listing.id for listing, _ in eligible]
    if not eligible:
        near = max(pairs, key=lambda pair: pair[1].score, default=None)
        if near is None:
            reason = "No listings to recommend."
        else:
            listing, score = near
            reason = (
                f"No trusted listing. Best near-miss: {listing.id} "
                f"({score.verdict.value}, {score.score})."
            )
        return Recommendation(
            recommended_listing_id=None,
            median_trusted_cents=None,
            savings_cents=None,
            eligible_ids=[],
            reason=reason,
            no_trusted_option=True,
        )

    best, _ = eligible[0]
    prices = [listing.price_cents for listing, _ in eligible]
    median_cents = int(median(prices))
    savings = median_cents - best.price_cents
    return Recommendation(
        recommended_listing_id=best.id,
        median_trusted_cents=median_cents,
        savings_cents=savings if savings > 0 else None,
        eligible_ids=ids,
        reason="Cheapest trusted listing.",
        no_trusted_option=False,
    )
