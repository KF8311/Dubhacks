# Sniff + Visa Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a trust-gated shopping agent that investigates every listing, recommends the cheapest trusted option, and completes the purchase through a sandboxed Visa mandate → passkey → token flow with a shareable trust receipt.

**Architecture:** React 19 SPA → FastAPI API. One anonymous session owns one multiplexed SSE stream; the server fans out five trust checks per listing, streams each result, scores deterministically, and emits a recommendation. The client sends only IDs into checkout; the server re-reads the persisted investigation and re-validates payability. MongoDB is persistence, never on the critical path.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, sse-starlette, httpx, motor, React 19, Vite, TypeScript, Tailwind, shadcn/ui, Framer Motion, Zustand, Gemini 2.5 Flash, SerpAPI Google Shopping, pytest, Vitest, Playwright.

**Spec:** the standalone product spec was removed on 2026-10-18; this plan is the spec of record.

---

## Global Constraints

- **Hackathon window:** hacking starts 12:30 PM Saturday; Devpost draft 10:30 PM Saturday; final submission 10:00 AM Sunday. No product code before 12:30 PM Saturday.
- **70/30 rule:** at least 70% of code must be written during the hackathon. The Sniff repo is an architecture reference only; do not copy its code, file layout, copy text, or visual identity. Commit by 12:45 PM Saturday and at least every 30 minutes per person; the commit history is the evidence.
- **Payment is a sandbox:** never claim production Visa integration. Label checkout and receipt "Sandbox — simulated Visa Intelligent Commerce flow."
- **No real card data, no real PII.** All customers, merchants, and transactions are synthetic. The villain merchant is fictional.
- **Hard product rule:** the server must reject checkout for any listing whose verdict is not `trusted`, whose score is below 70, or whose investigation has fewer than 3 completed checks — except allowlisted merchants, which are trusted by construction and skip the checks.
- **Deterministic score:** given the same check results and scoring version, the score is identical. No randomness, no LLM input.
- **LLM boundary:** the LLM generates clarifying questions, an optional narrative, and lazy explanations. It never selects checks, fetches URLs, or computes the score.
- **Money is integer cents** everywhere. Currency is an explicit ISO code. Format only at the UI edge.
- **One title track:** Visa. Up to 3 sponsored side tracks.
- **Video:** under 3 minutes, required for Visa judging.
- **Accessibility:** WCAG AA contrast, keyboard navigable, visible focus states.
- **Secrets:** all keys in backend `.env`; `.env` is gitignored; `.env.example` is committed. The frontend has exactly one env var: `VITE_API_BASE_URL`.
- **One Uvicorn worker.** In-memory sessions and the event bus assume a single process; `--workers 1` is mandatory. Do not enable gzip globally; it buffers `text/event-stream`.

---

## Review Focus

The inputs and failure modes most likely to break the product in a live demo. Each has a test in the task that owns the code.

1. **SerpAPI fails, rate-limits, or returns Google-hosted links** → the service falls back to the curated catalog, rejects listings without a merchant domain, and injects the hero and villain. (Task 4)
2. **A trust check hangs** → per-check `asyncio.wait_for` marks it `skipped` with `source: "timeout"`; the investigation completes inside a 14s global budget. (Task 8)
3. **Fewer than 3 checks complete** → the score is capped at 69 (caution), so the listing is not payable. "Insufficient evidence is not trust." (Task 14)
4. **Page scraper is pointed at a private IP, `file://`, or a redirect into the metadata service** → `validate_public_url` blocks it before any fetch and re-validates every redirect. (Task 13)
5. **Scraped page or Reddit text contains prompt injection** → only structured extractor output reaches the LLM; page text is delimited data, never instructions; no agentic tool loop. (Task 13)
6. **Client sends a forged price, merchant, or score** → checkout accepts only `session_id`, `listing_id`, and a cap; the server re-derives everything. (Task 22)
7. **Double-click or retry on confirm** → the checkout state machine uses an atomic conditional transition and a unique idempotency key; the second call returns the original receipt. (Task 23)
8. **SSE opens twice (React StrictMode) or reconnects** → the hook dedupes by `seq`, closes on completion, and falls back to the snapshot endpoint. (Task 20)
9. **MongoDB is slow or unreachable** → the in-memory repository serves the request; persistence happens asynchronously; `/api/health` reports `db: unavailable` but still returns 200. (Task 27)
10. **Villain does not reliably go red** → demo mode uses fixtures for RDAP, page HTML, and Reddit, and a golden test pins the villain's score to `danger`. (Task 28)

---

## 1. Executive Summary

Sniff + Visa is a 21-hour hackathon build with five moving parts: a shopping search layer, a session/event layer, a parallel trust engine, a deterministic recommendation, and a sandboxed Visa checkout. The engineering risk is concentrated in external API reliability, the credibility of the trust score, and the payment demo. Every external call sits behind an interface with a fallback, so no single failure kills the demo.

The build is organized as a vertical slice first: one session → search → two checks → score → checkout. Once that slice works end to end, the remaining checks, the receipt, and demo mode are added behind the same contracts. No task depends on a later task's internals.

---

## 2. Requirements

### 2.1 Functional Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| FR-1 | A session asks 2–3 clarifying questions and produces a search spec. | User reaches results without typing a full query. |
| FR-2 | Search returns up to 12 listings across 3+ merchants. | Demo catalog has 8 trusted + 1 villain across 5+ merchants. |
| FR-3 | Five trust checks run per listing, concurrently, streamed over one session SSE stream. | First check visible < 3s; all checks < 14s. |
| FR-4 | Each listing gets a 0–100 score, a confidence, and `trusted`/`caution`/`danger`. | Golden scoring tests pass. |
| FR-5 | The app recommends the cheapest trusted listing and shows savings vs. the trusted median. | No non-trusted listing is ever recommended. |
| FR-6 | Checkout creates a mandate, a simulated passkey assertion, a one-time token, a transaction, and a receipt. | Mandate cap enforced; token shown once as last-4; decline path works. |
| FR-7 | A receipt is immutable and shareable by unguessable link. | Receipt page loads by share ID; no PII. |
| FR-8 | Checkout is blocked for non-trusted, low-score, low-coverage, stale, or mismatched listings. | Each reason code returns 409 with the documented code. |
| FR-9 | Sessions, investigations, checkouts, and receipts are persisted. | MongoDB documents read back by ID; in-memory fallback works. |
| FR-10 | Demo mode guarantees the hero and villain without network luck. | `DEMO_MODE=1` produces identical listings, checks, scores, and recommendation on every run. |

### 2.2 Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | First listing visible | < 3s after answers |
| NFR-2 | All checks for 8 listings | < 14s global budget |
| NFR-3 | Single check p95 | < 4s; hard timeouts 3–6s |
| NFR-4 | Checkout create/confirm | < 400ms server time |
| NFR-5 | Availability during judging | 99%; every external call has a fallback |
| NFR-6 | Security | No real PII; SSRF protection; secrets in env; CORS allowlist |
| NFR-7 | Reproducibility | Seeded demo mode; deterministic scoring with a version string |
| NFR-8 | Accessibility | WCAG AA contrast; keyboard navigation; focus states |
| NFR-9 | Deployability | Vercel + Fly.io/Render + Atlas free tiers |
| NFR-10 | Code quality | Lint, typecheck, and tests pass in CI |

### 2.3 Out of Scope

- Real Visa Token Service, Visa Payment Passkey, or Visa Intelligent Commerce APIs.
- Real merchant checkout, shipping, inventory, or fulfillment.
- Accounts, authentication, or multi-tenancy.
- Real card data or payments.
- Chrome extension.
- Internationalization.
- Mobile-native app.

---

## 3. Architecture

### 3.1 System Context

```
┌────────────────────── EXTERNAL ACTORS ──────────────────────┐
│ Shopper (demo laptop, 1280x800)   Visa judges (3-min video) │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────────┐
│ Sniff + Visa Web — React 19 SPA on Vercel                   │
│ Discovery → Results/Investigation → Checkout → Receipt      │
└──────────────────────────┬──────────────────────────────────┘
                           │ JSON REST + text/event-stream
┌──────────────────────────▼──────────────────────────────────┐
│ Sniff + Visa API — FastAPI, one Uvicorn worker              │
│ Sessions · EventBus · Orchestrator · Trust · Mock VIC       │
└──┬───────────┬──────────────┬───────────────┬───────────────┘
   ▼           ▼              ▼               ▼
MongoDB     Gemini 2.5     SerpAPI Google   Public web
Atlas       Flash          Shopping /       (RDAP, TLS,
(motor)     2–3 calls      curated catalog  Safe Browsing,
            per session                     Reddit, pages)
```

**Trust boundary:** the browser is untrusted. API keys live only in the API process. The only unauthenticated public resource is `/r/{share_id}`, which contains no PII and no raw token.

### 3.2 Container Internals

```
FastAPI process (one asyncio event loop)
├── HTTP layer
│   ├── routes_sessions.py     POST /api/sessions, POST /{id}/answers, GET /{id}
│   ├── routes_events.py       GET /api/sessions/{id}/events (SSE)
│   ├── routes_checkout.py     POST /api/checkout, POST /{id}/confirm, POST /{id}/cancel
│   ├── routes_receipts.py     GET /api/receipts/{id}, GET /api/public/receipts/{share_id}
│   └── routes_health.py       GET /api/health, POST /api/demo/reset (DEMO_MODE only)
├── SessionRegistry            in-memory authoritative session state, 2h idle sweep
├── EventBus                   per-session monotonic seq log + subscriber queues
├── SessionOrchestrator        one background task per session
│     search → listing.found → fan-out checks (bounded) → score → recommend → close
├── SearchService              SerpAPI adapter (5s budget) → catalog fallback
├── TrustEngine
│   ├── Allowlist              exact host or dot-boundary subdomain match
│   ├── Checks: domain_age, ssl_cert, safe_browsing, reddit_sentiment, page_flags
│   ├── ScoringEngine          pure, versioned, unit-tested
│   └── RecommendationEngine   pure
├── PaymentService
│   ├── PayabilityGuard        hard server-side gate
│   ├── MandateService         cap, merchant, expiry, single-use
│   ├── MockVIC                token issue/consume, deterministic transaction
│   └── ReceiptService         immutable snapshot + HMAC share signature
├── Repository                 Mongo adapter | InMemory adapter
├── Cache                      in-process LRU + Mongo TTL collections
└── LLMClient                  Gemini; every call has a template fallback and 2.5s timeout
```

### 3.3 Why One Session Stream, Not One Stream Per Product

`EventSource` over HTTP/1.1 is capped at roughly six connections per origin. A results grid with 8–12 products would open 8–12 streams, stall, reconnect-storm, and multiply server state. Instead:

- One `EventSource` per session, opened once.
- Every event carries `session_id`, `listing_id` (where applicable), and a monotonic `seq`.
- The client dedupes by `seq` and upserts checks by `(listing_id, check.id)`.
- The server keeps a bounded replay log (last 500 events) and honors `Last-Event-ID`.

### 3.4 Session Lifecycle

```
POST /api/sessions          → stage: clarifying, 2–3 questions
POST /answers               → stage: searching; orchestrator starts in background
GET  /events                → SSE; replays from seq 0 (or Last-Event-ID)
  search.started
  listing.found × N
  check.started × 5N
  check.completed × 5N
  listing.scored × N
  recommendation.ready
  investigation.complete    → server closes stream
GET  /api/sessions/{id}     → snapshot for refresh/reconnect
```

### 3.5 Sequence — Investigation

```
Browser                API                  Checks                 Search
   │ POST /sessions     │                     │                      │
   │───────────────────▶│ questions           │                      │
   │◀───────────────────│                     │                      │
   │ POST /answers      │                     │                      │
   │───────────────────▶│ start orchestrator  │                      │
   │◀── 202 + events_url│                     │                      │
   │ GET /events        │                     │                      │
   │───────────────────▶│ search ─────────────┼─────────────────────▶│
   │◀─ search.started ──│◀────────────────────┼──── listings ────────│
   │◀─ listing.found ───│ emit per listing    │                      │
   │                    │ fan out ───────────▶│ domain_age           │
   │                    │                     │ ssl_cert             │
   │                    │                     │ safe_browsing        │
   │                    │                     │ reddit_sentiment     │
   │                    │                     │ page_flags           │
   │◀─ check.started ───│                     │                      │
   │◀─ check.completed ─│◀────────────────────│                      │
   │                    │ score per listing   │                      │
   │◀─ listing.scored ──│                     │                      │
   │                    │ recommend           │                      │
   │◀─ recommendation ──│                     │                      │
   │◀─ complete ────────│ close stream        │                      │
```

### 3.6 Sequence — Checkout

```
Browser                API                  Mock VIC
   │ POST /checkout     │                     │
   │ {session, listing, │                     │
   │  cap}              │                     │
   │───────────────────▶│ re-read investigation
   │                    │ assert_payable
   │                    │ create mandate ────▶│
   │                    │ issue token ───────▶│
   │◀── 201 checkout ───│                     │
   │ passkey dialog     │                     │
   │ POST /confirm      │                     │
   │ {assertion, idem}  │                     │
   │───────────────────▶│ atomic transition   │
   │                    │ consume token ─────▶│
   │                    │ authorize ─────────▶│
   │                    │◀──── approved ──────│
   │                    │ create receipt      │
   │◀── receipt + URL ──│                     │
```

---

## 4. Key Technology Decisions

| Decision | Choice | Rationale | Rejected alternative |
|---|---|---|---|
| Backend | **FastAPI** | Python is the team's strength; async; Pydantic; easy SSE | Next.js API routes |
| Frontend | **React + Vite SPA** | Fast dev server; no SSR; one runtime | Next.js |
| Streaming | **One SSE stream per session** | Avoids the 6-connection cap; one replay log | One stream per product, WebSocket |
| Domain age | **RDAP primary, `python-whois` fallback** | RDAP is JSON, fast, reliable; WHOIS hangs | `python-whois` only |
| Product search | **SerpAPI Google Shopping primary, curated catalog fallback** | Tavily is a research API; prices/domains unreliable | Tavily |
| Trust scoring | **Deterministic Python** | Auditable, reproducible, defensible | LLM scoring |
| Explanations | **Templates by default; lazy LLM explain** | Free-tier rate limits; 8×5 LLM calls kill the demo | Per-check LLM |
| Database | **MongoDB Atlas behind a Repository protocol** | Flexible documents; free tier; MongoDB track | Mongo on critical path |
| Payments | **In-process mock VIC state machine** | No production access; demo-safe; honest | Real Visa sandbox |
| Deploy | **Vercel + Fly.io (always-on 256MB) + Atlas** | Render free cold starts are 30–60s and ruin a demo | Render free |
| Tests | **pytest + Vitest + one Playwright path** | Fast unit tests; one E2E happy path | Manual QA only |

**Do not add:** Redis, Celery, RabbitMQ, background workers, auth, accounts, vector DB, a plugin/DI framework for five checks, or floats for money.

---

## 5. Data Model

Money is integer cents. Timestamps are ISO-8601 UTC. IDs are prefixed random strings: `ses_`, `lst_`, `inv_`, `chk_`, `man_`, `tok_`, `txn_`, `rcp_`, `shr_`. Listing IDs are `lst_` + `sha256(canonical_url)[:16]` so caches and investigations align across runs.

### 5.1 Enums

