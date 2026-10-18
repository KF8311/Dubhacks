from fastapi.testclient import TestClient

from app.main import create_app
from tests.integration.test_checkout_api import _setup


def test_public_receipt_by_share_id(monkeypatch):
    client = TestClient(create_app())
    sid, listing = _setup(client, monkeypatch)
    co = client.post(
        "/api/checkout",
        json={
            "session_id": sid,
            "listing_id": listing["id"],
            "mandate": {"max_amount_cents": 50000, "currency": "USD", "expires_in_seconds": 600},
        },
    ).json()
    receipt = client.post(
        f"/api/checkout/{co['checkout_id']}/confirm",
        json={
            "passkey_assertion": {"credential_id": "mock", "client_data": "mock"},
            "idempotency_key": "k",
        },
    ).json()
    share = receipt["receipt_url"].split("/r/")[1]
    r = client.get(f"/api/public/receipts/{share}")
    assert r.status_code == 200
    assert r.json()["token_last4"] == "4242"


def test_unknown_receipt_404():
    client = TestClient(create_app())
    assert client.get("/api/public/receipts/nope").status_code == 404


def test_get_receipt_by_id(monkeypatch):
    client = TestClient(create_app())
    sid, listing = _setup(client, monkeypatch)
    co = client.post(
        "/api/checkout",
        json={
            "session_id": sid,
            "listing_id": listing["id"],
            "mandate": {"max_amount_cents": 50000, "currency": "USD", "expires_in_seconds": 600},
        },
    ).json()
    confirmed = client.post(
        f"/api/checkout/{co['checkout_id']}/confirm",
        json={
            "passkey_assertion": {"credential_id": "mock", "client_data": "mock"},
            "idempotency_key": "k2",
        },
    ).json()
    r = client.get(f"/api/receipts/{confirmed['receipt_id']}")
    assert r.status_code == 200
    assert r.json()["id"] == confirmed["receipt_id"]
