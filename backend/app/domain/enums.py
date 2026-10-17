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


class SessionStage(str, Enum):
    CLARIFYING = "clarifying"
    SEARCHING = "searching"
    INVESTIGATING = "investigating"
    READY = "ready"
    NO_TRUSTED_OPTION = "no_trusted_option"
    FAILED = "failed"


class CheckoutStage(str, Enum):
    AWAITING_PASSKEY = "awaiting_passkey"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
