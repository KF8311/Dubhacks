from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.errors import AppError
from app.core.ids import new_id
from app.domain.enums import CheckoutStage
from app.domain.models import Checkout, Investigation, Listing
from app.payments.mandates import create_mandate
from app.payments.memory import store
from app.payments.mock_vic import authorize, consume_token, issue_token
from app.payments.payability import MandateDraft, PayabilityError, assert_payable
from app.payments.receipts import create_receipt
from app.search.catalog import load_catalog
from app.sessions.store import registry

SANDBOX = "Sandbox — simulated Visa Intelligent Commerce flow."
router = APIRouter()


class MandateIn(BaseModel):
    max_amount_cents: int = Field(gt=0)
    currency: str = "USD"
    expires_in_seconds: int = 600


class CheckoutIn(BaseModel):
    session_id: str
    listing_id: str
    mandate: MandateIn


class PasskeyIn(BaseModel):
    credential_id: str
    client_data: str


class ConfirmIn(BaseModel):
    passkey_assertion: PasskeyIn
    idempotency_key: str


def _get_listing(listing_id: str) -> Listing | None:
    found = registry.listing_by_id(listing_id)
    if found is not None:
        return found
    for item in load_catalog():
        if item.id == listing_id:
            return item
    return None


def _get_investigation(session_id: str, listing_id: str) -> Investigation | None:
    return registry.investigation_for(session_id, listing_id)


# The code is the machine contract; the message is what the checkout sheet shows.
PAYABILITY_MESSAGES = {
    "MERCHANT_NOT_TRUSTED": "This merchant did not pass the trust checks.",
    "SCORE_TOO_LOW": "This merchant's trust score is below the payment threshold.",
    "COVERAGE_TOO_LOW": "Too few trust checks completed to authorize payment.",
    "MERCHANT_MISMATCH": "The mandate is for a different merchant.",
    "AMOUNT_EXCEEDS_CAP": "The price is above the mandate cap.",
    "MANDATE_EXPIRED": "The mandate expired before payment.",
    "ALREADY_PAID": "This checkout was already paid.",
    "INVESTIGATION_STALE": "The investigation is stale; rerun it before paying.",
}


def _raise_payability(exc: PayabilityError) -> None:
    message = PAYABILITY_MESSAGES.get(exc.code.value, exc.code.value)
    raise AppError(exc.code.value, message, status_code=409, details=exc.details)


def _confirm_payload(checkout: Checkout) -> dict:
    receipt_id = store.by_checkout[checkout.id]
    receipt = store.receipts[receipt_id]
    txn = store.transactions[receipt.transaction_id]
    return {
        "checkout_id": checkout.id,
        "status": checkout.stage.value,
        "transaction": {
            "id": txn.id,
            "status": txn.status,
            "amount_cents": txn.amount_cents,
            "currency": txn.currency,
            "network": "visa",
            "token_last4": txn.token_last4,
            "processor": txn.processor,
            "mode": txn.mode,
        },
        "receipt_id": receipt.id,
        "receipt_url": f"/r/{receipt.share_id}",
        "sandbox_label": SANDBOX,
    }


