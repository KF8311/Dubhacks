---
title: Team Checklist
type: checklist
updated: 2026-10-18
owner: everyone
---

# Team Checklist

One shared checklist. Personal scratch notes do not belong here.

**How to use it:** Section 1 is once per machine. Then work your column in §4. Every task has a proof you produce before the block closes. Tick boxes in the commit that completes them. `docs/status.md` still wins if the two disagree.

> **The point: work until 04:00 PT, then freeze.** Nothing new after 04:00. The morning block is deploy and submit only.

## Where we are now — Sun 02:10 PT · kept build `96cf47f` + docs + search timeout fix

| Thing | State |
|---|---|
| **Code** | **`96cf47f`** — the build that actually searches what you type: live SerpAPI search, curated-catalog fallback, five checks, deterministic scoring, SSE, recommendation, checkout → passkey → receipt, Gemini copy with template fallback. |
| **Decision** | The 20 commits after `96cf47f` were removed from `main`. They are parked, not deleted: [`docs/ideas-after-96cf47f.md`](ideas-after-96cf47f.md) lists every one and where it still lives. |
| **Git** | **`main` is restored** — [PR #34](https://github.com/KF8311/Dubhacks/pull/34) merged as `2d53ca1`; the tree is `96cf47f` plus the archive and docs commits. The 20 removed commits stay reachable on `backup/main-post-96cf47f` and the `origin/restore/*` branches. |
| **Tests** | Backend **215 passed**. Frontend **47 passed**, `npm run build` clean. [`scripts/replay_offline.py`](../scripts/replay_offline.py) exits 0 with the frozen numbers. Docs that say 187/34 are stale (B's task). |
| **Run it** | `.\scripts\dev.cmd` — backend + frontend in one command. Modes and troubleshooting: [`docs/RUN.md`](RUN.md). |
| **Deploy** | **Fly is the path for this commit** (`fly.toml`, `backend/Dockerfile` copies `data/`). A Vercel Git deploy of this commit is broken — it ships no data. Do not submit `sykes.select`; it runs the removed code. |
| **Health note** | With `MONGODB_URI` unset, `/api/health` answers `degraded` by design. Read it as "optional store off", not "broken". |

**Before anyone starts:** **`main` is restored** (PR #34 is merged) — `git fetch && git checkout main && git pull`. If your clone still has the old tip, `git reset --hard origin/main` — this is the one time a reset is expected.

---

## 1. Universal — once per machine

- [ ] Open **[`Dubhacks/`](../)** as the working directory, not `Desktop/dubhacks/`.
- [ ] `git fetch origin && git checkout main && git pull` — `main` is the restored build after the PR merges.
- [ ] Read [`docs/status.md`](status.md), [`docs/RUN.md`](RUN.md), [`CLAUDE.md`](../CLAUDE.md).
- [ ] Backend venv (Python 3.11 or 3.12; 3.14 works but is untested by the docs):
  ```bash
  cd backend && python -m venv .venv
  .venv/Scripts/python.exe -m pip install -r requirements.txt
  ```
- [ ] Frontend deps: `cd frontend && npm ci`.
- [ ] Baseline before you change anything: **215 backend**, **47 frontend**, `npm run build` clean, replay exit 0. If your baseline differs, stop and ask.
- [ ] Start the stack with `.\scripts\dev.cmd` and click the demo path once.

## 2. Universal — every commit

- [ ] Tests pass. Run them; paste the output when you claim a task done.
- [ ] **No AI attribution.** No `Co-Authored-By`, no "Generated with" trailers. Commits carry your name only.
- [ ] Commit every 30 minutes. `feat:`, `fix:`, `docs:`, `chore:`.
- [ ] You touched only your own files. `backend/app/domain/models.py`, `frontend/src/lib/types.ts`, and `docs/contracts.md` belong to their owner.
- [ ] No secrets, no real PII, no real card numbers, no raw tokens.
- [ ] Fixture-sourced results carry `source: "fixture"`.

## 3. Universal — every gate

- [ ] Run the real command or the real browser path before claiming a gate passed. A green unit test is not a gate proof.
- [ ] Update [`docs/status.md`](status.md): gate, owners, blockers.
- [ ] Append to [`docs/decisions.md`](decisions.md) if you changed a decision.
- [ ] Push by **:45 of each hour**. The next person starts from pushed code.

---

## 4. Block R — 02:00–04:00 PT · make the kept build demo-ready

Five-minute sync at 02:45 and 03:45: each person says *done / blocked / next*, one scribe updates `status.md`, everyone pushes.

| Time | Everyone |
|---|---|
| 02:00–02:10 | Pull, baseline, start `dev.cmd`, open the board |
| 02:10–03:45 | Your column below |
| 03:45–03:55 | Gates in §6, push, update `status.md` |
| **04:00** | **Freeze.** Bugfixes and docs only after this |

### A — search quality, contracts, deploy readiness

1. **Baseline.** Run the suites and replay. Confirm `OFFLINE` is not set in your shell.
2. **Verify the live-search timeout fix — top priority.** The "it typed the number and showed the offline catalog" complaint was root-caused on 2026-10-18: `SerpAPIProvider` accepted `timeout_s=SEARCH_S - 1.0` but `httpx.AsyncClient` hardcoded `timeout=2.5`, so anything slower than 2.5 s fell back to the catalog. The client now uses `self.timeout_s` (4.0 s), with a regression test in [`test_serpapi.py`](../backend/tests/unit/test_serpapi.py). Re-run a numeric query (`mechanical keyboard under 150`) and confirm live listings, not the catalog.
3. **Optional, same window.** If a live query still falls back because SerpAPI is slow, or returns only one or two results, adopt the `<3` guard from parked commit `c55ce29` (idea **B** in [`ideas-after-96cf47f.md`](ideas-after-96cf47f.md)): fall back to the catalog when the live result count is below `min(3, limit)`.
   ```bash
   git show c55ce29 -- backend/app/search/service.py
   ```
   Hand-apply the one-line change and copy its test; do **not** check out the whole commit — `c55ce29` also carries unrelated frontend/CORS changes.
4. **Sign off the `Question` shape** in [`docs/contracts.md`](contracts.md) — the last G0 item. Read [`questions.py`](../backend/app/sessions/questions.py), confirm the fields the API actually returns, and remove "Not yet in `models.py`" if it is true.
5. **VEYZL decision by 03:00.** Default is **cut it**: the probe hardening lives in the removed commits and the app is not installed. If it is not installed by 03:00, mark the side track not selected in the Devpost and in [`docs/veylz-audit.md`](veylz-audit.md). Do not spend Block R time on it.
6. **Prove the kept build over HTTP:** create a session, answer **$300–$600**, confirm 9 listings / 8 trusted / villain red / pick `lst_tgt_bsp`, then checkout → confirm → public receipt. Record the `search.completed` `source` value for a live query and for `OFFLINE=1`.
7. **Docker sanity** (this is what Fly runs):
   ```powershell
   docker build -f backend/Dockerfile -t sniff-visa .
   docker run --rm -p 8080:8080 --env-file backend/.env sniff-visa
   ```
   If Docker is unavailable, say so in `status.md`; the morning deploy becomes higher risk.
8. **Push.** Morning: `fly deploy` from the repo root, then `smoke_http.py` against the URL.

**Done when:** a typed numeric query returns matching live listings (or falls back without a thin grid), `Question` is signed off, the HTTP path and refusal are recorded, and the VEYZL decision is written down.

### B — truth in the docs and the Devpost

1. **Record the revert.** Append a decision to [`docs/decisions.md`](decisions.md): `96cf47f` is the kept build, the later 20 commits are parked in [`ideas-after-96cf47f.md`](ideas-after-96cf47f.md), and this PR restores `main`. Number it after the last entry; do not reuse a number.
2. **Fix the test counts everywhere** to **215 backend / 47 frontend**: [`README.md`](../README.md#L142), [`docs/devpost.md`](devpost.md#L92), [`docs/status.md`](status.md), and this file. Do not invent a file count; use `pytest -q` and `npx vitest run` output.
3. **Scrub claims the kept code cannot support.** Anything that depends on the removed commits must go or be reworded: VEYZL probe behaviour beyond the guard that exists at `96cf47f`, Vercel data bundling, host-aware `apiBase`, `sykes.select` CORS, health diagnostics. Start with:
   ```bash
   grep -rn "VEYZL\|Vercel\|sykes.select\|host-aware" README.md docs/devpost*.md docs/status.md
   ```
4. **Decide the MLH MongoDB claim.** Keep it only if Atlas is actually exercised; otherwise remove the claim and the checkbox. In-memory remains the default.
5. **Pre-fill the Devpost form** in [`docs/devpost-form.md`](devpost-form.md) — every field that does not need A's URL, C's screenshots, or the video. Generative-AI answer: **Yes**.
6. **Final numbers:** put the replay output into [`docs/status.md`](status.md): 9 listings, 8 trusted, 1 danger (`lst_vln_xm5`), pick `lst_tgt_bsp`, median $374.49, savings $194.50.
7. **No secrets tracked:** `git ls-files | grep -i env` must show only `.env.example` files.
8. **Push.** Morning: drop in the URL and gallery, submit by 09:50.

**Done when:** no doc claims 187/34 or a removed feature, the decision entry exists, and the Devpost form is complete except for artifacts.

### C — browser proof and the two copy fixes

1. **Click the kept build through a real browser.** Start `.\scripts\dev.cmd`, open the URL Vite prints, query `noise cancelling headphones`, answer **$300–$600 / Travel / Noise cancelling**. Confirm: 9 cards, villain red with its reasons, `Best pick` = Target $179.99, savings $194.50. **Screenshot the grid.**
2. **Pay → passkey → receipt** on the best pick. Confirm the receipt shows the score, `4242`, and the sandbox line. **Screenshot the receipt.**
3. **Try the villain.** Confirm the refusal shows the server's code. **Screenshot the refusal.**
4. **`skipped` copy:** change [`CheckRow.tsx:15`](../frontend/src/features/results/CheckRow.tsx) from `"Skipped"` to **"Could not verify"**. Update the test that asserts the copy.
5. **Budget honesty ([D-022](decisions.md)):** add either an "over budget" badge on a listing above the answer or "closest match" copy next to the pick. Pick one and put it on screen. Do not call the budget a hard cap.
6. **Mock fallback:** with the backend stopped, open `?mock=1` and confirm the whole flow still renders.
7. **Record one full run** of the demo path (screen recording, phone-width optional).
8. **`npm run build` clean**, then push.

**Done when:** the three screenshots and the recording exist, both copy changes are visible in the app, and the build is clean.

### If your column finishes early

Help C with the video, then B with the claim scrub. Do **not** start new features, do not re-import work from the parked archive, and do not redeploy anything without saying so.

---

## 5. Gate board

| Gate | Due | State | Owner |
|---|---|---|---|
| G0 Contracts frozen + health | Sun 03:00 | 🟡 health live; `Question` shape is the last open item | A |
| G1 Listings to browser | Sun 03:00 | 🟡 server proof exists; browser proof owed on the kept build | C |
| G2 Investigation + score | Sun 03:00 | 🟡 same — villain must be red on screen | C |
| G3 Recommendation | Sun 03:00 | 🟡 same — best pick and savings on screen | C |
| G4 Checkout → receipt | Sun 03:15 | 🟡 server path proven; browser click-through owed | C |
| G5 Devpost draft | Sun 03:45 | 🟡 text written; URL, screenshots, video pending | B |
| G6 Freeze | Sun 04:00 | ⬜ | all |
| G7 Submit | Sun 09:50 | ⬜ | B |

## 6. Block R gates — run at 03:45

```powershell
cd backend;  .\.venv\Scripts\python.exe -m pytest -q        # 215 passed
cd frontend; npx vitest run                                 # 47 passed
cd frontend; npm run build                                  # clean
cd ..; backend\.venv\Scripts\python.exe scripts\replay_offline.py   # exit 0
git ls-files | Select-String -Pattern "\.env"               # only .env.example
```

Do **not** run the suite with `OFFLINE=1` exported. `test_ssl_cert.py` and `test_domain_age.py` pass `ctx=None` and read ambient settings, so 13 tests fail for reasons unrelated to the product. The freeze proof is: **215 pass with no `GEMINI_API_KEY`**, plus the replay. Set `OFFLINE` per-process only.

## 7. Live blockers

| Blocker | Owner | Impact |
|---|---|---|
| Live search can return one or two results | A | Thin live grids are shown as-is. Task A3 (the parked `<3` guard) is optional; the timeout half is fixed. |
| A slow live query falls back to the catalog | fixed 2026-10-18 | The client timeout was hardcoded at 2.5 s; it now uses `SEARCH_S - 1.0` (4.0 s). Regression test added. |
| Browser has not exercised the kept build | C | The wiring is merged but this exact commit has not been clicked through. Top G1–G4 risk. |
| Docs say 187/34; the code is 215/47 | B | Judges and teammates read the docs. Fix before submission. |
| `Question` shape not frozen | A | Last G0 item; cheap now, expensive at freeze. |
| Fly URL serves the removed build | A | Deploy in the morning from the repo root. Never submit `sykes.select` — it runs the removed code. |
| Vercel Git deploy is broken at this commit | A | It ships no `data/`. The fix is parked as idea A. Use Fly. |
| Offline mode skips the budget filter | B | All 9 cards appear regardless of answer. Say "full catalog", never "budget-filtered". |
| Budget answer changes the card count | C | Under $150 → 1 (villain only), $150–$300 → 3, $300–$600 → 9. The demo uses **$300–$600**. |
| An over-budget listing can be recommended | C | D-022: say "closest match" or show the badge. Never call the budget a hard cap. |
| Mongo / MLH claim | B | Keep only if Atlas is exercised; otherwise drop it. |
| VEYZL side track | A | Cut by 03:00 unless the app is installed and a check run is visible on a PR. |
| `GEMINI_API_KEY` absent on Fly | A | Templates are the fallback; the demo still runs. Set it only if the copy reads worse on stage. |
| Public health reads `degraded` | all | By design with Mongo off. Say "optional store off" before a judge asks. |

## 8. Cut order

Live page fetching → Reddit → SerpAPI → Mongo → page flags.

**Never cut:** scoring, the fixtures, the golden tests, the sandbox label, the payability gate, the refusal demo, offline replay.

## 9. Demo script — rehearse exactly this

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

**Gate check before each rehearsal:**

```powershell
cd backend;  .\.venv\Scripts\python.exe -m pytest -q        # 215 passed
cd frontend; npx vitest run; npm run build                  # 47 passed, clean
backend\.venv\Scripts\python.exe scripts\replay_offline.py  # exit 0
```

## 10. Morning — 08:30–09:50 PT · deploy and submit

| Time | Owner | Do |
|---|---|---|
| 08:30 | A | `fly deploy` from the **repo root**; set `SERPAPI_KEY` and `GEMINI_API_KEY` only if the deck needs them; run `backend/scripts/smoke_http.py` against the public URL. |
| 08:50 | C | Re-check the URL in a browser at phone width; replace any screenshot that shows the wrong build. |
| 09:00 | B | Fill the Devpost with the live URL, three images, the video, and the track selections; confirm every claim against §7. |
| 09:30 | all | Rehearse once on the public URL; say "no unprotected checkout" and show the refusal. |
| 09:50 | B | **Submit. Capture the confirmation.** |

**Do not** attempt a Vercel Git deploy in this window. It needs the parked data-bundling fix (idea A) and testing time you do not have. Fly is the path.

## 11. Already done — do not redo

- [x] Backend: scaffold, config, health, sessions, SSE, orchestrator fan-out
- [x] Search: `search(spec, limit)`, live SerpAPI path, catalog fallback, budget parsing (D-021, D-022)
- [x] Trust: all five checks, timeout-safe runner, fixtures, denylist, allowlist
- [x] Scoring: deterministic `score_investigation()`, golden tests, villain `0 / danger`
- [x] Recommendation: median/savings, `no_trusted_option`, allowlist exemption (D-015)
- [x] Payments: mandate, simulated passkey, token, checkout/confirm, HMAC receipts, public share, refusal paths
- [x] Frontend: discovery, results grid, check rows, best pick, purge, checkout sheet, receipt, `/r/:share_id`, `?mock=1`
- [x] Gemini: questions, narration, check explanations, 2.5 s timeout, template fallback; never scores or decides
- [x] Repository protocol with in-memory + Mongo adapters; `MONGODB_URI` unset is the default
- [x] Offline replay reproduces the live numbers exactly: 9 / 8 / 0 / 1, pick `lst_tgt_bsp`, median $374.49, savings $194.50
- [x] C's 390 px reflow, `api_key` redaction, immersive merchant resolution, `OFFLINE=1` catalog pinning
- [x] One-command startup: [`scripts/dev.cmd`](../scripts/dev.cmd) and [`docs/RUN.md`](RUN.md)
- [x] Live-search timeout fix: the SerpAPI client now honors `timeout_s` (4.0 s) instead of hardcoding 2.5 s — numeric queries no longer fall back to the catalog ([`serpapi.py`](../backend/app/search/serpapi.py), regression test in [`test_serpapi.py`](../backend/tests/unit/test_serpapi.py))
- [x] Post-`96cf47f` work archived with links and a revisit table: [`ideas-after-96cf47f.md`](ideas-after-96cf47f.md)
