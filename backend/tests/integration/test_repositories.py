from datetime import datetime, timedelta, timezone

import pytest

from app.core.logging import redact
from app.domain.enums import CheckoutStage
from app.domain.models import Checkout
from app.services.repository import InMemoryRepository


def test_redacts_email_and_phone():
    assert "a@b.com" not in redact("contact a@b.com")
    assert "555-123-4567" not in redact("call 555-123-4567")


def _checkout() -> Checkout:
    now = datetime.now(timezone.utc)
    return Checkout(
        id="chk_1",
        session_id="ses_1",
        listing_id="lst_1",
        investigation_id="inv_1",
        mandate_id="man_1",
        amount_cents=17999,
        stage=CheckoutStage.AWAITING_PASSKEY,
        idempotency_key="k1",
        created_at=now,
        expires_at=now + timedelta(minutes=5),
    )


@pytest.mark.asyncio
async def test_checkout_transition_is_atomic():
    repo = InMemoryRepository()
    checkout = _checkout()
    await repo.save_checkout(checkout)
    assert await repo.transition_checkout(checkout.id, "awaiting_passkey", "captured")
    assert not await repo.transition_checkout(checkout.id, "awaiting_passkey", "captured")


@pytest.mark.asyncio
async def test_memory_repo_round_trips_a_receipt_share_id():
    from app.domain.models import Investigation, Listing, Receipt, ScoreResult
    from app.domain.enums import Verdict

    now = datetime.now(timezone.utc)
    listing = Listing(
        id="lst_1",
        title="x",
        price_cents=1000,
        merchant_name="m",
        merchant_domain="bestbuy.com",
        image_url="",
        product_url="https://bestbuy.com/p/1",
    )
    inv = Investigation(
        id="inv_1",
        listing_id="lst_1",
        session_id="ses_1",
        checks=[],
        score=ScoreResult(score=90, verdict=Verdict.TRUSTED, confidence=1.0, top_reason="ok"),
        allowlisted=True,
        duration_ms=1,
        created_at=now,
    )
    receipt = Receipt(
        id="rcp_1",
        share_id="shr_abc123def456",
        checkout_id="chk_1",
        transaction_id="txn_1",
        listing=listing,
        investigation_snapshot=inv,
        amount_cents=1000,
        currency="USD",
        token_last4="4242",
        verified=["SSL"],
        unverified=[],
        issued_at=now,
        signature="sig",
    )
    repo = InMemoryRepository()
    await repo.save_receipt(receipt)
    loaded = await repo.get_receipt_by_share_id("shr_abc123def456")
    assert loaded is not None
    assert loaded.token_last4 == "4242"


class _FakeCollection:
    def __init__(self) -> None:
        self.docs: dict = {}
        self.calls: list = []
        self.indexes: list = []

    async def create_index(self, *args, **kwargs):
        self.indexes.append((args, kwargs))

    async def replace_one(self, filt, doc, upsert=False):
        self.docs[filt["_id"]] = doc

    async def find_one(self, filt):
        if "_id" in filt:
            return self.docs.get(filt["_id"])
        for doc in self.docs.values():
            if all(doc.get(key) == value for key, value in filt.items()):
                return doc
        return None

    async def find_one_and_update(self, filt, update):
        self.calls.append((filt, update))
        doc = self.docs.get(filt.get("_id"))
        if doc is None:
            return None
        if doc.get("stage") != filt.get("stage"):
            return None
        doc = {**doc, **update.get("$set", {})}
        self.docs[filt["_id"]] = doc
        return doc

    async def insert_one(self, doc):
        self.docs[doc.get("_id", len(self.docs))] = doc

    async def delete_many(self, _filt):
        self.docs.clear()


class _FakeDB:
    def __init__(self) -> None:
        self._cols: dict[str, _FakeCollection] = {}

    def __getattr__(self, name: str) -> _FakeCollection:
        if name not in self._cols:
            self._cols[name] = _FakeCollection()
        return self._cols[name]


