from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.domain.enums import CheckId, TrustStatus, Verdict
from app.domain.models import Investigation, ScoreResult, TrustCheckResult
from app.main import create_app
from app.search.catalog import load_catalog


def _setup(client, monkeypatch, verdict="trusted", completed=5):
    s = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    client.post(
        f"/api/sessions/{s['session_id']}/answers",
        json={"answers": [{"question_id": "q_budget", "option_id": "300"}]},
    )
    listing = next(item for item in load_catalog() if item.merchant_domain == "bestbuy.com")
    checks = [
        TrustCheckResult(
            id=cid,
            name=cid.value,
            status=TrustStatus.PASSED,
            severity=0,
            summary="ok",
            source="live",
        )
        for cid in list(CheckId)[:completed]
    ]
    inv = Investigation(
        id="inv_1",
        listing_id=listing.id,
        session_id=s["session_id"],
        checks=checks,
        score=ScoreResult(
            score=92 if verdict == "trusted" else 50,
            verdict=Verdict(verdict),
            confidence=0.9,
            top_reason="x",
        ),
        allowlisted=False,
        duration_ms=1,
        created_at=datetime.now(timezone.utc),
    )
    import app.api.routes_checkout as rc

    monkeypatch.setattr(rc, "_get_listing", lambda lid: listing)
    monkeypatch.setattr(rc, "_get_investigation", lambda sid, lid: inv)
    return s["session_id"], listing.model_dump()


def test_checkout_blocked_for_caution(monkeypatch):
    client = TestClient(create_app())
    sid, listing = _setup(client, monkeypatch, verdict="caution", completed=5)
    r = client.post(
        "/api/checkout",
        json={
            "session_id": sid,
            "listing_id": listing["id"],
            "mandate": {"max_amount_cents": 50000, "currency": "USD", "expires_in_seconds": 600},
        },
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "MERCHANT_NOT_TRUSTED"


def test_confirm_twice_returns_same_receipt(monkeypatch):
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
    body = {
        "passkey_assertion": {"credential_id": "mock", "client_data": "mock"},
        "idempotency_key": "same",
    }
    a = client.post(f"/api/checkout/{co['checkout_id']}/confirm", json=body).json()
    b = client.post(f"/api/checkout/{co['checkout_id']}/confirm", json=body).json()
    assert a["receipt_id"] == b["receipt_id"]


def test_confirm_fail_returns_402(monkeypatch):
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
    r = client.post(
        f"/api/checkout/{co['checkout_id']}/confirm",
        json={
            "passkey_assertion": {"credential_id": "mock", "client_data": "fail"},
            "idempotency_key": "k",
        },
    )
    assert r.status_code == 402
    assert r.json()["error"]["code"] == "PAYMENT_DECLINED"