```python
# backend/app/domain/enums.py
class CheckId(str, Enum):
    DOMAIN_AGE = "domain_age"
    SSL = "ssl_cert"
    SAFE_BROWSING = "safe_browsing"
    REDDIT = "reddit_sentiment"
    PAGE_FLAGS = "page_flags"

class TrustStatus(str, Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"

class Verdict(str, Enum):
    TRUSTED = "trusted"
    CAUTION = "caution"
    DANGER = "danger"

class SessionStage(str, Enum):
    CLARIFYING = "clarifying"
    SEARCHING = "searching"
    INVESTIGATING = "investigating"
    READY = "ready"
    NO_TRUSTED_OPTION = "no_trusted_option"
    FAILED = "failed"

class CheckoutStage(str, Enum):
    AWAITING_PASSKEY = "awaiting_passkey"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
```

### 5.2 Core Models

```python
# backend/app/domain/models.py
class Evidence(BaseModel):
    label: str
    value: str
    url: str | None = None

class TrustCheckResult(BaseModel):
    id: CheckId
    name: str
    status: TrustStatus
    severity: float = Field(ge=0, le=1)
    summary: str
    evidence: list[Evidence] = []
    source: Literal["live", "cache", "allowlist", "fixture", "timeout", "unavailable"]
    duration_ms: int = 0

class Listing(BaseModel):
    id: str
    title: str
    price_cents: int = Field(gt=0)
    currency: str = "USD"
    merchant_name: str
    merchant_domain: str
    image_url: str
    product_url: str
    category: str | None = None
    source: Literal["serpapi", "catalog", "fixture"] = "catalog"

class Penalty(BaseModel):
    check_id: CheckId
    points: int
    reason: str

class ScoreResult(BaseModel):
    score: int = Field(ge=0, le=100)
    verdict: Verdict
    confidence: float = Field(ge=0, le=1)
    penalties: list[Penalty] = []
    fatal_flags: list[str] = []
    top_reason: str
    scoring_version: str = "1.0"

class Investigation(BaseModel):
    id: str
    listing_id: str
    session_id: str
    checks: list[TrustCheckResult]
    score: ScoreResult
    allowlisted: bool
    duration_ms: int
    created_at: datetime
```

### 5.3 Session and Payment Models

```python
class Answer(BaseModel):
    question_id: str
    option_id: str | None = None
    text: str | None = None

class SearchSpec(BaseModel):
    query: str
    budget_max_cents: int | None = None
    category: str | None = None
    merchants_preferred: list[str] = []

class SessionStats(BaseModel):
    listings: int = 0
    trusted: int = 0
    caution: int = 0
    danger: int = 0
    duration_ms: int = 0

class Session(BaseModel):
    id: str
    client_id: str
    query: str
    stage: SessionStage
    answers: list[Answer] = []
    search_spec: SearchSpec
    listing_ids: list[str] = []
    recommended_listing_id: str | None = None
    stats: SessionStats = SessionStats()
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

class Mandate(BaseModel):
    id: str
    session_id: str
    listing_id: str
    investigation_id: str
    merchant_domain: str
    max_amount_cents: int = Field(gt=0)
    currency: str = "USD"
    expires_at: datetime
    status: Literal["active", "consumed", "expired"] = "active"

class Checkout(BaseModel):
    id: str
    session_id: str
    listing_id: str
    investigation_id: str
    mandate_id: str
    amount_cents: int
    currency: str = "USD"
    stage: CheckoutStage = CheckoutStage.AWAITING_PASSKEY
    idempotency_key: str
    created_at: datetime
    expires_at: datetime

class Transaction(BaseModel):
    id: str
    checkout_id: str
    status: Literal["approved", "declined"]
    amount_cents: int
    currency: str
    token_last4: str
    processor: Literal["mock-vic"] = "mock-vic"
    mode: Literal["sandbox"] = "sandbox"
    auth_code: str
    created_at: datetime

class Receipt(BaseModel):
    id: str
    share_id: str
    checkout_id: str
    transaction_id: str
    listing: Listing
    investigation_snapshot: Investigation
    amount_cents: int
    currency: str
    token_last4: str
    verified: list[str]
    unverified: list[str]
    issued_at: datetime
    signature: str
```

### 5.4 MongoDB Collections

| Collection | Document | Indexes |
|---|---|---|
| `sessions` | `Session` | `_id` unique, `expires_at` TTL 0, `updated_at` |
| `listings` | `Listing` | `_id` unique, `canonical_url` unique, `merchant_domain` |
| `investigations` | `Investigation` (checks embedded) | `listing_id`, `session_id`, `created_at` |
| `mandates` | `Mandate` | `session_id`, `(status, expires_at)` |
| `checkouts` | `Checkout` | `idempotency_key` unique sparse, `(stage, expires_at)` |
| `payment_tokens` | `id, checkout_id, token_hash, last4, status` | `checkout_id` |
| `transactions` | `Transaction` | `checkout_id` unique |
| `receipts` | `Receipt` | `share_id` unique, `checkout_id` unique |
| `merchant_cache` | RDAP, SSL, Safe Browsing results | `_id = domain`, `expires_at` TTL 0 |
| `reddit_cache` | mentions + classification | `_id = sha256(domain)`, `expires_at` TTL 0 |
| `audit_events` | `session_id, actor, action, subject_id, payload_redacted, ts` | `(session_id, ts)`, TTL 7d |

**Retention:** sessions 2h, caches 6–24h, receipts 30 days, audit 7 days. No PII. `POST /api/demo/reset` clears everything in demo mode.

---

## 6. API Contracts

### 6.1 Conventions

- Error envelope: `{"error": {"code": "...", "message": "...", "details": {}, "request_id": "..."}}`.
- Rate limits: 10 session creations/IP/hour; 3 answers/session; 12 listings max; 20 outbound page fetches/session; 5 checkout attempts/session.
- CORS: explicit origins plus `*.vercel.app`; no wildcard with credentials; no cookies.

### 6.2 `POST /api/sessions` → 201

```json
{
  "session_id": "ses_abc",
  "stage": "clarifying",
  "questions": [
    {
      "id": "q_budget",
      "prompt": "What's your ceiling?",
      "kind": "single_select",
      "options": [
        {"id": "150", "label": "Under $150"},
        {"id": "300", "label": "$150–$300"},
        {"id": "600", "label": "$300–$600"}
      ],
      "allow_free_text": true
    }
  ],
  "expires_at": "2026-10-17T20:30:00Z"
}
```

2–3 questions. LLM-generated with a 2.5s timeout; deterministic category templates on failure. Session creation never blocks on the LLM.

### 6.3 `POST /api/sessions/{session_id}/answers` → 202

```json
{
  "answers": [{"question_id": "q_budget", "option_id": "300"}],
  "skip_remaining": false
}
```

```json
{
  "session_id": "ses_abc",
  "stage": "searching",
  "events_url": "/api/sessions/ses_abc/events",
  "search_spec": {
    "query": "noise cancelling headphones for travel",
    "budget_max_cents": 30000,
    "category": "audio",
    "merchants_preferred": []
  }
}
```

The orchestrator starts in a background task before the response returns.

### 6.4 `GET /api/sessions/{session_id}` → snapshot

```json
{
  "session_id": "ses_abc",
  "stage": "ready",
  "query": "noise cancelling headphones for travel",
  "listings": [],
  "checks": {"lst_1": []},
  "scores": {"lst_1": {}},
  "recommendation": {},
  "last_seq": 137,
  "stats": {"listings": 8, "trusted": 4, "caution": 3, "danger": 1, "duration_ms": 14200}
}
```

### 6.5 `GET /api/sessions/{session_id}/events` → SSE

Headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no`.

Honors `Last-Event-ID` or `?since_seq=` from the bounded replay log. Heartbeat comment every 15s. Server closes after `investigation.complete`.

```
id: 42
event: check.completed
data: {"type":"check.completed","seq":42,"ts":"2026-10-17T18:22:31.412Z","session_id":"ses_abc","listing_id":"lst_1","check":{"id":"safe_browsing","name":"Safe Browsing","status":"passed","severity":0.0,"summary":"No threats found.","source":"live","duration_ms":310,"evidence":[]}}

: heartbeat
```

| Event | Payload (plus `type`, `seq`, `ts`, `session_id`) | When |
|---|---|---|
| `session.stage` | `stage` | Stage transitions |
| `search.started` | `query`, `providers` | Before search |
| `search.completed` | `count`, `source` | After search |
| `listing.found` | `listing`, `rank` | Per result |
| `check.started` | `listing_id`, `check_id`, `name`, `index` | Per check |
| `check.completed` | `listing_id`, `check` | Per check finish |
| `listing.scored` | `listing_id`, `score`, `verdict`, `confidence`, `top_reason`, `penalties` | After all checks |
| `recommendation.ready` | `recommended_listing_id`, `median_trusted_cents`, `savings_cents`, `eligible_ids` | After all listings |
| `investigation.complete` | `stats`, `duration_ms` | Final; close stream |
| `session.error` | `code`, `message`, `recoverable`, `listing_id?` | Per-listing or fatal |

Client rules: dedupe by `seq`; upsert checks by `(listing_id, check.id)`; `es.close()` on `investigation.complete` and on non-retryable `session.error`; set `retry: 60000`; on connection error, fall back to the snapshot endpoint. React StrictMode double-mounts effects in dev — the hook must handle two connections and clean both up.

### 6.6 `POST /api/checkout` → 201 or 409

```json
{
  "session_id": "ses_abc",
  "listing_id": "lst_1",
  "mandate": {"max_amount_cents": 30000, "currency": "USD", "expires_in_seconds": 600}
}
```

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
  "expires_at": "2026-10-17T19:05:00Z"
}
```

409 codes: `MERCHANT_NOT_TRUSTED`, `SCORE_TOO_LOW`, `COVERAGE_TOO_LOW`, `MERCHANT_MISMATCH`, `AMOUNT_EXCEEDS_CAP`, `MANDATE_EXPIRED`, `ALREADY_PAID`, `INVESTIGATION_STALE`.

### 6.7 `POST /api/checkout/{checkout_id}/confirm` → 200

```json
{
  "passkey_assertion": {"credential_id": "mock_cred_abc", "client_data": "mock"},
  "idempotency_key": "uuid"
}
```

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
    "mode": "sandbox",
    "processed_at": "2026-10-17T19:02:11Z"
  },
  "receipt_id": "rcp_abc",
  "receipt_url": "/r/shr_abc"
}
```

`passkey_assertion.client_data == "fail"` → 402 `PAYMENT_DECLINED`; no receipt.

### 6.8 Receipts

- `GET /api/receipts/{receipt_id}` → `Receipt` (app).
- `GET /api/public/receipts/{share_id}` → `Receipt` (share page, no auth, rate-limited, no PII).
- 404 `RECEIPT_NOT_FOUND`.

### 6.9 `GET /api/health` → 200 always while the process is alive

```json
{"status": "ok", "db": "ok", "version": "0.9.0", "demo_mode": true, "uptime_s": 1234}
```

Return 200 even when the DB is down; the keep-alive must succeed. `status: "degraded"` and `db: "unavailable"` communicate the state.

---

## 7. Component Design

### 7.1 Session Registry

```python
# backend/app/sessions/store.py
class SessionRegistry:
    def create(self, client_id: str, query: str) -> Session: ...
    def get(self, session_id: str) -> Session | None: ...
    def update(self, session: Session) -> None: ...
    def attach_investigation(self, session_id: str, inv: Investigation) -> None: ...
    def snapshot(self, session_id: str) -> dict: ...
    def sweep(self, now: datetime) -> int: ...
```

In-memory dict; one background sweep every 10 minutes removes sessions idle > 2h. The snapshot is the reconnect fallback.

### 7.2 Event Bus

```python
# backend/app/sessions/events.py
@dataclass(frozen=True)
class Event:
    seq: int
    type: str
    payload: dict

class EventBus:
    def publish(self, session_id: str, event_type: str, payload: dict) -> Event: ...
    def subscribe(self, session_id: str, since_seq: int = 0) -> AsyncIterator[Event]: ...
    def close(self, session_id: str) -> None: ...
```

- Per-session monotonic `seq`.
- Bounded replay log: last 500 events.
- Subscriber queues with a max size of 1000; slow consumers are disconnected, then recover via replay or snapshot.
- Publishing never blocks; `put_nowait` with a drop-oldest policy for a dead subscriber.

### 7.3 Orchestrator

```python
# backend/app/sessions/orchestrator.py
class SessionOrchestrator:
    async def start(self, session: Session) -> None: ...   # spawns a task
    async def _run(self, session_id: str) -> None: ...
```

Order:
1. `search.started`; call `SearchService` with a 5s budget.
2. `search.completed`; emit `listing.found` per listing.
3. Fan out checks with a semaphore (`CHECK_CONCURRENCY=8`) and a global `asyncio.wait_for(14s)`.
4. Emit `check.started` before each check and `check.completed` as each finishes.
5. Score each listing as its checks complete; emit `listing.scored`.
6. Recommend; emit `recommendation.ready`.
7. Emit `investigation.complete`; close the bus; persist asynchronously.

Every stage transition updates the session and appends an audit event.

### 7.4 Search Service

```python
# backend/app/search/provider.py
class SearchProvider(Protocol):
    name: str
    async def search(self, spec: SearchSpec, limit: int) -> list[Listing]: ...

# backend/app/search/service.py
async def search(spec: SearchSpec, limit: int = 8) -> tuple[list[Listing], str]:
    """Return (listings, source). source is 'serpapi' or 'catalog'."""
```

- SerpAPI Google Shopping with a 5s timeout; reject results whose URL has no merchant domain or whose domain is `google.com`.
- On any failure, load the curated catalog and filter by query tokens and budget.
- Deduplicate by canonical URL; cap at 8; always include the hero and villain in demo mode.
- Derive `merchant_domain` from the canonical URL; lowercase; strip `www.`.

### 7.5 Trust Engine

```python
# backend/app/checks/base.py
@dataclass(frozen=True)
class CheckTarget:
    listing_id: str
    product_url: str
    merchant_domain: str
    merchant_name: str
    price_cents: int
    category: str | None

@dataclass
class CheckContext:
    http: httpx.AsyncClient
    cache: Cache
    allowlist: Allowlist
    config: Settings

class TrustCheck(Protocol):
    id: CheckId
    display_name: str
    timeout_s: float
    async def run(self, target: CheckTarget, ctx: CheckContext) -> TrustCheckResult: ...
```

```python
# backend/app/checks/registry.py
def get_checks() -> list[TrustCheck]: ...
```

| Check | Primary source | Fallback | Timeout |
|---|---|---|---|
| `domain_age` | RDAP `https://rdap.org/domain/{domain}` | `python-whois` in a thread | 4s |
| `ssl_cert` | `ssl` + `cryptography`, thread-offloaded | `skipped`/`unavailable` | 4s |
| `safe_browsing` | Google Safe Browsing v4 | Static denylist + `unavailable` | 3s |
| `reddit_sentiment` | Reddit public JSON | Fixture + `unavailable` | 4s |
| `page_flags` | `httpx` + BeautifulSoup | Fixture + `skipped` | 6s |

**Runner semantics:** each check is wrapped in `asyncio.wait_for`. On timeout or exception, emit `status=SKIPPED`, `source="timeout"` (or `"unavailable"`), severity 0, with a human-readable summary. A skipped check is not a pass; it reduces coverage.

### 7.6 Scoring Engine

The spec's scoring is canonical. Do not substitute an alternative model.

