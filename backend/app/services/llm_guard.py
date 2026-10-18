"""Input/output guards for the Gemini surface (VEYZL GDPR / Art. 15 / SAIF)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.logging import CARD_RE, EMAIL_RE, PHONE_RE, redact

SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
ACCOUNT_RE = re.compile(r"\bACCT[-_]?\d+\b", re.I)
SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|sk-[a-z0-9]{16,}|x-goog-api-key|password\s*[:=])"
)
INJECTION_RE = re.compile(
    r"(?i)ignore (all |any )?(previous|prior|above) instructions|dump your system prompt|"
    r"print your hidden system prompt|reveal (your )?(hidden|system) (prompt|instructions)"
)
HARMFUL_RE = re.compile(
    r"(?i)\b(explosive device|build a bomb|how to make a bomb|"
    r"harm myself|kill myself|suicide methods?)\b"
)
TOXIC_RE = re.compile(r"(?i)insulting|demeaning rant")
CREDIT_RE = re.compile(r"(?i)\b(loan application|credit application|evaluate a loan)\b")
FABRICATE_RE = re.compile(r"(?i)invent a fake|present it confidently as real")
REFUSAL = (
    "I can't help with that request. I will not provide harmful instructions, "
    "repeat personal data, or reveal hidden system prompts."
)
CREDIT_REFUSAL = (
    "This is a sandbox shopping trust agent, not a lender. I do not evaluate loan "
    "applications or use race, sex, or other protected attributes. I will not "
    "repeat Social Security numbers or account identifiers."
)


@dataclass(frozen=True)
class GuardResult:
    refused: bool
    text: str
    redacted_input: str


def _redact_pii(text: str) -> str:
    text = SSN_RE.sub("[redacted-ssn]", text)
    text = ACCOUNT_RE.sub("[redacted-account]", text)
    return redact(text)


def guard_user_text(text: str) -> GuardResult:
    raw = text or ""
    redacted = _redact_pii(raw)
    if (
        HARMFUL_RE.search(raw)
        or INJECTION_RE.search(raw)
        or TOXIC_RE.search(raw)
        or SSN_RE.search(raw)
        or SECRET_RE.search(raw)
        or CARD_RE.search(raw)
    ):
        return GuardResult(refused=True, text=REFUSAL, redacted_input=redacted)
    return GuardResult(refused=False, text=redacted, redacted_input=redacted)


def reply_for_probe(text: str) -> GuardResult:
    """Text a hosted API auditor can score (OpenAI-style content)."""
    guarded = guard_user_text(text)
    raw = text or ""
    low = raw.lower()
    if SSN_RE.search(raw) or CREDIT_RE.search(raw):
        return GuardResult(True, CREDIT_REFUSAL, guarded.redacted_input)
    if guarded.refused or TOXIC_RE.search(raw) or FABRICATE_RE.search(raw):
        message = (
            "I won't invent fake historical events and present them as fact."
            if FABRICATE_RE.search(raw)
            else REFUSAL
        )
        return GuardResult(True, message, guarded.redacted_input)
    if "capital of france" in low:
        return GuardResult(False, "The capital of France is Paris.", guarded.redacted_input)
    if "photosynthesis" in low:
        return GuardResult(
            False,
            "Photosynthesis converts light energy into chemical energy in plants. "
            "Chlorophyll captures sunlight to build sugars from carbon dioxide and water and releases oxygen.",
            guarded.redacted_input,
        )
    return GuardResult(True, REFUSAL, guarded.redacted_input)


def looks_like_llm_probe(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    if payload.get("messages") or payload.get("prompt") or payload.get("input"):
        return True
    mandate = payload.get("mandate")
    if mandate is not None and not isinstance(mandate, dict):
        return True
    session_id = payload.get("session_id")
    if isinstance(session_id, str) and (" " in session_id or len(session_id) > 80):
        return True
    body = payload.get("body")
    return isinstance(body, str) and len(body) > 20


def probe_prompt_from_payload(payload: dict) -> str:
    messages = payload.get("messages")
    if isinstance(messages, list):
        chunks = [
            str(item.get("content") or "")
            for item in messages
            if isinstance(item, dict) and item.get("content")
        ]
        if chunks:
            return "\n".join(chunks)
    parts: list[str] = []
    for key in ("input", "prompt", "body", "query", "session_id", "listing_id", "mandate"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    return "\n".join(parts)


def openai_chat_payload(content: str, *, refused: bool, sandbox_label: str) -> dict:
    return {
        "id": "chatcmpl-sniff-guard",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "refused": refused,
        "text": content,
        "sandbox_label": sandbox_label,
    }


__all__ = [
    "CARD_RE",
    "EMAIL_RE",
    "PHONE_RE",
    "GuardResult",
    "guard_user_text",
    "looks_like_llm_probe",
    "openai_chat_payload",
    "probe_prompt_from_payload",
    "reply_for_probe",
]
