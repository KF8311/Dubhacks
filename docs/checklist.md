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

## Where we are now — 19:00 PT (after the Block 4 B merge)

| Thing | State |
|---|---|
| `main` | **Everything merged**: scaffold, session routes, SSE, `search()`, all five checks, `score_investigation()`, `recommend()`, orchestrator fan-out, payability guard, the live frontend, the offline replay, and the frozen refusal paths. **146 backend / 9 frontend tests pass**, `npm run build` clean, `scripts/replay_offline.py` exits 0. |
| Follow-on branch | **None. `main` is the source of truth** — branch from it for Block 4 (`a/checkout`, `c/checkout-ui`). `scratch/integration` is stale; do not reuse it. |
| Live API | `POST /api/sessions`, `POST /api/sessions/{id}/answers`, `GET /api/sessions/{id}`, `GET /api/sessions/{id}/events`. Checkout/confirm (Task 23) not built yet. |
| Frontend | Live by default. `?mock=1` (or `VITE_USE_MOCK=1`) runs the whole UI from `data/mock-session.json`. |
| Gates | G0 partial (health live, contracts not frozen). **G1, G2, G3 proven server-side and wired in the browser client.** G4 needs Task 23 + the checkout UI; B's guard and refusal tests are ready. |
| Dead branches | `b/trust`, `richard-dev`, `2026-10-17-6c1c`, `b/recommendation`, `b/domain-age`, `b/ssl-safe-browsing`, `b/page-flags`, `b/reddit-sentiment`, `agent_backend`, `c/web`, `merge/agent-backend`, `integration/hookup` all merged into `main`. |

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
- [ ] Baseline both suites before you change anything: `pytest -q` → **146 passed**; `npx vitest run` → 9 passed. If your baseline differs, stop and ask — someone's work is missing.

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

### Block 4 — 19:30–21:00 · G4: checkout

**Goal:** click through to a receipt against the real backend.

| Person | Do |
|---|---|
| **A** | Mandate → simulated passkey → one-time token → transaction → receipt. Server re-validates: `trusted` ∧ score ≥70 ∧ (allowlisted ∨ ≥3 checks). Atomic transitions, idempotency key, `processor: mock-vic`, `mode: sandbox`. Raw token never stored — SHA-256 and last4 only. |
| **B** | ✅ **Done** — golden values frozen: payability constants, the 30-minute stale boundary, and every refusal code. Refusal paths verified against the **real demo data**: villain → `MERCHANT_NOT_TRUSTED`, stale investigation → `INVESTIGATION_STALE`, cap exceeded → `AMOUNT_EXCEEDS_CAP`; the real allowlisted hero pays. No-LLM guard: `test_no_llm_path.py` fails if any module imports a generative client or reads the Gemini key outside config. |
| **C** | Checkout sheet: cap, sandbox banner, passkey step, disabled when not payable with the server's reason shown. Receipt page: merchant, checks, score, last4 only, sandbox line. |

**Proof:** full click-through on a trusted listing; then attempt the villain and get a visible refusal with the server's code.

**If late:** a receipt is the demo's closing image. Cut Mongo and Reddit before you cut this.

### Block 5 — 21:00–22:30 · G5: Devpost draft

| Person | Do |
|---|---|
| **A** | `fly deploy` from current `main` so the live app matches the repo. Confirm the health URL and a real session over the public URL. |
| **B** | Devpost technical section: the five checks, the scoring formula with real numbers, the payability rule, the sandbox disclosure. Fill `docs/status.md` with final numbers. |
| **C** | Three screenshots — results grid, danger detail, receipt — and one screen recording of the full path. |

**Proof:** Devpost draft saved with the URL, the screenshots, and the sandbox label visible in the copy.

### Block 6 — 22:30–02:00 · G6: harden and freeze

