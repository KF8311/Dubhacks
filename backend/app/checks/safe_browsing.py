"""Has anyone already reported this URL as dangerous?

Google Safe Browsing when a key is configured; a local threat list otherwise,
so the check still runs offline and the demo villain still fails.
"""

from __future__ import annotations

import json
import time
from functools import lru_cache
from urllib.parse import urlsplit

import httpx

from app.checks.base import CheckContext, CheckTarget
from app.core.config import get_settings
from app.core.paths import data_dir
from app.domain.enums import CheckId, TrustStatus
from app.domain.models import Evidence, TrustCheckResult

DENYLIST_PATH = data_dir() / "denylist.json"
API_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
API_TIMEOUT_S = 3.0
THREAT_TYPES = (
    "MALWARE",
    "SOCIAL_ENGINEERING",
    "UNWANTED_SOFTWARE",
    "POTENTIALLY_HARMFUL_APPLICATION",
)
LOCAL_MATCH = "LOCAL_DENYLIST"


def _normalize(domain: str) -> str:
    host = (domain or "").strip().lower().rstrip(".")
    return host.removeprefix("www.")


@lru_cache(maxsize=1)
def _denylist() -> frozenset[str] | None:
    """The local threat list, or ``None`` when the file is missing."""
    if not DENYLIST_PATH.exists():
        return None
    try:
        raw = json.loads(DENYLIST_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    entries = raw["domains"] if isinstance(raw, dict) else raw
    return frozenset(_normalize(entry) for entry in entries if entry)


def _local_lookup(url: str) -> list[str]:
    domains = _denylist()
    if not domains:
        return []
    host = _normalize(urlsplit(url).hostname or "")
    if not host:
        return []
    matched = any(host == entry or host.endswith("." + entry) for entry in domains)
    return [LOCAL_MATCH] if matched else []


async def _api_lookup(url: str, key: str) -> list[str]:
    body = {
        "client": {"clientId": "sniff-visa", "clientVersion": "0.9.0"},
        "threatInfo": {
            "threatTypes": list(THREAT_TYPES),
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    async with httpx.AsyncClient(timeout=API_TIMEOUT_S) as client:
        response = await client.post(API_URL, params={"key": key}, json=body)
        response.raise_for_status()
        payload = response.json()
    return [match.get("threatType", "UNKNOWN") for match in payload.get("matches", [])]


async def lookup(url: str) -> list[str]:
    settings = get_settings()
    if settings.google_safe_browsing_key:
        return await _api_lookup(url, settings.google_safe_browsing_key)
    return _local_lookup(url)


class SafeBrowsingCheck:
    id = CheckId.SAFE_BROWSING
    display_name = "Safe Browsing"
    timeout_s = API_TIMEOUT_S + 1.0

    async def run(
        self, target: CheckTarget, ctx: CheckContext | None = None
    ) -> TrustCheckResult:
        started = time.perf_counter()
        try:
            threats = await lookup(target.product_url)
        except Exception:  # noqa: BLE001 — an outage is a skipped check, not a pass
            return self._result(
                TrustStatus.SKIPPED,
                0.0,
                "The threat database could not be queried.",
                [],
                "unavailable",
                started,
            )

        settings = getattr(ctx, "config", None) or get_settings()
        using_api = bool(settings.google_safe_browsing_key)
        source = "live" if using_api else "fixture"

        if threats:
            unique = sorted(set(threats))
            label = "threat list" if using_api else "local threat list"
            return self._result(
                TrustStatus.FAILED,
                1.0,
                f"Reported by the {label}: {', '.join(unique)}.",
                [Evidence(label="Match", value=threat) for threat in unique],
                source,
                started,
            )

        if not using_api and _denylist() is None:
            return self._result(
                TrustStatus.SKIPPED,
                0.0,
                "Threat database is not configured.",
                [],
                "unavailable",
                started,
            )

        return self._result(
            TrustStatus.PASSED,
            0.0,
            "No threat reports for this URL.",
            [],
            source,
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
