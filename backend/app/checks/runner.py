"""Run every check in parallel and yield results as they land.

A check that times out or raises yields ``SKIPPED``. A skipped check is never
a pass: it does not count toward coverage, so a listing whose checks could not
run gets capped rather than trusted.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Iterable

from app.checks.base import CheckContext, CheckTarget, TrustCheck
from app.domain.models import TrustCheckResult


def _skipped(
    check: TrustCheck, source: str, summary: str, started: float
) -> TrustCheckResult:
    return TrustCheckResult(
        id=check.id,
        name=check.display_name,
        status="skipped",
        severity=0.0,
        summary=summary,
        evidence=[],
        source=source,
        duration_ms=int((time.perf_counter() - started) * 1000),
    )


async def _run_one(
    check: TrustCheck,
    target: CheckTarget,
    ctx: CheckContext | None,
    timeout_s: float,
) -> TrustCheckResult:
    started = time.perf_counter()
    budget = min(check.timeout_s, timeout_s)
    try:
        return await asyncio.wait_for(check.run(target, ctx), timeout=budget)
    except (asyncio.TimeoutError, TimeoutError):
        return _skipped(
            check,
            "timeout",
            f"{check.display_name} did not finish within {budget:.1f}s",
            started,
        )
    except Exception as exc:  # noqa: BLE001 - one bad check must not kill the run
        return _skipped(
            check,
            "unavailable",
            f"{check.display_name} could not run: {exc.__class__.__name__}",
            started,
        )


async def run_checks(
    target: CheckTarget,
    checks: Iterable[TrustCheck],
    ctx: CheckContext | None = None,
    timeout_s: float = 10.0,
) -> AsyncIterator[TrustCheckResult]:
    """Yield one result per check, in completion order.

    ``timeout_s`` is a global ceiling; each check's own ``timeout_s`` is capped
    by it, so one slow check cannot hold the whole investigation open.
    """
    tasks = [
        asyncio.create_task(_run_one(check, target, ctx, timeout_s))
        for check in checks
    ]
    try:
        for completed in asyncio.as_completed(tasks):
            yield await completed
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
