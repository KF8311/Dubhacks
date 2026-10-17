"""The set of checks a full investigation runs."""

from __future__ import annotations

import importlib
import logging

from app.checks.base import TrustCheck

logger = logging.getLogger(__name__)

# Modules are imported lazily so the app boots while Tasks 9-13 are still being
# written. Once all five exist, get_checks() returns five instances.
_CHECK_FACTORIES: tuple[tuple[str, str], ...] = (
    ("app.checks.domain_age", "DomainAgeCheck"),
    ("app.checks.ssl_cert", "SSLCertCheck"),
    ("app.checks.safe_browsing", "SafeBrowsingCheck"),
    ("app.checks.reddit_sentiment", "RedditSentimentCheck"),
    ("app.checks.page_flags", "PageFlagsCheck"),
)


def get_checks() -> list[TrustCheck]:
    """Return every implemented check.

    A missing module is logged rather than raised: a missing check reduces
    coverage, and reduced coverage caps the score, so the failure mode is
    "caution", not "trusted".
    """
    checks: list[TrustCheck] = []
    for module_name, class_name in _CHECK_FACTORIES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            logger.warning("check not implemented yet: %s", module_name)
            continue
        checks.append(getattr(module, class_name)())
    return checks
