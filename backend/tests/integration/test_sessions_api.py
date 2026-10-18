from fastapi.testclient import TestClient

from app.main import create_app


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
