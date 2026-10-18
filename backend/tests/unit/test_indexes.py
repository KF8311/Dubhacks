import pytest

from app.db.indexes import ensure_indexes


class FakeCollection:
    def __init__(self, name: str, calls: list) -> None:
        self.name = name
        self.calls = calls

    async def create_index(self, keys, **kwargs):
        self.calls.append((self.name, "create", keys, kwargs))

    async def index_information(self):
        if self.name == "listings":
            return {"product_url_1": {"key": [("product_url", 1)], "unique": True}}
        return {}

    async def drop_index(self, name):
        self.calls.append((self.name, "drop", name))


class FakeDB:
    def __init__(self) -> None:
        self.calls: list = []

    def __getattr__(self, name: str) -> FakeCollection:
        return FakeCollection(name, self.calls)


@pytest.mark.asyncio
async def test_product_url_index_is_dropped_when_it_is_unique():
    """Several Google results now share one results-page URL, so it is not unique."""
    db = FakeDB()
    await ensure_indexes(db)

    assert ("listings", "drop", "product_url_1") in db.calls
    created = [call for call in db.calls if call[0] == "listings" and call[1] == "create"]
    url_calls = [call for call in created if call[2] == "product_url"]
    assert url_calls == [("listings", "create", "product_url", {})]
