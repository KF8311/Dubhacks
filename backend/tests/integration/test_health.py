from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_200_even_without_db():
    client = TestClient(create_app())
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] in {"ok", "degraded"}
    body = r.json()
    assert "db" in body
    assert "version" in body
    assert "demo_mode" in body
    assert "uptime_s" in body


def test_demo_reset_ok_in_demo_mode():
    client = TestClient(create_app())
    r = client.post("/api/demo/reset")
    assert r.status_code == 200
    assert r.json()["ok"] is True
