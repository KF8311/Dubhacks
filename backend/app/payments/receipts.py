from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.ids import new_id
from app.domain.enums import TrustStatus
from app.domain.models import Checkout, Investigation, Listing, Receipt, Transaction


def _share_id() -> str:
    raw = base64.b32encode(secrets.token_bytes(8)).decode("ascii").rstrip("=").lower()
    return f"shr_{raw[:12]}"


def _sign(receipt_id: str, share_id: str, amount_cents: int, issued_at: datetime, secret: str) -> str:
    payload = f"{receipt_id}|{share_id}|{amount_cents}|{issued_at.isoformat()}"
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def create_receipt(
    checkout: Checkout,
    transaction: Transaction,
    listing: Listing,
    investigation: Investigation,
) -> Receipt:
    secret = get_settings().receipt_signing_secret
    issued_at = datetime.now(timezone.utc)
    receipt_id = new_id("rcp")
    share_id = _share_id()
    snapshot = investigation.model_copy(deep=True)
    verified = [check.name for check in investigation.checks if check.status == TrustStatus.PASSED]
    unverified = [check.name for check in investigation.checks if check.status != TrustStatus.PASSED]
    return Receipt(
        id=receipt_id,
        share_id=share_id,
        checkout_id=checkout.id,
        transaction_id=transaction.id,
        listing=listing.model_copy(deep=True),
        investigation_snapshot=snapshot,
        amount_cents=checkout.amount_cents,
        currency=checkout.currency,
        token_last4=transaction.token_last4,
        verified=verified,
        unverified=unverified,
        issued_at=issued_at,
        signature=_sign(receipt_id, share_id, checkout.amount_cents, issued_at, secret),
    )


def verify_receipt(receipt: Receipt, secret: str) -> bool:
    expected = _sign(receipt.id, receipt.share_id, receipt.amount_cents, receipt.issued_at, secret)
    return hmac.compare_digest(expected, receipt.signature)
