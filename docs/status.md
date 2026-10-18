---
title: Status
type: status
updated: 2026-10-17
owner: rotating scribe
---

# Status

This is the only file that claims to be current.

| Field | Value |
|---|---|
| Gate | **Block 4 is closed and G5 is close-out.** The code is done. What remains is a public deploy, C's browser screenshots, the video, and a clean VEYZL re-run. |
| Health | https://sniff-visa-dubhacks.fly.dev/api/health (serves the pre-merge build; redeploy is still owed) |
| Deploy | **Fly.io** org `dubhacks`, app `sniff-visa-dubhacks`, region `sjc` (D-010, D-012, D-013), from the repo root. **Vercel services** is now a second path — [`vercel.json`](../vercel.json), backend `bundle_data.py`, frontend same-origin `/api` — merged 22:49 PT and not yet exercised. Render is backup. |
| Contracts | `docs/contracts.md` carries domain types, `Recommendation`, SSE ordering, and checkout/confirm JSON. `listing.scored` now also carries `allowlisted` so the UI does not render a curated merchant as "0". |
| SerpAPI | No `SERPAPI_KEY`. Catalog-only in the deploy; the live path (D-021, superseding D-011) infers the merchant domain from Google Shopping's `source` and immersive `stores`, and is untested against a real key. |
| Tests | Backend **204 passed** (35 files). Frontend **39 passed** (15 files), `npm run build` clean. |
| Offline replay | `backend/.venv/Scripts/python.exe scripts/replay_offline.py` → same numbers as the live run, exit 0. Exits 1 if the demo drifts. |
| Routes | Sessions create/answer/snapshot/events/**explain**, orchestrator fan-out, payability guard and mandates, **checkout/confirm (Task 23)**, **receipts + public share (Task 24)**, **repository swap (Task 27)**. The frontend calls all of them live; `?mock=1` is the fallback. |
| Owners | A: platform + orchestrator + payments + **VEYZL (Task 29, D-020)**. B: trust + data + **Mongo review (Task 27, D-016)** + Devpost. C: frontend. |
| Blockers | **A still owes a public deploy** (Fly or Vercel) and a clean VEYZL re-run; C owes the browser click-through and screenshots; B fills `docs/devpost-form.md` as those artifacts land. None of them blocks the others. |
| Branches | **`main` carries everything and is pushed** ([PR #20](https://github.com/KF8311/Dubhacks/pull/20)–[PR #25](https://github.com/KF8311/Dubhacks/pull/25) rebase-merged or open; every working branch deleted after its diff against `main` came back empty). Run `git log --oneline origin/main` for the current tip — recording the hash here just goes stale on the next docs commit. Local and remote `main` are the same commit. Every other remote head is contained in `main`. |
| Model | **Gemini 3.5 Flash Lite** writes questions, narration, and check explanations (D-017–D-019), 2.5 s timeout, template fallback. It never scores, selects checks, or touches payability. |

Last updated: 2026-10-17 22:49 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health deployed | Sat 13:15 | 🟡 health live, `Question` shape still open | URL above + `docs/contracts.md` |
| G1 Listings stream to browser | Sat 15:30 | 🟢 server proof + live `EventSource` client wired (browser screenshot still owed) | 9 `listing.found`; `frontend/src/lib/sse.ts` + `useSessionStream` |
| G2 Full investigation, 5 checks, score | Sat 18:00 | 🟢 server proof; cards render `check.completed` | 45 `check.completed`, villain `0 / danger`, 8 trusted |
| G3 Recommendation + best pick | Sat 19:30 | 🟢 server proof; `BestPick` + best-pick ring in the grid | pick `lst_tgt_bsp` $179.99, median $374.49, savings $194.50 |
| G4 Checkout → passkey → receipt | Sat 21:00 | 🟡 **build complete and merged**; browser click-through opens Block 5 | 204 backend / 39 frontend tests; live HTTP checkout → confirm → public receipt; refusal shows `MERCHANT_NOT_TRUSTED` |
| G5 Devpost draft submitted | Sat 22:30 | 🟡 **close-out** — text done; URL, screenshots, video, and a clean VEYZL report pending. The VEYZL finding is already reproduced and fixed | `docs/devpost-form.md` + Devpost confirmation |
| G6 Feature freeze | Sun 02:00 | ⬜ | Team agreement |
| G7 Final submission | Sun 09:50 | ⬜ | Devpost confirmation |

## Proof of the connected path (2026-10-17 17:20 PT)

Backend over real HTTP, with `Origin: http://localhost:5173` (CORS verified on both the API and the SSE stream):

```
POST /api/sessions            → 201, question ids q_budget / q_use / q_priority
POST /api/sessions/{id}/answers → 202, stage "searching"
GET  /api/sessions/{id}       → stage "ready", 9 listings
GET  /api/sessions/{id}/events → 107 events, seq 1..107, closes on investigation.complete
stats:  {'listings': 9, 'trusted': 8, 'caution': 0, 'danger': 1}
pick:   lst_tgt_bsp ($179.99) · median $374.49 · savings $194.50
villain: lst_vln_xm5 → danger, score 0, "Reported by the local threat list: LOCAL_DENYLIST"
```

Frontend: `npx vitest run` → 6 files / 9 tests, `tsc --noEmit` clean, `npm run build` clean.

## In progress

| Owner | Task | Started | Expected | Notes |
|---|---|---|---|---|
| A | Public deploy; smoke the public URL; **VEYZL audit + fix (D-020, D-023)** | 18:25 | 22:30 | ✅ Search/budget work merged at 19:40. ✅ **VEYZL audit ran** (two hosted reports) and finding 1 — no guard on the generative path — is fixed with five tests, merged 22:49 PT. ✅ **Vercel services path** added. ⬜ A public deploy (Fly or Vercel) and a **clean VEYZL re-run** are the last A items |
| C | Browser screenshots — results grid, danger detail, receipt — plus one recording | 18:25 | 22:30 | ✅ Block 6 UI merged (`cf24bdb`, `3ceffbc`): 390px reflow (overflow 0), `api_key` redaction, immersive merchant resolution, offline catalog pinning. ⬜ Screenshots and video are the last G5 items |
| B | Devpost, final numbers, audit review | 18:40 | 22:30 | ✅ Devpost, README, `docs/devpost-form.md`, technical-claims handoff, audit scope + `/api/demo/reset` reproduction, repository review first pass (`8c89260`); ⬜ fill the form as A and C land artifacts |

## Done since last update

- [x] C: Tasks 17–21 — discovery, results grid, check rows, best pick, purge, empty/error states (PR #10)
- [x] Hookup: `api.ts` and `useSessionStream` now default to the **live** backend; `?mock=1` is the fallback
- [x] Fixed: discovery submitted answers to a hardcoded `ses_mock`, so the live flow 404'd at the second step
- [x] Fixed: allowlisted merchants rendered as `0 · Trusted`; the badge now reads `Verified · Trusted`
- [x] `listing.scored` carries `allowlisted` end to end
- [x] CORS confirmed for `http://localhost:5173` on both JSON and SSE
- [x] B: **Task 28** — offline replay (`app/demo/replay.py`, `scripts/replay_offline.py`) reproduces the live run with no server and no network; exit 1 on drift
- [x] B: domain age and SSL honour `OFFLINE=1`; the orchestrator accepts an injected `Settings`
- [x] B: villain integration golden test — real checks → `danger` → excluded from the pick even when cheapest
- [x] B: Block 4 refusal paths — real hero pays, real villain refused, stale/cap/currency/coverage pinned, no-LLM source guard
- [x] A: Task 23/24 — checkout, confirm, signed receipts, public share, demo reset (PR #13)
- [x] C: Tasks 25–26 — checkout sheet, mandate card, passkey dialog, processing state, receipt page, `/r/:share_id` (PR #14)
- [x] Hookup: C's client now sends the contracted mandate and passkey assertion, follows `receipt_url`, and renders the server's `PayabilityCode`; response shapes pinned in `frontend/src/lib/api.test.ts`
- [x] Hookup: refusal messages are human copy instead of the bare code
- [x] B: `docs/devpost.md` drafted with every number checked against the code; placeholders only for the URL, video, and screenshots
- [x] B: `README.md` rewritten — setup, env vars, API table, demo script, tests, offline replay, and the honesty notes (sandbox, no model in the path, in-memory store)
- [x] B: `docs/veylz-audit.md` scaffolded — scope, method, and six candidate controls; no finding is claimed until one is reproduced (PR #17)
- [x] Merge reconciliation: A's three Gemini decisions were renumbered D-017/D-018/D-019 (D-016 was already Mongo ownership); `README.md` and `docs/devpost.md` corrected — the model writes copy, never a verdict
- [x] A: **Gemini 3.5 Flash Lite** for questions, narration, and on-demand explanations; trust/check/payment modules still cannot import it
- [x] A: **`Repository` protocol** — in-memory + Mongo adapters, TTL indexes; `MONGODB_URI` unset remains the default
- [x] C: `c/web` — responsive layout, reduced motion, allowlisted merchants through checkout (D-015)
- [x] B: `docs/devpost-form.md` — all five Devpost steps mapped with limits, required fields, exact copy, and track selections (PR #19)
- [x] B: reproduced the unauthenticated `/api/demo/reset` (`200`, session destroyed) and recorded it in `docs/veylz-audit.md`
- [x] C: **API-unreachable alert** on discovery, and `Verified` rendering for allowlisted merchants on card, sheet, and receipt
- [x] Ownership: **Task 29 (VEYZL) moves to A** (D-020) because the GitHub App install needs repo admin; B's scoping and reproduction carry over
- [x] B: **Repository review, first pass (`8c89260`)** — protocol covers all 17 methods; `get_repository()` typed with the protocol; `idempotency_key` partial index replaces `sparse`, so keyless checkouts no longer collide on `null`
- [x] B: persistence claim narrowed — Mongo carries the payment path only; sessions, listings, and investigations stay in-process, and mock VIC tokens never leave the process
- [x] A merged (`8687203`) — Google `source`→domain (D-021, supersedes D-011), `under_150` budget parsing, upper-case `SERPAPI_KEY`, catalog fallback on an empty budget filter (D-022), session-guarded checkout. Three conflicts resolved by hand; A's `D-019` renumbered to `D-021`
- [x] C merged (`cf24bdb`, `3ceffbc`, fast-forwarded; rebase-merged as PR #20 rewrote the SHAs and dropped her merge commit) — phone-width reflow at 390px with zero horizontal overflow, `api_key`/`x-goog-api-key` redaction in `redact()`, unknown merchants resolved through Google Shopping's immersive `stores` with a 4-lookup/2 s cap, and `OFFLINE=1` pinned to the curated catalog so replay numbers cannot drift
- [x] B restored the receipt score assertion C's wrap fix dropped; the test now covers `Score 92` and `break-words` (`f0014c0`)
- [x] Verified after the merge: **187 backend / 34 frontend at the time** (now 204 / 39), build clean, replay exit 0, and the live HTTP run for **$300–$600** matches the replay exactly
- [x] A merged (`agent_backend`, 22:49 PT) — **VEYZL guard [D-023]**: `llm_guard.py` refuses jailbreaks, self-harm, explosives, SSNs, and secrets before Gemini, redacts PII, and answers VEYZL-shaped probe payloads with an OpenAI-style refusal; **Vercel services** config with `bundle_data.py` and `paths.py`; a failed live search falls back to the catalog rather than an empty grid. Five conflicts resolved: decision renumbered (D-020 was taken), audit doc merged rather than replaced, README kept, both SerpAPI tests and both orchestrator paths kept, and `apiBase()` restores the `localhost:8000` dev default
- [x] Post-merge: **204 backend**, **39 frontend**, build clean, replay exit 0

## Next three actions

1. **C or B, no dependency on A:** open `npm run dev` against `uvicorn` on :8000, click the live flow — answer **$300–$600**, villain red, best pick `lst_tgt_bsp`, Pay → passkey → receipt — and screenshot it. Local dev now falls back to `localhost:8000` with no `.env`.
2. **A:** deploy from the repo root, **either** `fly deploy` **or** the Vercel services path, then run `backend/scripts/smoke_http.py` against it; B fills `docs/devpost-form.md` as the URL and screenshots land.
3. **A:** re-run VEYZL against the fixed build and capture a report that is not all-error. Only a clean report earns the side track, and only then should `VEYZL Audit` go back on the ruleset.

## Demo trap to avoid

The demo run must answer **$300–$600**. Measured on the merged build: `Under $150` → 1 card (the villain, ending in `no_trusted_option`), `$150–$300` → 3 cards, `$300–$600` → all 9. The catalog runs to $549.99, so the lower answers are thinner, not wrong. Under `OFFLINE=1` the budget filter is skipped and all 9 cards appear regardless — do not describe plane mode as budget-filtered. See `docs/checklist.md` §10.

## Risks that are currently live

| Risk | Trigger seen? | Action taken |
|---|---|---|
| Checkout not reachable over HTTP | **cleared** | Tasks 23–26 merged; Fly still needs redeploy |
| Fly serves the pre-merge build | **yes** | Redeploy from `main`; the Vercel path is merged but has never been exercised |
| VEYZL audit produced no usable report | **yes** | Two runs, both all-error or wrong response shape. The guard and the response shape are fixed (D-023); a clean re-run is still owed. Do not claim the side track until one exists |
| A failed live search silently shows the demo catalog | **changed 22:49** | The orchestrator now falls back to `load_catalog()` on a search error and emits `SEARCH_FAILED`. Good for the demo, but do not describe a fallback render as live search |
| ~~`main` protected by a required check nothing reports~~ | **was yes — resolved 20:22** | The `VEYZL Audit` requirement was dropped from the repo ruleset, PR #20 was rebase-merged, and the branch deleted. **Do not re-add the check until the VEYZL GitHub App is installed** — a local run posts nothing, and re-adding it early blocks every merge again. |
| SerpAPI key unavailable | yes | Catalog-only in the deploy. D-021 adds a live path that is **untested against a real key** — run the spike before claiming live search |
| Contracts still open | yes | `Question` shape is the only unresolved item |
| An empty budget filter falls back to the full catalog | yes | D-022: an over-budget listing can be recommended and paid. Say "closest match" on stage; do not call the budget a hard cap |
| The demo budget answer changes the card count | **yes** | Measured: Under $150 → 1, $150–$300 → 3, $300–$600 → 9. The script uses $300–$600. Under `OFFLINE=1` the filter is skipped entirely |
| Receipt score coverage silently dropped | was yes | C's wrap fix replaced the score assertion; restored alongside it (`f0014c0`) |
| Browser never exercised the live flow | **yes** | Wiring is merged; C must click through it once |
| Devpost overstates the role of the model | **was yes** | Corrected after A's Gemini merge: the model writes copy, never a verdict; the generative-AI answer is **Yes** |
| Public health reads `degraded` with Mongo off | **yes, by design** | With `MONGODB_URI` unset the API is fully functional but answers `{"status":"degraded","db":"unavailable"}` — the contract in `docs/contracts.md`. Fly has no Mongo, so the public URL will always say this. Read it as "optional store off", not "broken"; say so before a judge asks. |
| `GEMINI_API_KEY` unset on Fly | likely | Templates are the fallback, so the demo still runs; set the key only if the template copy reads worse on stage |
| Local venv lacks `motor` | **yes** | `pip install motor`; one repository test otherwise fails to import |

## Cut list in effect

Live page fetching → Reddit → SerpAPI → Mongo → page flags. See `docs/checklist.md` §8.