@router.post("/api/checkout", status_code=201)
async def create_checkout(body: CheckoutIn) -> dict:
    if registry.get(body.session_id) is None:
        raise AppError("SESSION_NOT_FOUND", "Session not found.", status_code=404)
    listing = _get_listing(body.listing_id)
    if listing is None:
        raise AppError("LISTING_NOT_FOUND", "Listing not found.", status_code=404)
    investigation = _get_investigation(body.session_id, body.listing_id)
    if investigation is None:
        raise AppError("INVESTIGATION_STALE", "Investigation not found.", status_code=409)

    now = datetime.now(timezone.utc)
    draft = MandateDraft(
        merchant_domain=listing.merchant_domain,
        max_amount_cents=body.mandate.max_amount_cents,
        currency=body.mandate.currency,
    )
    try:
        assert_payable(investigation, listing, draft, now=now)
        mandate = create_mandate(
            listing,
            max_amount_cents=body.mandate.max_amount_cents,
            currency=body.mandate.currency,
            expires_in_seconds=body.mandate.expires_in_seconds,
            now=now,
            session_id=body.session_id,
            investigation_id=investigation.id,
        )
        assert_payable(investigation, listing, mandate, now=now)
    except PayabilityError as exc:
        _raise_payability(exc)
    except ValueError as exc:
        raise AppError("AMOUNT_EXCEEDS_CAP", str(exc), status_code=409) from exc

    checkout = Checkout(
        id=new_id("chk"),
        session_id=body.session_id,
        listing_id=listing.id,
        investigation_id=investigation.id,
        mandate_id=mandate.id,
        amount_cents=listing.price_cents,
        currency=listing.currency,
        stage=CheckoutStage.AWAITING_PASSKEY,
        idempotency_key="",
        created_at=now,
        expires_at=now + timedelta(minutes=5),
    )
    issued = await issue_token(checkout.id, listing.merchant_domain)
    store.mandates[mandate.id] = mandate
    store.checkouts[checkout.id] = checkout
    store.token_by_checkout[checkout.id] = issued.token_id
    return {
        "checkout_id": checkout.id,
        "stage": checkout.stage.value,
        "amount_cents": checkout.amount_cents,
        "currency": checkout.currency,
        "merchant": {"name": listing.merchant_name, "domain": listing.merchant_domain},
        "mandate": {
            "id": mandate.id,
            "max_amount_cents": mandate.max_amount_cents,
            "merchant_domain": mandate.merchant_domain,
            "expires_at": mandate.expires_at.isoformat().replace("+00:00", "Z"),
            "single_use": True,
        },
        "trust_snapshot": {
            "score": investigation.score.score,
            "verdict": investigation.score.verdict.value,
            "confidence": investigation.score.confidence,
            "investigation_id": investigation.id,
            "scoring_version": investigation.score.scoring_version,
        },
        "passkey_challenge": {
            "challenge": "c2ltdWxhdGVkLXBhc3NrZXktY2hhbGxlbmdl",
            "rp_id": "sniff.vercel.app",
            "timeout_ms": 60000,
            "mode": "simulated",
        },
        "sandbox_label": SANDBOX,
        "expires_at": checkout.expires_at.isoformat().replace("+00:00", "Z"),
    }


@router.post("/api/checkout/{checkout_id}/confirm")
async def confirm_checkout(checkout_id: str, body: ConfirmIn) -> dict:
    checkout = store.checkouts.get(checkout_id)
    if checkout is None:
        raise AppError("CHECKOUT_NOT_FOUND", "Checkout not found.", status_code=404)
    if checkout.stage == CheckoutStage.CAPTURED and checkout_id in store.by_checkout:
        return _confirm_payload(checkout)
    if checkout.stage == CheckoutStage.DECLINED:
        raise AppError("PAYMENT_DECLINED", "Payment was declined.", status_code=402)

    listing = _get_listing(checkout.listing_id)
    investigation = _get_investigation(checkout.session_id, checkout.listing_id)
    mandate = store.mandates.get(checkout.mandate_id)
    if listing is None or investigation is None or mandate is None:
        raise AppError("INVESTIGATION_STALE", "Checkout is missing investigation state.", status_code=409)

    now = datetime.now(timezone.utc)
    try:
        assert_payable(investigation, listing, mandate, now=now, checkout=checkout)
    except PayabilityError as exc:
        _raise_payability(exc)

    declined = body.passkey_assertion.client_data == "fail"
    token_id = store.token_by_checkout[checkout.id]
    txn = await authorize(checkout.amount_cents, token_id, declined=declined)
    if declined:
        checkout.stage = CheckoutStage.DECLINED
        store.checkouts[checkout.id] = checkout
        raise AppError("PAYMENT_DECLINED", "Payment was declined.", status_code=402)

    await consume_token(token_id)
    checkout.stage = CheckoutStage.AUTHORIZED
    checkout.idempotency_key = body.idempotency_key
    checkout.stage = CheckoutStage.CAPTURED
    mandate.status = "consumed"
    receipt = create_receipt(checkout, txn, listing, investigation)
    store.checkouts[checkout.id] = checkout
    store.mandates[mandate.id] = mandate
    store.transactions[txn.id] = txn
    store.receipts[receipt.id] = receipt
    store.by_share[receipt.share_id] = receipt.id
    store.by_checkout[checkout.id] = receipt.id
    return _confirm_payload(checkout)
