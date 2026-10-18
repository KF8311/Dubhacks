"""TTL and unique indexes. Safe to call on every startup."""

from __future__ import annotations

AUDIT_TTL_S = 7 * 24 * 3600
SESSION_TTL_S = 2 * 3600  # documents already carry expires_at; TTL 0 uses that field
CACHE_TTL_FIELD = "expires_at"


async def _drop_unique_index(collection, key: str) -> None:
    """Remove a unique index an older build created on a now-shared field."""
    for name, info in (await collection.index_information()).items():
        if info.get("key") == [(key, 1)] and info.get("unique"):
            await collection.drop_index(name)


async def ensure_indexes(db) -> None:
    await db.sessions.create_index("expires_at", expireAfterSeconds=0)
    await db.sessions.create_index("updated_at")

    # Listings are keyed by _id. product_url is not unique: every Google
    # Shopping result for a query now points at the same results page (D-030),
    # and a unique index turned the second save into a DuplicateKeyError that
    # killed the orchestrator mid-session.
    await _drop_unique_index(db.listings, "product_url")
    await db.listings.create_index("product_url")
    await db.listings.create_index("merchant_domain")

    await db.investigations.create_index("listing_id")
    await db.investigations.create_index("session_id")
    await db.investigations.create_index("created_at")

    await db.mandates.create_index("session_id")
    await db.mandates.create_index([("status", 1), ("expires_at", 1)])

    await db.checkouts.create_index(
        "idempotency_key",
        unique=True,
        partialFilterExpression={"idempotency_key": {"$type": "string"}},
    )
    await db.checkouts.create_index([("stage", 1), ("expires_at", 1)])

    await db.transactions.create_index("checkout_id", unique=True)
    await db.payment_tokens.create_index("checkout_id")

    await db.receipts.create_index("share_id", unique=True)
    await db.receipts.create_index("checkout_id", unique=True)

    await db.merchant_cache.create_index("expires_at", expireAfterSeconds=0)
    await db.reddit_cache.create_index("expires_at", expireAfterSeconds=0)

    await db.audit_events.create_index([("session_id", 1), ("ts", 1)])
    await db.audit_events.create_index("ts", expireAfterSeconds=AUDIT_TTL_S)
