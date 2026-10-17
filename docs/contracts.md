# API and domain contracts

Frozen at the 1:15 PM Saturday huddle. Owner: A (`backend/app/domain/models.py`, `frontend/src/lib/types.ts`, this file). Changes after freeze are announced in the team channel before they are committed.

Money is integer cents. IDs are prefixed: `ses_`, `lst_`, `inv_`, `chk_`, `man_`, `tok_`, `txn_`, `rcp_`, `shr_`. Listing IDs are `lst_` + `sha256(canonical_url)[:16]`.

## Error envelope

```json
{"error": {"code": "...", "message": "...", "details": {}, "request_id": "..."}}
```

CORS: explicit origins plus `*.vercel.app`. No wildcard with credentials. No cookies.

## `GET /api/health` → 200 while the process is alive

```json
{"status": "ok", "db": "ok", "version": "0.9.0", "demo_mode": true, "uptime_s": 1234}
```

200 even when Mongo is down. Then `status` is `"degraded"` and `db` is `"unavailable"`.

## `POST /api/sessions` → 201

Returns `session_id`, `stage: "clarifying"`, 2–3 `questions`, `expires_at`. Session creation never blocks on the LLM.

## `POST /api/sessions/{session_id}/answers` → 202

Body: `{ "answers": [...], "skip_remaining": false }`.

Returns `session_id`, `stage: "searching"`, `events_url`, `search_spec`. The orchestrator starts before the response returns.

## `GET /api/sessions/{session_id}` → snapshot

`session_id`, `stage`, `query`, `listings`, `checks`, `scores`, `recommendation`, `last_seq`, `stats`.

## `GET /api/sessions/{session_id}/events` → SSE

Headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no`.

Honors `Last-Event-ID` or `?since_seq=`. Heartbeat comment every 15s. Server closes after `investigation.complete`.

Envelope on every event: `type`, `seq`, `ts`, `session_id`.

| Event | Extra payload |
|---|---|
| `session.stage` | `stage` |
| `search.started` | `query`, `providers` |
| `search.completed` | `count`, `source` |
| `listing.found` | `listing`, `rank` |
| `check.started` | `listing_id`, `check_id`, `name`, `index` |
| `check.completed` | `listing_id`, `check` |
| `listing.scored` | `listing_id`, `score`, `verdict`, `confidence`, `top_reason`, `penalties` |
| `recommendation.ready` | `recommended_listing_id`, `median_trusted_cents`, `savings_cents`, `eligible_ids` |
| `investigation.complete` | `stats`, `duration_ms` |
| `session.error` | `code`, `message`, `recoverable`, `listing_id?` |

Client: dedupe by `seq`; upsert checks by `(listing_id, check.id)`; close on `investigation.complete`.

## `POST /api/checkout` → 201 or 409

Client sends only `session_id`, `listing_id`, and a mandate cap. Server re-derives price, merchant, and score.

409 codes: `MERCHANT_NOT_TRUSTED`, `SCORE_TOO_LOW`, `COVERAGE_TOO_LOW`, `MERCHANT_MISMATCH`, `AMOUNT_EXCEEDS_CAP`, `MANDATE_EXPIRED`, `ALREADY_PAID`, `INVESTIGATION_STALE`.

## `POST /api/checkout/{checkout_id}/confirm` → 200 or 402

`passkey_assertion.client_data == "fail"` → 402 `PAYMENT_DECLINED`. Confirm is idempotent.

## Receipts

- `GET /api/receipts/{receipt_id}` → `Receipt`
- `GET /api/public/receipts/{share_id}` → `Receipt` (no PII)

Checkout and receipt always carry: `Sandbox — simulated Visa Intelligent Commerce flow.`
