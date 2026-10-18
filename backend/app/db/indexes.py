"""TTL and unique indexes. Safe to call on every startup."""

from __future__ import annotations

AUDIT_TTL_S = 7 * 24 * 3600
SESSION_TTL_S = 2 * 3600  # documents already carry expires_at; TTL 0 uses that field
CACHE_TTL_FIELD = "expires_at"


async def ensure_indexes(db) -> None:
    await db.sessions.create_index("expires_at", expireAfterSeconds=0)
    await db.sessions.create_index("updated_at")

    await db.listings.create_index("product_url", unique=True)
    await db.listings.create_index("merchant_domain")

    await db.investigations.create_index("listing_id")
    await db.investigations.create_index("session_id")
    await db.investigations.create_index("created_at")

    await db.mandates.create_index("session_id")
    await db.mandates.create_index([("status", 1), ("expires_at", 1)])

    await db.checkouts.create_index("idempotency_key", unique=True, sparse=True)
    await db.checkouts.create_index([("stage", 1), ("expires_at", 1)])

    await db.transactions.create_index("checkout_id", unique=True)
    await db.payment_tokens.create_index("checkout_id")

    await db.receipts.create_index("share_id", unique=True)
    await db.receipts.create_index("checkout_id", unique=True)

    await db.merchant_cache.create_index("expires_at", expireAfterSeconds=0)
    await db.reddit_cache.create_index("expires_at", expireAfterSeconds=0)

    await db.audit_events.create_index([("session_id", 1), ("ts", 1)])
    await db.audit_events.create_index("ts", expireAfterSeconds=AUDIT_TTL_S)
