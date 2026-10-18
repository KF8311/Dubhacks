from __future__ import annotations

import logging

from app.core.config import get_settings
from app.db.indexes import ensure_indexes
from app.services.repository import InMemoryRepository, MongoRepository, set_repository

log = logging.getLogger(__name__)

_client = None


async def init_persistence() -> None:
    global _client
    settings = get_settings()
    uri = settings.mongodb_uri
    if not uri:
        set_repository(InMemoryRepository.shared(), "unavailable")
        return
    client = None
    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=800)
        await client.admin.command("ping")
        db = client[settings.mongodb_db]
        await ensure_indexes(db)
        _client = client
        set_repository(MongoRepository(db), "ok")
    except Exception:
        log.warning("mongodb ping failed; using in-memory repository", exc_info=True)
        if client is not None:
            client.close()
        _client = None
        set_repository(InMemoryRepository.shared(), "unavailable")


async def close_persistence() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
    set_repository(InMemoryRepository.shared(), "unavailable")
