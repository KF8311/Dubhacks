from typing import Protocol

from app.domain.models import Listing, SearchSpec


class SearchProvider(Protocol):
    name: str

    async def search(self, spec: SearchSpec, limit: int) -> list[Listing]: ...
