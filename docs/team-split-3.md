# Three-Person Work Split — Sniff + Visa

> **This is the reference map, not the live checklist.** Use it for ownership ("who owns Task 23?") and the cut order. For "what do I do in this block?", use **`docs/checklist.md` §9** — it tracks the actual gate state and carries the current assignments. `docs/status.md` still wins over both.

**Read with:** `docs/superpowers/plans/2026-10-17-sniff-visa.md` (task numbers below refer to §14 of that plan).

**Assumption:** three people, all on-site, AI/backend-strong. One person (C) owns the frontend; A and B own the backend. If C is also the strongest designer, protect their focus — A and B absorb copy, screenshots, and polish.

---

## Ground rules

1. **One owner per task and per file.** The owner writes the tests and the implementation. Nobody edits another owner's file without a 2-minute huddle.
2. **Contract freeze at 1:15 PM.** `backend/app/domain/models.py`, `frontend/src/lib/types.ts`, and `docs/contracts.md` are owned by A. Any change after 1:15 is announced in the team channel before it is committed.
3. **Every task ends with a passing test and a commit.** No "I'll commit later."
4. **Branches:** `a/platform`, `b/trust`, `c/web`. Rebase on `main` every 90 minutes. A is the merge captain; only A merges to `main` after 1:15 PM. Hotfixes go through A.
5. **10-minute sync every 90 minutes.** Each person answers: done, next, blocked. If blocked more than 15 minutes, say it immediately.
6. **The schedule is a budget, not a prediction.** If a gate is missed by 20 minutes, cut from the list in §Cut assignments — do not silently extend.
7. **70/30 evidence:** first commit by 12:45 PM, commit at least every 30 minutes per person, `ATTRIBUTION.md` present from the first commit.

---

## Ownership map

| Task | Owner | Deliverable | Unblocks |
|---|---|---|---|
| 1 | A | Repo, FastAPI app, health deployed | Everyone |
| 2 | A | Models, enums, IDs, money | Everyone |
| 3 | B | Catalog, allowlist, villain fixtures | A, C |
| 4 | B | Search service + catalog fallback | A |
| 5 | A | Session registry and routes | C |
| 6 | A | Event bus + SSE endpoint | C |
| 7 | A | Orchestrator skeleton | A |
| 8 | B | Check protocol + parallel runner | B |
| 9 | B | Domain age (RDAP) | B |
| 10 | B | SSL certificate | B |
| 11 | B | Safe Browsing | B |
| 12 | B | Reddit sentiment | B |
| 13 | B | URL safety + page flags | B |
| 14 | B | Scoring engine + golden tests | A |
| 15 | B | Recommendation engine | A, C |
| 16 | A | Wire checks → score → recommend | C |
| 17 | C | Frontend shell, types, API client | C |
| 18 | C | Discovery flow | C |
| 19 | C | Results grid, cards, badges, check rows | C |
| 20 | A | Multiplexed SSE hook | C |
| 21 | C | Best pick, purge, empty/error states | C |
| 22 | A | Payability guard + mandates | A |
| 23 | A | Mock VIC + checkout/confirm routes | C |
| 24 | A | Receipt service + routes | C |
| 25 | C | Checkout UI: mandate, passkey, processing | C |
| 26 | C | Receipt UI + share page | C |
| 27 | B | Mongo repositories, caches, audit, redaction (D-016) | A |
| 28 | B | Demo mode, fixtures, offline replay | All |
| 29 | A | VEYZL audit + docs (D-020) | All |
| 30 | C | Video, screenshots, Devpost visuals | All |

