import pytest
from pydantic import ValidationError

from app.domain.enums import CheckId, TrustStatus
from app.domain.models import Listing, TrustCheckResult


def test_listing_accepts_positive_cents():
    listing = Listing(
        id="lst_1",
        title="Sony WH-1000XM5",
        price_cents=24900,
        merchant_name="Best Buy",
        merchant_domain="bestbuy.com",
        image_url="https://img.example/x.jpg",
        product_url="https://bestbuy.com/p/1",
    )
    assert listing.price_cents == 24900
    assert listing.currency == "USD"


def test_listing_rejects_nonpositive_price():
    with pytest.raises(ValidationError):
        Listing(
            id="lst_1",
            title="x",
            price_cents=0,
            merchant_name="m",
            merchant_domain="d.com",
            image_url="",
            product_url="",
        )


def test_check_severity_bounds():
    with pytest.raises(ValidationError):
        TrustCheckResult(
            id=CheckId.SSL,
            name="SSL",
            status=TrustStatus.FAILED,
            severity=1.5,
            summary="x",
            source="live",
        )
