# Sykes + Visa

A trust-gated shopping agent. It searches listings, runs five trust checks on every merchant, streams the investigation to the browser, recommends the cheapest **trusted** option, and completes a **sandboxed** Visa Intelligent Commerce flow: mandate → passkey → one-time token → transaction → receipt.

Built for the Visa "Reimagine Shopping" track at DubHacks '26.

> **Sandbox notice.** The payment flow is simulated and labelled everywhere. This is a prototype, **not** a Visa production integration. Every shopper, merchant, and card is synthetic; no real PII and no real card numbers are used. The only card artefact is the fictional last-4 `4242`.

**Core rule:** the agent cannot initiate payment to a merchant it cannot verify.

Current state lives in [`docs/status.md`](docs/status.md).

## What it does

1. **Guided discovery** — three questions (budget, use, priority) become a `SearchSpec`.
2. **Search** — the catalog provider returns nine listings; a live provider is optional.
3. **Investigation** — five checks run per listing with bounded concurrency, streamed over SSE as they finish.
4. **Scoring** — deterministic arithmetic produces a 0–100 score and a `trusted` / `caution` / `danger` verdict.
5. **Recommendation** — the cheapest eligible listing, with median and savings.
6. **Checkout** — a spending mandate, a simulated passkey, a one-time token, and a signed receipt with a public share link.

## Trust checks

| Check | Question it answers | Source |
|---|---|---|
| `DOMAIN_AGE` | How old is the merchant's domain? | RDAP, then WHOIS; a fixture for the demo villain |
| `SSL` | Does the merchant hold a valid certificate for its own hostname? | Live TLS handshake |
| `SAFE_BROWSING` | Has this URL already been reported as dangerous? | Static denylist when no API key is set |
| `REDDIT_SENTIMENT` | What has Reddit already said about this merchant? | Public JSON, or fixtures offline |
| `PAGE_FLAGS` | Does the page use the language of a scam? | Server-side fetch, parsed and summarised |

A check that cannot run is `skipped`, never `passed`. **Skipped is not evidence of safety** — it lowers coverage, and coverage is capped.

## Scoring (deterministic — no model involved)

```
score = 100 − Σ penalties
  failed check  → round(severity × 40)
  warning check → round(severity × 15)

verdict        trusted ≥ 70 · caution ≥ 40 · danger < 40
coverage       fewer than 3 completed checks caps the score at 69
fatal signals  safe browsing failed            → 0
               page flags + domain age failed   → 0
               domain age failed (severity ≥ .85) → 5
```

Allowlisted merchants score 0 by design — the score measures *suspicion*, not safety — and carry `allowlisted: true` so downstream logic can tell the difference. This is decision D-015.

## Payability gate

Checkout is refused unless **all** of these hold, and the server re-checks them on both `POST /api/checkout` and `POST /api/checkout/{checkout_id}/confirm`:

- verdict is `trusted`
- score ≥ 70 (unless the merchant is allowlisted)
- at least 3 checks completed (unless allowlisted)
- the mandate's merchant matches the listing
- the amount is within the mandate cap
- the investigation is under 30 minutes old

Refusals are `409` with `{code, message, details}` where `code` is a `PayabilityCode`. A declined passkey is `402 PAYMENT_DECLINED`.

## Quick start

**Backend** (Python 3.11 or 3.12):

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # macOS/Linux: .venv/bin/python
cp .env.example .env
.venv/Scripts/python -m uvicorn app.main:app --reload --workers 1
```

`--workers 1` is mandatory: SSE streams and the in-memory store assume one process.

**Deploy:** Fly.io from the repo root (`fly.toml`), or Vercel via [`vercel.json`](vercel.json) — the backend build runs `python scripts/bundle_data.py` so the fixtures ship inside the function. The frontend reads `VITE_API_BASE_URL`; when it is unset it calls same-origin `/api`, which is what the Vercel service rewrite expects. Local dev defaults to `http://localhost:8000`.

**Frontend:**

```bash
cd frontend
npm ci
npm run dev            # http://localhost:5173
```

The frontend talks to `http://localhost:8000` by default. Add `?mock=1` to any URL to run the entire flow — including checkout — from `data/mock-session.json` with no backend.

## Environment variables

All optional; the demo runs with none of them set.

| Variable | Default | Purpose |
|---|---|---|
| `DEMO_MODE` | `true` | Force the catalog provider and fixture-backed checks |
| `OFFLINE` | `false` | Never open a socket; fixtures only |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS for JSON routes and SSE |
| `MAX_LISTINGS` | `9` | Caps the fan-out |
| `INVESTIGATION_BUDGET_S` | `14.0` | Wall-clock budget for one session's checks |
| `RECEIPT_SIGNING_SECRET` | `dev-only-change-me` | HMAC key for receipts |
| `SERPAPI_KEY` | unset | Live search; the catalog is used when unset (D-021, superseding D-011) |
| `GEMINI_API_KEY` | unset | Questions, narration, and check explanations; templates are the fallback |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Override if your key has different model access (D-019) |
| `GOOGLE_SAFE_BROWSING_KEY` | unset | Live reputation; static denylist when unset |
| `MONGODB_URI` | unset | Off by default; when set, persists the payment path only (D-006, D-016) |

