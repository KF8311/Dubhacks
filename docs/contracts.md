# API and domain contracts

Frozen at the 1:15 PM Saturday huddle. Owner: A (`backend/app/domain/models.py`, `frontend/src/lib/types.ts`, this file). Changes after freeze are announced in the team channel before they are committed.

Money is integer cents. IDs are prefixed: `ses_`, `lst_`, `inv_`, `chk_`, `man_`, `tok_`, `txn_`, `rcp_`, `shr_`. Listing IDs are `lst_` + `sha256(canonical_url)[:16]`.

## Domain types

Source of truth: `backend/app/domain/models.py` and `backend/app/domain/enums.py`. The frontend mirrors these in `frontend/src/lib/types.ts`. Timestamps are ISO 8601 UTC.

Enums:

| Enum | Values |
|---|---|
| `CheckId` | `domain_age`, `ssl_cert`, `safe_browsing`, `reddit_sentiment`, `page_flags` |
| `TrustStatus` | `passed`, `warning`, `failed`, `skipped` |
| `Verdict` | `trusted`, `caution`, `danger` |
| `SessionStage` | `clarifying`, `searching`, `investigating`, `ready`, `no_trusted_option`, `failed` |
| `CheckoutStage` | `awaiting_passkey`, `authorized`, `captured`, `declined`, `expired`, `cancelled` |

`Listing`:

```json
{"id": "lst_...", "title": "...", "price_cents": 17999, "currency": "USD",
 "merchant_name": "Best Buy", "merchant_domain": "bestbuy.com",
 "image_url": "https://...", "product_url": "https://...",
 "category": "headphones", "source": "catalog"}
```

`source` is `serpapi | catalog | fixture`.

`Evidence`:

```json
{"label": "Registered", "value": "2026-10-05", "url": null}
```

`TrustCheckResult` — the payload of `check.completed`:

```json
{"id": "domain_age", "name": "Domain age", "status": "failed", "severity": 0.95,
 "summary": "Domain registered 12 days ago.", "evidence": [], "source": "live", "duration_ms": 240}
```

`severity` is in [0, 1]. `source` is `live | cache | allowlist | fixture | timeout | unavailable`. A `skipped` status never deducts points; it only lowers confidence.

`Penalty`:

```json
{"check_id": "domain_age", "points": 38, "reason": "Registered 12 days ago"}
```

`ScoreResult`:

```json
{"score": 22, "verdict": "danger", "confidence": 1.0, "penalties": [],
 "fatal_flags": ["domain_age_fatal"], "top_reason": "Domain registered 12 days ago.",
 "scoring_version": "1.0"}
```

`SearchSpec`:

```json
{"query": "headphones", "budget_max_cents": 35000, "category": "headphones",
 "merchants_preferred": ["bestbuy.com"]}
```

`Question` — returned by `POST /api/sessions`. **Not yet in `models.py`; A confirms before freeze.**

```json
{"id": "use_case", "prompt": "What will you use them for?",
 "kind": "single_select", "options": [{"id": "commute", "label": "Commuting"}]}
```

`kind` is `single_select | multi_select | free_text`; `options` is `[]` for `free_text`.

`Answer`:

```json
{"question_id": "use_case", "option_id": "commute", "text": null}
```

`Investigation` — the receipt's frozen snapshot at checkout time: `id`, `listing_id`, `session_id`, `checks[]`, `score`, `allowlisted`, `duration_ms`, `created_at`.

`Receipt`: `id`, `share_id`, `checkout_id`, `transaction_id`, `listing`, `investigation_snapshot`, `amount_cents`, `currency`, `token_last4`, `verified[]`, `unverified[]`, `issued_at`, `signature`.

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

Ordering guarantee:

1. `seq` strictly increases across every event on the stream, replays included.
2. `session.stage` precedes any `search.*` event.
3. `search.started` precedes every `listing.found`.
4. `check.started` precedes the matching `check.completed` for the same `(listing_id, check_id)`.
5. `listing.scored` for a listing comes after all of that listing's `check.*` events.
6. `recommendation.ready` comes after every `listing.scored`.
7. `investigation.complete` is the last event and closes the stream.

