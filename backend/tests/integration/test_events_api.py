from fastapi.testclient import TestClient

from app.main import create_app


def test_stream_publishes_synthetic_events(monkeypatch):
    client = TestClient(create_app())
    s = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    sid = s["session_id"]
    from app.sessions.events import bus

    bus.publish(sid, "search.started", {"query": "headphones"})
    bus.publish(sid, "investigation.complete", {"stats": {}})
    bus.close(sid)
    with client.stream("GET", f"/api/sessions/{sid}/events") as r:
        body = "".join(r.iter_text())
    assert "event: search.started" in body
    assert "event: investigation.complete" in body


def test_stream_replays_from_last_event_id():
    client = TestClient(create_app())
    s = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    sid = s["session_id"]
    from app.sessions.events import bus

    bus.publish(sid, "search.started", {"query": "headphones"})
    second = bus.publish(sid, "listing.found", {"rank": 1})
    bus.publish(sid, "investigation.complete", {"stats": {}})
    bus.close(sid)
    with client.stream(
        "GET",
        f"/api/sessions/{sid}/events",
        headers={"Last-Event-ID": str(second.seq - 1)},
    ) as r:
        body = "".join(r.iter_text())
    assert "event: search.started" not in body
    assert "event: listing.found" in body
    assert "event: investigation.complete" in body
