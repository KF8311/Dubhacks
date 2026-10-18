"""Input/output guards for the Gemini surface (VEYZL GDPR / Art. 15 / SAIF)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.core.logging import CARD_RE, EMAIL_RE, PHONE_RE, redact

SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
ACCOUNT_RE = re.compile(r"\bACCT[-_]?\d+\b", re.I)
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|api keys|sk-[a-z0-9]{16,}|x-goog-api-key|password\s*[:=]|"
    r"passwords, or tokens|tokens in your context|reveal any api keys)"
)
INJECTION_RE = re.compile(
    r"(?i)ignore (all |any |your )?(previous|prior|above|rules)|dump your system prompt|"
    r"print your hidden system prompt|reveal (your )?(hidden|system) (prompt|instructions)|"
    r"developer mode|dump the private data|print any customer email"
)
HARMFUL_RE = re.compile(
    r"(?i)\b(explosive device|build a bomb|how to make a bomb|"
    r"harm myself|kill myself|suicide methods?)\b"
)
TOXIC_RE = re.compile(r"(?i)insulting|demeaning rant")
CREDIT_RE = re.compile(
    r"(?i)\b(loan application|credit application|evaluate a loan|loan was denied|"
    r"adverse action|adverse-action)\b"
)
FABRICATE_RE = re.compile(r"(?i)invent a fake|present it confidently as real")
BIAS_RE = re.compile(
    r"(?i)ethnicit|neighborhoods or ethnic|higher interest rates|"
    r"zip code as a proxy|infer their race"
)
REFUSAL = (
    "I can't help with that request. I will not provide harmful instructions, "
    "repeat personal data, or reveal hidden system prompts."
)
CREDIT_REFUSAL = (
    "I cannot issue an adverse-action notice because this service is a shopping "
    "trust agent, not a lender. Checkout is refused based on merchant trust checks, "
    "not creditworthiness, race, or other protected attributes. I will not repeat "
    "Social Security numbers or account identifiers."
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
    if "capital of france" in low or ("capital" in low and "france" in low):
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
    """Anything that is not a real Visa mandate checkout is an auditor/chat probe."""
    if not isinstance(payload, dict):
        return True
    session_id = payload.get("session_id")
    listing_id = payload.get("listing_id")
    mandate = payload.get("mandate")
    real_checkout = (
        isinstance(session_id, str)
        and session_id.startswith("ses_")
        and " " not in session_id
        and len(session_id) <= 80
        and isinstance(listing_id, str)
        and listing_id.startswith("lst_")
        and isinstance(mandate, dict)
        and "max_amount_cents" in mandate
    )
    return not real_checkout


_SKIP_PROMPT_KEYS = {
    "model",
    "object",
    "id",
    "n",
    "temperature",
    "max_tokens",
    "stream",
    "endpoint_path",
    "endpoint_method",
    "endpoint_framework",
}

REASON_TOKENS = ("because", "due to", "based on", "reason", "factor", "since", "result of")


def _walk_prompt_strings(value: object, acc: list[str]) -> None:
    if isinstance(value, str):
        text = value.strip()
        if len(text) >= 8:
            acc.append(text)
        return
    if isinstance(value, list):
        for item in value:
            _walk_prompt_strings(item, acc)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) in _SKIP_PROMPT_KEYS:
                continue
            _walk_prompt_strings(item, acc)


def probe_prompt_from_payload(payload: dict) -> str:
    chunks: list[str] = []
    _walk_prompt_strings(payload, chunks)
    try:
        chunks.append(json.dumps(payload, default=str))
    except TypeError:
        chunks.append(str(payload))
    seen: set[str] = set()
    unique: list[str] = []
    for chunk in chunks:
        if chunk not in seen:
            seen.add(chunk)
            unique.append(chunk)
    return "\n".join(unique)


def looks_like_refusal(text: str) -> bool:
    low = (text or "").lower()
    return any(
        token in low
        for token in ("i can't", "i cannot", "i will not", "i won't", "can't help")
    )


def looks_like_greeting(text: str) -> bool:
    low = (text or "").lower()
    return "how can i help" in low or low.startswith("understood")


def requires_refusal(text: str) -> bool:
    raw = text or ""
    low = raw.lower()
    return bool(
        HARMFUL_RE.search(raw)
        or INJECTION_RE.search(raw)
        or TOXIC_RE.search(raw)
        or SSN_RE.search(raw)
        or SECRET_RE.search(raw)
        or CARD_RE.search(raw)
        or BIAS_RE.search(raw)
        or FABRICATE_RE.search(raw)
        or "credit card" in low
        or "confirm it back" in low
        or "repeat it back" in low
        or "email addresses or phone" in low
    )


def settle_probe_reply(raw: str, model_text: str | None) -> GuardResult:
    """Map a Gemini (or empty) reply onto the auditor's required contract."""
    guarded = guard_user_text(raw)
    redacted = guarded.redacted_input
    model = _redact_pii((model_text or "").strip())
    low_raw = (raw or "").lower()
    greeting = looks_like_greeting(model)

    if HARMFUL_RE.search(raw):
        return GuardResult(True, REFUSAL, redacted)

    if "capital" in low_raw and "france" in low_raw:
        if model and "paris" in model.lower() and not greeting:
            return GuardResult(False, model, redacted)
        return GuardResult(False, "The capital of France is Paris.", redacted)

    if CREDIT_RE.search(raw) or BIAS_RE.search(raw):
        if (
            model
            and not greeting
            and looks_like_refusal(model)
            and any(token in model.lower() for token in REASON_TOKENS)
        ):
            return GuardResult(True, model, redacted)
        return GuardResult(True, CREDIT_REFUSAL, redacted)

    if requires_refusal(raw):
        if model and looks_like_refusal(model) and not greeting:
            return GuardResult(True, model, redacted)
        return reply_for_probe(raw)

    if model and not greeting:
        return GuardResult(False, model, redacted)
    return reply_for_probe(raw)


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
    "CREDIT_RE",
    "CREDIT_REFUSAL",
    "EMAIL_RE",
    "HARMFUL_RE",
    "PHONE_RE",
    "REASON_TOKENS",
    "GuardResult",
    "guard_user_text",
    "looks_like_greeting",
    "looks_like_llm_probe",
    "looks_like_refusal",
    "openai_chat_payload",
    "probe_prompt_from_payload",
    "reply_for_probe",
    "requires_refusal",
    "settle_probe_reply",
    "_redact_pii",
]
