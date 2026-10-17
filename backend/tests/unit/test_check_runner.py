import asyncio

import pytest

from app.checks.base import CheckTarget
from app.checks.runner import run_checks
from app.domain.enums import CheckId, TrustStatus
from app.domain.models import TrustCheckResult


class Good:
    id, display_name, timeout_s = CheckId.SSL, "SSL", 1.0

    async def run(self, target, ctx):
        return TrustCheckResult(
            id=self.id,
            name=self.display_name,
            status=TrustStatus.PASSED,
            severity=0,
            summary="ok",
            source="live",
        )


class Bad:
    id, display_name, timeout_s = CheckId.REDDIT, "Reddit", 0.05

    async def run(self, target, ctx):
        await asyncio.sleep(1)
        raise RuntimeError("slow")


@pytest.mark.asyncio
async def test_runner_skips_timeouts_and_keeps_good_checks():
    target = CheckTarget(
        listing_id="lst_1",
        product_url="https://d.com/p",
        merchant_domain="d.com",
        merchant_name="m",
        price_cents=100,
        category=None,
    )
    results = [
        r async for r in run_checks(target, [Good(), Bad()], ctx=None, timeout_s=1.0)
    ]
    assert {r.id for r in results} == {CheckId.SSL, CheckId.REDDIT}
    reddit = next(r for r in results if r.id == CheckId.REDDIT)
    assert reddit.status == TrustStatus.SKIPPED
    assert reddit.source == "timeout"
