---
title: Team Checklist
type: checklist
updated: 2026-10-17
owner: everyone
---

# Team Checklist

One shared checklist. Personal scratch notes do not belong here.

**How to use it:** do the universal sections once per machine, then work your own block top to bottom. Tick boxes in the commit that completes them. `docs/status.md` still wins if the two disagree.

---

## 1. Universal — before you write any code

- [ ] Open **`Dubhacks/`** as the working directory, not `Desktop/dubhacks/`. Skills load from `.claude/skills/` in the folder the session starts in.
- [ ] Type `/` and confirm the skills are listed. If not, the folder is wrong.
- [ ] `git pull origin main` and read `docs/status.md`, then `CLAUDE.md`, then `docs/INDEX.md`.
- [ ] Read your block in `docs/team-split-3.md` and the task numbers you own in the plan.
- [ ] Create your branch: `a/platform`, `b/trust`, `c/frontend`. Never commit product code to `main`.
- [ ] Create the backend venv and install deps:
  ```bash
  cd backend
  python -m venv .venv
  .venv/Scripts/python -m pip install pytest pytest-asyncio httpx pydantic beautifulsoup4 python-whois respx ruff
  ```
  Python 3.11 or 3.12. Do not use 3.14 — wheels are unreliable.
- [ ] Confirm the API keys you personally depend on, and record go/no-go in `docs/status.md`.
- [ ] Test the network calls you will make from the venue Wi-Fi before you build around them.

## 2. Universal — every commit

- [ ] Tests pass. Run them; paste the output when you claim a task is done.
- [ ] **No AI attribution.** No `Co-Authored-By`, no "Generated with" trailers. Commits carry your name only.
- [ ] Commit every 30 minutes. Small commits, imperative messages: `feat:`, `fix:`, `docs:`, `chore:`.
- [ ] You touched only your own files. `backend/app/domain/models.py`, `frontend/src/lib/types.ts`, and `docs/contracts.md` belong to their owner.
- [ ] No secrets, no real PII, no real card numbers, no raw tokens.
- [ ] Fixture-sourced results carry `source: "fixture"`.

## 3. Universal — at every gate

- [ ] Run the real command or demo path, not a mock, before claiming the gate passed.
- [ ] Update `docs/status.md`: current gate, who is doing what, blockers, live risks.
- [ ] If you changed a decision, append to `docs/decisions.md` with the alternatives you rejected.
- [ ] If you are changing owners or going to sleep, run `/handoff` into `docs/handoffs/`.

---

## 4. Person A — Platform / Agent

- [ ] **Task 1:** backend scaffold, `pyproject.toml` with `pythonpath = ["."]`, `app/domain/models.py`, `app/core/config.py`, `GET /api/health`. **Blocks B and C.**
- [ ] **Fly.io:** `fly launch` on one `shared-cpu-1x` 256 MB machine, `uvicorn --workers 1`, no global gzip. Public health URL recorded in `status.md`. Card required after the 2-hour trial (D-010).
- [ ] **Task 2:** freeze `docs/contracts.md` — API shapes, `TrustCheckResult`, SSE event names and ordering.
- [ ] **Task 5:** `SessionRegistry`, `POST /api/sessions`, `POST /api/sessions/{id}/answers`, snapshot route.
- [ ] **Task 6:** one SSE stream per session, monotonic `seq`, snapshot fallback. Verify with `curl -N`.
- [ ] **Orchestrator:** consume B's `get_checks()` / `run_checks()` / `score_investigation()` / `recommend()`; never let the LLM compute a score.
- [ ] **Payability gate:** server-side re-validation — `trusted` AND score ≥ 70 AND (allowlisted OR ≥ 3 checks completed). Reject everything else with a reason.
- [ ] **Checkout:** mock VIC mandate → simulated passkey → one-time token → transaction → receipt. Atomic state transitions, idempotency key. `processor: mock-vic`, `mode: sandbox` on every response.
- [ ] **Task 27:** Mongo repository behind the existing protocol, TTL indexes, PII redaction. In-memory adapter must keep working.
- [ ] **Handoffs owed to B/C:** contracts by 3:30, orchestrator wiring by 6:00, checkout by 9:00.

## 5. Person B — Trust / Data

