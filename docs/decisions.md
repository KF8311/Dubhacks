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

## D-010 — Backend deploys to Fly.io, not Cloud Run or Render
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** The FastAPI backend runs on one always-on Fly.io `shared-cpu-1x` 256 MB machine. The frontend stays on Vercel.
- **Why:** No cold start during judging. Cloud Run was the stronger technical fit and is also free within quota, but it requires a Google Cloud billing account. Render free sleeps after 15 minutes and wakes in about 60 seconds, which is unacceptable when a judge clicks the link.
- **Alternatives considered:** Cloud Run (free within quota, card required, cold start of a few seconds); Render free (no card, ~60 s cold start); laptop + Cloudflare Tunnel (no card, but the demo dies if the laptop sleeps).
- **Consequences:** About $2.19 per 30 days billed per second — roughly $0.15 for the event. The free trial is only 2 machine hours, so a card is required. Fly has no hard spend cap, so destroy the machines after judging. `fly launch` generates the Dockerfile. Uvicorn runs `--workers 1` with no global gzip so SSE streams.
## D-011 — SerpAPI stays catalog-only until a key proves merchant domains
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Ship search on the curated catalog. Re-run `python scripts/serpapi_spike.py` when `SERPAPI_KEY` exists, and only switch to live search if the results carry merchant domains.
- **Why:** The spike could not call SerpAPI because the key is unset. The plan already specifies a catalog fallback, so nothing is blocked.
- **Alternatives considered:** Blocking on the key (rejected: the catalog covers the demo query).
- **Consequences:** The demo is deterministic and offline-safe. Search quality is unchanged until a key appears.

## D-012 — Fly.io is the API host; `sniff-visa-dubhacks`
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Host the API on Fly.io as app `sniff-visa-dubhacks` in org `dubhacks`. Render remains the backup.
- **Why:** D-010 chose Fly.io for the always-on machine. An account now exists and the health endpoint is live.
- **Alternatives considered:** Render free (superseded by D-010 — cold start), local uvicorn + Cloudflare Tunnel (kept as the demo backup).
- **Consequences:** Health is live at `https://sniff-visa-dubhacks.fly.dev/api/health`. The region reference in this entry was inconsistent; resolved by D-013.

## D-013 — Fly primary region is `sjc`
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** `sjc` is the region. `fly.toml` line 8 sets `primary_region = "sjc"` and is authoritative.
- **Why:** `fly.toml` is the only file that controls where the machine runs. The earlier `sea` reference was a transcription artifact carried in from a branch merge, not a deployed setting.
- **Alternatives considered:** `sea` (no functional benefit; would require a redeploy to a new region mid-hackathon).
- **Consequences:** `status.md` updated; the region blocker is closed. Changing regions later is a new entry plus a redeploy.

## D-014 — Remove `oldIdeas/` from the repo
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Delete `oldIdeas/visa-ideas.md`, `visa-ideas-round2.md`, and `project-test-kitchen.md`.
- **Why:** They are pre-decision brainstorming that no code, doc, or task references. `D-001` already records the outcome of that comparison, which is the part worth keeping. Leaving 140 KB of rejected ideas at the repo root makes the project read as unfocused to a judge.
- **Alternatives considered:** Keep them (no cost, but no value); move them to a branch (extra step for files nobody will open).
- **Consequences:** `D-001`'s parenthetical "kept in `project-test-kitchen.md`" no longer resolves to a file; the decision itself stands. History retains both files if anyone actually wants them.

## D-015 — Carry allowlisting on `ScoreResult` and exempt allowlisted listings from the score floor
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** `ScoreResult` gains `allowlisted: bool = False`, set by `score_investigation()`. Recommendation eligibility becomes `verdict == trusted AND (score >= 70 OR allowlisted) AND confidence >= 0.6`. Payability keeps its existing rule, which already exempted allowlisted listings from the three-check floor.
- **Why:** The allowlist rule scores a merchant 0 while declaring it `trusted`, because the score measures suspicion, not safety. Downstream logic that reads only the number sees "0" and treats a curated merchant as unpayable. With 8 of the catalog's listings allowlisted, the old eligibility rule would have excluded every safe option and made the demo end in `no_trusted_option`. The flag makes the exemption explicit instead of inferring it from a score that cannot express it.
- **Alternatives considered:** Score allowlisted merchants 100 instead of 0 (loses the "no evidence needed" signal and diverges from the spec's scoring table); let `recommend()` re-read the allowlist file (duplicates a rule that belongs to scoring, and the caller may use a different allowlist); treat `verdict == trusted` alone as sufficient (also admits trusted listings under the 70 floor when coverage is thin).
- **Consequences:** A listing can be eligible at score 0, so any UI that sorts or badges by score must consult `allowlisted` too. `ScoreResult` is a contract type — A should acknowledge the added field. Golden tests are unchanged; the scoring math is untouched.

## D-016 — Mongo (Task 27) moves from A to B; the Block 6 slot does not move
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Task 27 (`MongoRepository`, TTL indexes, caches, audit, redaction) is owned by **B**. The work stays where it already sits on the calendar — B's 10:30 PM–2:00 AM block, inside Block 6 — so no block, gate, or deliverable changes for anyone else.
- **Why:** A does not want to take on MongoDB, and B already owns persistence-adjacent work: the `Repository` protocol shape, fixture data, redaction rules, and the offline replay that must keep working with `MONGODB_URI` unset. Ownership was the only thing out of place; the schedule was not.
- **Alternatives considered:** Drop Task 27 and stay in-memory only (loses the MLH MongoDB track and the "investigations and receipts are documents" story in D-006); move it to C (C is the critical path on G4/G5); assign it to A anyway (the owner has said no, and a half-owned task is worse than a deferred one).
- **Consequences:** Block 5 is unchanged — nobody starts Mongo work until Block 6. The in-memory adapter remains the default and the cut-order survivor; Mongo stays a swap behind the existing protocol. B owns the Atlas cluster question in `docs/open-questions.md`.