```python
# backend/app/trust/scoring.py
FAIL_DEDUCTION = 40
WARNING_DEDUCTION = 15
TRUSTED_THRESHOLD = 70
CAUTION_THRESHOLD = 40
MIN_COMPLETED_CHECKS = 3
COVERAGE_CAP = 69  # not payable

def score_investigation(
    checks: list[TrustCheckResult],
    *,
    allowlisted: bool,
    scoring_version: str = "1.0",
) -> ScoreResult:
    """Deterministic. See rules below."""
```

**Order of evaluation:**
1. Allowlist → `score=0`, `verdict=trusted`, `confidence=1.0`, all checks skipped with `source="allowlist"`.
2. Safe Browsing failed → `score=0`, `danger`, fatal flag `safe_browsing`.
3. Brand impersonation failed (if the optional check is present) → `score=5`, `danger`, fatal flag `brand_impersonation`.
4. Page flags failed AND domain age failed → `score=0`, `danger`, fatal flag `page_flags+domain_age`.
5. Domain age severity ≥ 0.85 → `score=5`, `danger`, fatal flag `domain_age`.
6. Otherwise start at 100: failed deducts `severity × 40`; warning deducts `severity × 15`; skipped deducts 0; clamp 0–100.
7. **Coverage rule:** if the number of non-skipped checks is < 3, `score = min(score, 69)` and the verdict cannot be `trusted`. This is "insufficient evidence is not trust."
8. Confidence = sum of completed check weights / sum of all weights. Equal weights for the five checks → `completed / 5`.
9. Verdict: `score ≥ 70` → trusted; `score ≥ 40` → caution; else danger.

`top_reason` is the largest single penalty's summary, or "All checks passed."

**Scoring version:** every investigation stores `scoring_version="1.0"`. Changing the rules requires a version bump and a golden-test update.

### 7.7 Recommendation Engine

```python
# backend/app/trust/recommendation.py
class Recommendation(BaseModel):
    recommended_listing_id: str | None
    median_trusted_cents: int | None
    savings_cents: int | None
    eligible_ids: list[str]
    reason: str
    no_trusted_option: bool

def recommend(pairs: list[tuple[Listing, ScoreResult]]) -> Recommendation:
    """Eligible = verdict trusted AND score >= 70 AND confidence >= 0.6.
    Primary = lowest price, tie-break higher score.
    Median is over eligible listings only."""
```

If no listing is eligible, return `no_trusted_option=True` with a reason. This is a feature, not an error: it is the on-screen proof of the hard rule.

### 7.8 Payability Guard

```python
# backend/app/payments/payability.py
@dataclass(frozen=True)
class MandateDraft:
    merchant_domain: str
    max_amount_cents: int
    currency: str = "USD"

class PayabilityCode(str, Enum):
    MERCHANT_NOT_TRUSTED = "MERCHANT_NOT_TRUSTED"
    SCORE_TOO_LOW = "SCORE_TOO_LOW"
    COVERAGE_TOO_LOW = "COVERAGE_TOO_LOW"
    MERCHANT_MISMATCH = "MERCHANT_MISMATCH"
    AMOUNT_EXCEEDS_CAP = "AMOUNT_EXCEEDS_CAP"
    MANDATE_EXPIRED = "MANDATE_EXPIRED"
    ALREADY_PAID = "ALREADY_PAID"
    INVESTIGATION_STALE = "INVESTIGATION_STALE"

class PayabilityError(Exception):
    code: PayabilityCode
    status_code: int = 409
    details: dict

def assert_payable(
    investigation: Investigation,
    listing: Listing,
    mandate: MandateDraft | Mandate,
    *,
    now: datetime,
) -> None: ...
```

Checks, in order:
1. Investigation exists; every check it contains is terminal (none in progress).
2. `investigation.created_at` is within 30 minutes.
3. `verdict == trusted`.
4. `score >= 70` (allowlisted investigations score 0 and are exempt).
5. Unless allowlisted: `confidence >= 0.6` and at least 3 completed checks.
6. `listing.merchant_domain == mandate.merchant_domain`.
7. `listing.price_cents <= mandate.max_amount_cents`.
8. Currency matches.
9. If `mandate` is a `Mandate`, it is unexpired and unconsumed; a `MandateDraft` is active by construction.
10. Checkout not already captured.

### 7.9 Mock VIC

```python
# backend/app/payments/mock_vic.py
async def issue_token(checkout_id: str, merchant_domain: str) -> IssuedToken:
    """Return raw token once; persist SHA-256(token) + last4 only."""

async def consume_token(token_id: str) -> None:
    """Atomic: status issued -> consumed. Raises if already consumed."""

async def authorize(amount_cents: int, token_id: str) -> Transaction:
    """Deterministic approval unless the passkey assertion was 'fail'.
    auth_code = 'MOCK' + 6 hex from sha256(token_id)."""
```

- The sandbox token is a fixed test value ending `4242`; `token_last4` is always `"4242"` in sandbox mode. It is published test data, never a real card.
- The raw token is never stored, logged, or returned after creation.
- `consume_token` uses a conditional update so a double-confirm cannot double-charge.
- `mode="sandbox"` and `processor="mock-vic"` are explicit in every response and the UI.

### 7.10 Receipt Service

```python
# backend/app/payments/receipts.py
def create_receipt(
    checkout: Checkout,
    transaction: Transaction,
    listing: Listing,
    investigation: Investigation,
) -> Receipt:
    """Deep-copy the investigation snapshot; compute share_id;
    HMAC-SHA256 over receipt_id|share_id|amount_cents|issued_at."""

def verify_receipt(receipt: Receipt, secret: str) -> bool: ...
```

The receipt lists `verified` and `unverified` checks so it never overclaims. `share_id` is 12-char base32 from `secrets.token_bytes`.

### 7.11 Repository

```python
# backend/app/services/repository.py
class Repository(Protocol):
    async def save_session(self, session: Session) -> None: ...
    async def save_listing(self, listing: Listing) -> None: ...
    async def save_investigation(self, inv: Investigation) -> None: ...
    async def get_investigation(self, investigation_id: str) -> Investigation | None: ...
    async def save_mandate(self, mandate: Mandate) -> None: ...
    async def save_checkout(self, checkout: Checkout) -> None: ...
    async def transition_checkout(self, checkout_id: str, from_stage: CheckoutStage,
                                  to_stage: CheckoutStage) -> bool: ...
    async def save_receipt(self, receipt: Receipt) -> None: ...
    async def get_receipt_by_share_id(self, share_id: str) -> Receipt | None: ...
    async def audit(self, event: AuditEvent) -> None: ...
```

Two adapters: `InMemoryRepository` (default in tests and when `MONGODB_URI` is empty) and `MongoRepository`. Writes in the request path are awaited only for payments; investigation persistence is fire-and-forget with error logging.

### 7.12 LLM Client

```python
# backend/app/services/llm.py
async def generate_questions(query: str) -> list[Question]: ...   # 2.5s timeout
async def narrate(recommendation: Recommendation) -> str: ...      # optional
async def explain_check(check: TrustCheckResult) -> str: ...       # lazy, on demand
```

- Exactly 2–3 calls per session on the happy path.
- Every call has a deterministic template fallback.
- Output is constrained to JSON with enums; invalid output is discarded.
- No check selection, no URL fetching, no score input.

---

## 8. Security, Privacy, and Trust

### 8.1 Threat Model

| Threat | Vector | Impact | Control |
|---|---|---|---|
| SSRF | Listing URL → page scraper | Internal network access | `validate_public_url`: https only, no IP literals, no non-standard ports, DNS resolution blocklist, redirect re-validation |
| Prompt injection | Scraped page or Reddit text | Manipulated LLM output | Structured extractors only; delimited untrusted data; no tool loop; schema-constrained output |
| XSS | Merchant/product strings | Script execution | React escaping; no `dangerouslySetInnerHTML`; CSP |
| Payment tampering | Client sends amount/merchant/score | Wrong charge | Client sends only IDs and cap; server re-derives |
| Double charge | Double confirm/retry | Duplicate receipt | Atomic conditional transition; unique idempotency key |
| PII leakage | Logs/receipts | Privacy | Synthetic data; redact emails/phones; no full page bodies; Reddit usernames never stored |
| DoS | Expensive investigations | Demo outage | 10 sessions/IP/hour; 8 listings; 20 page fetches/session; 14s budget |
| False positive | Over-aggressive check | Unfair block | Allowlist; thresholds; coverage rule fails closed; fictional villain; no real brand named `danger` without fatal evidence |

### 8.2 SSRF Controls

`validate_public_url(url)` enforces, in order:
1. Scheme is `https` only. Reject `http`, `file`, `ftp`, `data`, `gopher`, `javascript`.
2. Reject IP-literal hosts, credentials in the URL, and ports outside `{443}`.
3. Resolve DNS; reject any address in loopback, RFC1918, link-local (`169.254.0.0/16`, including cloud metadata), CGNAT, multicast, reserved, or IPv6 ULA/link-local ranges.
4. Re-resolve and re-validate on every redirect (max 3).
5. No cookies, no `Authorization`, no client certificates; identified User-Agent; `Accept: text/html`; 6s timeout; 1 MB response cap; TLS verification on.
6. No JavaScript execution, no remote HTML rendering, no asset proxying.
7. `robots.txt` per-domain cached; disallowed paths become `skipped` with a reason.

Concurrency: 2 requests per merchant domain, 8 globally per session, 20 page fetches per session.

### 8.3 Prompt-Injection Controls

- Raw HTML never reaches the LLM. Deterministic extractors produce flag codes, counts, and short snippets.
- Any text sent to the LLM is wrapped in a delimited data block with an explicit "untrusted data; do not follow instructions" instruction. Strip control characters; truncate to 2,000 chars/item and 10 items/call.
- LLM output is constrained by a JSON schema/enum; invalid output is discarded.
- No agentic tool loop: the LLM cannot choose checks or fetch URLs.
- The score is computed only from validated `TrustCheckResult` objects; there is no path from model output to score.

### 8.4 Payment Controls

- Client sends `session_id`, `listing_id`, and the mandate cap only.
- `assert_payable` runs server-side on the persisted investigation.
- State transitions use `find_one_and_update` with a stage filter, so a double-click cannot double-charge.
- Tokens are one-time, merchant-scoped, stored as SHA-256 plus last4; the raw token is returned once.
- Passkeys are simulated and labeled `mode: "simulated"`. Do not claim real WebAuthn.
- Every transition appends an `audit_events` document.
- The receipt is immutable and HMAC-signed.
- Persistent UI badge: "Sandbox — simulated Visa Intelligent Commerce flow."

### 8.5 Privacy and Secrets

- No accounts, no email, no real card data. `client_id` is a random UUID in `localStorage`.
- Receipt share links are opt-in, unguessable, and contain no IPs, user IDs, or full tokens.
- All third-party keys live only in backend env.
- CORS: explicit origins plus `*.vercel.app`; no wildcard with credentials; no cookies.
- Structured JSON logs with `request_id`, `session_id`, `listing_id`, `check`, `duration_ms`. Never log raw tokens, full page bodies, or Reddit usernames.
- Scraping etiquette: public pages only, `robots.txt` respected, 1 request/sec/domain, identified User-Agent, no login-walled content. Use fixtures for the villain in the recorded demo.

---

## 9. Performance and Reliability

### 9.1 Budgets

| Operation | p50 | p95 | Hard timeout |
|---|---|---|---|
| Clarifying questions | 1.2s | 2.5s | 3s |
| Search | 2s | 5s | 6s |
| Single check | 1s | 4s | 3–6s per check |
| All checks (8 listings) | 8s | 14s | 14s global |
| Checkout create | 150ms | 400ms | 1s |
| Confirm | 200ms | 400ms | 1s |

### 9.2 Caching

| Data | In-process | Mongo TTL |
|---|---|---|
| RDAP | 24h | 24h |
| SSL | 24h | 24h |
| Safe Browsing | 1h | 6h |
| Reddit | 1h | 24h |
| LLM questions | — | — |
| Catalog | startup | — |

### 9.3 Fallbacks

| Failure | Fallback |
|---|---|
| SerpAPI | Curated catalog + `search.completed.source="catalog"` |
| RDAP | `python-whois` in a thread; else `skipped` |
| SSL | `skipped`, `source="unavailable"` |
| Safe Browsing | Static denylist; `unavailable` if no key |
| Reddit | Fixture; `unavailable` on 403/429 |
| Page fetch | Fixture; `skipped` with reason |
| LLM | Template questions/explanations |
| MongoDB | In-memory repository; `db: unavailable` in health |
| Mock VIC | Always local; no external dependency |

**Circuit breaker:** after 3 consecutive failures of a provider, skip it for 60s and use the fallback.

### 9.4 Deployment Rule

`uvicorn app.main:app --workers 1 --proxy-headers`. Do not enable gzip globally. On Fly.io, run one always-on 256MB machine. On Render free, add a 5-minute uptime ping and warm the backend 20 minutes before recording.

---

## 10. Testing Strategy

### 10.1 Unit Tests (pytest)

| Area | Tests |
|---|---|
| Scoring | Allowlist; each fatal flag; thresholds 70/40; severity math; clamp; coverage cap at 69 |
| Recommendation | Eligible only; lowest price then highest score; median over trusted; no-trusted option |
| URL safety | https only; IP literals; private/loopback/link-local; redirect; credentials; ports |
| Each check | Pass/warn/fail/skip with mocked HTTP; timeout mapping |
| Payability | Every reason code returns 409; happy path |
| Mock VIC | Mandate cap; token hashed; atomic consume; decline; idempotency |
| Receipt | Snapshot immutability; signature verify; share ID uniqueness |
| PII redaction | Email, phone, card-like strings |

### 10.2 Integration Tests (pytest + httpx)

- Session create → answers → SSE order: `search.started → listing.found → check.started/completed → listing.scored → recommendation.ready → complete`.
- Reconnect with `Last-Event-ID` replays without duplicates.
- Snapshot endpoint returns the same state as the stream.
- Checkout for caution → 409 `MERCHANT_NOT_TRUSTED`.
- Checkout with <3 checks → 409 `COVERAGE_TOO_LOW`.
- Confirm twice → same receipt.
- Receipt unknown → 404.
- Mongo unavailable → request succeeds on the in-memory adapter.

### 10.3 Frontend Tests (Vitest + React Testing Library)

- Product card renders title, merchant, price.
- Trust badge colors by verdict.
- SSE hook appends checks, dedupes by `seq`, closes on completion.
- Checkout button disabled for non-trusted.
- Receipt renders summary.
- Purge removes `danger` cards.

### 10.4 E2E (Playwright, one happy path)

Discovery → results → checks stream → best pick → checkout → passkey → receipt → share link.

### 10.5 Golden Tests (no network)

1. Allowlisted domain → 0/trusted.
2. Safe Browsing hit → 0/danger.
3. 10-day domain + new cert + 3 scam reports + urgency flags → ≤31/danger.
4. 8-year domain, valid cert, clean page, no Reddit hits → ≥90/trusted.
5. Two checks timeout → score capped 69/caution/not payable.
6. Page flags failed with 4 high-severity flags → ≤30/danger.
7. Payability matrix: each of the eight reason codes → 409.

---

## 11. CI/CD and Deployment

### 11.1 GitHub Actions

```yaml
# .github/workflows/ci.yml
jobs:
  api:
    - ruff check
    - mypy app
    - pytest -q
  web:
    - npm ci
    - npm run lint
    - npm run typecheck
    - npm run test -- --run
    - npm run build
```

### 11.2 Deploy

