"""Read the merchant's page and look for the language of a scam.

Urgency pressure, a fake countdown, payment demanded before delivery, and a
policy that refuses every refund are the patterns that separate a bargain from
a con. Absence of flags is not proof of trust -- it only means this check
found nothing.
"""

from __future__ import annotations

import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import httpx

from app.checks.base import CheckContext, CheckTarget
from app.core.config import get_settings
from app.domain.enums import CheckId, TrustStatus
from app.domain.models import Evidence, TrustCheckResult
from app.services.url_safety import validate_public_url

FIXTURE_DIR = Path(__file__).resolve().parents[3] / "data" / "fixtures"
FIXTURES = {"premium-audio-deals.shop": "villain_page.html"}
MAX_BYTES = 1_000_000
FETCH_TIMEOUT_S = 6.0
MAX_REDIRECTS = 4
USER_AGENT = "SniffTrustCheck/1.0 (trust prototype; contact: demo@example.test)"

FLAG_WARNING = 0.4
FLAG_FAILED = 0.7
CRITICAL_FAILED = 0.85

URGENCY_RE = re.compile(
    r"today only|flash sale|before it'?s gone|act now|limited time|ends in"
    r"|only \d+ (?:left|remaining)",
    re.IGNORECASE,
)
COUNTDOWN_RE = re.compile(r"setinterval\s*\(", re.IGNORECASE)
REFUSAL_TERMS = (
    "no refunds",
    "all sales final",
    "sales are irreversible",
    "no returns",
)
ADVANCE_PAYMENT_TERMS = (
    "send payment first",
    "wire transfer",
    "western union",
    "money order",
    "gift card",
    "send payment and",
)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skipping = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self._skipping += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skipping:
            self._skipping -= 1

    def handle_data(self, data: str) -> None:
        if not self._skipping:
            self.parts.append(data)


def _visible_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return " ".join(parser.parts)


def _fixture_name(url: str) -> str | None:
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return FIXTURES.get(host)


def _fixture_html(url: str) -> str | None:
    name = _fixture_name(url)
    if name is None:
        return None
    path = FIXTURE_DIR / name
    return path.read_text(encoding="utf-8") if path.exists() else None


async def _live_fetch(url: str) -> str | None:
    async with httpx.AsyncClient(
        timeout=FETCH_TIMEOUT_S, follow_redirects=False
    ) as client:
        current = validate_public_url(url)
        for _ in range(MAX_REDIRECTS):
            response = await client.get(current, headers={"User-Agent": USER_AGENT})
            if response.is_redirect:
                target = response.headers.get("location")
                if not target:
                    return None
                current = validate_public_url(urljoin(current, target))
                continue
            response.raise_for_status()
            if len(response.content) > MAX_BYTES:
                return None
            return response.text
    return None


async def fetch_html(url: str, ctx: CheckContext | None = None) -> str | None:
    """The page's HTML: a fixture when one exists, live only outside demo mode."""
    fixture = _fixture_html(url)
    if fixture is not None:
        return fixture

    settings = getattr(ctx, "config", None) or get_settings()
    if getattr(settings, "demo_mode", True) or getattr(settings, "offline", False):
        return None

    try:
        return await _live_fetch(url)
    except Exception:  # noqa: BLE001 — an unreadable page is a skipped check
        return None


def _detect(html: str) -> list[Evidence]:
    text = _visible_text(html).lower()
    flags: list[Evidence] = []

    if URGENCY_RE.search(text):
        flags.append(
            Evidence(label="Urgency pressure", value="Countdown-style sales language")
        )
    if COUNTDOWN_RE.search(html):
        flags.append(
            Evidence(label="Fake countdown", value="Script resets its own timer")
        )
    if any(term in text for term in REFUSAL_TERMS):
        flags.append(
            Evidence(label="No refunds", value="The page refuses returns outright")
        )
    if any(term in text for term in ADVANCE_PAYMENT_TERMS):
        flags.append(
            Evidence(
                label="Payment before delivery",
                value="Funds are demanded before anything ships",
            )
        )
    return flags


class PageFlagsCheck:
    id = CheckId.PAGE_FLAGS
    display_name = "Page flags"
    timeout_s = FETCH_TIMEOUT_S

    async def run(
        self, target: CheckTarget, ctx: CheckContext | None = None
    ) -> TrustCheckResult:
        started = time.perf_counter()

        if urlsplit(target.product_url).scheme != "https":
            return self._result(
                TrustStatus.FAILED,
                CRITICAL_FAILED,
                "The checkout page does not use HTTPS.",
                [Evidence(label="No HTTPS", value=target.product_url)],
                "live",
                started,
            )

        html = await fetch_html(target.product_url, ctx)
        if not html:
            return self._result(
                TrustStatus.SKIPPED,
                0.0,
                "Could not read the merchant page.",
                [],
                "unavailable",
                started,
            )

        flags = _detect(html)
        source = "fixture" if _fixture_name(target.product_url) else "live"

        if not flags:
            return self._result(
                TrustStatus.PASSED,
                0.0,
                "No page red flags found.",
                [],
                source,
                started,
            )
        if len(flags) == 1:
            return self._result(
                TrustStatus.WARNING,
                FLAG_WARNING,
                f"Page shows one red flag: {flags[0].label}.",
                flags,
                source,
                started,
            )
        names = ", ".join(flag.label.lower() for flag in flags)
        return self._result(
            TrustStatus.FAILED,
            FLAG_FAILED,
            f"Page shows {len(flags)} red flags: {names}.",
            flags,
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
