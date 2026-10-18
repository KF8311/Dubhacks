from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.core.logging import redact


class AuditEvent(BaseModel):
    session_id: str
    actor: str
    action: str
    subject_id: str
    payload_redacted: dict = Field(default_factory=dict)
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def redact_payload(payload: dict) -> dict:
    out: dict = {}
    for key, value in payload.items():
        if isinstance(value, str):
            out[key] = redact(value)
        else:
            out[key] = value
    return out