| Component | Platform | Config |
|---|---|---|
| Frontend | Vercel | `VITE_API_BASE_URL`; rewrite `/r/*` → `index.html` |
| Backend | Fly.io (always-on 256MB) | `DEMO_MODE=1`, `GEMINI_API_KEY`, `SERPAPI_KEY`, `GOOGLE_SAFE_BROWSING_KEY`, `MONGODB_URI`, `RECEIPT_SIGNING_SECRET`, `ALLOWED_ORIGINS` |
| Database | MongoDB Atlas M0 | IP allowlist `0.0.0.0/0` for the hackathon |

Deploy both on Saturday at 1:15 PM, not Sunday morning. Put the URL in the Devpost draft.

---

## 12. Observability

- **Logs:** structured JSON with `timestamp`, `level`, `request_id`, `session_id`, `listing_id`, `check`, `stage`, `duration_ms`, `error_code`.
- **Metrics (in-process counters, exposed at `/api/metrics`):** sessions created, search source, check latency/failure by check ID, score distribution, checkout attempts/approved/blocked by reason.
- **Health:** `/api/health` returns 200 while alive; reports `db` and `demo_mode`.
- **Audit:** every stage transition, payment transition, and appeal appends to `audit_events`.
- **Alerts:** none for the hackathon; watch the Fly.io logs.

---

## 13. Repository Structure

```
sniff-visa/
├── README.md                      # setup, demo instructions, mock disclosure
├── ATTRIBUTION.md                 # "architecture inspiration: thenerd31/sniff; all code original"
├── docs/
│   ├── contracts.md               # frozen at 1:15 PM Saturday
│   ├── decisions.md               # the ten calls, one line each
│   ├── demo-script.md
│   ├── veylz-audit.md
│   └── qa-checklist.md
├── data/
│   ├── catalog.json               # 8 trusted + 1 villain across 5+ merchants
│   ├── allowlist.json             # 30–40 established retailer domains
│   └── fixtures/
│       ├── villain_page.html
│       ├── villain_rdap.json
│       └── villain_reddit.json
├── scripts/
│   ├── replay_offline.py          # full orchestration with OFFLINE=1
│   ├── smoke_sse.py               # SSE assertion
│   └── seed_cache.py
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── main.py
│   │   ├── core/{config.py,logging.py,errors.py,timeouts.py}
│   │   ├── api/{deps.py,routes_sessions.py,routes_events.py,
│   │   │        routes_checkout.py,routes_receipts.py,routes_health.py}
│   │   ├── domain/{models.py,enums.py}
│   │   ├── sessions/{store.py,orchestrator.py,events.py,questions.py}
│   │   ├── search/{provider.py,serpapi.py,catalog.py,service.py}
│   │   ├── checks/{base.py,registry.py,domain_age.py,ssl_cert.py,
│   │   │           safe_browsing.py,reddit_sentiment.py,page_flags.py}
│   │   ├── trust/{scoring.py,recommendation.py,allowlist.py}
│   │   ├── payments/{payability.py,mandates.py,mock_vic.py,receipts.py}
│   │   ├── services/{llm.py,repository.py,audit.py,ratelimit.py,url_safety.py}
│   │   └── db/{mongo.py,indexes.py}
│   └── tests/{unit/,integration/,golden/,fixtures/}
└── frontend/
    ├── package.json, vite.config.ts, tailwind.config.ts, vercel.json
    └── src/
        ├── main.tsx, App.tsx
        ├── lib/{api.ts,types.ts,sse.ts,format.ts}
        ├── store/sessionStore.ts
        ├── features/
        │   ├── discovery/DiscoveryFlow.tsx
        │   ├── results/{ResultsGrid,ProductCard,CheckRow,TrustBadge,BestPick,PurgeOverlay}.tsx
        │   ├── checkout/{CheckoutSheet,MandateCard,PasskeyDialog,ProcessingState}.tsx
        │   └── receipt/ReceiptPage.tsx
        └── components/ui/        # shadcn, unmodified unless necessary
```

**Ownership:** `backend/app/domain/models.py` and `frontend/src/lib/types.ts` are contract files. One person owns them; they freeze at 1:15 PM Saturday. Everyone else requests changes in the team channel.

---

## 14. Implementation Tasks

> Tasks are ordered by dependency. Each ends with an independently testable deliverable and a commit. Times assume one engineer; parallelize where the Interfaces block allows.

### Task 1: Scaffold, health endpoint, and contracts

**Files:**
- Create: `backend/app/main.py`, `backend/app/core/config.py`
- Create: `backend/tests/__init__.py`, `backend/tests/unit/__init__.py`, `backend/tests/integration/__init__.py`, `backend/tests/golden/__init__.py`
- Create: `backend/tests/integration/test_health.py`
- Create: `backend/requirements.txt`, `backend/.env.example`, `backend/pytest.ini`
- Create: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/src/main.tsx`, `frontend/src/App.tsx`
- Create: `.gitignore`, `docs/contracts.md`

**Interfaces:**
- Produces: `create_app() -> FastAPI`; `GET /api/health`; `Settings` with `demo_mode`, `offline`, `allowed_origins`, `mongodb_uri`, `gemini_api_key`, `serpapi_key`, `google_safe_browsing_key`, `receipt_signing_secret`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/integration/test_health.py
from fastapi.testclient import TestClient
from app.main import create_app

def test_health_returns_200_even_without_db():
    client = TestClient(create_app())
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] in {"ok", "degraded"}
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd backend && pytest tests/integration/test_health.py -v`  
Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `create_app()` and the health route**

FastAPI app, CORS from settings, router include, `app = create_app()`. Health returns 200 with `status`, `db`, `version`, `demo_mode`, `uptime_s`. `pytest.ini` sets `asyncio_mode = auto` and `pythonpath = .` so `from tests.integration...` and async tests work without decorators.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd backend && pytest tests/integration/test_health.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend frontend .gitignore docs/contracts.md
git commit -m "chore: scaffold api and web; add health endpoint"
```

---

### Task 2: Domain models, enums, IDs, money

**Files:**
- Create: `backend/app/domain/enums.py`, `backend/app/domain/models.py`
- Create: `backend/app/core/ids.py`
- Create: `backend/tests/unit/test_models.py`, `backend/tests/unit/test_ids.py`

**Interfaces:**
- Produces: `CheckId`, `TrustStatus`, `Verdict`, `SessionStage`, `CheckoutStage`, `Listing`, `TrustCheckResult`, `ScoreResult`, `Investigation`, `Session`, `Mandate`, `Checkout`, `Transaction`, `Receipt`; `new_id(prefix) -> str`; `listing_id(url) -> str`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/unit/test_models.py
import pytest
from pydantic import ValidationError
from app.domain.models import Listing, TrustCheckResult
from app.domain.enums import CheckId, TrustStatus

def test_listing_rejects_nonpositive_price():
    with pytest.raises(ValidationError):
        Listing(id="lst_1", title="x", price_cents=0, merchant_name="m",
                merchant_domain="d.com", image_url="", product_url="")

def test_check_severity_bounds():
    with pytest.raises(ValidationError):
        TrustCheckResult(id=CheckId.SSL, name="SSL", status=TrustStatus.FAILED,
                         severity=1.5, summary="x", source="live")
```

```python
# backend/tests/unit/test_ids.py
from app.core.ids import new_id, listing_id

def test_ids_are_prefixed():
    assert new_id("ses").startswith("ses_")

def test_listing_id_is_deterministic():
    assert listing_id("https://bestbuy.com/p/1") == listing_id("https://bestbuy.com/p/1")
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/unit/test_models.py tests/unit/test_ids.py -v`  
Expected: FAIL — modules missing.

- [ ] **Step 3: Implement the models and helpers**

Copy the models from §5. Use `Field(gt=0)` for cents and `Field(ge=0, le=1)` for severity/confidence. `new_id(prefix)` returns `prefix + "_" + secrets.token_urlsafe(12)`. `listing_id(url)` returns `"lst_" + hashlib.sha256(normalized_url.encode()).hexdigest()[:16]`.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/unit/test_models.py tests/unit/test_ids.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/domain backend/app/core/ids.py backend/tests/unit
git commit -m "feat: add domain models, enums, and id helpers"
```

---

### Task 3: Config, catalog, allowlist, fixtures

**Files:**
- Create: `backend/app/core/config.py` (extend from Task 1)
- Create: `backend/app/search/catalog.py`
- Create: `backend/app/trust/allowlist.py`
- Create: `data/catalog.json`, `data/allowlist.json`, `data/fixtures/villain_page.html`, `data/fixtures/villain_rdap.json`, `data/fixtures/villain_reddit.json`
- Create: `backend/tests/unit/test_catalog.py`

**Interfaces:**
- Produces: `load_catalog() -> list[Listing]`; `load_allowlist() -> Allowlist`; `Allowlist.matches(domain: str) -> bool`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/unit/test_catalog.py
from app.search.catalog import load_catalog
from app.trust.allowlist import load_allowlist

def test_catalog_has_hero_and_villain():
    listings = load_catalog()
    assert len(listings) >= 9
    domains = {l.merchant_domain for l in listings}
    assert "bestbuy.com" in domains
    assert any(d.endswith(".shop") for d in domains)

def test_allowlist_matches_subdomains_only_on_boundary():
    a = load_allowlist()
    assert a.matches("bestbuy.com")
    assert a.matches("www.bestbuy.com")
    assert not a.matches("bestbuy.com.evil.shop")
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/unit/test_catalog.py -v`  
Expected: FAIL — modules missing.

- [ ] **Step 3: Implement the loader, allowlist, and data**

`load_catalog()` resolves the repo root from `__file__`, reads `data/catalog.json`, and returns `Listing` objects. The catalog has 8 trusted listings across Amazon, Best Buy, Walmart, Target, and B&H, plus one fictional villain on `premium-audio-deals.shop` with a plausible price. The villain fixtures contain a 12-day RDAP record, a page with urgency copy, no return policy, and a crypto-only note, and three Reddit scam reports. `Allowlist.matches` normalizes to lowercase, strips `www.`, and matches exact host or a dot-boundary suffix.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/unit/test_catalog.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/config.py backend/app/search/catalog.py backend/app/trust/allowlist.py data backend/tests/unit/test_catalog.py
git commit -m "feat: add catalog, allowlist, and villain fixtures"
```

---

### Task 4: Search service with SerpAPI and catalog fallback

**Files:**
- Create: `backend/app/search/provider.py`, `backend/app/search/serpapi.py`, `backend/app/search/service.py`
- Create: `backend/tests/unit/test_search_service.py`

**Interfaces:**
- Consumes: `load_catalog()`, `SearchSpec`.
- Produces: `search(spec: SearchSpec, limit: int = 8) -> tuple[list[Listing], str]`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/unit/test_search_service.py
import pytest
from app.domain.models import SearchSpec
from app.search import service

@pytest.mark.asyncio
async def test_falls_back_when_provider_fails(monkeypatch):
    async def boom(spec, limit):
        raise RuntimeError("serpapi down")
    monkeypatch.setattr(service, "_provider_search", boom)
    listings, source = await service.search(SearchSpec(query="headphones"))
    assert source == "catalog"
    assert len(listings) >= 1

@pytest.mark.asyncio
async def test_rejects_results_without_merchant_domain(monkeypatch):
    async def fake(spec, limit):
        return [dict(id="lst_x", title="x", price_cents=100, merchant_name="m",
                     merchant_domain="", image_url="", product_url="https://google.com/x")]
    monkeypatch.setattr(service, "_provider_search", fake)
    listings, _ = await service.search(SearchSpec(query="headphones"))
    assert all(l.merchant_domain for l in listings)
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/unit/test_search_service.py -v`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the provider, SerpAPI adapter, and service**

`_provider_search` calls SerpAPI Google Shopping with a 5s timeout. `search` catches any exception, loads the catalog, filters by query tokens and `budget_max_cents`, dedupes by canonical URL, caps at `limit`, and returns `(listings, source)`. Reject results with an empty or `google.com` domain.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/unit/test_search_service.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/search backend/tests/unit/test_search_service.py
git commit -m "feat: add search service with serpapi and catalog fallback"
```

---

### Task 5: Session registry and session routes

**Files:**
- Create: `backend/app/sessions/store.py`, `backend/app/sessions/questions.py`
- Create: `backend/app/api/routes_sessions.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/integration/test_sessions_api.py`

**Interfaces:**
- Consumes: `new_id`, models, `Settings`.
- Produces: `SessionRegistry`; `POST /api/sessions`; `POST /api/sessions/{id}/answers`; `GET /api/sessions/{id}`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/integration/test_sessions_api.py
from fastapi.testclient import TestClient
from app.main import create_app

def test_create_session_returns_questions():
    client = TestClient(create_app())
    r = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"})
    assert r.status_code == 201
    body = r.json()
    assert body["stage"] == "clarifying"
    assert 2 <= len(body["questions"]) <= 3

def test_answers_advance_stage():
    client = TestClient(create_app())
    s = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    r = client.post(f"/api/sessions/{s['session_id']}/answers",
                    json={"answers": [{"question_id": "q_budget", "option_id": "300"}]})
    assert r.status_code == 202
    assert r.json()["stage"] == "searching"
    assert r.json()["events_url"].endswith("/events")
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/integration/test_sessions_api.py -v`  
Expected: FAIL — 404.

- [ ] **Step 3: Implement the registry, question generator, and routes**

`SessionRegistry` is an in-memory dict with `create/get/update/sweep`. `create(client_id, query)` sets `search_spec=SearchSpec(query=query)` provisionally plus `created_at`, `updated_at`, and `expires_at=now+2h`; the answers route replaces `search_spec` once the questions are answered. `questions.py` has category templates and an optional LLM call with a 2.5s timeout. The create route returns 201 with 2–3 questions. The answers route validates question IDs, builds `SearchSpec`, sets stage `searching`, and returns 202 with `events_url`. The snapshot route returns the session plus listings, checks, scores, recommendation, and `last_seq`.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/integration/test_sessions_api.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/sessions backend/app/api/routes_sessions.py backend/app/main.py backend/tests/integration/test_sessions_api.py
git commit -m "feat: add session registry and routes"
```

---

### Task 6: Event bus and SSE endpoint

**Files:**
- Create: `backend/app/sessions/events.py`, `backend/app/api/routes_events.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/integration/test_events_api.py`

**Interfaces:**
- Produces: `Event`, `EventBus.publish/subscribe/close`; `GET /api/sessions/{id}/events`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/integration/test_events_api.py
from fastapi.testclient import TestClient
from app.main import create_app

def test_stream_publishes_synthetic_events(monkeypatch):
    client = TestClient(create_app())
    s = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    sid = s["session_id"]
    from app.sessions.events import bus
    bus.publish(sid, "search.started", {"query": "headphones"})
    bus.publish(sid, "investigation.complete", {"stats": {}})
    bus.close(sid)
    with client.stream("GET", f"/api/sessions/{sid}/events") as r:
        body = "".join(r.iter_text())
    assert "event: search.started" in body
    assert "event: investigation.complete" in body
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd backend && pytest tests/integration/test_events_api.py -v`  
Expected: FAIL — 404 or import error.

- [ ] **Step 3: Implement the bus and SSE route**

