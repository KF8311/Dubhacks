from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from enum import Enum
from collections.abc import Awaitable
from typing import Protocol

from pydantic import BaseModel

from app.domain.enums import CheckoutStage
from app.domain.models import (
    Checkout,
    Investigation,
    Listing,
    Mandate,
    Receipt,
    Session,
    Transaction,
)
from app.services.audit import AuditEvent, redact_payload

_repo: "Repository | None" = None
_db_status = "unavailable"


def _stage_value(stage: CheckoutStage | str) -> str:
    if isinstance(stage, CheckoutStage):
        return stage.value
    return str(stage)


def _as_stage(stage: CheckoutStage | str) -> CheckoutStage:
    return stage if isinstance(stage, CheckoutStage) else CheckoutStage(stage)


def _doc(model: BaseModel) -> dict:
    data = model.model_dump(mode="python")
    data["_id"] = data.pop("id")

    def convert(value):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return {key: convert(item) for key, item in value.items()}
        if isinstance(value, list):
            return [convert(item) for item in value]
        return value

    return convert(data)


def _utc(value):
    """BSON hands datetimes back without tzinfo; the domain compares them to an aware now."""
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    if isinstance(value, dict):
        return {key: _utc(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_utc(item) for item in value]
    return value


def _hydrate(model_cls, doc: dict | None):
    if doc is None:
        return None
    data = dict(doc)
    if "_id" in data:
        data["id"] = data.pop("_id")
    return model_cls.model_validate(_utc(data))


class Repository(Protocol):
    def clear(self) -> Awaitable[None] | None: ...
    async def save_session(self, session: Session) -> None: ...
    async def save_listing(self, listing: Listing) -> None: ...
    async def save_investigation(self, inv: Investigation) -> None: ...
    async def get_investigation(self, investigation_id: str) -> Investigation | None: ...
    async def save_mandate(self, mandate: Mandate) -> None: ...
    async def get_mandate(self, mandate_id: str) -> Mandate | None: ...
    async def save_checkout(self, checkout: Checkout) -> None: ...
    async def get_checkout(self, checkout_id: str) -> Checkout | None: ...
    async def transition_checkout(
        self,
        checkout_id: str,
        from_stage: CheckoutStage | str,
        to_stage: CheckoutStage | str,
    ) -> bool: ...
    async def save_receipt(self, receipt: Receipt) -> None: ...
    async def get_receipt(self, receipt_id: str) -> Receipt | None: ...
    async def get_receipt_by_share_id(self, share_id: str) -> Receipt | None: ...
    async def get_receipt_for_checkout(self, checkout_id: str) -> Receipt | None: ...
    async def save_transaction(self, transaction: Transaction) -> None: ...
    async def get_transaction(self, transaction_id: str) -> Transaction | None: ...
    async def audit(self, event: AuditEvent) -> None: ...


class InMemoryRepository:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._sessions: dict[str, Session] = {}
        self._listings: dict[str, Listing] = {}
        self._investigations: dict[str, Investigation] = {}
        self._mandates: dict[str, Mandate] = {}
        self._checkouts: dict[str, Checkout] = {}
        self._receipts: dict[str, Receipt] = {}
        self._receipts_by_share: dict[str, str] = {}
        self._receipts_by_checkout: dict[str, str] = {}
        self._transactions: dict[str, Transaction] = {}
        self._audit: list[AuditEvent] = []

    @classmethod
    def shared(cls) -> "InMemoryRepository":
        global _shared_memory
        if _shared_memory is None:
            _shared_memory = cls()
        return _shared_memory

    def clear(self) -> None:
        self._sessions.clear()
        self._listings.clear()
        self._investigations.clear()
        self._mandates.clear()
        self._checkouts.clear()
        self._receipts.clear()
        self._receipts_by_share.clear()
        self._receipts_by_checkout.clear()
        self._transactions.clear()
        self._audit.clear()

    async def save_session(self, session: Session) -> None:
        async with self._lock:
            self._sessions[session.id] = session.model_copy(deep=True)

    async def save_listing(self, listing: Listing) -> None:
        async with self._lock:
            self._listings[listing.id] = listing.model_copy(deep=True)

    async def save_investigation(self, inv: Investigation) -> None:
        async with self._lock:
            self._investigations[inv.id] = inv.model_copy(deep=True)

    async def get_investigation(self, investigation_id: str) -> Investigation | None:
        async with self._lock:
            found = self._investigations.get(investigation_id)
            return found.model_copy(deep=True) if found else None

    async def save_mandate(self, mandate: Mandate) -> None:
        async with self._lock:
            self._mandates[mandate.id] = mandate.model_copy(deep=True)

    async def get_mandate(self, mandate_id: str) -> Mandate | None:
        async with self._lock:
            found = self._mandates.get(mandate_id)
            return found.model_copy(deep=True) if found else None

    async def save_checkout(self, checkout: Checkout) -> None:
        async with self._lock:
            self._checkouts[checkout.id] = checkout.model_copy(deep=True)

    async def get_checkout(self, checkout_id: str) -> Checkout | None:
        async with self._lock:
            found = self._checkouts.get(checkout_id)
            return found.model_copy(deep=True) if found else None

    async def transition_checkout(
        self,
        checkout_id: str,
        from_stage: CheckoutStage | str,
        to_stage: CheckoutStage | str,
    ) -> bool:
        async with self._lock:
            checkout = self._checkouts.get(checkout_id)
            if checkout is None or checkout.stage != _as_stage(from_stage):
                return False
            self._checkouts[checkout_id] = checkout.model_copy(
                update={"stage": _as_stage(to_stage)}
            )
            return True

    async def save_receipt(self, receipt: Receipt) -> None:
        async with self._lock:
            self._receipts[receipt.id] = receipt.model_copy(deep=True)
            self._receipts_by_share[receipt.share_id] = receipt.id
            self._receipts_by_checkout[receipt.checkout_id] = receipt.id

    async def get_receipt(self, receipt_id: str) -> Receipt | None:
        async with self._lock:
            found = self._receipts.get(receipt_id)
            return found.model_copy(deep=True) if found else None

    async def get_receipt_by_share_id(self, share_id: str) -> Receipt | None:
        async with self._lock:
            receipt_id = self._receipts_by_share.get(share_id)
            found = self._receipts.get(receipt_id) if receipt_id else None
            return found.model_copy(deep=True) if found else None

    async def get_receipt_for_checkout(self, checkout_id: str) -> Receipt | None:
        async with self._lock:
            receipt_id = self._receipts_by_checkout.get(checkout_id)
            found = self._receipts.get(receipt_id) if receipt_id else None
            return found.model_copy(deep=True) if found else None

    async def save_transaction(self, transaction: Transaction) -> None:
        async with self._lock:
            self._transactions[transaction.id] = transaction.model_copy(deep=True)

    async def get_transaction(self, transaction_id: str) -> Transaction | None:
        async with self._lock:
            found = self._transactions.get(transaction_id)
            return found.model_copy(deep=True) if found else None

    async def audit(self, event: AuditEvent) -> None:
        redacted = event.model_copy(update={"payload_redacted": redact_payload(event.payload_redacted)})
        async with self._lock:
            self._audit.append(redacted)


_shared_memory: InMemoryRepository | None = None


class MongoRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def save_session(self, session: Session) -> None:
        await self.db.sessions.replace_one({"_id": session.id}, _doc(session), upsert=True)

    async def save_listing(self, listing: Listing) -> None:
        await self.db.listings.replace_one({"_id": listing.id}, _doc(listing), upsert=True)

    async def save_investigation(self, inv: Investigation) -> None:
        await self.db.investigations.replace_one({"_id": inv.id}, _doc(inv), upsert=True)

    async def get_investigation(self, investigation_id: str) -> Investigation | None:
        return _hydrate(Investigation, await self.db.investigations.find_one({"_id": investigation_id}))

    async def save_mandate(self, mandate: Mandate) -> None:
        await self.db.mandates.replace_one({"_id": mandate.id}, _doc(mandate), upsert=True)

    async def get_mandate(self, mandate_id: str) -> Mandate | None:
        return _hydrate(Mandate, await self.db.mandates.find_one({"_id": mandate_id}))

    async def save_checkout(self, checkout: Checkout) -> None:
        await self.db.checkouts.replace_one({"_id": checkout.id}, _doc(checkout), upsert=True)

    async def get_checkout(self, checkout_id: str) -> Checkout | None:
        return _hydrate(Checkout, await self.db.checkouts.find_one({"_id": checkout_id}))

    async def transition_checkout(
        self,
        checkout_id: str,
        from_stage: CheckoutStage | str,
        to_stage: CheckoutStage | str,
    ) -> bool:
        doc = await self.db.checkouts.find_one_and_update(
            {"_id": checkout_id, "stage": _stage_value(from_stage)},
            {"$set": {"stage": _stage_value(to_stage)}},
        )
        return doc is not None

    async def save_receipt(self, receipt: Receipt) -> None:
        await self.db.receipts.replace_one({"_id": receipt.id}, _doc(receipt), upsert=True)

    async def get_receipt(self, receipt_id: str) -> Receipt | None:
        return _hydrate(Receipt, await self.db.receipts.find_one({"_id": receipt_id}))

    async def get_receipt_by_share_id(self, share_id: str) -> Receipt | None:
        return _hydrate(Receipt, await self.db.receipts.find_one({"share_id": share_id}))

    async def get_receipt_for_checkout(self, checkout_id: str) -> Receipt | None:
        return _hydrate(Receipt, await self.db.receipts.find_one({"checkout_id": checkout_id}))

    async def save_transaction(self, transaction: Transaction) -> None:
        await self.db.transactions.replace_one({"_id": transaction.id}, _doc(transaction), upsert=True)

    async def get_transaction(self, transaction_id: str) -> Transaction | None:
        return _hydrate(Transaction, await self.db.transactions.find_one({"_id": transaction_id}))

    async def audit(self, event: AuditEvent) -> None:
        payload = event.model_dump(mode="python")
        payload["payload_redacted"] = redact_payload(event.payload_redacted)
        await self.db.audit_events.insert_one(payload)

    async def clear(self) -> None:
        for name in (
            "sessions",
            "listings",
            "investigations",
            "mandates",
            "checkouts",
            "transactions",
            "receipts",
            "audit_events",
        ):
            await getattr(self.db, name).delete_many({})


def get_repository() -> Repository:
    return _repo if _repo is not None else InMemoryRepository.shared()


def get_db_status() -> str:
    return _db_status


def set_repository(repo: InMemoryRepository | MongoRepository, db_status: str) -> None:
    global _repo, _db_status
    _repo = repo
    _db_status = db_status


async def reset_repository() -> None:
    repo = get_repository()
    clearer = getattr(repo, "clear", None)
    if clearer is None:
        return
    result = clearer()
    if asyncio.iscoroutine(result):
        await result
