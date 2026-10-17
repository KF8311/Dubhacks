import hashlib
import secrets
from urllib.parse import urlsplit, urlunsplit


def new_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_urlsafe(12)}"


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    path = parts.path.rstrip("/") or "/"
    netloc = host
    if parts.port and parts.port not in (80, 443):
        netloc = f"{host}:{parts.port}"
    return urlunsplit((parts.scheme.lower(), netloc, path, parts.query, ""))


def listing_id(url: str) -> str:
    digest = hashlib.sha256(normalize_url(url).encode()).hexdigest()[:16]
    return f"lst_{digest}"