Per-session `seq`, bounded deque of 500, subscriber `asyncio.Queue`s, `subscribe(since_seq)` replays then follows, `close` ends subscribers. The route uses `EventSourceResponse` with `ping=15`, honors `Last-Event-ID`, and sets `X-Accel-Buffering: no`. Expose the bus and session registry as module-level singletons (`events.bus`, `store.registry`) and import them in the routes, so tests and the app share one instance.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd backend && pytest tests/integration/test_events_api.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/sessions/events.py backend/app/api/routes_events.py backend/app/main.py backend/tests/integration/test_events_api.py
git commit -m "feat: add event bus and sse endpoint"
```

---

### Task 7: Orchestrator skeleton — search to listings to complete

**Files:**
- Create: `backend/app/sessions/orchestrator.py`
- Modify: `backend/app/api/routes_sessions.py`
- Create: `backend/tests/integration/test_orchestrator.py`

**Interfaces:**
- Consumes: `SessionRegistry`, `EventBus`, `search`.
- Produces: `SessionOrchestrator.start(session)`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/integration/test_orchestrator.py
import pytest
from app.sessions.orchestrator import SessionOrchestrator
from app.sessions.store import SessionRegistry
from app.sessions.events import EventBus
from app.domain.models import SearchSpec

@pytest.mark.asyncio
async def test_orchestrator_emits_listings_and_completes(monkeypatch):
    store, bus = SessionRegistry(), EventBus()
    orch = SessionOrchestrator(store, bus, checks=[])
    session = store.create("c1", "headphones")
    session.search_spec = SearchSpec(query="headphones")
    await orch._run(session.id)
    events = [e async for e in bus.subscribe(session.id)]
    types = [e.type for e in events]
    assert "search.started" in types
    assert "listing.found" in types
    assert types[-1] == "investigation.complete"
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd backend && pytest tests/integration/test_orchestrator.py -v`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the skeleton**

`start` spawns `asyncio.create_task(self._run(id))`. `_run` emits `search.started`, calls `search`, emits `search.completed` and `listing.found` per listing, then `investigation.complete` and `bus.close`. When `checks` is non-empty, fan out and score (Task 16 wires the rest).

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd backend && pytest tests/integration/test_orchestrator.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/sessions/orchestrator.py backend/app/api/routes_sessions.py backend/tests/integration/test_orchestrator.py
git commit -m "feat: add orchestrator skeleton"
```

---

### Task 8: Check protocol and parallel runner with coverage

**Files:**
- Create: `backend/app/checks/base.py`, `backend/app/checks/registry.py`, `backend/app/checks/runner.py`
- Create: `backend/tests/unit/test_check_runner.py`

**Interfaces:**
- Produces: `CheckTarget`, `CheckContext`, `TrustCheck` protocol; `run_checks(target, checks, ctx, timeout_s) -> AsyncIterator[TrustCheckResult]`; `get_checks()`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/unit/test_check_runner.py
import asyncio, pytest
from app.checks.base import CheckTarget
from app.checks.runner import run_checks
from app.domain.models import TrustCheckResult
from app.domain.enums import CheckId, TrustStatus

class Good:
    id, display_name, timeout_s = CheckId.SSL, "SSL", 1.0
    async def run(self, target, ctx):
        return TrustCheckResult(id=self.id, name=self.display_name,
                                status=TrustStatus.PASSED, severity=0,
                                summary="ok", source="live")

class Bad:
    id, display_name, timeout_s = CheckId.REDDIT, "Reddit", 0.05
    async def run(self, target, ctx):
        await asyncio.sleep(1)
        raise RuntimeError("slow")

@pytest.mark.asyncio
async def test_runner_skips_timeouts_and_keeps_good_checks():
    target = CheckTarget(listing_id="lst_1", product_url="https://d.com/p",
                         merchant_domain="d.com", merchant_name="m",
                         price_cents=100, category=None)
    results = [r async for r in run_checks(target, [Good(), Bad()], ctx=None, timeout_s=1.0)]
    assert {r.id for r in results} == {CheckId.SSL, CheckId.REDDIT}
    reddit = next(r for r in results if r.id == CheckId.REDDIT)
    assert reddit.status == TrustStatus.SKIPPED
    assert reddit.source == "timeout"
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd backend && pytest tests/unit/test_check_runner.py -v`  
Expected: FAIL — modules missing.

- [ ] **Step 3: Implement the protocol and runner**

Use `asyncio.create_task` per check, `asyncio.wait_for` with the check's own timeout capped by the global timeout, and `asyncio.as_completed` to yield. On exception or timeout, yield a `SKIPPED` result with `source="timeout"` or `"unavailable"` and a human-readable summary. `get_checks()` returns the five check instances.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd backend && pytest tests/unit/test_check_runner.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/checks backend/tests/unit/test_check_runner.py
git commit -m "feat: add check protocol and parallel runner"
```

---

### Task 9: Domain age check — RDAP primary, WHOIS fallback

**Files:**
- Create: `backend/app/checks/domain_age.py`
- Create: `backend/tests/unit/test_domain_age.py`

**Interfaces:**
- Produces: `DomainAgeCheck.run(target, ctx) -> TrustCheckResult` with evidence `age_days`, `registrar`, `source_of_truth`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/unit/test_domain_age.py
import pytest
from app.checks.base import CheckTarget
from app.checks.domain_age import DomainAgeCheck
from app.domain.enums import TrustStatus

def target(domain="newstore.shop"):
    return CheckTarget("lst_1", "https://newstore.shop/p", domain, "m", 100, None)

@pytest.mark.asyncio
async def test_young_domain_fails(monkeypatch):
    async def fake_rdap(domain):
        return {"age_days": 12, "registrar": "Namecheap"}
    monkeypatch.setattr("app.checks.domain_age.fetch_rdap", fake_rdap)
    r = await DomainAgeCheck().run(target(), ctx=None)
    assert r.status == TrustStatus.FAILED
    assert r.severity >= 0.9

@pytest.mark.asyncio
async def test_old_domain_passes(monkeypatch):
    async def fake_rdap(domain):
        return {"age_days": 2000, "registrar": "MarkMonitor"}
    monkeypatch.setattr("app.checks.domain_age.fetch_rdap", fake_rdap)
    r = await DomainAgeCheck().run(target("bestbuy.com"), ctx=None)
    assert r.status == TrustStatus.PASSED
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/unit/test_domain_age.py -v`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the check**

`fetch_rdap(domain)` GETs `https://rdap.org/domain/{domain}` with a 4s timeout and parses `events` for the registration date. If RDAP fails, fall back to `python-whois` via `asyncio.to_thread`. Age < 30 days → `FAILED` 0.95; < 90 days → `WARNING` 0.6; else `PASSED`. No date → `SKIPPED` with `source="unavailable"`.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/unit/test_domain_age.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/checks/domain_age.py backend/tests/unit/test_domain_age.py
git commit -m "feat: add domain age check with rdap"
```

---

### Task 10: SSL certificate check

**Files:**
- Create: `backend/app/checks/ssl_cert.py`
- Create: `backend/tests/unit/test_ssl_cert.py`

**Interfaces:**
- Produces: `SslCertCheck.run(target, ctx) -> TrustCheckResult`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/unit/test_ssl_cert.py
import pytest
from app.checks.base import CheckTarget
from app.checks.ssl_cert import SslCertCheck
from app.domain.enums import TrustStatus

def target(domain="bestbuy.com"):
    return CheckTarget("lst_1", f"https://{domain}/p", domain, "m", 100, None)

@pytest.mark.asyncio
async def test_free_cert_is_warning(monkeypatch):
    async def fake(domain):
        return {"issuer": "Let's Encrypt", "valid": True, "hostname_match": True}
    monkeypatch.setattr("app.checks.ssl_cert.inspect_cert", fake)
    r = await SslCertCheck().run(target("newstore.shop"), ctx=None)
    assert r.status == TrustStatus.WARNING

@pytest.mark.asyncio
async def test_invalid_cert_fails(monkeypatch):
    async def fake(domain):
        return {"issuer": "X", "valid": False, "hostname_match": False}
    monkeypatch.setattr("app.checks.ssl_cert.inspect_cert", fake)
    r = await SslCertCheck().run(target(), ctx=None)
    assert r.status == TrustStatus.FAILED
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd backend && pytest tests/unit/test_ssl_cert.py -v`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the check**

`inspect_cert` runs in a thread: `ssl.create_default_context()`, `socket.create_connection((domain, 443), timeout=4)`, `getpeercert()`, parse issuer and validity. Invalid/expired/mismatch → `FAILED` 0.8; free issuer (`Let's Encrypt`, `ZeroSSL`, `BuyPass`, `Cloudflare`) → `WARNING` 0.4; else `PASSED`. Any connection error → `SKIPPED` `source="unavailable"`.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd backend && pytest tests/unit/test_ssl_cert.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/checks/ssl_cert.py backend/tests/unit/test_ssl_cert.py
git commit -m "feat: add ssl certificate check"
```

---

### Task 11: Safe Browsing check

**Files:**
- Create: `backend/app/checks/safe_browsing.py`
- Create: `backend/tests/unit/test_safe_browsing.py`

**Interfaces:**
- Produces: `SafeBrowsingCheck.run(target, ctx) -> TrustCheckResult`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/unit/test_safe_browsing.py
import pytest
from app.checks.base import CheckTarget
from app.checks.safe_browsing import SafeBrowsingCheck
from app.domain.enums import TrustStatus

def target(url="https://scam.example/p"):
    return CheckTarget("lst_1", url, "scam.example", "m", 100, None)

@pytest.mark.asyncio
async def test_threat_match_fails(monkeypatch):
    async def fake(url):
        return ["MALWARE"]
    monkeypatch.setattr("app.checks.safe_browsing.lookup", fake)
    r = await SafeBrowsingCheck().run(target(), ctx=None)
    assert r.status == TrustStatus.FAILED
    assert r.severity == 1.0

@pytest.mark.asyncio
async def test_clean_passes(monkeypatch):
    async def fake(url):
        return []
    monkeypatch.setattr("app.checks.safe_browsing.lookup", fake)
    r = await SafeBrowsingCheck().run(target("https://bestbuy.com/p"), ctx=None)
    assert r.status == TrustStatus.PASSED
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/unit/test_safe_browsing.py -v`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the check**

`lookup(url)` POSTs to `https://safebrowsing.googleapis.com/v4/threatMatches:find` with the API key, 3s timeout. Return threat types. A hit → `FAILED` 1.0. No key → check the static denylist; if absent, `PASSED` with `source="unavailable"` and a summary that says the database was not configured. Error → `SKIPPED` `source="unavailable"`.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/unit/test_safe_browsing.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/checks/safe_browsing.py backend/tests/unit/test_safe_browsing.py
git commit -m "feat: add safe browsing check"
```

---

### Task 12: Reddit sentiment check

**Files:**
- Create: `backend/app/checks/reddit_sentiment.py`
- Create: `backend/tests/unit/test_reddit_sentiment.py`

**Interfaces:**
- Produces: `RedditSentimentCheck.run(target, ctx) -> TrustCheckResult`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/unit/test_reddit_sentiment.py
import pytest
from app.checks.base import CheckTarget
from app.checks.reddit_sentiment import RedditSentimentCheck
from app.domain.enums import TrustStatus

def target(domain="scam.shop"):
    return CheckTarget("lst_1", f"https://{domain}/p", domain, "m", 100, None)

@pytest.mark.asyncio
async def test_scam_mentions_warn(monkeypatch):
    async def fake(domain):
        return [{"title": "scam", "permalink": "/r/Scams/1"},
                {"title": "fraud", "permalink": "/r/Scams/2"}]
    monkeypatch.setattr("app.checks.reddit_sentiment.search", fake)
    r = await RedditSentimentCheck().run(target(), ctx=None)
    assert r.status == TrustStatus.WARNING

@pytest.mark.asyncio
async def test_no_mentions_passes(monkeypatch):
    async def fake(domain):
        return []
    monkeypatch.setattr("app.checks.reddit_sentiment.search", fake)
    r = await RedditSentimentCheck().run(target("bestbuy.com"), ctx=None)
    assert r.status == TrustStatus.PASSED
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd backend && pytest tests/unit/test_reddit_sentiment.py -v`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the check**

`search(domain)` GETs `https://www.reddit.com/search.json?q={domain}+scam&limit=10` with an identified User-Agent and a 4s timeout. Store permalink and title only, never usernames. Classify with keywords (`scam`, `fraud`, `stole`, `never arrived`). 1–2 hits → `WARNING` 0.5; 3+ → `FAILED` 0.8; none → `PASSED`. Error/403/429 → `SKIPPED` `source="unavailable"`.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd backend && pytest tests/unit/test_reddit_sentiment.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/checks/reddit_sentiment.py backend/tests/unit/test_reddit_sentiment.py
git commit -m "feat: add reddit sentiment check"
```

---

### Task 13: URL safety and page flags check

**Files:**
- Create: `backend/app/services/url_safety.py`
- Create: `backend/app/checks/page_flags.py`
- Create: `backend/tests/unit/test_url_safety.py`, `backend/tests/unit/test_page_flags.py`
- Create: `backend/tests/fixtures/scam_page.html`

**Interfaces:**
- Produces: `validate_public_url(url: str) -> str`; `PageFlagsCheck.run(target, ctx) -> TrustCheckResult`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/unit/test_url_safety.py
import pytest
from app.services.url_safety import validate_public_url

@pytest.mark.parametrize("url", [
    "http://127.0.0.1/x", "https://localhost/x", "http://169.254.169.254/latest",
    "http://10.0.0.1/x", "file:///etc/passwd", "ftp://example.com/x",
    "https://user:pass@example.com/x", "https://example.com:8443/x",
])
def test_rejects_unsafe_urls(url):
    with pytest.raises(ValueError):
        validate_public_url(url)

def test_accepts_https():
    assert validate_public_url("https://bestbuy.com/p/1").startswith("https://")
```

```python
# backend/tests/unit/test_page_flags.py
import pytest
from app.checks.base import CheckTarget
from app.checks.page_flags import PageFlagsCheck
from app.domain.enums import TrustStatus

def target():
    return CheckTarget("lst_1", "https://scam.shop/p/1", "scam.shop", "m", 100, None)

@pytest.mark.asyncio
async def test_urgency_and_missing_policy_fail(monkeypatch):
    html = open("tests/fixtures/scam_page.html").read()
    async def fake(url, ctx):
        return html
    monkeypatch.setattr("app.checks.page_flags.fetch_html", fake)
    r = await PageFlagsCheck().run(target(), ctx=None)
    assert r.status in {TrustStatus.WARNING, TrustStatus.FAILED}
    assert r.severity >= 0.4
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/unit/test_url_safety.py tests/unit/test_page_flags.py -v`  
Expected: FAIL — modules missing.

- [ ] **Step 3: Implement URL safety and the page flags check**

