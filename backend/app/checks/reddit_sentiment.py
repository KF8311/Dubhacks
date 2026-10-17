"""What has Reddit already said about this merchant?

Only titles and permalinks are kept -- never usernames, never post bodies.
The page text is data for a keyword classifier, not instructions for a model.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import httpx

from app.checks.base import CheckContext, CheckTarget
from app.core.config import get_settings
from app.domain.enums import CheckId, TrustStatus
from app.domain.models import Evidence, TrustCheckResult

FIXTURE_DIR = Path(__file__).resolve().parents[3] / "data" / "fixtures"
FIXTURES = {"premium-audio-deals.shop": "villain_reddit.json"}
SEARCH_URL = "https://www.reddit.com/search.json"
SEARCH_TIMEOUT_S = 4.0
SEARCH_LIMIT = 10
USER_AGENT = "SniffTrustCheck/1.0 (trust prototype; contact: demo@example.test)"

WARNING_SEVERITY = 0.5
FAILED_SEVERITY = 0.8
WARNING_AT = 1
FAILED_AT = 3

SCAM_RE = re.compile(
    r"\bscam\w*|\bfraud\w*|\bstole\b|\bstolen\b|took my money"
    r"|never arrived|do not order|don'?t order|chargeback|ripped off",
    re.IGNORECASE,
)


def _fixture_name(domain: str) -> str | None:
    return FIXTURES.get(domain.strip().lower().rstrip("."))


def _fixture_posts(domain: str) -> list[dict] | None:
    name = _fixture_name(domain)
    if name is None:
        return None
    path = FIXTURE_DIR / name
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        {
            "title": child.get("data", {}).get("title", ""),
            "permalink": child.get("data", {}).get("permalink", ""),
        }
        for child in payload.get("data", {}).get("children", [])
    ]


async def _search_live(domain: str) -> list[dict]:
    params = {"q": f"{domain} scam", "limit": SEARCH_LIMIT, "sort": "relevance"}
    async with httpx.AsyncClient(timeout=SEARCH_TIMEOUT_S) as client:
        response = await client.get(
            SEARCH_URL, params=params, headers={"User-Agent": USER_AGENT}
        )
        response.raise_for_status()
        payload = response.json()
    return [
        {
            "title": child.get("data", {}).get("title", ""),
            "permalink": child.get("data", {}).get("permalink", ""),
        }
        for child in payload.get("data", {}).get("children", [])
    ]


async def search(domain: str) -> list[dict]:
    """Search results for the domain, or a fixture when the demo has one."""
    fixture = _fixture_posts(domain)
    if fixture is not None:
        return fixture

    settings = get_settings()
    if settings.demo_mode or settings.offline:
        return []
    return await _search_live(domain)


class RedditSentimentCheck:
    id = CheckId.REDDIT
    display_name = "Reddit sentiment"
    timeout_s = SEARCH_TIMEOUT_S + 1.0

    async def run(
        self, target: CheckTarget, ctx: CheckContext | None = None
    ) -> TrustCheckResult:
        started = time.perf_counter()
        try:
            posts = await search(target.merchant_domain)
        except Exception:  # noqa: BLE001 — Reddit blocking us is not a pass
            return self._result(
                TrustStatus.SKIPPED,
                0.0,
                "Reddit could not be searched.",
                [],
                "unavailable",
                started,
            )

        hits = [post for post in posts if SCAM_RE.search(post.get("title", ""))]
        source = "fixture" if _fixture_name(target.merchant_domain) else "live"
        evidence = [
            Evidence(
                label="Report",
                value=post.get("title", ""),
                url=_permalink_url(post.get("permalink", "")),
            )
            for post in hits
        ]

        if len(hits) >= FAILED_AT:
            return self._result(
                TrustStatus.FAILED,
                FAILED_SEVERITY,
                f"{len(hits)} Reddit posts report this merchant.",
                evidence,
                source,
                started,
            )
        if len(hits) >= WARNING_AT:
            return self._result(
                TrustStatus.WARNING,
                WARNING_SEVERITY,
                f"{len(hits)} Reddit post reports this merchant.",
                evidence,
                source,
                started,
            )
        return self._result(
            TrustStatus.PASSED,
            0.0,
            "No scam reports found on Reddit.",
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


def _permalink_url(permalink: str) -> str | None:
    if not permalink:
        return None
    return permalink if permalink.startswith("http") else f"https://www.reddit.com{permalink}"
