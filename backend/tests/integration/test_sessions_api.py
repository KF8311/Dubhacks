from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.domain.enums import CheckId, TrustStatus, Verdict
from app.domain.models import Investigation, ScoreResult, TrustCheckResult
from app.main import create_app
from app.sessions.store import registry


def test_create_session_uses_llm_questions(monkeypatch):
    async def fake_questions(query, *, complete=None, fallback=None):
        assert query == "travel headphones"
        return [
            {
                "id": "q_budget",
                "prompt": "LLM: what's your ceiling for travel cans?",
                "kind": "single_select",
                "options": [
                    {"id": "150", "label": "Under $150"},
                    {"id": "300", "label": "$150–$300"},
                ],
            },
            {
                "id": "q_use",
                "prompt": "LLM: where will you wear them?",
                "kind": "single_select",
                "options": [
                    {"id": "plane", "label": "Plane"},
                    {"id": "train", "label": "Train"},
                ],
            },
        ]

    monkeypatch.setattr("app.services.llm.generate_questions", fake_questions)
    client = TestClient(create_app())
    response = client.post("/api/sessions", json={"query": "travel headphones", "client_id": "c1"})
    assert response.status_code == 201
    prompts = [item["prompt"] for item in response.json()["questions"]]
    assert prompts[0].startswith("LLM:")


def test_create_session_returns_questions():
    client = TestClient(create_app())
    r = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"})
    assert r.status_code == 201
    body = r.json()
    assert body["stage"] == "clarifying"
    assert 2 <= len(body["questions"]) <= 3


def test_answers_advance_stage():
    client = TestClient(create_app())
    s = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    r = client.post(
        f"/api/sessions/{s['session_id']}/answers",
        json={"answers": [{"question_id": "q_budget", "option_id": "300"}]},
    )
    assert r.status_code == 202
    assert r.json()["stage"] == "searching"
    assert r.json()["events_url"].endswith("/events")


def test_explain_route_uses_llm(monkeypatch):
    async def fake_explain(check):
        assert check.id == CheckId.SSL
        return "LLM: the certificate is valid."

    monkeypatch.setattr("app.services.llm.explain_check", fake_explain)
    client = TestClient(create_app())
    session = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    check = TrustCheckResult(
        id=CheckId.SSL,
        name="SSL certificate",
        status=TrustStatus.PASSED,
        severity=0,
        summary="Valid certificate.",
        source="live",
    )
    registry.attach_investigation(
        session["session_id"],
        Investigation(
            id="inv_test",
            listing_id="lst_test",
            session_id=session["session_id"],
            checks=[check],
            score=ScoreResult(score=100, verdict=Verdict.TRUSTED, confidence=1, top_reason="ok"),
            allowlisted=True,
            duration_ms=1,
            created_at=datetime.now(timezone.utc),
        ),
    )
    response = client.post(
        f"/api/sessions/{session['session_id']}/explain",
        json={"listing_id": "lst_test", "check_id": "ssl_cert"},
    )
    assert response.status_code == 200
    assert response.json()["explanation"] == "LLM: the certificate is valid."


def test_explain_without_an_investigation_is_404():
    client = TestClient(create_app())
    s = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    r = client.post(
        f"/api/sessions/{s['session_id']}/explain",
        json={"listing_id": "lst_missing", "check_id": "ssl_cert"},
    )
    assert r.status_code == 404


def test_snapshot_includes_last_seq():
    client = TestClient(create_app())
    s = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    r = client.get(f"/api/sessions/{s['session_id']}")
    assert r.status_code == 200
    body = r.json()
    assert body["session_id"] == s["session_id"]
    assert "last_seq" in body
    assert "listings" in body
