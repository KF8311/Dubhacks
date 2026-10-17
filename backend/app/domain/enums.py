"""Enumerations shared by the domain, the trust engine, and the UI.

STOPGAP — read before editing.
Task 1 (owner: A) creates this file. Person B added only the three enums that
Tasks 8 and 14 depend on, so the trust engine could start before the platform
scaffold landed. Merge A's version in when it arrives.
"""

from enum import Enum


class CheckId(str, Enum):
    DOMAIN_AGE = "domain_age"
    SSL = "ssl_cert"
    SAFE_BROWSING = "safe_browsing"
    REDDIT = "reddit_sentiment"
    PAGE_FLAGS = "page_flags"


class TrustStatus(str, Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


class Verdict(str, Enum):
    TRUSTED = "trusted"
    CAUTION = "caution"
    DANGER = "danger"
