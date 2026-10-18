from pydantic import BaseModel

from fastapi import APIRouter

from app.core.errors import AppError
from app.domain.enums import SessionStage
from app.domain.models import Answer
from app.sessions.events import bus
from app.sessions.orchestrator import SessionOrchestrator
from app.sessions.questions import build_search_spec, generate_questions
from app.sessions.store import registry

router = APIRouter()
orchestrator = SessionOrchestrator(registry, bus)


class SessionCreateIn(BaseModel):
    query: str
    client_id: str


class AnswerIn(BaseModel):
    question_id: str
    option_id: str | None = None
    text: str | None = None


class AnswersIn(BaseModel):
    answers: list[AnswerIn]
    skip_remaining: bool = False


def _require_session(session_id: str):
    session = registry.get(session_id)
    if session is None:
        raise AppError("SESSION_NOT_FOUND", "Session not found.", status_code=404)
    return session


@router.post("/api/sessions", status_code=201)
async def create_session(body: SessionCreateIn) -> dict:
    session = registry.create(body.client_id, body.query)
    questions = await generate_questions(body.query)
    registry.set_questions(session.id, questions)
    return {
        "session_id": session.id,
        "stage": session.stage.value,
        "questions": questions,
        "expires_at": session.expires_at.isoformat().replace("+00:00", "Z"),
    }


@router.post("/api/sessions/{session_id}/answers", status_code=202)
async def submit_answers(session_id: str, body: AnswersIn) -> dict:
    session = _require_session(session_id)
    known = {item["id"] for item in registry.get_questions(session_id)}
    for item in body.answers:
        if known and item.question_id not in known:
            raise AppError(
                "UNKNOWN_QUESTION",
                f"Unknown question_id {item.question_id}.",
                status_code=400,
            )
    session.answers = [
        Answer(question_id=item.question_id, option_id=item.option_id, text=item.text)
        for item in body.answers
    ]
    session.search_spec = build_search_spec(session.query, session.answers)
    session.stage = SessionStage.SEARCHING
    registry.update(session)
    await orchestrator.start(session)
    return {
        "session_id": session.id,
        "stage": session.stage.value,
        "events_url": f"/api/sessions/{session.id}/events",
        "search_spec": session.search_spec.model_dump(),
    }


@router.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    _require_session(session_id)
    snapshot = registry.snapshot(session_id, last_seq=bus.last_seq(session_id))
    if snapshot is None:
        raise AppError("SESSION_NOT_FOUND", "Session not found.", status_code=404)
    return snapshot
