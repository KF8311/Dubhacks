from fastapi.testclient import TestClient

from app.main import create_app


def test_root_points_at_health():
    client = TestClient(create_app())
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["health"] == "/api/health"


def test_health_returns_200_even_without_db(monkeypatch):
    from app.core.config import Settings

    monkeypatch.setattr("app.db.mongo.get_settings", lambda: Settings(mongodb_uri=None))
    client = TestClient(create_app())
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "degraded"
    assert body["db"] == "unavailable"
    assert "version" in body
    assert "demo_mode" in body
    assert "uptime_s" in body


def test_demo_reset_ok_in_demo_mode():
    client = TestClient(create_app())
    r = client.post("/api/demo/reset")
    assert r.status_code == 200
    assert r.json()["ok"] is True
