from datetime import datetime, timedelta, timezone

from app.core.ids import new_id
from app.domain.enums import SessionStage
from app.domain.models import Investigation, Listing, SearchSpec, Session, SessionStats


class SessionRegistry:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._listings: dict[str, list[Listing]] = {}
        self._investigations: dict[str, list[Investigation]] = {}
        self._questions: dict[str, list[dict]] = {}
        self._recommendations: dict[str, dict] = {}

    def create(self, client_id: str, query: str) -> Session:
        now = datetime.now(timezone.utc)
        session = Session(
            id=new_id("ses"),
            client_id=client_id,
            query=query,
            stage=SessionStage.CLARIFYING,
            search_spec=SearchSpec(query=query),
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(hours=2),
        )
        self._sessions[session.id] = session
        self._listings[session.id] = []
        self._investigations[session.id] = []
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def update(self, session: Session) -> None:
        session.updated_at = datetime.now(timezone.utc)
        self._sessions[session.id] = session

    def set_questions(self, session_id: str, questions: list[dict]) -> None:
        self._questions[session_id] = questions

    def get_questions(self, session_id: str) -> list[dict]:
        return self._questions.get(session_id, [])

    def replace_listings(self, session_id: str, listings: list[Listing]) -> None:
        self._listings[session_id] = list(listings)

    def listings(self, session_id: str) -> list[Listing]:
        return list(self._listings.get(session_id, []))

    def listing_by_id(self, listing_id: str) -> Listing | None:
        for items in self._listings.values():
            for item in items:
                if item.id == listing_id:
                    return item
        return None

    def attach_investigation(self, session_id: str, inv: Investigation) -> None:
        self._investigations.setdefault(session_id, []).append(inv)

    def investigation_for(self, session_id: str, listing_id: str) -> Investigation | None:
        for inv in reversed(self._investigations.get(session_id, [])):
            if inv.listing_id == listing_id:
                return inv
        return None

    def set_recommendation(self, session_id: str, payload: dict) -> None:
        self._recommendations[session_id] = payload

    def snapshot(self, session_id: str, last_seq: int = 0) -> dict | None:
        session = self.get(session_id)
        if session is None:
            return None
        listings = self.listings(session_id)
        checks: dict[str, list] = {listing.id: [] for listing in listings}
        scores: dict[str, dict] = {listing.id: {} for listing in listings}
        for inv in self._investigations.get(session_id, []):
            checks[inv.listing_id] = [c.model_dump(mode="json") for c in inv.checks]
            scores[inv.listing_id] = inv.score.model_dump(mode="json")
        return {
            "session_id": session.id,
            "stage": session.stage.value,
            "query": session.query,
            "listings": [item.model_dump(mode="json") for item in listings],
            "checks": checks,
            "scores": scores,
            "recommendation": self._recommendations.get(session_id)
            or (
                {"listing_id": session.recommended_listing_id}
                if session.recommended_listing_id
                else {}
            ),
            "last_seq": last_seq,
            "stats": session.stats.model_dump(),
        }

    def sweep(self, now: datetime | None = None) -> int:
        now = now or datetime.now(timezone.utc)
        expired = [sid for sid, session in self._sessions.items() if session.expires_at <= now]
        for sid in expired:
            self._sessions.pop(sid, None)
            self._listings.pop(sid, None)
            self._investigations.pop(sid, None)
            self._questions.pop(sid, None)
            self._recommendations.pop(sid, None)
        return len(expired)

    def clear(self) -> None:
        self._sessions.clear()
        self._listings.clear()
        self._investigations.clear()
        self._questions.clear()
        self._recommendations.clear()


registry = SessionRegistry()