@pytest.mark.asyncio
async def test_mongo_transition_uses_find_one_and_update():
    from app.services.repository import MongoRepository

    db = _FakeDB()
    repo = MongoRepository(db)
    checkout = _checkout()
    await repo.save_checkout(checkout)
    assert await repo.transition_checkout(checkout.id, "awaiting_passkey", "captured")
    assert not await repo.transition_checkout(checkout.id, "awaiting_passkey", "captured")
    filt, update = db.checkouts.calls[0]
    assert filt == {"_id": checkout.id, "stage": "awaiting_passkey"}
    assert update == {"$set": {"stage": "captured"}}


@pytest.mark.asyncio
async def test_mongo_hydrates_naive_datetimes_as_utc():
    """Motor hands back naive UTC datetimes; the payability gate compares them to an aware now."""
    from app.services.repository import MongoRepository

    db = _FakeDB()
    repo = MongoRepository(db)
    checkout = _checkout()
    await repo.save_checkout(checkout)
    stored = db.checkouts.docs[checkout.id]
    stored["created_at"] = stored["created_at"].replace(tzinfo=None)
    stored["expires_at"] = stored["expires_at"].replace(tzinfo=None)

    loaded = await repo.get_checkout(checkout.id)
    assert loaded is not None
    assert loaded.created_at.tzinfo is not None
    assert loaded.created_at == checkout.created_at
    assert loaded.expires_at == checkout.expires_at


@pytest.mark.asyncio
async def test_indexes_include_ttl_and_unique():
    from app.db.indexes import ensure_indexes

    db = _FakeDB()
    await ensure_indexes(db)
    session_ttl = [kwargs for args, kwargs in db.sessions.indexes if kwargs.get("expireAfterSeconds") == 0]
    assert session_ttl
    audit_ttl = [kwargs for args, kwargs in db.audit_events.indexes if kwargs.get("expireAfterSeconds") == 7 * 24 * 3600]
    assert audit_ttl
    unique_share = [kwargs for args, kwargs in db.receipts.indexes if kwargs.get("unique") is True]
    assert unique_share


@pytest.mark.asyncio
async def test_empty_or_failed_mongo_selects_memory(monkeypatch):
    from app.core.config import Settings
    from app.db.mongo import init_persistence
    from app.services.repository import InMemoryRepository, get_db_status, get_repository

    monkeypatch.setattr("app.db.mongo.get_settings", lambda: Settings(mongodb_uri=None))
    await init_persistence()
    assert isinstance(get_repository(), InMemoryRepository)
    assert get_db_status() == "unavailable"

    class _BoomAdmin:
        async def command(self, _name):
            raise RuntimeError("down")

    class _BoomClient:
        def __init__(self, *_args, **_kwargs):
            self.admin = _BoomAdmin()

        def close(self):
            return None

        def __getitem__(self, _name):
            raise AssertionError("should not open a db after ping failure")

    monkeypatch.setattr("app.db.mongo.get_settings", lambda: Settings(mongodb_uri="mongodb://example/sniff"))
    monkeypatch.setattr("motor.motor_asyncio.AsyncIOMotorClient", _BoomClient)
    await init_persistence()
    assert isinstance(get_repository(), InMemoryRepository)
    assert get_db_status() == "unavailable"


def _public_callables(cls: type) -> set[str]:
    return {name for name in dir(cls) if not name.startswith("_") and callable(getattr(cls, name))}


def test_protocol_declares_every_method_both_adapters_expose():
    from app.services.repository import InMemoryRepository, MongoRepository, Repository

    shared = _public_callables(InMemoryRepository) & _public_callables(MongoRepository)
    declared = {name for name in dir(Repository) if not name.startswith("_")}
    assert shared - declared == set()


def test_get_repository_is_typed_as_the_protocol():
    from typing import get_type_hints

    from app.services.repository import Repository, get_repository

    assert get_type_hints(get_repository)["return"] is Repository


@pytest.mark.asyncio
async def test_checkout_idempotency_index_ignores_nulls_but_rejects_duplicates():
    from app.db.indexes import ensure_indexes

    db = _FakeDB()
    await ensure_indexes(db)
    [index] = [kwargs for args, kwargs in db.checkouts.indexes if args and args[0] == "idempotency_key"]
    assert index.get("unique") is True
    assert index.get("sparse") is not True
    assert index.get("partialFilterExpression") == {"idempotency_key": {"$type": "string"}}