**Shared:** B owns the Devpost and its technical claims (the checks, scoring, and payability rule are B's area); A reviews every technical claim before submission; C owns visuals and the video edit.

---

## First 45 minutes — 12:30–1:15 PM (all three)

This is the highest-leverage block. Do not spend it discussing the name or the logo.

- [v ] **A:** `git init`, `.gitignore`, `ATTRIBUTION.md`, FastAPI scaffold, `GET /api/health`, deploy to Fly.io. **First commit by 12:45.**
- [v ] **A:** `backend/app/domain/models.py`, `enums.py`, `ids.py` from plan §5.
- [ v] **A:** SerpAPI spike: one real query, confirm product URLs carry merchant domains. If not, decide "catalog only" now and tell B.
- [ ] **B:** `data/catalog.json` — 8 trusted listings across 5 merchants + 1 fictional villain on `premium-audio-deals.shop`.
- [ ] **B:** `data/allowlist.json` — 30–40 established retailer domains.
- [ ] **B:** Villain fixtures: `villain_rdap.json` (12-day domain), `villain_page.html` (urgency copy, no return policy, crypto-only note), `villain_reddit.json` (3 scam reports).
- [ ] **C:** Vite + React + TypeScript + Tailwind + shadcn/ui running locally.
- [ ] **C:** `frontend/src/lib/types.ts` mirroring the Pydantic models; `data/mock-session.json` with 8 listings and fake checks.
- [ ] **C:** App shell with the product name, a discovery placeholder, and the sandbox badge.
- [ ] **All:** Read `docs/contracts.md` aloud once. Freeze it. Anyone who disagrees speaks now.

**Gate 1:15:** health URL works; contracts frozen; SerpAPI go/no-go recorded; three commits on `main`.

---

## Person A — Platform / Agent

### 1:15–3:30 PM — sessions and streaming

- [x] Task 5: `SessionRegistry`, `POST /api/sessions`, `POST /{id}/answers`, `GET /{id}`.
- [x] Task 6: `EventBus` + `GET /api/sessions/{id}/events`; replay by `Last-Event-ID`.
- [x] Task 7: orchestrator skeleton, `search.started` → `listing.found` → `investigation.complete`.
- [x] Post the event schema in `docs/contracts.md` and tell C.

**Done when:** `curl -N` on a session shows ordered events and closes cleanly.

### 3:30–6:00 PM — orchestration and the payment gate

- [x] Task 16: fan out B's `get_checks()`, emit `check.started/completed`, call `score_investigation`, emit `listing.scored` and `recommendation.ready`.
- [x] Task 22: `assert_payable`, `PayabilityCode`, `create_mandate`, every 409 path tested.
- [x] Send C the exact checkout/confirm JSON.

**Done when:** one real session streams five checks and a score; a caution listing is refused with `MERCHANT_NOT_TRUSTED`.

### 6:00–7:30 PM — checkout backend

- [x] Task 23: `POST /api/checkout`, `POST /{id}/confirm`, mock VIC token issue/consume, atomic transition, idempotency.
- [x] Task 24: `create_receipt`, HMAC signature, `GET /api/receipts/{id}`, `GET /api/public/receipts/{share_id}`.

**Done when:** create → confirm twice returns the same receipt; decline path returns 402.

### 7:30–9:00 PM — persistence (moved to B)

- Task 27 was built on `agent_backend` by A: `InMemoryRepository` + `MongoRepository`, TTL indexes, `transition_checkout` via `find_one_and_update`.
- [x] Verified the app still runs with `MONGODB_URI` unset.
- As of D-016 the task and its review belong to B. B reviews the `Repository` protocol in Block 6 and keeps Mongo types from leaking into `app/`.

### 9:00–10:30 PM — integration and Devpost draft

- [x] Sit with C and wire the real checkout into the real UI.
- [x] Fix the first three integration bugs; do not start new features.
- [x] Give B the technical claims for the Devpost by 10:00.

### 10:30 PM–2:00 AM — hardening

- [ ] Task 23 hardening: stale investigation, double-confirm, amount cap, merchant mismatch.
- [ ] Task 24 share link + receipt immutability test.
- [ ] Backend test suite green.

### 2:00–4:00 AM — freeze

- [ ] Run the offline replay script.
- [ ] Feature freeze at 2:00 AM. Only bugfixes after this.
- [ ] Sleep 4:00–8:00.

### Sunday 8:00–9:50 AM

- [ ] Final health check and smoke test on the deployed URL.
- [ ] Review Devpost technical claims and the sandbox disclosure.
- [ ] Rehearse the demo twice; warm the backend at 9:30.
- [ ] Submit by 9:50.

---

## Person B — Trust / Data

### 1:15–3:30 PM — search, runner, first check

- [ ] Task 4: SerpAPI adapter + catalog fallback; reject results without merchant domains.
- [ ] Task 8: `TrustCheck` protocol + `run_checks` with per-check timeouts and `skipped` mapping.
- [ ] Task 9: domain age via RDAP, WHOIS fallback.
- [ ] Agree with A on the `TrustCheckResult` shape and the scoring constants.

### 3:30–6:00 PM — the remaining checks and scoring

- [ ] Task 10: SSL certificate check.
- [ ] Task 11: Safe Browsing + static denylist fallback.
- [ ] Task 12: Reddit sentiment, keywords only, usernames never stored.
- [ ] Task 13: `validate_public_url` (SSRF) + page flags.
- [ ] Task 14: scoring engine + coverage rule + golden tests.
- [ ] Task 15 if time permits; otherwise 6:00–6:30.

**Done when:** the villain's five checks produce `danger` and the hero produces `trusted`, with no network in the golden tests.

### 6:00–7:30 PM — recommendation and demo fixtures

- [ ] Task 15: cheapest-trusted recommendation + median + no-trusted option.
- [ ] Task 28: villain fixtures wired behind `DEMO_MODE=1`; hero and villain always present.
- [ ] Golden test: villain ≤ 31/danger; hero ≥ 90/trusted.

### 7:30–9:00 PM — demo mode and Devpost

- [ ] `scripts/replay_offline.py` with `OFFLINE=1`; `scripts/smoke_sse.py`.
- [ ] Start the Devpost draft: problem, solution, tracks, stack, what's mocked.
- [ ] Tell C which three screenshots the Devpost needs.

### 9:00–10:30 PM — **Devpost draft submitted by 10:30**

- [ ] Fill every required field; mark the Visa track; select up to 3 sponsored tracks.
- [ ] State plainly: sandbox payment, synthetic data, no production Visa integration.
- [ ] Submit the draft. Screenshots can be replaced later.

### 10:30 PM–2:00 AM — VEYZL, docs, and persistence (Block 6)

- [ ] Task 29 (**A** as of D-020): install the VEYZL app on `KF8311/Dubhacks`, run the audit on a PR, pick one real finding, fix it, write `docs/veylz-audit.md`. B's scope and the reproduced `/api/demo/reset` transcript are already in that file.
- [ ] `README.md`: setup, env vars, demo script, mock disclosure.
- [ ] **Task 27 (owned by B as of D-016):** `InMemoryRepository` + `MongoRepository` behind the same protocol, TTL indexes, cache collections, PII redaction, `transition_checkout` via `find_one_and_update`.
- [ ] Verify the app still runs with `MONGODB_URI` unset — the in-memory adapter is the default and the cut-order survivor.

### 2:00–4:00 AM — freeze

- [ ] Offline replay from a clean checkout.
- [ ] Confirm every fixture-sourced check carries `source: "fixture"`.
- [ ] Sleep 4:00–8:00.

### Sunday 8:00–9:50 AM

- [ ] Final Devpost fields: stack list, track selections, repo link.
- [ ] Paste the audit evidence and the health URL.
- [ ] Rehearse the trust explanation (why skipped ≠ passed).

---

## Person C — Frontend / UX

C builds against mocks from 1:15 PM. Do not wait for the backend.

### 1:15–3:30 PM — shell and results against mock data

- [ ] Task 17: shell, `types.ts`, `api.ts`, Zustand store.
- [ ] Task 18: discovery flow (query → 2–3 questions → submit).
- [ ] Task 19: results grid, product cards, `TrustBadge`, `CheckRow`.
- [ ] Design tokens: trusted green, caution amber, danger red, pending gray; WCAG AA contrast.
- [ ] Use `data/mock-session.json` so the UI renders without the API.

**Done when:** the full discovery → results flow works offline with fake checks.

### 3:30–6:00 PM — the stream and the pick

- [ ] Task 20 with A: `useSessionStream`, `seq` dedupe, reconnect, snapshot fallback, StrictMode cleanup.
- [ ] Task 21: best pick, savings, purge overlay, empty/error states.
- [ ] Start the checkout sheet shell with a disabled pay button.

**Done when:** mock events animate the grid; a `danger` card can be purged; the best pick is highlighted.

### 6:00–7:30 PM — checkout and receipt UI

- [ ] Task 25: mandate card, simulated passkey dialog, three-step processing state, inline errors.
- [ ] Task 26: receipt page, score ring, verified/unverified lists, copy-link button.
- [ ] Keep the sandbox badge visible on both screens.

**Done when:** mocked checkout → receipt works end to end in the browser.

### 7:30–9:00 PM — full-stack integration (highest risk)

- [ ] Replace `mock-session.json` with the real `POST /api/sessions`.
- [ ] Replace mock events with the real `EventSource`.
- [ ] Replace mock checkout with the real `POST /api/checkout` and `/confirm`.
- [ ] Fix layout breakage from real data (long titles, missing images, 8 cards).
- [ ] Ask A to sit with you for the first 30 minutes.

**Done when:** a real session → real checks → real checkout → real receipt, with no mock data on screen.

### 9:00–10:30 PM — screenshots and polish

- [ ] Capture results, trust card, checkout, receipt for B's Devpost draft.
- [ ] Fix contrast, focus states, and the 1024px layout.
- [ ] Add the `prefers-reduced-motion` fallback for the purge animation.

### 10:30 PM–2:00 AM — visual hardening

- [ ] Purge animation, skeleton rows, empty states, error banners.
- [ ] Receipt share page at `/r/:shareId`; 404 state.
- [ ] No horizontal scroll at 1024px or 1280px.

### 2:00–4:00 AM — freeze and backup video

- [ ] Record a backup screen capture of the full happy path.
- [ ] Feature freeze at 2:00 AM.
- [ ] Sleep 4:00–8:00.

### Sunday 8:00–9:50 AM

- [ ] Record the final 3-minute video: problem → discovery → stream → purge → best pick → checkout → receipt.
- [ ] Capture the final screenshots.
- [ ] Rehearse the on-screen story twice.
- [ ] Submit by 9:50.

---

## Shared gates

| Time | Gate | Proof |
|---|---|---|
| 12:45 | First commit | `git log` timestamp |
| 1:15 | Contracts frozen + health deployed | URL + `docs/contracts.md` |
| 3:30 | Listings stream to the browser | Screen recording or live `curl -N` |
| 6:00 | One full investigation with 5 checks and a score | Browser |
| 7:30 | Recommendation and best pick | Browser |
| 9:00 | Checkout → passkey → receipt | Browser, real backend |
| 10:30 | Devpost draft submitted | Devpost confirmation |
| 2:00 AM | Feature freeze | Team agreement in writing |
| 9:50 AM | Final submission | Devpost confirmation |

---

## Handoffs you must not miss

| From → To | Artifact | By |
|---|---|---|
| A → C | SSE event schema + runnable `/events` | 3:30 PM |
| B → A | `get_checks()`, `score_investigation`, `recommend` signatures | 3:30 PM |
| B → A | Real check implementations + scoring | 6:00 PM |
| A → C | Checkout/confirm request + response JSON | 6:00 PM |
| A → C | Receipt JSON + share URL shape | 7:30 PM |
| C → B | Screenshots for Devpost | 9:00 PM |
| B → A | Devpost technical claims to review | 10:00 PM |

If a handoff is late, the receiver works against the contract in `docs/contracts.md` and flags it at the next sync. Do not block.

---

## Cut assignments if you fall behind

Cut in this order, per owner. Announce the cut in the channel so nobody waits for it.

**Backend behind (A or B):**
1. Live page fetching (Task 13) → fixtures only; keep the check card.
2. Live Reddit (Task 12) → fixture only.
3. SerpAPI (Task 4) → catalog only.
4. MongoDB (Task 27) → in-memory adapter; keep the repository interface.

**Frontend behind (C):**
1. Purge animation (Task 21) → instant removal.
2. Share page (Task 26) → keep the receipt on screen.
3. Fancy processing animation (Task 25) → a single spinner.

**Payments behind (A):**
1. Share link → receipt stays on screen.
2. Audit events → keep the state machine.
3. Never cut the payability guard, the atomic transition, or the idempotency check.

**Never cut, by anyone:** Task 14 scoring, Task 20 SSE, Task 23 checkout, the sandbox label.

---

## If only two people show up

- A takes A + payments (already does).
- B takes B + Task 17 (shell/types) and Task 20 (SSE hook).
- Drop Tasks 12, 13 live fetching, 21, 26 share page, 29 VEYZL.
- The demo is: discovery → 3 checks → score → best pick → checkout → receipt on screen.

## If a fourth person joins

Give them C's Task 19 + 21 (results grid, best pick, purge) and let C focus on checkout/receipt and the video. Do not give them the database or the payment flow; those are on the critical path and already owned.