| Person | Do |
|---|---|
| **A** | Mongo repository behind the existing protocol **only if** everything above is green. Otherwise skip — the in-memory adapter is the cut-order survivor. |
| **B** | ✅ **Done** — `scripts/replay_offline.py` runs a full session in-process with no server and no network: 9 listings, 8/0/1, villain `danger`, pick `lst_tgt_bsp`, median `$374.49`, savings `$194.50`. Exits 1 if those numbers drift. Domain age and SSL now honour `OFFLINE=1` (fixtures still load, nothing opens a socket). |
| **C** | Phone-width reflow, loading and error states, `?mock=1` fallback path. |

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
- [x] **All merges landed** — PRs #9, #10, #11 into `main`; `main` is `fa6c2a7` and green
- [x] B: **Block 4 refusal paths** — real villain/host data through `assert_payable`; danger, low confidence, low coverage, missing investigation, currency, cap, and the 30-minute boundary pinned; no-LLM source guard (`test_refusal_paths.py`, `test_no_llm_path.py`)
- [x] B: villain integration golden test — real checks → `danger` → excluded from `recommend()` even when cheapest (`tests/integration/test_villain_end_to_end.py`)
- [x] B: **Task 28** — `app/demo/replay.py` + `scripts/replay_offline.py`. Reports `9 / 8 / 0 / 1`, villain `lst_vln_xm5`, pick `lst_tgt_bsp`, median `$374.49`, savings `$194.50`, identical to the live HTTP run; exits 1 on drift. `SessionOrchestrator` takes an optional `Settings` and domain age + SSL short-circuit on `offline`. 7 new tests.

## 6. Gate board

| Gate | Due | State | Owner |
|---|---|---|---|
| G0 Contracts frozen + health | Sat 13:15 | 🟡 health live, `Question` shape needs A's sign-off | A |
| G1 Listings to browser | Sat 15:30 | 🟢 live `EventSource` client wired; one browser screenshot still owed | A + B + C |
| G2 Investigation + score | Sat 18:00 | 🟢 server proof + `check.completed` rendering; browser click-through owed | A + B + C |
| G3 Recommendation | Sat 19:30 | 🟢 server proof + `BestPick` and best-pick ring; browser click-through owed | A + B + C |
| G4 Checkout → receipt | Sat 21:00 | ⬜ | A + C |
| G5 Devpost draft | Sat 22:30 | ⬜ | B |
| G6 Freeze | Sun 02:00 | ⬜ | all |
| G7 Submit | Sun 09:50 | ⬜ | all |

## 7. Live blockers

| Blocker | Owner | Impact |
|---|---|---|
| Task 23 checkout routes unbuilt | A | G4 cannot be reached over HTTP; payability logic itself is tested |
| No browser click-through yet | C | The live wiring is merged but has never rendered in a real browser; one run closes G1–G3 for good |
| "Under $150" empties the trusted set | C | Demo run must answer **$150–$300**; see §9 |
| Contracts not frozen | A | `Question` shape is a guess; cheap to confirm, expensive to discover at 21:00 |
| SerpAPI key | A | Catalog only (D-011). Not blocking. |
| Safe Browsing key | B | Static denylist with `source="unavailable"`. Not blocking. |
| Mongo unassigned | A | In-memory adapter until Block 5. Not blocking. |

## 8. Cut order

Cut in this order: live page fetching → Reddit → SerpAPI → Mongo → page flags.

## 9. Block 4 — G4 checkout · start here

**State:** everything through G3 is merged and green, and B's half of Block 4 (the refusal paths and the offline replay) is in this merge. G4 is blocked on exactly two things: **Task 23 checkout routes (A)** and **the checkout/receipt screens (C)**.

**First 15 minutes of the block, every person:**

1. `git checkout main && git pull`
2. Run your baseline: backend `pytest -q` → **146 passed**; frontend `npx vitest run` → **9 passed**; `backend/.venv/Scripts/python.exe scripts/replay_offline.py` → exit 0.
3. Say out loud what you are taking from the lists below, then work top to bottom. Each person owns their column; nobody waits on another column.

**Your next action, in one line:**

| Owner | Next action | Unblocks |
|---|---|---|
| **A** | Build `POST /api/checkout` + `POST /api/checkouts/{id}/confirm` on `assert_payable` | C, G4 |
| **C** | Click through the live flow once and screenshot it, then build the checkout sheet against A's JSON | G1–G3 proof, G4 |
| **B** | Task 29 VEYZL audit + `README.md`; Devpost technical section | G5 |