Client: dedupe by `seq`; upsert checks by `(listing_id, check.id)`; ignore unknown `type` values; close on `investigation.complete`.

**Live for C (Tasks 6/7/16):** After answers the stream is:

`search.started` → `listing.found` → `check.started` / `check.completed` → `listing.scored` → `recommendation.ready` → `investigation.complete` (close).

Allowlisted merchants emit `source: "allowlist"` skipped checks and `verdict: "trusted"`. A caution listing is not payable (`MERCHANT_NOT_TRUSTED`).

Example `listing.found` data:

```json
{
  "type": "listing.found",
  "seq": 4,
  "ts": "2026-10-17T22:40:00.000Z",
  "session_id": "ses_abc",
  "listing": {
    "id": "lst_...",
    "title": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
    "price_cents": 32800,
    "currency": "USD",
    "merchant_name": "Best Buy",
    "merchant_domain": "bestbuy.com",
    "image_url": "",
    "product_url": "https://www.bestbuy.com/site/sony-wh-1000xm5/6505727.p",
    "source": "catalog"
  },
  "rank": 1
}
```

## `POST /api/checkout` → 201 or 409

**For C — request (Task 23 wires the HTTP route; this JSON is frozen):**

```json
{
  "session_id": "ses_abc",
  "listing_id": "lst_1",
  "mandate": {"max_amount_cents": 30000, "currency": "USD", "expires_in_seconds": 600}
}
```

Client sends only IDs and a cap. Server re-derives price, merchant, and score.

**201 response:**

```json
{
  "checkout_id": "chk_abc",
  "stage": "awaiting_passkey",
  "amount_cents": 24900,
  "currency": "USD",
  "merchant": {"name": "Best Buy", "domain": "bestbuy.com"},
  "mandate": {
    "id": "man_abc",
    "max_amount_cents": 30000,
    "merchant_domain": "bestbuy.com",
    "expires_at": "2026-10-17T19:10:00Z",
    "single_use": true
  },
  "trust_snapshot": {
    "score": 92,
    "verdict": "trusted",
    "confidence": 0.92,
    "investigation_id": "inv_abc",
    "scoring_version": "1.0"
  },
  "passkey_challenge": {
    "challenge": "b64...",
    "rp_id": "sniff.vercel.app",
    "timeout_ms": 60000,
    "mode": "simulated"
  },
  "sandbox_label": "Sandbox — simulated Visa Intelligent Commerce flow.",
  "expires_at": "2026-10-17T19:05:00Z"
}
```

409 codes: `MERCHANT_NOT_TRUSTED`, `SCORE_TOO_LOW`, `COVERAGE_TOO_LOW`, `MERCHANT_MISMATCH`, `AMOUNT_EXCEEDS_CAP`, `MANDATE_EXPIRED`, `ALREADY_PAID`, `INVESTIGATION_STALE`.

A caution or danger listing is always `MERCHANT_NOT_TRUSTED`. Payability is enforced in `assert_payable` now; the HTTP route is Task 23.

## `POST /api/checkout/{checkout_id}/confirm` → 200 or 402

**Request:**

```json
{
  "passkey_assertion": {"credential_id": "mock_cred_abc", "client_data": "mock"},
  "idempotency_key": "uuid"
}
```

**200 response:**

```json
{
  "checkout_id": "chk_abc",
  "status": "captured",
  "transaction": {
    "id": "txn_abc",
    "status": "approved",
    "amount_cents": 24900,
    "currency": "USD",
    "network": "visa",
    "token_last4": "4242",
    "processor": "mock-vic",
    "mode": "sandbox"
  },
  "receipt_id": "rcp_abc",
  "receipt_url": "/r/shr_abc",
  "sandbox_label": "Sandbox — simulated Visa Intelligent Commerce flow."
}
```

`passkey_assertion.client_data == "fail"` → 402 `PAYMENT_DECLINED`. Confirm is idempotent.

## Receipts

- `GET /api/receipts/{receipt_id}` → `Receipt`
- `GET /api/public/receipts/{share_id}` → `Receipt` (no PII)

Checkout and receipt always carry: `Sandbox — simulated Visa Intelligent Commerce flow.`
