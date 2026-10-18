from typing import Protocol

from app.domain.models import Listing, SearchSpec


class SearchQuotaExhausted(RuntimeError):
    """The provider's plan has no searches left.

    This is not a timeout: waiting and retrying cannot help, and the user
    deserves to know the difference instead of watching the app fail in one
    second with "taking too long".
    """


class SearchProvider(Protocol):
    name: str

    async def search(self, spec: SearchSpec, limit: int) -> list[Listing]: ...