## API

| Route | Purpose |
|---|---|
| `POST /api/sessions` | Create a session and its questions |
| `POST /api/sessions/{id}/answers` | Submit answers; starts the investigation |
| `GET /api/sessions/{id}` | Snapshot: listings, checks, scores, recommendation |
| `GET /api/sessions/{id}/events` | SSE stream, monotonic `seq`, replay via `Last-Event-ID` |
| `POST /api/checkout` | Create a mandate and a checkout |
| `POST /api/checkout/{checkout_id}/confirm` | Passkey assertion → transaction → receipt |
| `GET /api/receipts/{receipt_id}` | Receipt by id |
| `GET /api/public/receipts/{share_id}` | Public receipt behind `/r/{share_id}` |
| `POST /api/demo/reset` | Clear sessions and payment state between rehearsals |
| `GET /api/health` | Liveness; reports `degraded` when a dependency is down |

Full shapes: [`docs/contracts.md`](docs/contracts.md).

## Demo script

| Step | Action | Expected |
|---|---|---|
| 1 | Ask "noise cancelling headphones" | Three questions appear |
| 2 | Answer **$300–$600**, Travel, Noise cancelling | 9 listings: 8 trusted + 1 danger |
| 3 | Watch the stream | 45 checks fill in; the villain turns red |
| 4 | Read the villain reason | Denylisted, 12-day domain, scam reports, urgency copy |
| 5 | Point at the pick | $179.99, saving $194.50 against a $374.49 median |
| 6 | Purge the danger card | It disappears from the grid |
| 7 | Check out | Sandbox banner → mandate → passkey → receipt |
| 8 | Optional | Try the villain; the server refuses with a code |

Only **$300–$600** contains all nine listings — the catalog runs to $549.99 — so the other answers are thinner: **$150–$300** returns 3 cards, and **Under $150** leaves only the villain and ends in `no_trusted_option`. That last one is a legitimate second demo, not the happy path.

## Tests

```bash
cd backend && .venv/Scripts/python.exe -m pytest -q          # 232 passed
cd frontend && npx vitest run && npm run build               # 55 passed, build clean
```

**Offline rehearsal** — the whole session in-process, no server, no network:

```bash
backend/.venv/Scripts/python.exe scripts/replay_offline.py
```

It must print the same numbers as the live demo and exit 0. A non-zero exit means the demo drifted.

## Repository layout

```
backend/app/
  api/          session, checkout, receipt, health routes
  checks/       the five checks + registry + timeout-safe runner
  trust/        scoring, recommendation, allowlist
  payments/     payability gate, mandates, mock VIC, signed receipts
  sessions/     registry, event bus, orchestrator
  demo/         offline replay
frontend/src/
  features/     discovery, results, checkout, receipt
  lib/          api client, SSE hook, mock mode
data/           catalog, allowlist, villain fixtures
docs/           status, contracts, decisions, plans
```

## Honesty notes

- **The payment is a mock.** No Visa network, no token service, no real merchant. Every response carries `processor: "mock-vic"`, `mode: "sandbox"`, and the sandbox label.
- **The score is deterministic; a model never decides anything.** Gemini Flash Lite writes the clarifying questions, the one-line recommendation narration, and on-demand check explanations when `GEMINI_API_KEY` is set — every call has a 2.5 s timeout and falls back to templates. Scoring, checks, payability, and checkout are Python-only, and `backend/tests/unit/test_no_llm_path.py` fails the build if the trust, check, or payment modules import the LLM or read the key.
- **The store is in memory by default; Mongo covers the payment path only.** With `MONGODB_URI` unset — the default — everything lives in the in-memory adapter, which keeps the demo reproducible. With it set, `MongoRepository` persists mandates, checkouts, transactions, receipts, and audit events. Session state, listings, and investigations stay in the in-process registry either way, so a restart loses them. The mock VIC token store is also in-process: raw tokens are never stored anywhere, and even the token hash and `last4` stay out of Mongo.
- **Fixtures are labelled.** Any check that answers from a fixture carries `source: "fixture"`.

## Docs

Start at [`docs/INDEX.md`](docs/INDEX.md). The live state is [`docs/status.md`](docs/status.md); decisions are append-only in [`docs/decisions.md`](docs/decisions.md); the VEYZL finding and fix are in [`docs/veylz-audit.md`](docs/veylz-audit.md).