**Handoff contract for A → C (do not improvise this):** every refusal is `409` with `{"code": <PayabilityCode>, "message": <human string>, "details": {...}}`. C renders `code` and `message` verbatim; the codes and the guard are frozen in `backend/app/payments/payability.py` and `docs/contracts.md` §409. If the JSON shape has to change, say it in the channel before committing.

### A — checkout backend (G4's critical path)

1. **Task 23** `POST /api/checkout` and `POST /api/checkouts/{id}/confirm` on top of `assert_payable`. Server re-validates every time; the client sends only `listing_id`, `session_id`, `max_amount_cents`, and an idempotency key.
2. Return every refusal as 409 with `{code, message, details}` from `PayabilityCode` so C can render the server's reason verbatim.
3. **Task 24** receipt service — HMAC signature, `GET /api/receipts/{id}`, `GET /api/public/receipts/{share_id}`; `processor: mock-vic`, `mode: sandbox` on every response.
4. `POST /api/demo/reset` to clear the registry between rehearsals.
5. Parsing a budget out of free text (`"under $300"` currently yields `budget_max_cents: null`).

**Proof:** `create → confirm` twice returns the same receipt; the villain returns 409 `MERCHANT_NOT_TRUSTED`.

### C — browser proof and the last two screens

1. Run `uvicorn app.main:app --port 8000 --workers 1` and `npm run dev`, open `http://localhost:5173`, answer **$150–$300**, and confirm: villain card red, its five rows named, `Best pick` = Target $179.99 with $194.50 savings. **Screenshot it** — that closes G1, G2, G3.
2. Verify `?mock=1` still renders the old mock session (the demo fallback).
3. **Task 25** checkout sheet: cap, sandbox banner, passkey step, disabled when the server refuses, and the server's `PayabilityCode` shown on screen.
4. **Task 26** receipt page: merchant, checks, score (or `Verified` when allowlisted), last4 only, sandbox line.
5. Polish: render `skipped` as "Could not verify", name failed checks on a danger card, add the "why this one" panel.

**Proof:** click a trusted listing → passkey → receipt; then click the villain → visible refusal with the server's code.

### B — audit, README, Devpost (Block 4 half is done)

Done in this merge:

1. ✅ **Refusal paths frozen** — `tests/integration/test_refusal_paths.py` runs the real demo session through `assert_payable`: hero payable, villain `MERCHANT_NOT_TRUSTED`, cap `AMOUNT_EXCEEDS_CAP`, stale `INVESTIGATION_STALE`. `tests/unit/test_payability.py` adds danger, low confidence, missing investigation, currency, the allowlist exemption, and the 30-minute boundary.
2. ✅ **No fixture text reaches an LLM** — `tests/unit/test_no_llm_path.py` fails if any module imports a generative client or reads the Gemini key outside config.
3. ✅ **Task 28** — `scripts/replay_offline.py`; run it before every rehearsal. Exit 1 means the demo drifted.
4. ✅ **Villain golden test** — real checks → `danger` → excluded from `recommend()` even when cheapest.

Remaining in Block 4:

5. Task 29: connect the repo to VEYZL, pick one real finding, fix it, write `docs/veylz-audit.md`.
6. `README.md`: setup, env vars, demo script, sandbox disclosure, the "why skipped ≠ passed" explanation.
7. Draft the Devpost technical section now (five checks, scoring formula with the real numbers, payability rule, sandbox label); fill the URL and screenshots after G4.

**Proof:** offline replay exits 0; the audit file names one real finding; the Devpost draft exists with the sandbox disclosure.

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
cd backend && .venv/Scripts/python.exe -m pytest -q                     # 146 passed
cd frontend && npx vitest run && npm run build                          # 9 passed, clean
backend/.venv/Scripts/python.exe scripts/replay_offline.py              # exit 0
```

**Never cut:** scoring (Task 14), the fixtures, the golden tests, the sandbox label, the payability gate, the refusal demo.