`validate_public_url`: https only; reject credentials, IP literals, non-443 ports, length > 2048; resolve DNS and reject private/loopback/link-local/CGNAT/multicast/reserved/IPv6 ULA. `fetch_html`: `httpx.AsyncClient(follow_redirects=True, timeout=6)`, re-validate every redirect, 1 MB cap, no cookies/auth, identified User-Agent. `PageFlagsCheck`: BeautifulSoup flags for urgency phrases, missing return/refund policy, no contact page, crypto-only/wire-transfer payment text, fake countdown scripts, missing HTTPS. 1 flag → `WARNING` 0.4; 2+ → `FAILED` 0.7; critical (no HTTPS or crypto-only) → `FAILED` 0.85. Fetch failure → `SKIPPED` with a reason.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/unit/test_url_safety.py tests/unit/test_page_flags.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/url_safety.py backend/app/checks/page_flags.py backend/tests
git commit -m "feat: add ssrf-safe page flags check"
```

---

### Task 14: Scoring engine with coverage rule

**Files:**
- Create: `backend/app/trust/scoring.py`
- Create: `backend/tests/unit/test_scoring.py`, `backend/tests/golden/test_scoring_golden.py`

**Interfaces:**
- Consumes: `TrustCheckResult`, `Verdict`.
- Produces: `score_investigation(checks, *, allowlisted, scoring_version="1.0") -> ScoreResult`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/unit/test_scoring.py
from app.domain.models import TrustCheckResult
from app.domain.enums import CheckId, TrustStatus, Verdict
from app.trust.scoring import score_investigation

def check(id, status, severity, source="live"):
    return TrustCheckResult(id=id, name=id.value, status=status,
                            severity=severity, summary="x", source=source)

def test_allowlist_wins():
    r = score_investigation([], allowlisted=True)
    assert (r.score, r.verdict, r.confidence) == (0, Verdict.TRUSTED, 1.0)

def test_safe_browsing_fatal():
    r = score_investigation([check(CheckId.SAFE_BROWSING, TrustStatus.FAILED, 1.0)],
                            allowlisted=False)
    assert (r.score, r.verdict) == (0, Verdict.DANGER)

def test_warning_math():
    checks = [
        check(CheckId.DOMAIN_AGE, TrustStatus.WARNING, 0.6),
        check(CheckId.SSL, TrustStatus.PASSED, 0),
        check(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0),
    ]
    r = score_investigation(checks, allowlisted=False)
    assert r.score == 91

def test_coverage_caps_at_caution():
    checks = [check(CheckId.SSL, TrustStatus.PASSED, 0)]
    checks += [check(CheckId.REDDIT, TrustStatus.SKIPPED, 0, "timeout"),
               check(CheckId.PAGE_FLAGS, TrustStatus.SKIPPED, 0, "timeout"),
               check(CheckId.DOMAIN_AGE, TrustStatus.SKIPPED, 0, "timeout"),
               check(CheckId.SAFE_BROWSING, TrustStatus.SKIPPED, 0, "timeout")]
    r = score_investigation(checks, allowlisted=False)
    assert r.score == 69
    assert r.verdict == Verdict.CAUTION
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/unit/test_scoring.py -v`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the scoring engine**

Copy the constants from §7.6. Implement the ordered evaluation exactly. Deduplicate by `CheckId`, keeping the highest severity. Compute `confidence = completed / 5`. `top_reason` = the largest penalty's summary, or "All checks passed."

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/unit/test_scoring.py -v`  
Expected: PASS.

- [ ] **Step 5: Add the golden test**

```python
# backend/tests/golden/test_scoring_golden.py
from app.domain.models import TrustCheckResult
from app.domain.enums import CheckId, TrustStatus, Verdict
from app.trust.scoring import score_investigation

def result(id, status, severity, source="live"):
    return TrustCheckResult(id=id, name=id.value, status=status,
                            severity=severity, summary="x", source=source)

def villain():
    return [
        result(CheckId.DOMAIN_AGE, TrustStatus.FAILED, 0.95),
        result(CheckId.SSL, TrustStatus.WARNING, 0.4),
        result(CheckId.SAFE_BROWSING, TrustStatus.PASSED, 0.0),
        result(CheckId.REDDIT, TrustStatus.FAILED, 0.8),
        result(CheckId.PAGE_FLAGS, TrustStatus.FAILED, 0.85),
    ]

def test_villain_is_danger():
    r = score_investigation(villain(), allowlisted=False)
    assert r.verdict == Verdict.DANGER
    assert r.score <= 31
```

Run: `cd backend && pytest tests/golden/test_scoring_golden.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/trust/scoring.py backend/tests/unit/test_scoring.py backend/tests/golden
git commit -m "feat: add deterministic scoring engine with coverage rule"
```

---

### Task 15: Recommendation engine

**Files:**
- Create: `backend/app/trust/recommendation.py`
- Create: `backend/tests/unit/test_recommendation.py`

**Interfaces:**
- Produces: `Recommendation`; `recommend(pairs) -> Recommendation`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/unit/test_recommendation.py
from app.domain.models import Listing, ScoreResult
from app.domain.enums import Verdict
from app.trust.recommendation import recommend

def listing(id, cents):
    return Listing(id=id, title="x", price_cents=cents, merchant_name="m",
                   merchant_domain="d.com", image_url="", product_url="")

def score(verdict, n=90, confidence=0.9):
    return ScoreResult(score=n, verdict=verdict, confidence=confidence,
                       top_reason="x", scoring_version="1.0")

def test_cheapest_trusted_wins():
    pairs = [(listing("a", 12000), score(Verdict.TRUSTED, 95)),
             (listing("b", 10000), score(Verdict.TRUSTED, 90)),
             (listing("c", 8000), score(Verdict.DANGER, 5))]
    r = recommend(pairs)
    assert r.recommended_listing_id == "b"
    assert r.savings_cents == 1000  # median trusted 11000 - 10000

def test_no_trusted_option():
    pairs = [(listing("a", 10000), score(Verdict.CAUTION, 50))]
    r = recommend(pairs)
    assert r.recommended_listing_id is None
    assert r.no_trusted_option is True
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/unit/test_recommendation.py -v`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement `recommend`**

Eligible = `verdict == trusted` AND `score >= 70` AND `confidence >= 0.6`. Sort by price ascending, then score descending. Median over eligible listings; savings = median − best price (None if ≤ 0). If empty, `no_trusted_option=True` with a reason naming the best near-miss.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/unit/test_recommendation.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/trust/recommendation.py backend/tests/unit/test_recommendation.py
git commit -m "feat: add cheapest-trusted recommendation"
```

---

### Task 16: Wire checks, scoring, and recommendation into the orchestrator

**Files:**
- Modify: `backend/app/sessions/orchestrator.py`
- Create: `backend/tests/integration/test_full_investigation.py`

**Interfaces:**
- Consumes: `get_checks`, `run_checks`, `score_investigation`, `recommend`.
- Produces: stream order `listing.found → check.started/completed → listing.scored → recommendation.ready → investigation.complete`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/integration/test_full_investigation.py
import pytest
from app.sessions.orchestrator import SessionOrchestrator
from app.sessions.store import SessionRegistry
from app.sessions.events import EventBus
from app.domain.models import SearchSpec, TrustCheckResult
from app.domain.enums import CheckId, TrustStatus

class FakeCheck:
    timeout_s = 1.0
    def __init__(self, id): self.id, self.display_name = id, id.value
    async def run(self, target, ctx):
        return TrustCheckResult(id=self.id, name=self.display_name,
                                status=TrustStatus.PASSED, severity=0,
                                summary="ok", source="live")

@pytest.mark.asyncio
async def test_full_investigation_emits_score_and_recommendation():
    store, bus = SessionRegistry(), EventBus()
    checks = [FakeCheck(i) for i in CheckId]
    orch = SessionOrchestrator(store, bus, checks=checks)
    s = store.create("c1", "headphones")
    s.search_spec = SearchSpec(query="headphones")
    await orch._run(s.id)
    events = [e async for e in bus.subscribe(s.id)]
    types = [e.type for e in events]
    assert "listing.scored" in types
    assert "recommendation.ready" in types
    assert types[-1] == "investigation.complete"
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd backend && pytest tests/integration/test_full_investigation.py -v`  
Expected: FAIL — no `listing.scored`.

- [ ] **Step 3: Implement the fan-out and scoring**

For each listing, spawn the five checks under a semaphore. Emit `check.started` before each and `check.completed` as each finishes. When a listing's checks are terminal, call `score_investigation`; store the `Investigation`; emit `listing.scored`. After all listings, call `recommend`; set the session's `recommended_listing_id`; emit `recommendation.ready`. Finally emit `investigation.complete` with stats and close the bus.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd backend && pytest tests/integration/test_full_investigation.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/sessions/orchestrator.py backend/tests/integration/test_full_investigation.py
git commit -m "feat: wire checks, scoring, and recommendation into orchestrator"
```

---

### Task 17: Frontend shell, types, and API client

**Files:**
- Create: `frontend/src/lib/types.ts`, `frontend/src/lib/api.ts`, `frontend/src/store/sessionStore.ts`
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/App.test.tsx`

**Interfaces:**
- Produces: TS types mirroring §5; `createSession`, `submitAnswers`, `getSnapshot`, `createCheckout`, `confirmCheckout`, `getReceipt`.

- [ ] **Step 1: Write the failing test**

```tsx
// frontend/src/App.test.tsx
import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders the app shell", () => {
  render(<App />);
  expect(screen.getByText(/sniff/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd frontend && npm test -- --run`  
Expected: FAIL — no test setup or component.

- [ ] **Step 3: Implement the types, client, store, and shell**

Mirror the Pydantic models in `types.ts` (cents as `number`). `api.ts` uses `VITE_API_BASE_URL`. `sessionStore.ts` holds `sessionId`, `stage`, `listings`, `checks`, `scores`, `recommendation`, `checkout`, `receipt`. Render a minimal shell with the product name and a discovery placeholder.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd frontend && npm test -- --run`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src
git commit -m "feat: add frontend shell, types, and api client"
```

---

### Task 18: Discovery flow

**Files:**
- Create: `frontend/src/features/discovery/DiscoveryFlow.tsx`, `DiscoveryFlow.test.tsx`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: `createSession`, `submitAnswers`.
- Produces: `<DiscoveryFlow onStarted={(sessionId) => ...} />`.

- [ ] **Step 1: Write the failing test**

```tsx
// frontend/src/features/discovery/DiscoveryFlow.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { DiscoveryFlow } from "./DiscoveryFlow";

test("renders questions and submits", async () => {
  render(<DiscoveryFlow onStarted={() => {}} />);
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i),
                    { target: { value: "headphones" } });
  fireEvent.click(screen.getByRole("button", { name: /find products/i }));
  expect(await screen.findByText(/what's your ceiling/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd frontend && npm test -- --run`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the flow**

Three states: query input → 2–3 questions with single-select pills and a free-text fallback → submitting. On submit, call `submitAnswers`, which returns `events_url`; pass `sessionId` up. Show a skeleton while the orchestrator starts.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd frontend && npm test -- --run`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/discovery frontend/src/App.tsx
git commit -m "feat: add guided discovery flow"
```

---

### Task 19: Results grid, product cards, trust badges, check rows

**Files:**
- Create: `frontend/src/features/results/ResultsGrid.tsx`, `ProductCard.tsx`, `TrustBadge.tsx`, `CheckRow.tsx`
- Create: `frontend/src/features/results/ResultsGrid.test.tsx`

**Interfaces:**
- Consumes: `Listing`, `TrustCheckResult`, `ScoreResult`.
- Produces: `<ResultsGrid />`, `<ProductCard />`, `<TrustBadge score verdict />`, `<CheckRow check />`.

- [ ] **Step 1: Write the failing test**

```tsx
// frontend/src/features/results/ResultsGrid.test.tsx
import { render, screen } from "@testing-library/react";
import { ResultsGrid } from "./ResultsGrid";

test("renders title, merchant, and formatted price", () => {
  render(<ResultsGrid listings={[{
    id: "lst_1", title: "Sony XM5", price_cents: 24900, currency: "USD",
    merchant_name: "Best Buy", merchant_domain: "bestbuy.com",
    image_url: "", product_url: "", source: "catalog",
  }]} checks={{}} scores={{}} />);
  expect(screen.getByText("Sony XM5")).toBeInTheDocument();
  expect(screen.getByText("Best Buy")).toBeInTheDocument();
  expect(screen.getByText(/\$249\.00/)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd frontend && npm test -- --run`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the components**

`ResultsGrid` maps listings to cards and keeps the best pick first. `ProductCard` shows the image with a gradient fallback, title, merchant, formatted price, `TrustBadge`, and a `CheckRow` list that renders skeleton rows for started checks. `TrustBadge`: green `trusted`, amber `caution`, red `danger`, gray while pending.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd frontend && npm test -- --run`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/results
git commit -m "feat: add results grid and trust ui"
```

---

### Task 20: Multiplexed SSE hook with snapshot fallback

**Files:**
- Create: `frontend/src/lib/sse.ts`
- Create: `frontend/src/features/results/useSessionStream.ts`, `useSessionStream.test.tsx`

**Interfaces:**
- Consumes: `EventSource`, `getSnapshot`.
- Produces: `useSessionStream(sessionId)` returning `{ lastSeq, onEvent, applied }`; the store applies events idempotently.

- [ ] **Step 1: Write the failing test**

```tsx
// frontend/src/features/results/useSessionStream.test.tsx
import { renderHook, act } from "@testing-library/react";
import { useSessionStream } from "./useSessionStream";

test("applies events and dedupes by seq", () => {
  const { result } = renderHook(() => useSessionStream(null));
  act(() => result.current.onEvent({ type: "check.completed", seq: 1, payload: {} }));
  act(() => result.current.onEvent({ type: "check.completed", seq: 1, payload: {} }));
  expect(result.current.applied).toBe(1);
});
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd frontend && npm test -- --run`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the hook**

Open `EventSource` when `sessionId` is non-null. Parse events, drop `seq <= lastSeq`, dispatch to the store, close on `investigation.complete` and non-retryable `session.error`, set `retry: 60000` in the stream preamble, and on connection error fetch the snapshot and re-render. Handle React StrictMode double-mount by closing the first connection in the effect cleanup.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd frontend && npm test -- --run`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/sse.ts frontend/src/features/results/useSessionStream.ts frontend/src/features/results/useSessionStream.test.tsx
git commit -m "feat: add multiplexed sse hook with snapshot fallback"
```

---

### Task 21: Best pick, purge, error, and empty states

**Files:**
- Create: `frontend/src/features/results/BestPick.tsx`, `PurgeOverlay.tsx`
- Create: `frontend/src/components/EmptyState.tsx`, `ErrorBanner.tsx`
- Create: `frontend/src/features/results/BestPick.test.tsx`

**Interfaces:**
- Produces: `<BestPick recommendation listings />`; `<PurgeOverlay onComplete />`; `<EmptyState />`; `<ErrorBanner message />`.

- [ ] **Step 1: Write the failing test**

```tsx
// frontend/src/features/results/BestPick.test.tsx
import { render, screen } from "@testing-library/react";
import { BestPick } from "./BestPick";

test("shows the best pick and savings", () => {
  render(<BestPick
    recommendation={{ recommended_listing_id: "lst_1", median_trusted_cents: 26000,
      savings_cents: 1100, eligible_ids: ["lst_1"], reason: "cheapest trusted",
      no_trusted_option: false }}
    listings={[{ id: "lst_1", title: "Sony XM5", price_cents: 24900,
      currency: "USD", merchant_name: "Best Buy", merchant_domain: "bestbuy.com",
      image_url: "", product_url: "", source: "catalog" }]} />);
  expect(screen.getByText(/Sony XM5/)).toBeInTheDocument();
  expect(screen.getByText(/\$11\.00/)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd frontend && npm test -- --run`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the components**

`BestPick` highlights the recommended listing with the savings. `PurgeOverlay` uses Framer Motion to wipe `danger` cards and calls `onComplete`. `EmptyState` shows a friendly message and a "Start over" button. `ErrorBanner` is dismissible and non-blocking. `no_trusted_option` renders the empty state with the reason, not an error.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd frontend && npm test -- --run`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/results frontend/src/components
git commit -m "feat: add best pick, purge, and empty states"
```

---

### Task 22: Payability guard and mandates

**Files:**
- Create: `backend/app/payments/payability.py`, `backend/app/payments/mandates.py`
- Create: `backend/tests/unit/test_payability.py`

