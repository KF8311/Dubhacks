"""How old is the merchant's domain? RDAP first, WHOIS second.

A domain registered last week cannot have a reputation, so its youth is
evidence in its own right. The demo's villain is served from a fixture so the
headline failure reproduces with no network at all.
"""

from __future__ import annotations

import asyncio
import json
import socket
import time
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

import httpx

from app.checks.base import CheckContext, CheckTarget
from app.core.config import get_settings
from app.domain.enums import CheckId, TrustStatus
from app.domain.models import Evidence, TrustCheckResult

RDAP_URL = "https://rdap.org/domain/{domain}"
RDAP_TIMEOUT_S = 4.0
WHOIS_TIMEOUT_S = 4.0
FIXTURE_DIR = Path(__file__).resolve().parents[3] / "data" / "fixtures"

YOUNG_DOMAIN_DAYS = 30
NEW_DOMAIN_DAYS = 90
YOUNG_SEVERITY = 0.95
NEW_SEVERITY = 0.6

_WHOIS_CREATION_KEYS = {
    "creation date",
    "created",
    "created on",
    "registered on",
    "domain registration date",
    "registration date",
}


def _age_days(registered: datetime) -> int:
    if registered.tzinfo is None:
        registered = registered.replace(tzinfo=UTC)
    return (datetime.now(UTC) - registered).days


def _parse_registration(payload: dict) -> datetime | None:
    for event in payload.get("events", []):
        if event.get("eventAction") != "registration":
            continue
        raw = event.get("eventDate")
        if not raw:
            continue
        try:
            return datetime.fromisoformat(raw)
        except ValueError:
            return None
    return None


def _parse_registrar(payload: dict) -> str | None:
    for entity in payload.get("entities", []):
        if "registrar" not in entity.get("roles", []):
            continue
        vcard = entity.get("vcardArray") or [None, []]
        for item in vcard[1]:
            if item and item[0] == "fn" and len(item) > 3:
                return item[3]
    return None


def _from_rdap(payload: dict) -> dict | None:
    registered = _parse_registration(payload)
    if registered is None:
        return None
    return {"age_days": _age_days(registered), "registrar": _parse_registrar(payload)}


@lru_cache(maxsize=8)
def _load_fixture(domain: str) -> dict | None:
    """A fixture whose ``ldhName`` matches the domain, if any."""
    host = domain.strip().lower().rstrip(".")
    if not FIXTURE_DIR.exists():
        return None
    for path in FIXTURE_DIR.glob("*_rdap.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if str(payload.get("ldhName", "")).strip().lower().rstrip(".") == host:
            return payload
    return None


def _fixture_facts(domain: str) -> dict | None:
    """Registration facts from a local fixture, with no network call."""
    fixture = _load_fixture(domain)
    if fixture is None:
        return None
    parsed = _from_rdap(fixture)
    if parsed is not None:
        parsed["source_of_truth"] = "fixture"
    return parsed


async def fetch_rdap(domain: str) -> dict | None:
    """Registration age from RDAP, or a local fixture when one exists."""
    fixture = _fixture_facts(domain)
    if fixture is not None:
        return fixture
    try:
        async with httpx.AsyncClient(timeout=RDAP_TIMEOUT_S) as client:
            response = await client.get(RDAP_URL.format(domain=domain))
            response.raise_for_status()
            return _from_rdap(response.json())
    except Exception:  # noqa: BLE001 — fall back to WHOIS on any RDAP fault
        return None


def _whois_query(server: str, query: str) -> str:
    with socket.create_connection((server, 43), timeout=WHOIS_TIMEOUT_S) as sock:
        sock.sendall((query + "\r\n").encode())
        chunks: list[bytes] = []
        while chunk := sock.recv(4096):
            chunks.append(chunk)
    return b"".join(chunks).decode("utf-8", "replace")


def _whois_text(domain: str) -> str:
    """Ask IANA which server is authoritative, then ask that server."""
    root = _whois_query("whois.iana.org", domain)
    referral = next(
        (
            line.split(":", 1)[1].strip()
            for line in root.splitlines()
            if line.lower().startswith("refer:")
        ),
        "",
    )
    return _whois_query(referral, domain) if referral else root


def _parse_whois_date(text: str) -> datetime | None:
    for line in text.splitlines():
        key, separator, value = line.partition(":")
        if not separator or key.strip().lower() not in _WHOIS_CREATION_KEYS:
            continue
        raw = value.strip()
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            try:
                return datetime.strptime(raw[:11], "%d-%b-%Y").replace(
                    tzinfo=UTC
                )
            except ValueError:
                continue
    return None


async def fetch_whois(domain: str) -> dict | None:
    try:
        text = await asyncio.wait_for(
            asyncio.to_thread(_whois_text, domain), timeout=WHOIS_TIMEOUT_S
        )
    except (TimeoutError, OSError):
        return None
    registered = _parse_whois_date(text)
    if registered is None:
        return None
    return {"age_days": _age_days(registered), "registrar": None, "source_of_truth": "whois"}


class DomainAgeCheck:
    id = CheckId.DOMAIN_AGE
    display_name = "Domain age"
    timeout_s = RDAP_TIMEOUT_S + WHOIS_TIMEOUT_S

    async def run(
        self, target: CheckTarget, ctx: CheckContext | None = None
    ) -> TrustCheckResult:
        started = time.perf_counter()
        settings = getattr(ctx, "config", None) or get_settings()
        if getattr(settings, "offline", False):
            # Fixtures only: an offline replay must not open a socket.
            info = _fixture_facts(target.merchant_domain)
        else:
            info = await fetch_rdap(target.merchant_domain)
            if info is None:
                info = await fetch_whois(target.merchant_domain)

        if info is None or info.get("age_days") is None:
            return self._result(
                TrustStatus.SKIPPED,
                0.0,
                "Could not determine when the domain was registered.",
                [],
                "unavailable",
                started,
            )

        age = int(info["age_days"])
        source_of_truth = info.get("source_of_truth", "rdap")
        evidence = [
            Evidence(label="Age", value=f"{age} days"),
            Evidence(label="Registrar", value=info.get("registrar") or "unknown"),
            Evidence(label="Source", value=source_of_truth),
        ]

        if age < YOUNG_DOMAIN_DAYS:
            return self._result(
                TrustStatus.FAILED,
                YOUNG_SEVERITY,
                f"Domain registered {age} days ago.",
                evidence,
                "fixture" if source_of_truth == "fixture" else "live",
                started,
            )
        if age < NEW_DOMAIN_DAYS:
            return self._result(
                TrustStatus.WARNING,
                NEW_SEVERITY,
                f"Domain is only {age} days old.",
                evidence,
                "fixture" if source_of_truth == "fixture" else "live",
                started,
            )
        return self._result(
            TrustStatus.PASSED,
            0.0,
            f"Domain registered {age} days ago.",
            evidence,
            "fixture" if source_of_truth == "fixture" else "live",
            started,
        )

    def _result(
        self,
        status: TrustStatus,
        severity: float,
        summary: str,
        evidence: list[Evidence],
        source: str,
        started: float,
    ) -> TrustCheckResult:
        return TrustCheckResult(
            id=self.id,
            name=self.display_name,
            status=status,
            severity=severity,
            summary=summary,
            evidence=evidence,
            source=source,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
