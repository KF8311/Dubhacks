"""Reject URLs that would make the server fetch something it must not.

The page check is the only place we follow a merchant-supplied URL. Without
this guard, a crafted listing could point the fetcher at the loopback
interface, a private network, or a cloud metadata endpoint.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit

MAX_URL_LENGTH = 2048
ALLOWED_PORTS = {None, 443}


def _resolved_addresses(host: str) -> list[str]:
    """Every address the host resolves to. Empty when DNS cannot answer."""
    try:
        infos = socket.getaddrinfo(host, None)
    except (socket.gaierror, OSError, UnicodeError):
        return []
    return [str(info[4][0]) for info in infos]


def _is_public(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return ip.is_global


def _is_ip_literal(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


def validate_public_url(url: str) -> str:
    """Return ``url`` unchanged, or raise ``ValueError`` explaining the refusal."""
    if not url or len(url) > MAX_URL_LENGTH:
        raise ValueError("URL is empty or too long")

    parts = urlsplit(url)
    if parts.scheme != "https":
        raise ValueError("only https URLs may be fetched")
    if parts.username or parts.password:
        raise ValueError("URLs with embedded credentials are refused")
    if parts.port not in ALLOWED_PORTS:
        raise ValueError("only the default https port may be used")

    host = (parts.hostname or "").strip().lower().rstrip(".")
    if not host:
        raise ValueError("URL has no host")
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("localhost is refused")
    if _is_ip_literal(host):
        raise ValueError("IP literals are refused")

    # No DNS answer means no connection, which a later failure handles safely.
    for address in _resolved_addresses(host):
        if not _is_public(address):
            raise ValueError("host resolves to a non-public address")

    return url