**Interfaces:**
- Produces: `PayabilityCode`, `PayabilityError`, `assert_payable(investigation, listing, mandate, *, now) -> None`; `create_mandate(listing: Listing, *, max_amount_cents: int, currency: str = "USD", expires_in_seconds: int = 600, now: datetime | None = None) -> Mandate`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/unit/test_payability.py
import pytest
from datetime import datetime, timedelta, timezone
from app.payments.payability import assert_payable, PayabilityError, PayabilityCode
from app.payments.mandates import create_mandate
from app.domain.models import Listing, Investigation, ScoreResult, Mandate, TrustCheckResult
from app.domain.enums import Verdict, CheckId, TrustStatus

NOW = datetime(2026, 10, 17, 19, 0, tzinfo=timezone.utc)

def listing(cents=10000, domain="bestbuy.com"):
    return Listing(id="lst_1", title="x", price_cents=cents, merchant_name="m",
                   merchant_domain=domain, image_url="", product_url="")

def inv(verdict=Verdict.TRUSTED, score=92, confidence=0.9, minutes_ago=1, completed=5):
    checks = [TrustCheckResult(id=cid, name=cid.value, status=TrustStatus.PASSED,
                               severity=0, summary="ok", source="live")
              for cid in list(CheckId)[:completed]]
    return Investigation(id="inv_1", listing_id="lst_1", session_id="ses_1",
        checks=checks,
        score=ScoreResult(score=score, verdict=verdict, confidence=confidence,
                          top_reason="x", scoring_version="1.0"),
        allowlisted=False, duration_ms=1,
        created_at=NOW - timedelta(minutes=minutes_ago))

def mandate(cents=30000, domain="bestbuy.com",
            expires=NOW + timedelta(minutes=10), status="active"):
    return Mandate(id="man_1", session_id="ses_1", listing_id="lst_1",
                   investigation_id="inv_1", merchant_domain=domain,
                   max_amount_cents=cents, expires_at=expires, status=status)

def test_trusted_is_payable():
    assert_payable(inv(), listing(), mandate(), now=NOW)

def test_mandate_below_price_raises():
    with pytest.raises(ValueError):
        create_mandate(listing(10000), max_amount_cents=5000, now=NOW)

def test_caution_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(Verdict.CAUTION, 50), listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.MERCHANT_NOT_TRUSTED

def test_low_coverage_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(completed=2), listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.COVERAGE_TOO_LOW

def test_amount_over_cap_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(), listing(40000), mandate(30000), now=NOW)
    assert e.value.code == PayabilityCode.AMOUNT_EXCEEDS_CAP

def test_stale_investigation_blocked():
    with pytest.raises(PayabilityError) as e:
        assert_payable(inv(minutes_ago=45), listing(), mandate(), now=NOW)
    assert e.value.code == PayabilityCode.INVESTIGATION_STALE
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/unit/test_payability.py -v`  
Expected: FAIL — modules missing.

- [ ] **Step 3: Implement the guard and mandate factory**

`create_mandate` validates `max_amount_cents >= listing.price_cents`, sets expiry `now + expires_in_seconds`, status `active`. `assert_payable` runs the ten checks from §7.8 in order and raises `PayabilityError(code, details)`.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/unit/test_payability.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/payments backend/tests/unit/test_payability.py
git commit -m "feat: add payability guard and mandates"
```

---

### Task 23: Mock VIC, checkout, and confirm routes

**Files:**
- Create: `backend/app/payments/mock_vic.py`, `backend/app/api/routes_checkout.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/integration/test_checkout_api.py`

**Interfaces:**
- Consumes: `assert_payable`, `create_mandate`, repository.
- Produces: `POST /api/checkout`, `POST /api/checkout/{id}/confirm`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/integration/test_checkout_api.py
from fastapi.testclient import TestClient
from app.main import create_app
from app.search.catalog import load_catalog
from app.domain.models import Investigation, ScoreResult, TrustCheckResult
from app.domain.enums import Verdict, CheckId, TrustStatus

def _setup(client, monkeypatch, verdict="trusted", completed=5):
    s = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    client.post(f"/api/sessions/{s['session_id']}/answers",
                json={"answers": [{"question_id": "q_budget", "option_id": "300"}]})
    # Select the listing directly from the catalog: the orchestrator runs in a
    # background task and is not guaranteed to have finished inside TestClient.
    listing = next(l for l in load_catalog() if l.merchant_domain == "bestbuy.com")
    checks = [TrustCheckResult(id=cid, name=cid.value, status=TrustStatus.PASSED,
                               severity=0, summary="ok", source="live")
              for cid in list(CheckId)[:completed]]
    inv = Investigation(id="inv_1", listing_id=listing.id, session_id=s["session_id"],
        checks=checks, score=ScoreResult(score=92 if verdict == "trusted" else 50,
            verdict=Verdict(verdict), confidence=0.9, top_reason="x"),
        allowlisted=False, duration_ms=1,
        created_at="2026-10-17T19:00:00Z")
    import app.api.routes_checkout as rc
    monkeypatch.setattr(rc, "_get_listing", lambda lid: listing)
    monkeypatch.setattr(rc, "_get_investigation", lambda sid, lid: inv)
    return s["session_id"], listing.model_dump()

def test_checkout_blocked_for_caution(monkeypatch):
    client = TestClient(create_app())
    sid, listing = _setup(client, monkeypatch, verdict="caution", completed=5)
    r = client.post("/api/checkout", json={"session_id": sid, "listing_id": listing["id"],
        "mandate": {"max_amount_cents": 50000, "currency": "USD", "expires_in_seconds": 600}})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "MERCHANT_NOT_TRUSTED"

def test_confirm_twice_returns_same_receipt(monkeypatch):
    client = TestClient(create_app())
    sid, listing = _setup(client, monkeypatch)
    co = client.post("/api/checkout", json={"session_id": sid, "listing_id": listing["id"],
        "mandate": {"max_amount_cents": 50000, "currency": "USD", "expires_in_seconds": 600}}).json()
    body = {"passkey_assertion": {"credential_id": "mock", "client_data": "mock"},
            "idempotency_key": "same"}
    a = client.post(f"/api/checkout/{co['checkout_id']}/confirm", json=body).json()
    b = client.post(f"/api/checkout/{co['checkout_id']}/confirm", json=body).json()
    assert a["receipt_id"] == b["receipt_id"]
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/integration/test_checkout_api.py -v`  
Expected: FAIL — 404.

- [ ] **Step 3: Implement the routes and mock VIC**

`POST /checkout`: define `_get_listing(listing_id) -> Listing` and `_get_investigation(session_id, listing_id) -> Investigation` in `routes_checkout.py` (tests monkeypatch these names). Build a `MandateDraft` from the request's cap and currency, call `assert_payable` on the draft, then `create_mandate`, issue a token (store hash + last4), create the checkout, persist, return 201. Map `PayabilityError` to 409 with the code. `POST /confirm`: load the checkout; if captured, return the existing receipt; validate the assertion; atomically transition `awaiting_passkey → authorized → captured`; consume the token; create the transaction; create the receipt; persist; return 200. `client_data == "fail"` → 402 `PAYMENT_DECLINED`.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/integration/test_checkout_api.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/payments/mock_vic.py backend/app/api/routes_checkout.py backend/app/main.py backend/tests/integration/test_checkout_api.py
git commit -m "feat: add mock vic and checkout endpoints"
```

---

### Task 24: Receipt service and routes

**Files:**
- Create: `backend/app/payments/receipts.py`, `backend/app/api/routes_receipts.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/integration/test_receipts_api.py`

**Interfaces:**
- Produces: `create_receipt`, `verify_receipt`; `GET /api/receipts/{id}`, `GET /api/public/receipts/{share_id}`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/integration/test_receipts_api.py
from fastapi.testclient import TestClient
from app.main import create_app
from tests.integration.test_checkout_api import _setup

def test_public_receipt_by_share_id(monkeypatch):
    client = TestClient(create_app())
    sid, listing = _setup(client, monkeypatch)
    co = client.post("/api/checkout", json={"session_id": sid, "listing_id": listing["id"],
        "mandate": {"max_amount_cents": 50000, "currency": "USD", "expires_in_seconds": 600}}).json()
    receipt = client.post(f"/api/checkout/{co['checkout_id']}/confirm",
        json={"passkey_assertion": {"credential_id": "mock", "client_data": "mock"},
              "idempotency_key": "k"}).json()
    share = receipt["receipt_url"].split("/r/")[1]
    r = client.get(f"/api/public/receipts/{share}")
    assert r.status_code == 200
    assert r.json()["token_last4"] == "4242"

def test_unknown_receipt_404():
    client = TestClient(create_app())
    assert client.get("/api/public/receipts/nope").status_code == 404
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/integration/test_receipts_api.py -v`  
Expected: FAIL — 404.

- [ ] **Step 3: Implement the service and routes**

`create_receipt` deep-copies the investigation, computes `share_id` (12-char base32), signs `receipt_id|share_id|amount_cents|issued_at` with HMAC-SHA256, and sets `verified`/`unverified` from the check statuses. Routes return the receipt or 404; the public route is rate-limited and strips nothing because the model already contains no PII.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/integration/test_receipts_api.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/payments/receipts.py backend/app/api/routes_receipts.py backend/app/main.py backend/tests/integration/test_receipts_api.py
git commit -m "feat: add receipt service and routes"
```

---

### Task 25: Checkout UI — mandate, passkey, processing

**Files:**
- Create: `frontend/src/features/checkout/CheckoutSheet.tsx`, `MandateCard.tsx`, `PasskeyDialog.tsx`, `ProcessingState.tsx`
- Create: `frontend/src/features/checkout/CheckoutSheet.test.tsx`

**Interfaces:**
- Consumes: `createCheckout`, `confirmCheckout`.
- Produces: `<CheckoutSheet listing verdict score confidence onComplete />`.

- [ ] **Step 1: Write the failing test**

```tsx
// frontend/src/features/checkout/CheckoutSheet.test.tsx
import { render, screen } from "@testing-library/react";
import { CheckoutSheet } from "./CheckoutSheet";

const listing = { id: "lst_1", title: "Sony XM5", price_cents: 24900, currency: "USD",
  merchant_name: "Best Buy", merchant_domain: "bestbuy.com", image_url: "",
  product_url: "", source: "catalog" as const };

test("disables pay for caution", () => {
  render(<CheckoutSheet listing={listing} verdict="caution" score={50}
    confidence={0.9} onComplete={() => {}} />);
  expect(screen.getByRole("button", { name: /pay/i })).toBeDisabled();
});

test("enables pay for trusted", () => {
  render(<CheckoutSheet listing={listing} verdict="trusted" score={92}
    confidence={0.9} onComplete={() => {}} />);
  expect(screen.getByRole("button", { name: /pay/i })).toBeEnabled();
});
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd frontend && npm test -- --run`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the components**

`CheckoutSheet` shows the merchant, amount, trust snapshot, and a persistent sandbox badge. The pay button is disabled unless `verdict === "trusted" && score >= 70 && confidence >= 0.6`. On click: `createCheckout` → `MandateCard` (cap, merchant, expiry) → `PasskeyDialog` (simulated biometric) → `confirmCheckout` → `ProcessingState` with three animated steps (tokenizing, authorizing, capturing) → `onComplete(receipt)`. Errors render inline with the server's message.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd frontend && npm test -- --run`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/checkout
git commit -m "feat: add checkout ui with mandate and passkey"
```

---

### Task 26: Receipt UI and share page

**Files:**
- Create: `frontend/src/features/receipt/ReceiptPage.tsx`, `Receipt.test.tsx`
- Modify: `frontend/src/App.tsx` (route `/r/:shareId`)

**Interfaces:**
- Consumes: `getReceipt`.
- Produces: `<ReceiptPage />`; receipt card with score, checks, amount, token last4, share button.

- [ ] **Step 1: Write the failing test**

```tsx
// frontend/src/features/receipt/Receipt.test.tsx
import { render, screen } from "@testing-library/react";
import { ReceiptView } from "./ReceiptPage";

const receipt = {
  id: "rcp_1", share_id: "shr_1", checkout_id: "chk_1", transaction_id: "txn_1",
  listing: { id: "lst_1", title: "Sony XM5", price_cents: 24900, currency: "USD",
    merchant_name: "Best Buy", merchant_domain: "bestbuy.com", image_url: "",
    product_url: "", source: "catalog" },
  investigation_snapshot: { id: "inv_1", listing_id: "lst_1", session_id: "ses_1",
    checks: [], score: { score: 92, verdict: "trusted", confidence: 0.9,
      penalties: [], fatal_flags: [], top_reason: "ok", scoring_version: "1.0" },
    allowlisted: false, duration_ms: 1, created_at: "" },
  amount_cents: 24900, currency: "USD", token_last4: "4242",
  verified: ["Domain age", "SSL", "Safe Browsing"], unverified: [],
  issued_at: "", signature: "",
};

