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

## Reference links — the things this checklist talks about

| Thing | Link |
|---|---|
| Repository | [KF8311/Dubhacks](https://github.com/KF8311/Dubhacks) · [`main`](https://github.com/KF8311/Dubhacks/tree/main) |
| Live health | [`/api/health`](https://sniff-visa-dubhacks.fly.dev/api/health) ([Fly config](../fly.toml)) |
| Current state | [`docs/status.md`](status.md) · [decisions](decisions.md) · [contracts](contracts.md) · [index](INDEX.md) |
| Spec and plan | [product spec](../project-a-sniff-visa.md) · [implementation plan](superpowers/plans/2026-10-17-sniff-visa.md) · [3-person split](team-split-3.md) |
| Devpost | [draft story](devpost.md) · [field-by-field form](devpost-form.md) · [technical claims](devpost-technical-claims.md) |
| Security side track | [VEYZL audit scope and reproduction](veylz-audit.md) |
| Person C's Block 6 | [checklist and measurements](personC%20files/person-c-block-6.md) |
| Backend entry points | [`app/main.py`](../backend/app/main.py) · [routes](../backend/app/api) · [checks](../backend/app/checks) · [scoring](../backend/app/trust) · [payments](../backend/app/payments) · [orchestrator](../backend/app/sessions/orchestrator.py) |
| Frontend entry points | [`App.tsx`](../frontend/src/App.tsx) · [features](../frontend/src/features) · [API client](../frontend/src/lib/api.ts) · [SSE hook](../frontend/src/features/results/useSessionStream.ts) |
| Test commands | [backend suite](../backend/tests) · [frontend suite](../frontend/src) · [offline replay](../scripts/replay_offline.py) |
| Local servers | [localhost:5173](http://localhost:5173) · [localhost:8000/docs](http://localhost:8000/docs) |

## Where we are now — 20:30 PT · **Block 5 running; C's work is on `origin/main`**

| Thing | State |
|---|---|
| `main` | **Everything merged and pushed** ([`3e349b8`](https://github.com/KF8311/Dubhacks/commit/3e349b8), rebase-merged as [PR #20](https://github.com/KF8311/Dubhacks/pull/20) and [PR #21](https://github.com/KF8311/Dubhacks/pull/21)): scaffold, session routes, SSE, `search()`, all five checks, `score_investigation()`, `recommend()`, orchestrator fan-out, payability guard, checkout/confirm, receipts, the live frontend, the offline replay, the frozen refusal paths, **Gemini questions/narration/explanations (D-017–D-019)**, **the `Repository` protocol with in-memory + Mongo adapters**, **A's live-search path plus budget parsing (D-021, D-022)**, and **C's phone-width reflow, unknown-merchant resolution, offline catalog pinning, and `api_key` redaction**. **187 backend / 13 files · 34 frontend tests pass**, [`npm run build`](../frontend) clean, [`scripts/replay_offline.py`](../scripts/replay_offline.py) exits 0. |
| Follow-on branch | **None pending.** [PR #20](https://github.com/KF8311/Dubhacks/pull/20) merged; the working branch was deleted after `git diff main <branch>` came back empty. Local `main` and `origin/main` are the same commit. [`scratch/integration`](https://github.com/KF8311/Dubhacks/tree/scratch/integration) is stale; do not reuse it. |
| Live API | Sessions create/answers/snapshot/events/**explain**, orchestrator fan-out, payability guard and mandates, **checkout/confirm**, **receipts + public share**, `POST /api/demo/reset`. Contracts: [`docs/contracts.md`](contracts.md). |
| Frontend | Live by default, and the checkout sheet + receipt page call the live endpoints. `?mock=1` (or `VITE_USE_MOCK=1`) runs the whole UI, including checkout, from [`frontend/src/data/mock-session.json`](../frontend/src/data/mock-session.json). The sheet refuses to offer payment without a real session id — no more `ses_mock` fallback. Reflowed for 390px ([C's Block 6 notes](personC%20files/person-c-block-6.md)). |
| Gates | G0 partial (health live, contracts not frozen). **G1, G2, G3 proven server-side and wired in the browser client.** **G4 is built and merged end to end**; its gate proof (one browser click-through) is the first action of Block 5. **G5 is open**: the stories are written, the artifacts are not. |
| Dead branches | All of them. `b/trust`, `richard-dev`, `2026-10-17-6c1c`, `b/recommendation`, `b/domain-age`, `b/ssl-safe-browsing`, `b/page-flags`, `b/reddit-sentiment`, `agent_backend`, `c/web`, `merge/agent-backend`, `integration/hookup`, `integration/block4`, `integration/block4-ui`, `b/block4-refusals`, `b/block5-devpost`, `b/block5-veylz-audit`, `b/mongo-ownership` are all contained in `main` (`git rev-list --count main..origin/<branch>` is 0 for every head). `scratch/integration` is stale — do not reuse it. |

**Before anyone starts:** `git checkout main && git pull`. There is nothing left to merge — if you are on an older branch, rebase onto `main` before writing code. Baseline commands are in [§1](#1-universal--once-per-machine); current health is at [`docs/status.md`](status.md).

**Recovery stance:** G1 was 45 minutes late, not lost. Do not skip a block's proof to catch up — the proofs are the gate.

---

## 1. Universal — once per machine

- [ ] Open **[`Dubhacks/`](../)** as the working directory, not `Desktop/dubhacks/`. Skills load from [`.claude/skills/`](../.claude/skills) in the folder the session starts in.
- [ ] `git fetch origin && git checkout main && git pull` — then `git checkout -B <your-branch> origin/main`. Everyone starts from current `main`.
- [ ] Read [`docs/status.md`](status.md), then [`CLAUDE.md`](../CLAUDE.md), then [`docs/INDEX.md`](INDEX.md).
- [ ] Backend venv (Python 3.11 or 3.12, **not** 3.14):
  ```bash
  cd backend && python -m venv .venv
  .venv/Scripts/python -m pip install -r requirements.txt
  ```
- [ ] Frontend deps: `cd frontend && npm ci`.
- [ ] Baseline both suites before you change anything: `pytest -q` → **187 passed**; `npx vitest run` → **34 passed**. If your baseline differs, stop and ask — someone's work is missing.

## 2. Universal — every commit

- [ ] Tests pass. Run them; paste the output when you claim a task is done.
- [ ] **No AI attribution.** No `Co-Authored-By`, no "Generated with" trailers. Commits carry your name only.
- [ ] Commit every 30 minutes. `feat:`, `fix:`, `docs:`, `chore:`.
- [ ] You touched only your own files. [`backend/app/domain/models.py`](../backend/app/domain/models.py), [`frontend/src/lib/types.ts`](../frontend/src/lib/types.ts), and [`docs/contracts.md`](contracts.md) belong to their owner.
- [ ] No secrets, no real PII, no real card numbers, no raw tokens.
- [ ] Fixture-sourced results carry `source: "fixture"`.

## 3. Universal — every gate

- [ ] Run the real command or the real browser path before claiming the gate passed. A green unit test is not a gate proof.
- [ ] Update [`docs/status.md`](status.md): gate, owners, blockers, live risks.
- [ ] Append to [`docs/decisions.md`](decisions.md) if you changed a decision.
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
| **A** | ✅ **Merged post-block:** the SerpAPI `source`→domain fallback ([D-021](decisions.md), [`serpapi.py`](../backend/app/search/serpapi.py)), `under_150`-style budget parsing ([`questions.py`](../backend/app/sessions/questions.py)), and the checkout sheet's session guard. ⬜ [`fly deploy`](../fly.toml) from current `main` so [the live app](https://sniff-visa-dubhacks.fly.dev/api/health) matches the repo; [`smoke_http.py`](../backend/scripts/smoke_http.py) against the public URL. **Then Task 29 ([D-020](decisions.md)):** install the VEYZL app on the repo, run the audit on a PR, fix one finding with a test — scope in [`docs/veylz-audit.md`](veylz-audit.md). |
| **B** | ✅ Devpost story ([`docs/devpost.md`](devpost.md)), [README](../README.md), [`docs/devpost-form.md`](devpost-form.md), and the audit scope/reproduction. ⬜ Fill the form as A's URL and C's screenshots land; final numbers in [`status.md`](status.md); review A's audit finding. |
| **C** | ✅ Block 6 UI work landed early ([notes](personC%20files/person-c-block-6.md)). ⬜ Three screenshots — results grid, danger detail, receipt — and one screen recording of the full path. This is the only thing G5 is waiting on from C. |

**Proof:** Devpost draft saved with the URL, the screenshots, and the sandbox label visible in the copy.

### Block 6 — 22:30–02:00 · G6: harden and freeze

| Person | Do |
|---|---|
| **A** | ✅ The protocol no longer leaks Mongo types and `MONGODB_URI` unset stays the default (B's review landed in [`8c89260`](https://github.com/KF8311/Dubhacks/commit/8c89260)). **Own the VEYZL fix PR ([D-020](decisions.md))** — the only Block 6 code change left. Then freeze: no new features after 02:00. |
| **B** | ✅ **Task 27 review ([D-016](decisions.md))** — [`repository.py`](../backend/app/services/repository.py) declares every method both adapters expose, `get_repository()` returns the protocol, and [`checkouts.idempotency_key`](../backend/app/db/indexes.py) uses a partial filter so keyless checkouts no longer collide on `null`. The `MONGODB_URI`-unset path is pinned by `test_empty_or_failed_mongo_selects_memory`. **Still open:** TTL index verification against a real cluster and the MLH MongoDB claim. Keep the claim only if Atlas is actually exercised; otherwise remove it. |
| **C** | ✅ **Done** (`cf24bdb`, `3ceffbc`) — phone-width reflow at 390px, loading and error states, `?mock=1` fallback path. Evidence and measurements: [C's Block 6 notes](personC%20files/person-c-block-6.md). |

**Block 6 required before freeze:**

- [ ] **A** — `pytest -q` green with **no** `GEMINI_API_KEY` and `OFFLINE=1`; the template fallback ([`llm.py`](../backend/app/services/llm.py)) is the demo path.
- [ ] **B** — [`scripts/replay_offline.py`](../scripts/replay_offline.py) exits 0 and prints the frozen numbers.
- [ ] **C** — `npm run build` clean; `?mock=1` renders the whole flow.
- [ ] **C** — a pick above the user's stated budget is labelled ([D-022](decisions.md)); the budget is not described as a hard cap.
- [ ] **B** — no `.env` or key is tracked (`git ls-files | grep -i env`).
- [ ] **B** — every claim in [`README.md`](../README.md) and [`docs/devpost.md`](devpost.md) matches the merged code; the generative-AI answer is **Yes**.
- [ ] **B** — Devpost fields in [`docs/devpost-form.md`](devpost-form.md) all filled; VEYZL selected as a Sponsored Side Track.
- [ ] **A** — a VEYZL check run is visible on a PR and linked from [`docs/veylz-audit.md`](veylz-audit.md).
- [ ] **B** — [`docs/status.md`](status.md) carries the final numbers.
- [ ] **All** — no new infrastructure without a decision entry.

**Proof:** offline replay produces the same numbers as live; plane-mode demo works.
**2:00 AM: freeze.** After this, docs and bugfixes only.

### Block 7 — Sunday 08:00–09:50 · G7: submit

- [ ] Wake the Fly machine; hit [`/api/health`](https://sniff-visa-dubhacks.fly.dev/api/health) until it returns 200.
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
- [x] B: **Repository review, first pass (`8c89260`)** — `Repository` declares all 17 methods both adapters expose; `get_repository()` is typed with the protocol; `checkouts.idempotency_key` is a partial filter over strings instead of `sparse`, so the many keyless checkouts no longer collide on `null`. Three new tests, watched failing first.
- [x] B: persistence claim narrowed — only mandates, checkouts, transactions, receipts, and audit events reach Mongo; sessions, listings, and investigations stay in-process, and mock VIC tokens never leave the process (`README.md` honesty notes)
- [x] **A merged (`8687203`, `9af147a`)** — Google Shopping `source` → merchant domain (D-021, supersedes D-011), `under_150`-style budget parsing, `SERPAPI_KEY` read from the upper-case env name, catalog fallback when a budget matches nothing (D-022), and a checkout sheet that refuses to pay without a real session id
- [x] Merge fixes: the sheet keeps the D-015 allowlist exemption *and* requires a session; [`App.tsx`](../frontend/src/App.tsx) passes the real id or nothing; the duplicate `allowlisted` prop and the `string | undefined` build error are gone (`npm run build` clean)
- [x] **C's Block 6 work merged (`cf24bdb`, `3ceffbc`)** — fast-forwarded onto `main` because her branch sat exactly on `fb6b12e`; no conflicts. 12 files, +279/−30. (Rebase-merged as PR #20, which rewrote the SHAs and dropped her merge commit.)
- [x] C: **phone-width reflow** — headers and mains use `px-4 sm:px-6`, the grid collapses to one 342px column at 390px, the sandbox badge wraps instead of clipping, and receipt titles use `break-words`. Measured horizontal overflow: 0. Notes: [C's Block 6 checklist](personC%20files/person-c-block-6.md).
- [x] C: **`api_key` redaction** — [`redact()`](../backend/app/core/logging.py) now scrubs `api_key=` and `x-goog-api-key=` query values before email/phone/card, so a logged SerpAPI or Google URL cannot leak a key. Pinned by [`test_logging.py`](../backend/tests/unit/test_logging.py).
- [x] C: **unknown merchants resolve** — [`listing_from_immersive()`](../backend/app/search/serpapi.py) walks Google Shopping's immersive `stores` and takes the first store whose link is a real merchant host, so a listing with no direct merchant domain now gets one instead of being dropped. Four lookups max, 2 s cap, already-returned stores kept. 108 lines of new tests in [`test_serpapi.py`](../backend/tests/unit/test_serpapi.py).
- [x] C: **offline demos stay on the catalog** — with `OFFLINE=1` the [orchestrator](../backend/app/sessions/orchestrator.py) loads the curated catalog directly instead of calling the search provider, so a stray `SERPAPI_KEY` in the environment cannot change the replay or refusal numbers.
- [x] B: restored the receipt **score assertion** that C's wrap fix replaced (`Score 92` via its aria-label) and kept the new `break-words` check; both behaviours now have coverage ([`Receipt.test.tsx`](../frontend/src/features/receipt/Receipt.test.tsx), `f0014c0`).
- [x] Verified after the merge: **187 backend**, **34 frontend**, `npm run build` clean, `replay_offline.py` exit 0, and the live HTTP run for **$300–$600** matches the replay exactly (pick `lst_tgt_bsp`, median $374.49, savings $194.50).

## 6. Gate board

| Gate | Due | State | Owner |
|---|---|---|---|
| G0 Contracts frozen + health | Sat 13:15 | 🟡 health live, `Question` shape needs A's sign-off | A |
| G1 Listings to browser | Sat 15:30 | 🟢 live `EventSource` client wired; one browser screenshot still owed | A + B + C |
| G2 Investigation + score | Sat 18:00 | 🟢 server proof + `check.completed` rendering; browser click-through owed | A + B + C |
| G3 Recommendation | Sat 19:30 | 🟢 server proof + `BestPick` and best-pick ring; browser click-through owed | A + B + C |
| G4 Checkout → receipt | Sat 21:00 | 🟡 **build complete and merged**; browser click-through is Block 5's first action | A + C |
| G5 Devpost draft | Sat 22:30 | 🟡 stories written; URL, screenshots, video, and A's VEYZL check run pending | B |
| G6 Freeze | Sun 02:00 | ⬜ | all |
| G7 Submit | Sun 09:50 | ⬜ | all |

## 7. Live blockers

| Blocker | Owner | Impact |
|---|---|---|
| Fly serves the pre-merge build | A | Redeploy from the repo root so the public URL carries checkout and receipts. **First action of Block 5.** |
| No browser click-through yet | C | The live wiring is merged but has never rendered in a real browser; one run closes G1–G4 for good. **First action of Block 5.** |
| Budget answer changes the card count | C | Measured on the merged build: **Under $150 → 1 card** (villain only, `no_trusted_option`), **$150–$300 → 3 cards** (2 trusted + villain), **$300–$600 → all 9** (8 trusted + villain). The demo script in §10 uses **$300–$600**; earlier drafts said $150–$300. |
| `OFFLINE=1` skips the budget filter | B | [C's catalog pinning](../backend/app/sessions/orchestrator.py) loads all 9 listings regardless of the answer, so the plane-mode demo shows every card. That is deliberate for replay stability — say "full catalog" if asked, and never describe the offline run as budget-filtered. |
| Contracts not frozen | A | `Question` shape is a guess; cheap to confirm, expensive to discover at 21:00. Shape lives in [`docs/contracts.md`](contracts.md) and [`questions.py`](../backend/app/sessions/questions.py). |
| SerpAPI key | A | Catalog-only in the deploy. **[D-021](decisions.md) is untested against a real key** — run [`scripts/serpapi_spike.py`](../scripts/serpapi_spike.py) before claiming live search anywhere. Not blocking. |
| A budget that matches nothing falls back to the full catalog | B | [D-022](decisions.md): a listing above the user's stated budget can be recommended and paid, because the payability cap is the listing price. Say "closest match" on stage or add an over-budget badge. Do not call the budget a hard cap. |
| Safe Browsing key | B | Static denylist with `source="unavailable"`. Not blocking. |
| Mongo deferred to Block 6 (D-016) | B | In-memory is the default; A's `MongoRepository` is merged but unreviewed. Not blocking. |
| ~~`main` could not be pushed to or merged into~~ | A (D-020) | **Resolved 20:22.** The required `VEYZL Audit` check was dropped from the repo ruleset, [PR #20](https://github.com/KF8311/Dubhacks/pull/20) was rebase-merged, and the branch deleted. **Re-add the required check only after the VEYZL GitHub App is installed** — a local VEYZL run posts no status check, so re-adding it early blocks every merge again, exactly as it did before. |
| VEYZL check has not run on a PR yet | **A** (D-020) | The app must be installed on `KF8311/Dubhacks` and the project linked before a fix PR opens; without a visible check run the side track is not eligible. B's reproduction is in [`docs/veylz-audit.md`](veylz-audit.md). |
| `GEMINI_API_KEY` absent on Fly | A | The app falls back to templates; the demo still works, but the narration is deterministically worded. Set it only if the fallback copy reads worse on stage. |
| Local venv missing `motor` | everyone | `pip install motor`; it is in `requirements.txt`. Without it one repository test fails to import. |

## 8. Cut order

Cut in this order: live page fetching → Reddit → SerpAPI → Mongo → page flags.

## 9. Next blocks — start here

**State (20:30 PT, [`3e349b8`](https://github.com/KF8311/Dubhacks/commit/3e349b8)):** `main` carries everything from all three people — checkout → confirm → receipt, the live frontend, all five checks, Gemini for questions/narration/explanations, the in-memory + Mongo repositories, A's live-search and budget changes ([D-021](decisions.md), [D-022](decisions.md)), C's phone-width reflow and search hardening, and the offline replay. Green: **187 backend / 13 files · 34 frontend tests**, `npm run build` clean, [`replay_offline.py`](../scripts/replay_offline.py) exits 0.

**Block 5 is close-out only.** Every text artifact is written: the Devpost story, the field-by-field form map, the technical-claims handoff, the README, the audit scope, and the reproduced reset transcript. What is missing is artifacts that only A and C can produce. Do not start Block 6 work until your Block 5 action is done or explicitly cut.

**What changed in the last hour:**

- **C's branch landed (`cf24bdb`, `3ceffbc`) — fast-forward, no conflicts.** Three pieces: the 390px reflow (`px-4 sm:px-6` on every header and main, one-column grid, wrapping sandbox badge), `api_key`/`x-goog-api-key` redaction in [`logging.py`](../backend/app/core/logging.py), and two search fixes — unknown merchants now resolve through Google Shopping's immersive `stores` ([`listing_from_immersive()`](../backend/app/search/serpapi.py)), and `OFFLINE=1` reads the curated catalog directly so a stray key cannot move the replay numbers. Her own evidence is in [C's Block 6 checklist](personC%20files/person-c-block-6.md).
- **The receipt test keeps both assertions.** C's wrap fix had swapped the score check for `break-words`; [`Receipt.test.tsx`](../frontend/src/features/receipt/Receipt.test.tsx) now asserts the score *and* the wrap (`f0014c0`).
- **A pushed `8687203` at 19:40 and it is now merged.** Live search infers the merchant domain from Google Shopping's `source` (D-021, supersedes D-011), `under_150`-style budget ids parse, an empty budget filter falls back to the catalog (D-022), and the checkout sheet no longer falls back to `ses_mock`. Three conflicts were resolved by hand: the allowlist exemption is kept, a session id is now required, `docs/INDEX.md` points at both Devpost docs, and A's `D-019` was renumbered to `D-021` because that number already belonged to the Gemini model.
- **B's repository review, first pass landed (`8c89260`).** The protocol now covers all 17 methods, `get_repository()` is typed with it, and the idempotency index no longer treats `null` as a key. Three tests were written failing first.
- **C merged twice more**: an API-unreachable alert on discovery, and allowlisted merchants render as `Verified` (D-015) on the card, sheet, and receipt.
- **B merged PR #19**: `docs/devpost-form.md`, the honest Gemini claims, the updated plan, and the `/api/demo/reset` reproduction.
- **Task 29 (VEYZL) moved to A (D-020).** A owns the repo and therefore the GitHub App install. B's scope, candidate controls, and reproduction stay in `docs/veylz-audit.md` — A picks up at step "install the app".

**Your next action, in one line:**

| Owner | Next action | Closes |
|---|---|---|
| **A** | `fly deploy` from the repo root, then `smoke_http.py` against the public URL | G4 on the public URL |
| **C** | Click the live flow through to a receipt (answer **$300–$600**) and screenshot the grid + receipt. Her Block 6 UI work is already merged — only the artifacts are missing | G1–G4 proof + G5 screenshots |
| **B** | Fill `docs/devpost-form.md` as A's URL and C's screenshots land; put final numbers in `status.md` | G5 |

**First 15 minutes, every person:**

1. `git checkout main && git pull`
2. Baseline: backend `pytest -q` → **187 passed**; frontend `npx vitest run` → **34 passed**; [`scripts/replay_offline.py`](../scripts/replay_offline.py) → exit 0. If `motor` is missing, `pip install motor`.
3. Take your column below. Nobody waits on another column.

**Handoff contract, now live (do not improvise this):** every refusal is `409` with `{"code": <PayabilityCode>, "message": <human string>, "details": {...}}`; a declined passkey is `402 PAYMENT_DECLINED`. The confirm path is **`POST /api/checkout/{checkout_id}/confirm`** (singular `checkout`) and takes `{passkey_assertion: {credential_id, client_data}, idempotency_key}`. Confirm returns a **pointer** (`receipt_id`, `receipt_url`); the receipt itself is `GET /api/public/receipts/{share_id}`. Every response carries `processor: "mock-vic"`, `mode: "sandbox"`, and the sandbox label. The frontend's request/response mapping is pinned in `frontend/src/lib/api.test.ts` — if the shape has to change, say it in the channel before committing.

### A — public URL, then VEYZL (Block 5 into Block 6)

1. `git checkout main && git pull` — **your `agent_backend` work is merged into `main` now** (`8687203`, reconciled in `9af147a`). Deploying your old branch would drop everyone else's work and deploying before pulling would ship the same stale image as before.
2. `fly deploy` from the **repo root** (that is where `fly.toml` lives; deploying from `backend/` ships a stale image).
3. Run `backend/scripts/smoke_http.py` against the public URL: health, session, 9 listings, checkout, confirm, public receipt. **This closes G4's server half.**
4. **Task 29 (D-020):**
   - Install the VEYZL GitHub App on `KF8311/Dubhacks`; create/link the project in the VEYZL portal.
   - Open a PR that carries the fix. PR #19 is already merged; open a new one from the fix branch.
   - Trigger the audit and capture the report. Until that check run exists, the side track is not eligible.
   - Reproduce one reported finding, write the failing test, fix it, re-run the audit, and fill §Results in `docs/veylz-audit.md`.
   - B already reproduced `/api/demo/reset`: unauthenticated POST → `200`, session destroyed. If VEYZL reports the same, the transcript is ready; if VEYZL reports something else, **the tool's finding wins**.
5. Sign off the `Question` shape in `docs/contracts.md` (the last G0 item).

**Proof:** [public health URL](https://sniff-visa-dubhacks.fly.dev/api/health) + checkout and receipt on the public URL; a VEYZL check run visible on a PR; `pytest -q` still 187.

### C — browser proof + screenshots

The screens are merged. This block is about proving them in a real browser:

1. Run `uvicorn app.main:app --port 8000 --workers 1` and `npm run dev`, open `http://localhost:5173`, answer **$300–$600** (that is the only answer that returns all nine). Confirm: villain card red with its five rows named, `Best pick` = Target $179.99 with $194.50 savings. **Screenshot it** — closes G1, G2, G3.
2. Click **Pay → passkey → receipt** on the best pick. Confirm the receipt shows the score, `4242`, and the sandbox line. **Screenshot that** — closes G4.
3. Try the villain; confirm the refusal shows the server's code on screen.
4. Verify `?mock=1` still renders the whole flow (the demo fallback), and that killing the API shows the new "search unreachable" alert.
5. Hand the screenshots to B for the Devpost gallery (3:2, 5 MB max).

**Proof:** three screenshots (grid, receipt, refusal) plus the mock fallback still working.

### B — Devpost, final numbers, and the audit review

The story and the form map are written. Remaining:

1. **Devpost** — fill `docs/devpost-form.md` in order as artifacts land: live URL (A), gallery images (C), video (team), VEYZL side-track selection (A's check run). Story: `docs/devpost.md`. Generative-AI answer: **Yes**, with the paragraph in the form map.
2. **Final numbers** — run [`scripts/replay_offline.py`](../scripts/replay_offline.py), put its numbers in [`docs/status.md`](status.md), and confirm the Devpost's `187` / `34` claims match the run.
3. **Review A's audit finding** before it is written up — B owns the trust/payment claims, A owns the run. If the finding touches the payability gate, check it against D-015 and the refusal tests.
4. **Never submit a claim the code cannot support.** Sandbox label, synthetic data, no production Visa integration, and the model never decides.

**Proof:** the Devpost draft exists with the URL, screenshots, VEYZL track, and sandbox disclosure; every number traced to a command.

## 10. Block 6 — what "moving forward" means (22:30–02:00)

The Block 6 table in §4 is the authority. This is the same work in start order:

| Order | Task | Owner | Done when |
|---|---|---|---|
| 1 | Deploy and public smoke | A | [`smoke_http.py`](../backend/scripts/smoke_http.py) passes against [Fly](https://sniff-visa-dubhacks.fly.dev/api/health) |
| 2 | VEYZL audit + fix PR | A | check run visible; one finding fixed with a test ([scope](veylz-audit.md)) |
| 3 | Devpost fields filled | B | [form](devpost-form.md) has URL, images, video, VEYZL track |
| 4 | Repository review ([D-016](decisions.md)) | B | ✅ first pass in [`8c89260`](https://github.com/KF8311/Dubhacks/commit/8c89260) — protocol complete, `idempotency_key` null-safe. ⬜ TTL indexes checked against a real cluster; no Mongo type leaks |
| 5 | MLH MongoDB claim | B | only if 4 passes **and** Atlas is exercised in the demo; otherwise remove the claim |
| 6 | Budget honesty ([D-022](decisions.md)) | C | either an "over budget" badge on a listing above the answer, or "closest match" copy next to the pick — pick one and put it on screen |
| 7 | Frontend polish | C | `skipped` reads "Could not verify"; mock path green |
| 8 | Freeze at 02:00 | all | checklist below complete |

**Freeze checklist (G6):**

- [ ] `pytest -q` green with **no** `GEMINI_API_KEY` and `OFFLINE=1`
- [ ] `replay_offline.py` exits 0 with the frozen numbers
- [ ] `npm run build` clean; `?mock=1` renders the whole flow
- [ ] `git ls-files | grep -i env` shows no `.env` and no key
- [ ] Every README/Devpost claim matches the code (Gemini writes copy, never a verdict)
- [ ] VEYZL check run linked in `docs/veylz-audit.md`
- [ ] `docs/status.md` carries the final numbers
- [ ] No new infrastructure without a decision entry

### Demo script (rehearse exactly this)

| Step | Action | Expected |
|---|---|---|
| 1 | Query "noise cancelling headphones" | 3 questions appear |
| 2 | Answer **$300–$600**, **Travel**, **Noise cancelling** | 9 cards: 8 trusted + 1 danger |
| 3 | Watch the stream | 45 checks fill in, villain turns red |
| 4 | Read the villain reason | `LOCAL_DENYLIST`, 12-day domain, 3 Reddit reports, 4 page flags |
| 5 | Point at the pick | Target $179.99, saves $194.50 vs median $374.49 |
| 6 | Purge danger | villain card disappears |
| 7 | Checkout | sandbox banner, passkey, receipt |
| 8 | Optional refusal | try the villain; server refuses with a code |

**Budget answer controls the card count — measured on `f0014c0`, not estimated:**

| Answer | Cards | Result |
|---|---|---|
| Under $150 | 1 | Villain only → `no_trusted_option`. A legitimate *second* demo, never the happy path. |
| $150–$300 | 3 | 2 trusted + villain. Works, but thin: the median and savings are less impressive. |
| **$300–$600** | **9** | **8 trusted + villain — the numbers in rows 3–5 above.** |

The catalog runs to $549.99 (AirPods Max), so only `$300–$600` contains all nine listings. Under `OFFLINE=1` the budget filter is skipped and all 9 cards appear for any answer — do not describe the plane-mode demo as budget-filtered.

**Gate check before each rehearsal:**

```bash
cd backend && .venv/Scripts/python.exe -m pytest -q                     # 187 passed
cd frontend && npx vitest run && npm run build                          # 34 passed, clean
backend/.venv/Scripts/python.exe scripts/replay_offline.py              # exit 0
```

**Never cut:** scoring (Task 14), the fixtures, the golden tests, the sandbox label, the payability gate, the refusal demo.