- [x] **Pre-flight:** venv on Python 3.11 with pytest, httpx, pydantic, bs4, python-whois, respx, ruff.
- [x] **Task 3:** `data/catalog.json` — 8 trusted listings across 5 merchants plus the villain on `premium-audio-deals.shop`.
- [x] **Task 3:** `data/allowlist.json` — 36 established domains, dot-boundary matching (`bestbuy.com.evil.shop` → false).
- [x] **Task 3:** villain fixtures — 12-day RDAP record, scam page with urgency/crypto-only/no refunds, 3 Reddit reports with titles and permalinks only.
- [x] **Task 3:** `load_catalog()`, `load_allowlist()`, `test_catalog.py` — **2 passed**.
- [x] **Deploy decision:** Fly.io recorded as D-010.
- [x] **Task 8:** `TrustCheck` protocol, `get_checks()`, `run_checks()` — timeouts yield `SKIPPED` with `source="timeout"`, never a pass. **3 unit tests passing.**
- [ ] **Unblock:** replace the stopgap `backend/app/domain/models.py` and `backend/app/domain/enums.py` with A's Task 1 versions. They currently hold `Listing`, `SearchSpec`, `Evidence`, `TrustCheckResult`, `CheckId`, `TrustStatus`, `Verdict`.
- [ ] **Task 4:** `search(spec, limit=8) -> (listings, source)` — SerpAPI with a 5s timeout, catalog fallback, reject empty or `google.com` domains.
- [ ] **Task 9:** domain age — RDAP primary, WHOIS fallback. <30 days → `FAILED` 0.95, <90 days → `WARNING` 0.6.
- [ ] **Task 10:** SSL — invalid or mismatched `FAILED` 0.8, free issuer `WARNING` 0.4.
- [ ] **Task 11:** Safe Browsing — any hit `FAILED` 1.0; no key → static denylist with `source="unavailable"`.
- [ ] **Task 12:** Reddit sentiment — 1–2 hits `WARNING` 0.5, 3+ `FAILED` 0.8, errors `SKIPPED`. Titles and permalinks only.
- [ ] **Task 13:** `validate_public_url` rejects non-HTTPS, credentials, IP literals, non-443, >2048 chars, private/loopback/link-local/CGNAT/reserved. Then `page_flags`.
- [ ] **Task 14:** `score_investigation()` — `severity × 40` failed, `severity × 15` warning, thresholds 70/40, coverage cap 69. Golden test: villain ≤31 danger, hero ≥90 trusted.
- [ ] **Task 15:** `recommend()` — eligible means trusted AND ≥70 AND confidence ≥0.6; median of eligible; `no_trusted_option` names the best near-miss.
- [ ] **Task 28:** `DEMO_MODE`, `DEMO_PACING`, `OFFLINE`, deterministic reset, fixtures labeled.
- [ ] **Support Task 27** with A: TTL indexes, cache collections, redaction.

## 6. Person C — Frontend / UX

- [ ] Build against `data/mock-session.json` from 1:15 PM; do not wait for the backend.
- [ ] Results grid with checks landing one at a time; every card shows verdict and score.
- [ ] Danger card must make the *reason* obvious — which checks failed, what evidence.
- [ ] Skipped checks render as "could not verify", never as a green tick.
- [ ] Checkout UI: cap, sandbox banner, passkey step, disabled when not payable.
- [ ] Receipt page: merchant, checks, score, token last4 only, "Sandbox — simulated Visa Intelligent Commerce flow."
- [ ] Integrate real APIs at 7:30 PM and replay the full path.
- [ ] Three screenshots for the Devpost by 9:00 PM: results grid, danger card detail, receipt.
- [ ] Reflow works at phone width; no horizontal scroll.

---

## 7. Gate board

| Gate | Due | Owner | Proof |
|---|---|---|---|
| G0 Contracts frozen + health deployed | Sat 1:15 PM | A | public URL + `docs/contracts.md` |
| G1 Listings stream to browser | Sat 3:30 PM | A + B | `curl -N` or screen recording |
| G2 Full investigation, 5 checks, score | Sat 6:00 PM | B | browser |
| G3 Recommendation + best pick | Sat 7:30 PM | B | browser |
| G4 Checkout → passkey → receipt | Sat 9:00 PM | A + C | browser against real backend |
| G5 Devpost draft submitted | Sat 10:30 PM | B | Devpost confirmation |
| G6 Feature freeze | Sun 2:00 AM | all | team agreement |
| G7 Final submission | Sun 9:50 AM | all | Devpost confirmation |

## 8. Judge-day (Sunday)

- [ ] Backend warm **20 minutes** before recording. Fly machine running, health returns 200.
- [ ] Offline path rehearsed: `OFFLINE=1 python scripts/replay_offline.py`.
- [ ] Demo script read twice by the person driving.
- [ ] Every claim in the Devpost is true: sandbox payment, synthetic data, no production Visa integration.
- [ ] Evidence of the VEYZL finding in `docs/veylz-audit.md`.
- [ ] Submitted by 9:50 AM. Capture the confirmation.

## 9. Current blockers

| Blocker | Owner | Impact |
|---|---|---|
| No backend scaffold, no pytest config | A | B shipped stopgap `models.py`/`enums.py` on `b/trust`, so Tasks 4 and 9–15 can proceed; app wiring and C's integration still blocked |
| No public health URL | A | G0 missed |
| SerpAPI key unconfirmed | A | Task 4 falls back to catalog |
| Safe Browsing key unconfirmed | B | Check ships as `source="unavailable"` |
| MongoDB Atlas owner unassigned | A | In-memory adapter until resolved |

## 10. Cut order — same for everyone

Cut in this order: live page fetching → live Reddit → SerpAPI → Mongo. **Never cut:** scoring (Task 14), the fixtures, the golden tests, the sandbox label, the payability gate.
