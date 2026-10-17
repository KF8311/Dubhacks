"""Does the merchant hold a valid certificate for its own hostname?

The certificate is not a reputation signal on its own -- a phishing page can
buy one in minutes -- but a broken, expired, or mismatched one is a hard
failure, and a free short-lived certificate is worth a warning.
"""

from __future__ import annotations

import asyncio
import socket
import ssl
import time
from datetime import UTC, datetime

from app.checks.base import CheckContext, CheckTarget
from app.domain.enums import CheckId, TrustStatus
from app.domain.models import Evidence, TrustCheckResult

CONNECT_TIMEOUT_S = 4.0
INVALID_SEVERITY = 0.8
FREE_CERT_SEVERITY = 0.4
EXPIRY_WARNING_DAYS = 14

FREE_ISSUERS = ("let's encrypt", "zerossl", "buypass", "cloudflare")


def _issuer_name(cert: dict) -> str | None:
    for key in ("organizationName", "commonName"):
        for entry in cert.get("issuer", ()):
            if len(entry) == 2 and entry[0] == key:
                return str(entry[1])
    return None


def _days_left(cert: dict) -> int | None:
    not_after = cert.get("notAfter")
    if not not_after:
        return None
    try:
        expiry = datetime.fromtimestamp(
            ssl.cert_time_to_seconds(not_after), tz=UTC
        )
    except (ValueError, OverflowError):
        return None
    return (expiry - datetime.now(UTC)).days


def _inspect_blocking(domain: str) -> dict | None:
    context = ssl.create_default_context()
    try:
        with (
            socket.create_connection((domain, 443), timeout=CONNECT_TIMEOUT_S) as sock,
            context.wrap_socket(sock, server_hostname=domain) as tls,
        ):
            cert = tls.getpeercert()
    except ssl.SSLError:
        # Expired, self-signed, wrong hostname, or otherwise unverifiable.
        return {"issuer": None, "valid": False, "hostname_match": False, "days_left": None}
    except OSError:
        return None

    return {
        "issuer": _issuer_name(cert),
        "valid": True,
        "hostname_match": True,
        "days_left": _days_left(cert),
    }


async def inspect_cert(domain: str) -> dict | None:
    """Peer certificate facts, or ``None`` when the host cannot be reached."""
    return await asyncio.to_thread(_inspect_blocking, domain)


class SSLCertCheck:
    id = CheckId.SSL
    display_name = "SSL certificate"
    timeout_s = CONNECT_TIMEOUT_S + 1.0

    async def run(
        self, target: CheckTarget, ctx: CheckContext | None = None
    ) -> TrustCheckResult:
        started = time.perf_counter()
        info = await inspect_cert(target.merchant_domain)

        if info is None:
            return self._result(
                TrustStatus.SKIPPED,
                0.0,
                "Could not reach the merchant to inspect its certificate.",
                [],
                "unavailable",
                started,
            )

        issuer = info.get("issuer") or "unknown issuer"
        evidence = [
            Evidence(label="Issuer", value=issuer),
            Evidence(label="Valid", value=str(bool(info.get("valid")))),
        ]
        days_left = info.get("days_left")
        if days_left is not None:
            evidence.append(Evidence(label="Expires in", value=f"{days_left} days"))

        if not info.get("valid") or not info.get("hostname_match"):
            return self._result(
                TrustStatus.FAILED,
                INVALID_SEVERITY,
                "The certificate is invalid, expired, or issued for another host.",
                evidence,
                "live",
                started,
            )

        if isinstance(issuer, str) and any(
            free in issuer.lower() for free in FREE_ISSUERS
        ):
            return self._result(
                TrustStatus.WARNING,
                FREE_CERT_SEVERITY,
                f"Certificate is free and short-lived ({issuer}).",
                evidence,
                "live",
                started,
            )

        if days_left is not None and days_left < EXPIRY_WARNING_DAYS:
            return self._result(
                TrustStatus.WARNING,
                FREE_CERT_SEVERITY,
                f"Certificate expires in {days_left} days.",
                evidence,
                "live",
                started,
            )

        return self._result(
            TrustStatus.PASSED,
            0.0,
            f"Valid certificate issued by {issuer}.",
            evidence,
            "live",
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
