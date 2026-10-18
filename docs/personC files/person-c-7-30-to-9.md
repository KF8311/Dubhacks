# Person C — 7:30–9:00 checklist

Done when a real session runs real checks, a real checkout, and a real receipt, with no mock data on screen.

Verified on 2026-10-17 against `uvicorn` at `http://127.0.0.1:8000`. `scripts/smoke_http.py` returned checkout `201`, confirm `200`, and a public receipt with token `4242` and the sandbox label. The browser reached the live results, the Target best pick, the mandate, and the simulated passkey.

## Live path

- [x] `POST /api/sessions` and `POST /api/sessions/{id}/answers` are the live path. Mock is opt-in with `?mock=1` or `VITE_USE_MOCK=1`.
- [x] `EventSource` is the live path. The stream emits `listing.found`, `check.completed`, `listing.scored`, and `recommendation.ready`.
- [x] Discovery submits the real session id.
- [x] An allowlisted merchant shows `Verified · Trusted` on the card, in checkout, and on the receipt ring. The stored score stays 0.
- [x] Happy-path answers are `$150–$300`, then use, then priority. `Under $150` leaves only the villain and ends in `no_trusted_option`.
- [x] `POST /api/checkout` sends `{ session_id, listing_id, mandate: { max_amount_cents, currency, expires_in_seconds } }`.
- [x] Confirm sends `{ passkey_assertion: { credential_id, client_data }, idempotency_key }`. `client_data: "fail"` shows the decline inline.
- [x] A successful confirm follows `receipt_url` like `/r/shr_abc` and loads `GET /api/public/receipts/{share_id}`.

## Layout on the live payload

- [x] Long titles stay inside the card.
- [x] A missing image keeps the letter placeholder.
- [x] The live best pick is `lst_tgt_bsp` at $179.99.
- [x] The villain renders danger with the local-denylist reason.
