import json
import logging
import re
from datetime import datetime, timezone

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")
CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
QUERY_SECRET_RE = re.compile(r"((?:api_key|x-goog-api-key)=)[^&\s\"\\]+", re.I)


def redact(text: str) -> str:
    text = QUERY_SECRET_RE.sub(r"\1[redacted]", text)
    text = EMAIL_RE.sub("[redacted]", text)
    text = PHONE_RE.sub("[redacted]", text)
    return CARD_RE.sub("[redacted-card]", text)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "message": redact(record.getMessage()),
            "logger": record.name,
        }
        for key in (
            "request_id",
            "session_id",
            "listing_id",
            "check",
            "stage",
            "duration_ms",
            "error_code",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(payload)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
