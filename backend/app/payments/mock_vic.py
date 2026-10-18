from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.ids import new_id
from app.domain.models import Transaction

SANDBOX_LAST4 = "4242"
_RAW_ONCE = "vic_sandbox_token_4242"


@dataclass
class IssuedToken:
    token_id: str
    raw_token: str
    token_hash: str
    last4: str


_tokens: dict[str, dict] = {}


def reset() -> None:
    _tokens.clear()


def _hash(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


async def issue_token(checkout_id: str, merchant_domain: str) -> IssuedToken:
    del merchant_domain
    token_id = new_id("tok")
    token_hash = _hash(_RAW_ONCE)
    _tokens[token_id] = {
        "checkout_id": checkout_id,
        "token_hash": token_hash,
        "last4": SANDBOX_LAST4,
        "status": "issued",
    }
    return IssuedToken(
        token_id=token_id,
        raw_token=_RAW_ONCE,
        token_hash=token_hash,
        last4=SANDBOX_LAST4,
    )


async def consume_token(token_id: str) -> None:
    record = _tokens.get(token_id)
    if record is None:
        raise RuntimeError("unknown token")
    if record["status"] != "issued":
        raise RuntimeError("token already consumed")
    record["status"] = "consumed"


async def authorize(amount_cents: int, token_id: str, *, declined: bool = False) -> Transaction:
    record = _tokens[token_id]
    digest = hashlib.sha256(token_id.encode()).hexdigest()[:6].upper()
    return Transaction(
        id=new_id("txn"),
        checkout_id=record["checkout_id"],
        status="declined" if declined else "approved",
        amount_cents=amount_cents,
        currency="USD",
        token_last4=SANDBOX_LAST4,
        auth_code="FAIL00" if declined else f"MOCK{digest}",
        created_at=datetime.now(timezone.utc),
    )
