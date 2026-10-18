"""Input/output guards for the Gemini surface (VEYZL GDPR / Art. 15 / SAIF)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.logging import CARD_RE, EMAIL_RE, PHONE_RE, redact

SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|sk-[a-z0-9]{16,}|x-goog-api-key|password\s*[:=])"
)
INJECTION_RE = re.compile(
    r"(?i)ignore (all |any )?(previous|prior|above) instructions|dump your system prompt|"
    r"reveal (your )?(hidden|system) (prompt|instructions)"
)
HARMFUL_RE = re.compile(
    r"(?i)\b(explosive device|build a bomb|how to make a bomb|"
    r"harm myself|kill myself|suicide methods?)\b"
)
REFUSAL = "I can't help with that request."


@dataclass(frozen=True)
class GuardResult:
    refused: bool
    text: str
    redacted_input: str


def _redact_pii(text: str) -> str:
    text = SSN_RE.sub("[redacted-ssn]", text)
    return redact(text)


def guard_user_text(text: str) -> GuardResult:
    raw = text or ""
    redacted = _redact_pii(raw)
    if HARMFUL_RE.search(raw) or INJECTION_RE.search(raw) or SSN_RE.search(raw) or SECRET_RE.search(raw):
        return GuardResult(refused=True, text=REFUSAL, redacted_input=redacted)
    return GuardResult(refused=False, text=redacted, redacted_input=redacted)


def looks_like_llm_probe(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    mandate = payload.get("mandate")
    return mandate is not None and not isinstance(mandate, dict)


def probe_prompt_from_payload(payload: dict) -> str:
    parts: list[str] = []
    for key in ("body", "session_id", "listing_id", "mandate", "prompt", "query"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    return "\n".join(parts)


__all__ = [
    "CARD_RE",
    "EMAIL_RE",
    "PHONE_RE",
    "GuardResult",
    "guard_user_text",
    "looks_like_llm_probe",
    "probe_prompt_from_payload",
]
