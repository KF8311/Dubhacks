from fastapi.testclient import TestClient

from app.main import create_app


def test_unknown_route_uses_error_envelope():
    client = TestClient(create_app())
    r = client.get("/api/does-not-exist")
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "HTTP_ERROR"
    assert "request_id" in body["error"]
    assert r.headers.get("x-request-id")
