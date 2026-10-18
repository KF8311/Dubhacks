import json
import time
import urllib.error
import urllib.request


def req(method: str, url: str, data=None):
    body = None if data is None else json.dumps(data).encode()
    request = urllib.request.Request(
        url, data=body, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        return exc.code, parsed


def main() -> None:
    print("FLY health:", end=" ")
    try:
        status, body = req("GET", "https://sniff-visa-dubhacks.fly.dev/api/health")
        print(status, body.get("status"), "uptime", body.get("uptime_s"))
    except Exception as exc:  # noqa: BLE001
        print("FAIL", exc)

    print("LOCAL health:", end=" ")
    status, body = req("GET", "http://127.0.0.1:8000/api/health")
    print(status, body)

    status, session = req(
        "POST",
        "http://127.0.0.1:8000/api/sessions",
        {"query": "headphones", "client_id": "smoke"},
    )
    print("create", status, session.get("session_id"), session.get("stage"))
    sid = session["session_id"]
    status, answers = req(
        "POST",
        f"http://127.0.0.1:8000/api/sessions/{sid}/answers",
        {"answers": [{"question_id": "q_budget", "option_id": "300"}]},
    )
    print("answers", status, answers.get("stage"))
    time.sleep(2)
    status, snap = req("GET", f"http://127.0.0.1:8000/api/sessions/{sid}")
    rec = snap.get("recommendation") or {}
    print(
        "snapshot",
        status,
        snap.get("stage"),
        "listings",
        len(snap.get("listings") or []),
        "rec",
        rec.get("recommended_listing_id"),
    )
    listing_id = rec.get("recommended_listing_id")
    if not listing_id and snap.get("listings"):
        listing_id = snap["listings"][0]["id"]
    print("listing", listing_id)
    status, checkout = req(
        "POST",
        "http://127.0.0.1:8000/api/checkout",
        {
            "session_id": sid,
            "listing_id": listing_id,
            "mandate": {
                "max_amount_cents": 50000,
                "currency": "USD",
                "expires_in_seconds": 600,
            },
        },
    )
    print("checkout", status, checkout.get("checkout_id") or checkout.get("error"))
    if status != 201:
        return
    confirm_url = f"http://127.0.0.1:8000/api/checkout/{checkout['checkout_id']}/confirm"
    payload = {
        "passkey_assertion": {"credential_id": "mock", "client_data": "mock"},
        "idempotency_key": f"smoke-{checkout['checkout_id']}",
    }
    status, confirmed = req("POST", confirm_url, payload)
    print(
        "confirm",
        status,
        confirmed.get("receipt_id") or confirmed.get("error"),
        confirmed.get("receipt_url"),
    )
    if status != 200:
        return
    share = confirmed["receipt_url"].split("/r/")[-1]
    status, receipt = req("GET", f"http://127.0.0.1:8000/api/public/receipts/{share}")
    print("public receipt", status, receipt.get("token_last4"), receipt.get("sandbox_label"))
    status2, confirmed2 = req("POST", confirm_url, payload)
    print("confirm2 same receipt", confirmed.get("receipt_id") == confirmed2.get("receipt_id"), status2)


if __name__ == "__main__":
    main()
