---
title: Decisions
type: log
updated: 2026-10-17
---

# Decision Log

Append-only. One entry per decision that would cost time to re-litigate. If you want to change a decision, add a new entry that supersedes the old one; do not edit history.

Format:

```markdown
## D-00X — Title
- **Date:** YYYY-MM-DD
- **Status:** accepted | superseded by D-00Y | rejected
- **Decision:** one sentence
- **Why:** the constraint or evidence that drove it
- **Alternatives considered:** what was rejected and why
- **Consequences:** what this commits us to
```

---

## D-001 — Build Project A (Sniff + Visa), not Test Kitchen
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Build the trust-gated shopping agent.
- **Why:** Weighted matrix scored it 8.6 vs. 6.5 on Visa-rubric fit, demoability, and side-track stack. Test Kitchen's simulation is harder to show in three minutes and fits the track less directly.
- **Alternatives considered:** Test Kitchen (kept in `project-test-kitchen.md` for reference).
- **Consequences:** Every task serves the investigation → recommendation → payment path. No simulation work.

## D-002 — FastAPI + React/Vite, not Next.js
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Python FastAPI backend, React 19 + Vite SPA frontend.
- **Why:** The team is AI/backend-strong in Python; the app needs no SSR, no server components, and no file-based routing. A separate API makes SSE and the payment state machine easier to test.
- **Alternatives considered:** Next.js full-stack (rejected: one runtime for UI and API, extra framework surface).
- **Consequences:** Two deploy targets (Vercel + Fly.io/Render) and one CORS allowlist.

## D-003 — One multiplexed SSE stream per session
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** All investigation events for a session flow over one `EventSource`.
- **Why:** HTTP/1.1 caps connections per origin at roughly six. One stream per product would stall an 8–12 card grid.
- **Alternatives considered:** One stream per product (rejected: connection cap), WebSocket (rejected: more server state, no built-in replay semantics).
- **Consequences:** Monotonic `seq`, client dedupe, bounded 500-event replay, `Last-Event-ID` support, snapshot fallback.

## D-004 — SerpAPI primary, curated catalog fallback
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Product search uses SerpAPI Google Shopping; on any failure, the curated catalog.
- **Why:** Tavily is a research API; its product prices and merchant domains are unreliable, and checkout depends on the merchant domain. SerpAPI returns structured shopping results with merchant URLs.
- **Alternatives considered:** Tavily (rejected), scraping Google directly (rejected: brittle and against terms).
- **Consequences:** A SerpAPI key is a Saturday 1:15 PM go/no-go. The catalog must cover the demo query.

## D-005 — Scoring follows the spec exactly, plus a coverage cap
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Failed = `severity × 40`, warning = `severity × 15`, start at 100, thresholds 70/40, all fatal flags per spec. If fewer than 3 checks complete, cap at 69.
- **Why:** The spec is the source of truth for the Visa pitch; changing the math silently would be indefensible. "Insufficient evidence is not trust" is a stronger story than a different weighting scheme.
- **Alternatives considered:** Per-check max penalties with 75/45 thresholds (rejected: diverges from the spec and changes the demo's numbers).
- **Consequences:** Golden tests pin the villain and hero. Any rule change bumps `scoring_version`.

## D-006 — MongoDB as the primary store
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** MongoDB Atlas behind a `Repository` protocol, with an in-memory adapter.
- **Why:** Investigations and receipts are documents; TTL indexes cover sessions and caches; `motor` is mature; MongoDB is an MLH side track.
- **Alternatives considered:** PostgreSQL (the only serious swap — stronger payment-ledger integrity, but migrations cost time); MySQL (dominated by Postgres here); SQLite (kept for tests/offline replay, not the primary store).
- **Consequences:** No foreign keys; integrity is app-enforced. The repository interface keeps the swap to one task.

## D-007 — Payment is a labeled sandbox, not a real Visa integration
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Implement a mock VIC state machine: mandate → simulated passkey → one-time token → transaction → receipt. Label it everywhere.
- **Why:** No production Visa access; the demo must be honest. The state machine still demonstrates the trust gate and idempotency.
- **Alternatives considered:** Faking a single "payment succeeded" screen (rejected: no substance), claiming a real integration (rejected: dishonest).
- **Consequences:** Raw tokens never stored; SHA-256 + last4 only; atomic transitions; every response carries `processor: mock-vic`, `mode: sandbox`.

## D-008 — Three-person split with mock-first frontend
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** A owns platform/payments, B owns trust/data, C owns frontend/UX. C builds against `data/mock-session.json` from 1:15 PM and integrates real APIs at 7:30 PM.
- **Why:** Removes the frontend's dependency on backend completion and keeps C off the backend critical path.
- **Alternatives considered:** Strict layer-by-layer (rejected: C idle until 7 PM), everyone full-stack (rejected: merge conflicts).
- **Consequences:** One owner per task; A is merge captain; contracts freeze at 1:15 PM.

## D-009 — Context lives in the repo, not a separate Obsidian vault
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** `docs/` is the single source of truth, with `status.md` as the living state and `decisions.md` as the append-only log. Handoffs only at shift changes.
- **Why:** One store, versioned with the code, readable by teammates and agents, no sync or stale-note problem. Obsidian is an optional viewer.
- **Alternatives considered:** Obsidian vault as the primary brain (rejected: sync, merge conflicts, maintenance cost at 3 AM), handoffs only (rejected: no current truth).
- **Consequences:** Update `status.md` at every gate; a handoff never overrides it.
