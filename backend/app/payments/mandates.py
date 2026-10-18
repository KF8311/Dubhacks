from datetime import datetime, timedelta, timezone

from app.core.ids import new_id
from app.domain.models import Listing, Mandate


def create_mandate(
    listing: Listing,
    *,
    max_amount_cents: int,
    currency: str = "USD",
    expires_in_seconds: int = 600,
    now: datetime | None = None,
    session_id: str = "ses_pending",
    investigation_id: str = "inv_pending",
) -> Mandate:
    if max_amount_cents < listing.price_cents:
        raise ValueError("max_amount_cents must be >= listing.price_cents")
    now = now or datetime.now(timezone.utc)
    return Mandate(
        id=new_id("man"),
        session_id=session_id,
        listing_id=listing.id,
        investigation_id=investigation_id,
        merchant_domain=listing.merchant_domain,
        max_amount_cents=max_amount_cents,
        currency=currency,
        expires_at=now + timedelta(seconds=expires_in_seconds),
        status="active",
    )
