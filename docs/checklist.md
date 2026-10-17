---
title: Team Checklist
type: checklist
updated: 2026-10-17
owner: everyone
---

# Team Checklist

One shared checklist. Personal scratch notes do not belong here.

**How to use it:** Section 1 is once per machine. After that, work the timed block you are in — each block has a column per person and a proof you have to produce before moving on. Tick boxes in the commit that completes them. `docs/status.md` still wins if the two disagree.

## Where we are now — 16:05 PT

| Thing | State |
|---|---|
| `main` | `58e4427` — backend scaffold, trust foundation, data, docs. **15 backend tests pass.** |
| `c/web` | `88dcee5` — `main` merged in, frontend added. **4 frontend tests pass, build clean.** PR #2 open, needs one merge. |
| Live API | `GET /api/health` and `POST /api/demo/reset` are the only routes. Nothing to click yet. |
| Gates | G0 partial (health live, contracts not frozen). **G1 missed at 15:30** — no listings reach the browser. |
| Dead branches | `b/trust`, `richard-dev`, `agent_backend` fully merged. `2026-10-17-6c1c` is an ancestor of `c/web`. |

**Recovery stance:** G1 is 45 minutes late, not lost. Every later gate shifts only if a block overruns. Do not skip the proof step to catch up — the proofs are the gate.

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
- [ ] Baseline both suites before you change anything: `pytest -q` → 15 passed; `npx vitest run` → 4 passed. If your baseline differs, stop and ask.

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
| **A** | Mount the session routes: `POST /api/sessions`, `POST /api/sessions/{id}/answers`, `GET /api/sessions/{id}`. Add `GET /api/sessions/{id}/events` as SSE with the envelope from `contracts.md`. Emit `session.stage`, `search.started`, `listing.found`. Keep `last_seq` on the session. |
| **B** | **Task 4** — `search(spec, limit=8) -> (listings, source)` in `app/search/service.py`. Catalog fallback on any SerpAPI failure or empty result. Then **Task 14** — `score_investigation()` with the golden tests. |
| **C** | Point `frontend/src/lib/api.ts` at `VITE_API_BASE_URL`. Replace the mock listings with `listing.found` events from the SSE stream. Keep the mock path behind `?mock=1` so a dead backend never kills the demo. |

**Proof:** `curl -N http://127.0.0.1:8000/api/sessions/<id>/events` shows `seq` incrementing and 9 `listing.found` events; the same 9 cards render in the browser.

**If late:** ship the snapshot route first (`GET /api/sessions/{id}` with listings) and stream second. The browser only needs one of them to pass this gate.

### Block 2 — 17:00–18:00 · G2: full investigation, five checks, a score

**Goal:** the villain card turns red on screen, for a stated reason.

| Person | Do |
|---|---|
| **A** | Orchestrator: for each listing call `run_checks()`, then `score_investigation()`, emit `check.started`, `check.completed`, `listing.scored`. Bounded concurrency — do not open 45 sockets at once. |
| **B** | **Task 9** domain age (RDAP → WHOIS), **Task 10** SSL, **Task 13** URL validation + page flags. **Task 11** against the static denylist if no Safe Browsing key; record the key status in `status.md`. |
| **C** | `CheckRow` consumes `check.completed` and upserts by `(listing_id, check_id)`. Skipped renders as "could not verify" — never a green tick. Danger card must name the failed checks. |

**Proof:** browser — `premium-audio-deals.shop` shows `danger` with at least domain age and page flags named, and at least one big merchant shows `trusted`.

**If late:** cut page flags (Task 13) before SSL or domain age. Three checks still clears the coverage floor.

### Block 3 — 18:00–19:30 · G3: recommendation

**Goal:** one pick, justified, and the villain is not it.

| Person | Do |
|---|---|
| **A** | Emit `recommendation.ready`; expose the recommendation in the snapshot. Wire `POST /api/demo/reset` to clear the session registry. |
| **B** | **Task 15** `recommend()` — eligible = trusted ∧ ≥70 ∧ confidence ≥0.6; median of eligible; `no_trusted_option` names the best near-miss. **Task 12** Reddit sentiment. |
| **C** | Recommended-pick banner plus a "why this one" panel: median price, savings, which checks each candidate passed. Empty-state for `no_trusted_option`. |

**Proof:** browser — the cheapest *trusted* listing is the pick, the villain's lower price is visibly rejected with a reason, and savings matches the median minus the pick.

**If late:** cut Reddit (Task 12). The recommendation math does not depend on it.

### Block 4 — 19:30–21:00 · G4: checkout

**Goal:** click through to a receipt against the real backend.

| Person | Do |
|---|---|
| **A** | Mandate → simulated passkey → one-time token → transaction → receipt. Server re-validates: `trusted` ∧ score ≥70 ∧ (allowlisted ∨ ≥3 checks). Atomic transitions, idempotency key, `processor: mock-vic`, `mode: sandbox`. Raw token never stored — SHA-256 and last4 only. |
| **B** | Freeze golden tests. Verify the refusal paths: danger, low score, low coverage, stale investigation. Confirm no fixture text reaches an LLM. |
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
| **B** | `scripts/replay_offline.py` with `OFFLINE=1`, deterministic output. Verify every fixture path works with the network off. |
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

## 6. Gate board

| Gate | Due | State | Owner |
|---|---|---|---|
| G0 Contracts frozen + health | Sat 13:15 | 🟡 health live, `Question` shape needs A's sign-off | A |
| G1 Listings to browser | Sat 15:30 | 🔴 missed — Block 1 recovers it | A + B |
| G2 Investigation + score | Sat 18:00 | ⬜ | B |
| G3 Recommendation | Sat 19:30 | ⬜ | B |
| G4 Checkout → receipt | Sat 21:00 | ⬜ | A + C |
| G5 Devpost draft | Sat 22:30 | ⬜ | B |
| G6 Freeze | Sun 02:00 | ⬜ | all |
| G7 Submit | Sun 09:50 | ⬜ | all |

## 7. Live blockers

| Blocker | Owner | Impact |
|---|---|---|
| No session routes | A | G1 cannot pass; C is on mock data |
| Contracts not frozen | A | `Question` shape is a guess; cheap to confirm, expensive to discover at 21:00 |
| SerpAPI key | A | Catalog only (D-011). Not blocking. |
| Safe Browsing key | B | Static denylist with `source="unavailable"`. Not blocking. |
| Mongo unassigned | A | In-memory adapter until Block 5. Not blocking. |

## 8. Cut order

Cut in this order: live page fetching → Reddit → SerpAPI → Mongo → page flags.

**Never cut:** scoring (Task 14), the fixtures, the golden tests, the sandbox label, the payability gate, the refusal demo.
