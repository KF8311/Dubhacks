---
title: Team Checklist
type: checklist
updated: 2026-10-17
owner: everyone
---

# Team Checklist

One shared checklist. Personal scratch notes do not belong here.

**How to use it:** Section 1 is once per machine. After that, work the timed block you are in — each block has a column per person and a proof you have to produce before moving on. Tick boxes in the commit that completes them. `docs/status.md` still wins if the two disagree.

> **This is the live working document.** `docs/team-split-3.md` is the original ownership map and task numbering — useful for "who owns Task 23" and the cut order, not for "what do I do next." When the two disagree, this file and `status.md` win.

## Where we are now — 19:10 PT · **Block 4 closed, Block 5 running**

| Thing | State |
|---|---|
| `main` | **Everything merged** (`3038c6b`): scaffold, session routes, SSE, `search()`, all five checks, `score_investigation()`, `recommend()`, orchestrator fan-out, payability guard, checkout/confirm, receipts, the live frontend, the offline replay, the frozen refusal paths, **Gemini questions/narration/explanations (D-017–D-019)**, and **the `Repository` protocol with in-memory + Mongo adapters**. **177 backend / 26 frontend tests pass**, `npm run build` clean, `scripts/replay_offline.py` exits 0. |
| Follow-on branch | **None. `main` is the source of truth** — branch from it. `scratch/integration` is stale; do not reuse it. |
| Live API | Sessions create/answers/snapshot/events/**explain**, orchestrator fan-out, payability guard and mandates, **checkout/confirm**, **receipts + public share**, `POST /api/demo/reset`. |
| Frontend | Live by default, and the checkout sheet + receipt page call the live endpoints. `?mock=1` (or `VITE_USE_MOCK=1`) runs the whole UI, including checkout, from `data/mock-session.json`. |
| Gates | G0 partial (health live, contracts not frozen). **G1, G2, G3 proven server-side and wired in the browser client.** **G4 is built and merged end to end**; its gate proof (one browser click-through) is the first action of Block 5. **G5 is open**: the stories are written, the artifacts are not. |
| Dead branches | `b/trust`, `richard-dev`, `2026-10-17-6c1c`, `b/recommendation`, `b/domain-age`, `b/ssl-safe-browsing`, `b/page-flags`, `b/reddit-sentiment`, `agent_backend`, `c/web`, `merge/agent-backend`, `integration/hookup`, `integration/block4`, `integration/block4-ui`, `b/block4-refusals`, `b/block5-devpost`, `b/block5-veylz-audit`, `b/mongo-ownership` all merged into `main`. `scratch/integration` is stale (main is ahead of it) — do not reuse it. |

**Before anyone starts:** `git checkout main && git pull`. There is nothing left to merge — if you are on an older branch, rebase onto `main` before writing code.

**Recovery stance:** G1 was 45 minutes late, not lost. Do not skip a block's proof to catch up — the proofs are the gate.

---

## 1. Universal — once per machine

- [ ] Open **`Dubhacks/`** as the working directory, not `Desktop/dubhacks/`. Skills load from `.claude/skills/` in the folder the session starts in.
- [ ] `git fetch origin && git checkout main && git pull` — then `git checkout -B <your-branch> origin/main`. Everyone starts from current `main`.
- [ ] Read `docs/status.md`, then `CLAUDE.md`, then `docs/INDEX.md`.
- [ ] Backend venv (Python 3.11 or 3.12, **not** 3.14):
  ```bash
  cd backend && python -m venv .venv
  .venv/Scripts/python -m pip install -r requirements.txt
  ```
- [ ] Frontend deps: `cd frontend && npm ci`.
- [ ] Baseline both suites before you change anything: `pytest -q` → **153 passed**; `npx vitest run` → **22 passed**. If your baseline differs, stop and ask — someone's work is missing.

## 2. Universal — every commit

- [ ] Tests pass. Run them; paste the output when you claim a task is done.
- [ ] **No AI attribution.** No `Co-Authored-By`, no "Generated with" trailers. Commits carry your name only.
- [ ] Commit every 30 minutes. `feat:`, `fix:`, `docs:`, `chore:`.
- [ ] You touched only your own files. `backend/app/domain/models.py`, `frontend/src/lib/types.ts`, and `docs/contracts.md` belong to their owner.
- [ ] No secrets, no real PII, no real card numbers, no raw tokens.
- [ ] Fixture-sourced results carry `source: "fixture"`.

## 3. Universal — every gate

- [ ] Run the real command or the real browser path before claiming the gate passed. A green unit test is not a gate proof.
- [ ] Update `docs/status.md`: gate, owners, blockers, live risks.
- [ ] Append to `docs/decisions.md` if you changed a decision.
- [ ] Push by :57 of each block. The next block starts from pushed code, not local code.

---

## 4. Timed blocks

Five-minute sync at the end of each block: each person says *done / blocked / next*, one scribe updates `status.md`, everyone pushes.

### Block 1 — 16:15–17:00 · Recover G1: listings reach the browser

**Goal:** a real HTTP request produces real listing events that render as cards.

| Person | Do |
|---|---|
| **A** | ✅ **Done** — session routes, SSE, orchestrator, event bus (PR #3). ✅ **Task 16** — orchestrator calls `run_checks()` then `score_investigation()` per listing with bounded concurrency, emits `check.started/completed`, `listing.scored`, `recommendation.ready`. Remaining: parse a budget out of free text (`"under $300"` currently yields `budget_max_cents: null`). |
| **B** | ✅ **Task 4** — `search(spec, limit)` in `app/search/service.py`, catalog fallback on any provider fault, budget filter. ✅ **Task 14** — `score_investigation()` with golden tests. ✅ **Task 15** — `recommend()` with the D-015 allowlist exemption. ✅ **Tasks 9–13** — all five checks implemented and tested. |
| **C** | ✅ **Done** — `api.ts` honours `VITE_API_BASE_URL`; `sse.ts` + `useSessionStream` consume `listing.found` over `EventSource`; mock is now opt-in via `?mock=1`, so a dead backend still never kills the demo. |

**Proof:** `curl -N http://127.0.0.1:8000/api/sessions/<id>/events` shows `seq` incrementing and 9 `listing.found` events; the same cards render in the browser.

**Server-side proof captured:** 9 `listing.found` events (8 trusted + villain), `source: "catalog"`, stream closes on `investigation.complete`. What is still unproven is the **browser** half — that is C's step.

**If late:** ship the snapshot route first (`GET /api/sessions/{id}` with listings) and stream second. The browser only needs one of them to pass this gate.

### Block 2 — 17:00–18:00 · G2: full investigation, five checks, a score

**Goal:** the villain card turns red on screen, for a stated reason.

| Person | Do |
|---|---|
| **A** | ✅ **Done** — for each listing calls `run_checks()`, then `score_investigation()`, emits `check.started`, `check.completed`, `listing.scored`. `CHECK_CONCURRENCY = 8` bounds the fan-out. |
| **B** | ✅ **Task 9** domain age (RDAP → WHOIS), ✅ **Task 10** SSL, ✅ **Task 13** URL validation + page flags, ✅ **Task 11** Safe Browsing with the static denylist (no key), ✅ **Task 12** Reddit sentiment. |
| **C** | ✅ **Done** — `CheckRow` consumes `check.completed` and upserts by `(listing_id, check_id)` through the store; a missing check renders as a skeleton, and `skipped` renders as "Skipped", never a green tick. Remaining polish: label `skipped` as "Could not verify" and name the failed checks on a danger card. |

**Proof:** browser — `premium-audio-deals.shop` shows `danger` with at least domain age and page flags named, and at least one big merchant shows `trusted`.

**Server-side proof captured:** 45 `check.completed` across 9 listings; `premium-audio-deals.shop` scores `0 / danger` on `LOCAL_DENYLIST` plus domain age and Reddit; the eight safe listings are `trusted`.

**If late:** cut page flags (Task 13) before SSL or domain age. Three checks still clears the coverage floor.

### Block 3 — 18:00–19:30 · G3: recommendation

**Goal:** one pick, justified, and the villain is not it.

| Person | Do |
|---|---|
| **A** | ✅ **Done** — emits `recommendation.ready`, exposes the recommendation in the snapshot. Remaining: wire `POST /api/demo/reset` to clear the session registry. |
| **B** | ✅ **Task 15** `recommend()` done — eligible = trusted ∧ (≥70 ∨ allowlisted) ∧ confidence ≥0.6 (D-015); median of eligible; `no_trusted_option` names the best near-miss. ✅ **Task 12** Reddit sentiment. |
| **C** | ✅ **Done** — `BestPick` banner with median/savings, best pick lifted to the top of the grid, `EmptyState` for `no_trusted_option`. Remaining: a "why this one" panel naming which checks each candidate passed. |

**Proof:** browser — the cheapest *trusted* listing is the pick, the villain's lower price is visibly rejected with a reason, and savings matches the median minus the pick.

**Server-side proof captured:** pick `lst_tgt_bsp` ($179.99), median `$374.49`, savings `$194.50`; `lst_vln_xm5` is cheaper but `danger`, so it is not eligible.

**If late:** cut Reddit (Task 12). The recommendation math does not depend on it.

### Block 4 — 19:30–21:00 · G4: checkout — ✅ **CLOSED**

**Goal:** click through to a receipt against the real backend.

| Person | Do |
|---|---|
| **A** | ✅ **Done** — mandate → simulated passkey → one-time token → transaction → receipt. Server re-validates: `trusted` ∧ score ≥70 ∧ (allowlisted ∨ ≥3 checks). Atomic transitions, idempotency key, `processor: mock-vic`, `mode: sandbox`. Raw token never stored — SHA-256 and last4 only. |
| **B** | ✅ **Done** — golden values frozen: payability constants, the 30-minute stale boundary, and every refusal code. Refusal paths verified against the **real demo data**: villain → `MERCHANT_NOT_TRUSTED`, stale investigation → `INVESTIGATION_STALE`, cap exceeded → `AMOUNT_EXCEEDS_CAP`; the real allowlisted hero pays. No-LLM guard: `test_no_llm_path.py` fails if any module imports a generative client or reads the Gemini key outside config. |
| **C** | ✅ **Done** — checkout sheet (cap, sandbox banner, passkey step, disabled when not payable, server's `PayabilityCode` shown), receipt page (merchant, checks, score, last4 only, sandbox line), `/r/:share_id` route. |

**Proof:** ✅ server half captured — `POST /api/checkout` 201 → `/confirm` 200 → `GET /api/public/receipts/{share}` 200 with last4 `4242`; villain refused `409 MERCHANT_NOT_TRUSTED`; the frontend's wire shapes are pinned in `src/lib/api.test.ts`. ⬜ **browser half carries into Block 5** — nobody has clicked the merged UI yet.

**If late:** a receipt is the demo's closing image. Cut Mongo and Reddit before you cut this.

### Block 5 — 21:00–22:30 · G5: Devpost draft — ▶ **CURRENT BLOCK** (detail in §9)

| Person | Do |
|---|---|
| **A** | `fly deploy` from current `main` so the live app matches the repo. Confirm the health URL and a real session over the public URL. Then `smoke_http.py` against it. This is the only thing G5 is waiting on from A. |
| **B** | ✅ Devpost story, README, and `docs/devpost-form.md` written. ⬜ Task 29: run VEYZL on a PR, reproduce one finding, fix it with a test, write the before/after. Then fill the Devpost placeholders and `docs/status.md`. |
| **C** | Three screenshots — results grid, danger detail, receipt — and one screen recording of the full path. This is the only thing G5 is waiting on from C. |

**Proof:** Devpost draft saved with the URL, the screenshots, and the sandbox label visible in the copy.

### Block 6 — 22:30–02:00 · G6: harden and freeze

| Person | Do |
|---|---|
| **A** | Review the merged `Repository` protocol that A built on `agent_backend` — confirm no Mongo type leaks into `app/` and that `MONGODB_URI` unset stays the default. Then freeze: no new features after 02:00. |
| **B** | **Task 27 review (D-016)** — A's `InMemoryRepository` + `MongoRepository` are now on `main`; B owns the review, the Atlas cluster question, and the MLH MongoDB claim. **Only** if every Block 5 item is green: add TTL index verification, redaction checks, and a `MONGODB_URI`-unset regression test. Otherwise skip — the in-memory adapter is the cut-order survivor. ✅ Replay half already done — 9 listings, 8/0/1, villain `danger`, pick `lst_tgt_bsp`, median `$374.49`, savings `$194.50`, exit 1 on drift. |
| **C** | Phone-width reflow, loading and error states, `?mock=1` fallback path, reduced motion. |

**Block 6 required before freeze:**

- [ ] Every claim in `README.md` and `docs/devpost.md` matches the merged code — Gemini is in the questions/narration/explain path (D-017–D-019), not in scoring; the devpost's generative-AI answer is **Yes**, not N/A.
- [ ] `pytest -q` green with **no** `GEMINI_API_KEY` and `OFFLINE=1` — the template fallback is the demo path.
- [ ] `scripts/replay_offline.py` exits 0 and prints the frozen numbers.
- [ ] `npm run build` clean; `?mock=1` renders the whole flow.
- [ ] No `.env` or key is tracked (`git ls-files | grep -i env`).
- [ ] Devpost fields in `docs/devpost-form.md` all filled; VEYZL selected as a Sponsored Side Track.
- [ ] `docs/status.md` updated with the final numbers.

**Proof:** offline replay produces the same numbers as live; plane-mode demo works.
**2:00 AM: freeze.** After this, docs and bugfixes only.

### Block 7 — Sunday 08:00–09:50 · G7: submit

- [ ] Wake the Fly machine; hit `/api/health` until it returns 200.
- [ ] Rehearse offline path once.
- [ ] Every Devpost claim true: sandbox payment, synthetic data, no production Visa integration.
- [ ] Say out loud: "no unprotected checkout" — then show the refusal.
- [ ] Submit by **09:50**. Capture the confirmation.

---

## 5. Already done — do not redo

- [x] B: catalog (9 listings, 8 trusted + villain), 36-domain allowlist, villain fixtures
- [x] B: `TrustCheck` protocol, registry, timeout-safe runner — 3 tests
- [x] A: backend scaffold, config/ids/logging/timeouts, health route, Fly deploy
- [x] C: frontend scaffold, discovery flow, results grid, trust badges, mock session — 4 tests
- [x] All branches merged into `main`; `main` and `c/web` both green
- [x] B: **Task 4** — `search()` with catalog fallback, budget filter, limit guard — 8 tests
- [x] B: **Task 14** — `score_investigation()` with fatal rules, coverage cap, golden tests — villain `0 / danger`, hero `100 / trusted` — 17 tests
- [x] B: **Task 15** — `recommend()` with `Recommendation`, median/savings, `no_trusted_option` — 9 tests; allowlisted listings are eligible at score 0 (D-015)
- [x] A: session routes, SSE stream, orchestrator, event bus — 7 integration tests (PR #3)
- [x] A: **Task 16** — orchestrator fan-out (`run_checks` → `score_investigation` → `recommend`), per-listing `check.started/completed`, bounded concurrency
- [x] A: **Task 22** — `assert_payable`, `PayabilityCode` 409, `create_mandate`, `MandateDraft` — 10 tests
- [x] B: **Task 9** domain age (RDAP → WHOIS) — 9 tests; **Task 10** SSL — 10 tests; **Task 11** Safe Browsing + denylist — 6 tests; **Task 12** Reddit sentiment — 8 tests; **Task 13** URL safety + page flags — 23 tests
- [x] Fix: `MAX_LISTINGS` was 8, silently dropping the ninth catalog entry (the villain). Raised to 9 with a regression test.
- [x] G1/G2/G3 server proofs: 9 `listing.found`, 45 `check.completed`, 9 `listing.scored`, one `recommendation.ready`; villain `0 / danger`, pick `lst_tgt_bsp`
- [x] C: **Tasks 17–21** — `EventSource` client with seq dedupe and snapshot fallback, results grid, `CheckRow`, `BestPick`, purge overlay, empty/error states — 9 frontend tests
- [x] Hookup: mock is opt-in (`?mock=1` or `VITE_USE_MOCK=1`); the live API is the default
- [x] Hookup fix: discovery submitted to a hardcoded `ses_mock`, so the live flow 404'd on the answers step. It now uses the session id the server returned, pinned by `DiscoveryFlow.test.tsx`.
- [x] Hookup fix: allowlisted merchants rendered as `0 · Trusted`. `listing.scored` now carries `allowlisted` and the badge reads `Verified · Trusted` (D-015 display consequence).
- [x] CORS verified for `http://localhost:5173` on both the JSON routes and the SSE stream
- [x] **All merges landed** — PRs #9, #10, #11 into `main`; that merge was green
- [x] B: **Block 4 refusal paths** — real villain/host data through `assert_payable`; danger, low confidence, low coverage, missing investigation, currency, cap, and the 30-minute boundary pinned; no-LLM source guard (`test_refusal_paths.py`, `test_no_llm_path.py`)
- [x] B: villain integration golden test — real checks → `danger` → excluded from `recommend()` even when cheapest (`tests/integration/test_villain_end_to_end.py`)
- [x] A: **Tasks 23–24** — `POST /api/checkout`, `POST /api/checkout/{checkout_id}/confirm`, HMAC-signed receipts, public share route, `POST /api/demo/reset` (PR #13)
- [x] C: **Tasks 25–26** — checkout sheet, mandate card, passkey dialog, processing state, receipt page, `/r/:share_id` route (PR #14)
- [x] Hookup: C's client sends the contracted `mandate` and full passkey assertion, follows `receipt_url` to the public receipt, and renders the server's `PayabilityCode`; `src/lib/api.test.ts` pins every request and response shape against the live routes (PR #14)
- [x] B: **Task 28** — `app/demo/replay.py` + `scripts/replay_offline.py`. Reports `9 / 8 / 0 / 1`, villain `lst_vln_xm5`, pick `lst_tgt_bsp`, median `$374.49`, savings `$194.50`, identical to the live HTTP run; exits 1 on drift. `SessionOrchestrator` takes an optional `Settings` and domain age + SSL short-circuit on `offline`. 7 new tests.
- [x] B: refusal messages are human copy, not bare codes; `CheckoutSheet` renders `PayabilityCode` + message (PR #14)
- [x] B: `README.md` rewritten; `docs/devpost.md` drafted; `docs/veylz-audit.md` scaffolded (PR #17)
- [x] A: **Gemini** — questions, recommendation narration, on-demand check explanations, 2.5 s timeout, template fallback; trust/check/payment modules still cannot import it (`test_no_llm_path.py`) — D-017–D-019
- [x] A: **`Repository` protocol** — `InMemoryRepository` + `MongoRepository`, TTL indexes, atomic `transition_checkout`; `MONGODB_URI` unset stays the default (B reviews in Block 6, D-016)
- [x] C: `c/web` — 1024px layout, reduced motion, purge overlay test; second commit lets allowlisted merchants through checkout (D-015)
- [x] Merge reconciliation: A's three Gemini decisions were renumbered D-017/D-018/D-019 because D-016 was already Mongo ownership; `README.md` and `docs/devpost.md` corrected to say the model writes copy but never decides

## 6. Gate board

| Gate | Due | State | Owner |
|---|---|---|---|
| G0 Contracts frozen + health | Sat 13:15 | 🟡 health live, `Question` shape needs A's sign-off | A |
| G1 Listings to browser | Sat 15:30 | 🟢 live `EventSource` client wired; one browser screenshot still owed | A + B + C |
| G2 Investigation + score | Sat 18:00 | 🟢 server proof + `check.completed` rendering; browser click-through owed | A + B + C |
| G3 Recommendation | Sat 19:30 | 🟢 server proof + `BestPick` and best-pick ring; browser click-through owed | A + B + C |
| G4 Checkout → receipt | Sat 21:00 | 🟡 **build complete and merged**; browser click-through is Block 5's first action | A + C |
| G5 Devpost draft | Sat 22:30 | 🟡 stories written; URL, screenshots, video, and VEYZL evidence pending | B |
| G6 Freeze | Sun 02:00 | ⬜ | all |
| G7 Submit | Sun 09:50 | ⬜ | all |

## 7. Live blockers

| Blocker | Owner | Impact |
|---|---|---|
| Fly serves the pre-merge build | A | Redeploy from the repo root so the public URL carries checkout and receipts. **First action of Block 5.** |
| No browser click-through yet | C | The live wiring is merged but has never rendered in a real browser; one run closes G1–G4 for good. **First action of Block 5.** |
| "Under $150" empties the trusted set | C | Demo run must answer **$150–$300**; see §9 |
| Contracts not frozen | A | `Question` shape is a guess; cheap to confirm, expensive to discover at 21:00 |
| SerpAPI key | A | Catalog only (D-011). Not blocking. |
| Safe Browsing key | B | Static denylist with `source="unavailable"`. Not blocking. |
| Mongo deferred to Block 6 (D-016) | B | In-memory is the default; A's `MongoRepository` is merged but unreviewed. Not blocking. |
| VEYZL check has not run on a PR yet | B | The app must be installed and the project created before the fix PR opens; without a visible check run the side track is not eligible. |
| `GEMINI_API_KEY` absent on Fly | A | The app falls back to templates; the demo still works, but the narration is deterministically worded. Set it only if the fallback copy reads worse on stage. |
| Local venv missing `motor` | everyone | `pip install motor`; it is in `requirements.txt`. Without it one repository test fails to import. |

## 8. Cut order

Cut in this order: live page fetching → Reddit → SerpAPI → Mongo → page flags.

## 9. Block 5 — G5 Devpost draft · start here

**State:** **Block 4 is closed and Block 5 is running.** `main` is at `3038c6b` and carries everything from all three people: checkout → confirm → receipt, C's checkout sheet and receipt page, C's responsive/reduced-motion fixes, and A's `agent_backend` work (Gemini questions/narration/explanations, `InMemoryRepository` + `MongoRepository`, health/session hardening). Green on merge: **177 backend / 26 frontend tests**, `npm run build` clean, offline replay exits 0.

**What changed since Block 4 closed, and what it means:**

- **Gemini is now in the app** (D-017–D-019): it writes the clarifying questions, the one-line recommendation narration, and on-demand check explanations. Every call has a 2.5 s timeout and a template fallback. It is **not** in scoring, checks, payability, or checkout — `test_no_llm_path.py` still enforces that.
- **The Devpost answer to "did you implement a generative AI model or API?" is therefore Yes, not N/A.** `README.md` and `docs/devpost.md` have already been corrected; do not reintroduce "no model anywhere in the request path."
- **Mongo now exists in the code** (A built Task 27 on `agent_backend`). `MONGODB_URI` unset remains the default. B owns the review and the MLH MongoDB claim in Block 6 (D-016).
- **C's allowlisted-merchant checkout fix** is merged — a curated merchant at score 0 can pay, matching D-015.

Two Block 4 items carry over, both small and both first-in-line here:

- **G4's gate proof** — one browser click-through of the merged flow. The build is done; the screenshot is not.
- **Fly still serves the pre-merge build** — until A redeploys, the public URL does not carry checkout.

**First 15 minutes of this block, every person:**

1. `git checkout main && git pull`
2. Run your baseline: backend `pytest -q` → **177 passed**; frontend `npx vitest run` → **26 passed**; `backend/.venv/Scripts/python.exe scripts/replay_offline.py` → exit 0. If `motor` is missing, `pip install motor` (it is in `requirements.txt`).
3. Say out loud what you are taking from the lists below, then work top to bottom. Each person owns their column; nobody waits on another column.

**Your next action, in one line:**

| Owner | Next action | Unblocks |
|---|---|---|
| **A** | `fly deploy` from the repo root, then `backend/scripts/smoke_http.py` against the public URL | G4 on the public URL |
| **C** | Click the live flow through to a receipt and screenshot the grid + receipt | G1–G4 proof |
| **B** | Run VEYZL on the fix PR, reproduce one finding, patch it, write `docs/veylz-audit.md`; then fill `docs/devpost-form.md` | G5 |

**Handoff contract, now live (do not improvise this):** every refusal is `409` with `{"code": <PayabilityCode>, "message": <human string>, "details": {...}}`; a declined passkey is `402 PAYMENT_DECLINED`. The confirm path is **`POST /api/checkout/{checkout_id}/confirm`** (singular `checkout`) and takes `{passkey_assertion: {credential_id, client_data}, idempotency_key}`. Confirm returns a **pointer** (`receipt_id`, `receipt_url`); the receipt itself is `GET /api/public/receipts/{share_id}`. Every response carries `processor: "mock-vic"`, `mode: "sandbox"`, and the sandbox label. The frontend's request/response mapping is pinned in `frontend/src/lib/api.test.ts` — if the shape has to change, say it in the channel before committing.

### A — ship the public URL

Block 4's backend is merged. Only deployment remains:

1. `fly deploy` from the **repo root** (that is where `fly.toml` lives; deploying from `backend/` ships a stale image).
2. Run `backend/scripts/smoke_http.py` against the public URL: health, session, 9 listings, checkout, confirm, public receipt.
3. Free-text budget parsing — `"under $300"` currently yields `budget_max_cents: null`. Nice-to-have; skip it if anything above is red.
4. Close the last contract item: sign off the `Question` shape in `docs/contracts.md` (G0).

**Proof:** the public health URL plus a checkout and receipt on the public URL; `pytest -q` still 177.

### C — close the gate

The screens are merged. This block is about proving them in a real browser:

1. Run `uvicorn app.main:app --port 8000 --workers 1` and `npm run dev`, open `http://localhost:5173`, answer **$150–$300**. Confirm: villain card red with its five rows named, `Best pick` = Target $179.99 with $194.50 savings. **Screenshot it** — that closes G1, G2, G3.
2. Click **Pay → passkey → receipt** on the best pick. Confirm the receipt shows the score, `4242`, and the sandbox line. **Screenshot that** — that closes G4.
3. Try the villain and confirm the refusal shows the server's code on screen.
4. Verify `?mock=1` still renders the whole flow from the mock (the demo fallback).
5. Polish: render `skipped` as "Could not verify", name the failed checks on a danger card, add the "why this one" panel.

**Proof:** three screenshots (grid, receipt, refusal) plus the mock fallback still working.

### B — audit, Devpost, final numbers

Block 4's trust half is merged (`test_refusal_paths.py`, `test_no_llm_path.py`, `test_villain_end_to_end.py`, and `api.test.ts` pinning the wire shapes). Remaining:

1. **Task 29 — VEYZL.** VEYZL is a GitHub App that audits a PR against EU AI Act / NIST AI RMF / ISO 42001 controls and posts a check. The side track (Cloudforce) is $500 + lifetime pro, and judging wants a real audit on a PR plus evidence the finding changed the build.
   - Confirm the GitHub App is installed on `KF8311/Dubhacks` and the project exists in the VEYZL portal.
   - Open the **fix PR** — it must be the PR that carries the finding's fix, not a throwaway.
   - Reproduce the finding by hand first; an unreproduced finding is not a finding.
   - Write the failing test, fix it, re-run the audit, record before/after in `docs/veylz-audit.md`.
   - Candidates already scoped in that file; `/api/demo/reset` (unauthenticated while `demo_mode` defaults true) is the strongest.
2. `README.md` — done, including the corrected Gemini paragraph.
3. **Devpost** — story done in `docs/devpost.md`; field-by-field map in `docs/devpost-form.md`. Select **Visa: Reimagine Shopping** as the title track and **VEYZL** as a sponsored side track; answer the generative-AI question **Yes** with the paragraph in `devpost-form.md`.
4. Put the final numbers in `docs/status.md`.

**Proof:** offline replay exits 0; the audit file names one real finding with a test that pins the fix; the Devpost draft exists with the sandbox disclosure and no production-Visa claim.

### Demo script (rehearse exactly this)

| Step | Action | Expected |
|---|---|---|
| 1 | Query "noise cancelling headphones" | 3 questions appear |
| 2 | Answer **$150–$300**, **Travel**, **Noise cancelling** | 8 trusted + 1 danger |
| 3 | Watch the stream | 45 checks fill in, villain turns red |
| 4 | Read the villain reason | `LOCAL_DENYLIST`, 12-day domain, 3 Reddit reports, 4 page flags |
| 5 | Point at the pick | Target $179.99, saves $194.50 vs median $374.49 |
| 6 | Purge danger | villain card disappears |
| 7 | Checkout | sandbox banner, passkey, receipt |
| 8 | Optional refusal | try the villain; server refuses with a code |

**Gate check before each rehearsal:**

```bash
cd backend && .venv/Scripts/python.exe -m pytest -q                     # 177 passed
cd frontend && npx vitest run && npm run build                          # 26 passed, clean
backend/.venv/Scripts/python.exe scripts/replay_offline.py              # exit 0
```

**Never cut:** scoring (Task 14), the fixtures, the golden tests, the sandbox label, the payability gate, the refusal demo.