test("renders score and amount", () => {
  render(<ReceiptView receipt={receipt as any} />);
  expect(screen.getByText(/92/)).toBeInTheDocument();
  expect(screen.getByText(/\$249\.00/)).toBeInTheDocument();
  expect(screen.getByText(/4242/)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd frontend && npm test -- --run`  
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the receipt page**

Route `/r/:shareId` fetches `getReceipt(shareId)`. Render the score ring, merchant, amount, token last4, verified/unverified lists, issued time, and a "Copy link" button. Include the sandbox badge and "What this receipt proves" copy. Unknown ID → 404 state.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd frontend && npm test -- --run`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/receipt frontend/src/App.tsx
git commit -m "feat: add receipt page and share link"
```

---

### Task 27: MongoDB repositories, caches, audit, PII redaction

**Files:**
- Create: `backend/app/db/mongo.py`, `backend/app/db/indexes.py`
- Create: `backend/app/services/repository.py`, `backend/app/services/audit.py`
- Modify: `backend/app/payments/receipts.py` (use the repository)
- Create: `backend/tests/integration/test_repositories.py`

**Interfaces:**
- Produces: `InMemoryRepository`, `MongoRepository`; `redact(text) -> str`; TTL indexes.

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/integration/test_repositories.py
import pytest
from app.services.repository import InMemoryRepository
from app.core.logging import redact

def test_redacts_email_and_phone():
    assert "a@b.com" not in redact("contact a@b.com")
    assert "555-123-4567" not in redact("call 555-123-4567")

@pytest.mark.asyncio
async def test_checkout_transition_is_atomic():
    repo = InMemoryRepository()
    await repo.save_checkout(checkout)
    assert await repo.transition_checkout(checkout.id, "awaiting_passkey", "captured")
    assert not await repo.transition_checkout(checkout.id, "awaiting_passkey", "captured")
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && pytest tests/integration/test_repositories.py -v`  
Expected: FAIL — modules missing.

- [ ] **Step 3: Implement the repositories and redaction**

`InMemoryRepository` uses dicts with asyncio locks. `MongoRepository` uses `motor`; `transition_checkout` uses `find_one_and_update({"_id": id, "stage": from_stage}, {"$set": {"stage": to_stage}})`. `indexes.py` creates the TTL and unique indexes. `redact` replaces emails and phone numbers with `[redacted]`. If `MONGODB_URI` is empty or the ping fails, select the in-memory adapter and set `db: "unavailable"`.

- [ ] **Step 4: Run them and confirm they pass**

Run: `cd backend && pytest tests/integration/test_repositories.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db backend/app/services backend/app/payments/receipts.py backend/tests/integration/test_repositories.py
git commit -m "feat: add repositories, caches, audit, and pii redaction"
```

---

### Task 28: Demo mode, offline replay, and seed

**Files:**
- Create: `backend/app/core/demo.py`
- Create: `scripts/replay_offline.py`, `scripts/seed_cache.py`, `scripts/smoke_sse.py`
- Create: `backend/tests/integration/test_demo_mode.py`

**Interfaces:**
- Produces: `DEMO_MODE`, `DEMO_PACING`, `OFFLINE` behavior; `POST /api/demo/reset`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/integration/test_demo_mode.py
from fastapi.testclient import TestClient
from app.main import create_app

def test_demo_mode_is_deterministic(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "1")
    client = TestClient(create_app())
    a = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    b = client.post("/api/sessions", json={"query": "headphones", "client_id": "c1"}).json()
    assert [q["id"] for q in a["questions"]] == [q["id"] for q in b["questions"]]
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd backend && pytest tests/integration/test_demo_mode.py -v`  
Expected: FAIL — no demo behavior.

- [ ] **Step 3: Implement demo mode and scripts**

When `DEMO_MODE=1`: force catalog search, use villain fixtures for RDAP/page/Reddit, inject exactly one villain and one hero, and stagger `check.completed` by 300–900ms when `DEMO_PACING=1`. All fixture-sourced checks carry `source="fixture"`. `POST /api/demo/reset` clears sessions, investigations, checkouts, and receipts. `replay_offline.py` runs the full orchestration with `OFFLINE=1` and no network. `smoke_sse.py` asserts the event order.

- [ ] **Step 4: Run it and confirm it passes**

Run: `cd backend && pytest tests/integration/test_demo_mode.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/demo.py scripts backend/tests/integration/test_demo_mode.py
git commit -m "feat: add deterministic demo mode and offline replay"
```

---

### Task 29: VEYZL audit and docs

**Files:**
- Create: `docs/veylz-audit.md`
- Modify: `README.md`
- Create: `docs/qa-checklist.md`, `docs/decisions.md`

**Deliverable:** A real VEYZL audit finding a missing control, the fix, and evidence. No automated test; the QA checklist verifies the docs exist and the demo links work.

- [ ] **Step 1: Connect the repo to VEYZL and run the audit.**
- [ ] **Step 2: Pick one finding (e.g., missing human approval for high-value payments) and fix it in code.**
- [ ] **Step 3: Write `docs/veylz-audit.md` with the finding, the fix, and before/after evidence.**
- [ ] **Step 4: Update `README.md` with setup, env vars, and the demo script.**
- [ ] **Step 5: Commit**

```bash
git add docs README.md
git commit -m "docs: add veyzl audit and runbook"
```

---

### Task 30: Video, Devpost, and final QA

**Files:**
- Create: `docs/devpost.md`, `docs/video-script.md`
- Extend: `docs/qa-checklist.md`

**Deliverable:** A 3-minute video, a complete Devpost, a deployed URL, and a passing QA checklist.

- [ ] **Step 1: Record the 3-minute video using the beats in §17.1.**
- [ ] **Step 2: Fill `docs/devpost-form.md`, then `docs/devpost.md`.**
- [ ] **Step 3: Run the QA checklist: session, questions, listings, checks, purge, best pick, checkout, passkey, receipt, share, 1024px width, keyboard nav.**
- [ ] **Step 4: Submit the Devpost draft by 10:30 PM Saturday; final by 10:00 AM Sunday.**
- [ ] **Step 5: Commit**

```bash
git add docs
git commit -m "docs: add video script and devpost"
```

---

## 15. 21-Hour Execution Schedule

### 15.1 Roles

| Role | Owns | If 3 people |
|---|---|---|
| **A — Agent/API** | FastAPI, sessions, EventBus, SSE, orchestrator, LLM client, repository | Keep |
| **B — Trust/Data** | 5 checks, URL safety, caches, scoring, recommendation, fixtures, Mongo indexes | Keep |
| **C — Frontend/UX** | All React, design system, SSE hook, animations, copy | Keep |
| **D — Payments/Demo** | Payability, mandates, mock VIC, receipts, demo mode, Devpost, video | Merge into A (backend) and C (checkout/receipt UI) |

C is the bottleneck. A and B must contribute UI polish and copy in the last 4 hours.

### 15.2 Schedule

| Time | Tasks | Owner(s) | Milestone |
|---|---|---|---|
| Sat 12:30–1:15 | 1, 2, 3 | All | Repo, contracts frozen, health deployed, SerpAPI go/no-go |
| Sat 1:15–3:30 | 4, 5, 6, 7 | A + B | Session → search → listings streamed |
| Sat 3:30–6:00 | 8, 9, 10, 11 | B | Runner + domain age + SSL + Safe Browsing |
| Sat 6:00–7:30 | 12, 13, 14 | B | Reddit + page flags + scoring golden tests |
| Sat 7:30–9:00 | 15, 16 | A + B | Recommendation + full orchestration |
| Sat 9:00–10:30 | 17, 18, 19, 20 | C | Shell + discovery + results + SSE hook |
| Sat 10:30 | — | All | **Devpost draft submitted** |
| Sat 10:30–12:30 | 21, 22, 23 | A + C | Purge + payability + checkout |
| Sat 12:30–2:00 | 24, 25, 26 | A + C | Receipt + checkout UI + receipt page |
| Sat 2:00–3:00 | 27 | B | Mongo, caches, audit, redaction |
| Sat 3:00–4:00 | 28 | All | Demo mode + offline replay |
| Sat 4:00–8:00 | — | Rotating | Sleep in shifts; at least two people get 4 hours |
| Sun 8:00–9:00 | 29, 30 | All | VEYZL + video + docs |
| Sun 9:00–9:30 | 30 | All | Final Devpost, screenshots, stack list |
| Sun 9:30–9:50 | — | All | Rehearse twice; warm backend |
| Sun 9:50–10:00 | — | All | **Submit; capture confirmation** |

**Critical path:** 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 14 → 16 → 20 → 22 → 23 → 25 → 26. Protect these.

### 15.3 Cut List, In Order

1. Chrome extension (do not build).
2. Merchant badge / appeal UI.
3. Live Reddit and page scraping (use fixtures; keep the check cards).
4. SerpAPI (catalog only).
5. MongoDB (in-memory adapter + snapshot; state the persistence design instead).
6. Share link (keep the receipt on-screen).
7. Fourth and fifth checks (keep domain age, Safe Browsing, page flags).

**Never cut:** the payment moment, the score, the streaming investigation, the receipt.

### 15.4 Three-Person Work Split

The task-by-task ownership map, per-person time-blocked checklist, shared gates, handoffs, and cut assignments live in `docs/team-split-3.md`. Use that checklist during the event; this plan remains the architecture and contract source of truth.

---

## 16. Risk Register

| # | Risk | Prob. | Impact | Mitigation | Trigger to act |
|---|---|---|---|---|---|
| R1 | Backend cold start or deploy failure | High | High | Fly.io always-on; 5-min ping; warm 20 min before recording; backup video; local path | Health latency > 3s |
| R2 | Search API fails or returns Google links | High | High | 5s timeout; catalog fallback; reject empty domains; inject hero/villain | Any listing without a merchant domain |
| R3 | SSE stalls behind a proxy | Medium | High | One stream; `X-Accel-Buffering: no`; no gzip; 15s heartbeat; snapshot fallback | Checks arrive in a burst after 10s |
| R4 | A check hangs | High | High | Per-check `wait_for`; RDAP primary; thread offload; 14s global budget | Any check > 6s |
| R5 | Safe Browsing key unavailable | Medium | Medium | 6h cache; static denylist; `source: unavailable`; never silently pass | 403/quota |
| R6 | Reddit 403/429 | High | Medium | Cache; identified User-Agent; fixture fallback | First 429 |
| R7 | Page fetch blocked or JS shell | Medium | Medium | httpx + BeautifulSoup; 1 MB cap; villain fixture; `skipped` with reason | Empty/boilerplate HTML |
| R8 | False positive on a real brand | Medium | High | Allowlist; thresholds; coverage rule; fictional villain; never publish a real brand as `danger` without fatal evidence | Any real brand scores `danger` |
| R9 | SSRF or prompt injection | Medium | High | URL safety; redirect re-validation; structured extractors; no tool loop | Any fetch to a private IP or LLM output outside schema |
| R10 | Time overrun or contract drift | High | High | Contracts frozen at 1:15; one owner per file; hard gates; cut list | Any gate missed by 20 min |
| R11 | Villain does not go red | Medium | High | Fixtures + golden test pinning `danger` | Villain scores above caution |
| R12 | Payment mock feels fake | Medium | Medium | State machine, sandbox labels, realistic UI, receipt | Judge asks "is this real?" |

---

## 17. Demo and Submission

### 17.1 3-Minute Video

| Time | Beat |
|---|---|
| 0:00–0:15 | Problem: online fraud is invisible; agentic commerce makes it worse. |
| 0:15–0:35 | Discovery: three questions, then a search spec. |
| 0:35–1:20 | Results grid; checks stream in one by one; the villain goes red. |
| 1:20–1:45 | Purge; scores and confidence land. |
| 1:45–2:10 | Best pick: cheapest trusted; savings vs. median. |
| 2:10–2:40 | Checkout: mandate → passkey → token → captured; sandbox badge visible. |
| 2:40–3:00 | Receipt; "the agent can only pay a merchant it can verify." |

### 17.2 Submission Checklist

- [ ] Devpost draft by 10:30 PM Saturday.
- [ ] Final Devpost by 10:00 AM Sunday.
- [ ] 3-minute video uploaded and linked.
- [ ] Deployed frontend URL works.
- [ ] `/api/health` returns 200.
- [ ] Repo public or shared with judges.
- [ ] Visa track selected.
- [ ] Up to 3 sponsored side tracks selected.
- [ ] Non-sponsored tracks selected (NEXT, Gemini, MongoDB, DEV).
- [ ] Screenshots: results, trust card, checkout, receipt.
- [ ] Backup video recorded.
- [ ] `ATTRIBUTION.md` present.
- [ ] Team on-site for judging.

---

## 18. Post-Hackathon Roadmap

| Priority | Item | Why |
|---|---|---|
| P0 | Real Visa Intelligent Commerce sandbox | Production credibility |
| P0 | Real merchant data integration | Trust signals need real inputs |
| P1 | Chrome extension | Meet users where they shop |
| P1 | Merchant verification dashboard | B2B revenue |
| P2 | Seller history + counterfeit detection | Deeper trust signals |
| P2 | Price history + deal authenticity | Adjacent wedge |
| P3 | Public receipt API | Platform play |
| P3 | Multi-language support | Global commerce |

---

## 19. Self-Review

**Spec coverage:** FR-1→5/18, FR-2→4, FR-3→6/8/16/20, FR-4→14, FR-5→15, FR-6→23/25, FR-7→24/26, FR-8→22, FR-9→27, FR-10→28. Every NFR maps to a budget, a test, or a constraint.

**Step scan:** each step is one action with a checkable result. No "TBD" or "handle edge cases." Code blocks are tests and signatures; the implementer writes the bodies.

**Type consistency:** `TrustCheckResult`, `Listing`, `ScoreResult`, `Investigation`, `Session`, `Mandate`, `Checkout`, `Transaction`, and `Receipt` are defined once in Task 2 and reused. Cents are `int` everywhere. API field names match the TypeScript types.

**Review Focus:** each of the ten failure modes has a test in its owning task: #1 Task 4, #2 Task 8, #3 Task 14, #4 Task 13, #5 Task 13, #6 Task 22, #7 Task 23, #8 Task 20, #9 Task 27, #10 Task 28.

**Deviation from the spec, deliberate:** the spec sketches one stream per product; this plan uses one stream per session to avoid the browser's 6-connection cap. The spec names Tavily; this plan uses SerpAPI because Tavily is a research API and its prices/merchant domains are unreliable. The spec's scoring, thresholds, fatal flags, and allowlist behavior are preserved exactly. The coverage rule (fewer than 3 completed checks → not trusted) is an addition that strengthens the spec's "insufficient evidence is not trust" posture.

**Proportion:** the design sections carry the decisions; the task list carries the test cycles. The plan does not transcribe the implementation.

---

## Appendix A — Scoring Golden Cases

1. Allowlisted → 0/trusted.
2. Safe Browsing hit → 0/danger.
3. 10-day domain + new cert + 3 scam reports + urgency → ≤31/danger.
4. 8-year domain, valid cert, clean page, no Reddit → ≥90/trusted.
5. Two timeouts → capped 69/caution/not payable.
6. Page flags failed with 4 high-severity flags → ≤30/danger.
7. Payability matrix: eight reason codes, each 409.

## Appendix B — Environment Variables

Backend: `APP_ENV`, `DEMO_MODE`, `DEMO_PACING`, `OFFLINE`, `ALLOWED_ORIGINS`, `MONGODB_URI`, `MONGODB_DB`, `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-2.5-flash`, `SERPAPI_KEY`, `GOOGLE_SAFE_BROWSING_KEY`, `RECEIPT_SIGNING_SECRET`, `MAX_LISTINGS=8`, `INVESTIGATION_BUDGET_S=14`, `CHECK_CONCURRENCY=8`.

Frontend: `VITE_API_BASE_URL` only.

## Appendix C — Demo Mode Contract

`DEMO_MODE=1` guarantees, without network luck:
- Exactly one fictional villain (`premium-audio-deals.shop`) with fixture RDAP, page, and Reddit data.
- Four trusted listings across Amazon, Best Buy, Walmart, and a boutique; the hero is the cheapest trusted.
- If SerpAPI fails, the catalog supplies all listings; the stream is identical.
- `DEMO_PACING=1` staggers `check.completed` by 300–900ms; only timing is staged.
- `POST /api/demo/reset` clears sessions, investigations, checkouts, and receipts.
- Every fixture-sourced check carries `source: "fixture"`.

## Appendix D — Glossary

See the Terms section in `docs/devpost-form.md` and the decision log in `docs/decisions.md`; the standalone glossary was removed on 2026-10-18.

## Appendix E — Database Alternatives

The `Repository` protocol (§7.11) isolates persistence to Task 27. Switching engines changes that task and the schema, not the trust, payment, or API code.

| Engine | Best for here | Costs / gaps | Verdict |
|---|---|---|---|
| **MongoDB** (current) | Document-shaped investigations and receipts; built-in TTL for sessions and caches; mature async `motor`; MLH track | No foreign keys; integrity is app-enforced; aggregations less familiar than SQL | **Default.** Best fit for the data and the 21-hour budget. |
| **PostgreSQL** | Strongest SQL option: `jsonb` + GIN, partial and unique indexes, `UPDATE … RETURNING` for atomic transitions, `pg_cron` for TTL, `asyncpg` | Migrations at hour 14; no native TTL; another vendor | **Only serious swap.** Choose it if relational integrity of the payment ledger is a pitch point. |
| **MySQL** | Widely hosted; familiar | MySQL 8.0 lacks `UPDATE … RETURNING`; JSON indexing needs generated columns or multi-valued indexes; `CHECK` enforced only from 8.0.16; fewer async-friendly managed options | **Dominated by Postgres.** No reason to choose it here. |
| **SQLite** | Zero ops; ideal for tests and offline replay; survives network outages; `aiosqlite` | Single writer; no network access; no TTL; needs a Fly volume; cannot serve multiple instances | **Resilience option.** Viable on one always-on machine; not for multi-instance. |

**Decision rule:** stay on MongoDB unless the team is materially faster in SQL (then Postgres) or the demo must survive a total network outage on a single machine (then SQLite). Do not run two engines.
