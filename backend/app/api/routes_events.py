import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.core.errors import AppError
from app.sessions.events import bus
from app.sessions.store import registry

router = APIRouter()


def _since_seq(request: Request, since_seq: int | None) -> int:
    if since_seq is not None:
        return since_seq
    header = request.headers.get("last-event-id")
    if header and header.isdigit():
        return int(header)
    return 0


@router.get("/api/sessions/{session_id}/events")
async def session_events(session_id: str, request: Request, since_seq: int | None = None):
    if registry.get(session_id) is None:
        raise AppError("SESSION_NOT_FOUND", "Session not found.", status_code=404)

    start = _since_seq(request, since_seq)

    async def gen():
        async for event in bus.subscribe(session_id, since_seq=start):
            yield {
                "id": str(event.seq),
                "event": event.type,
                "data": json.dumps(event.payload, default=str),
            }

    return EventSourceResponse(
        gen(),
        ping=15,
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
