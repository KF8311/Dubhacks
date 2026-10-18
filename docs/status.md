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
| Gate | **Block 5 is closed and G5 is close-out.** The code is done and the public deploy is live. What remains is C's browser screenshots, the video, the Devpost form, and a clean VEYZL re-run. |
| Health | **https://sykes.select/api/health** → 200, `{"status":"degraded","db":"unavailable","version":"0.9.0"}` (`degraded` is correct: Mongo is optional and unset). Served by Vercel. The Fly URL still serves the pre-merge build. |
| Deploy | **Live on Vercel at `https://sykes.select`** via [`vercel.json`](../vercel.json) — backend `app.main:app` with `bundle_data.py`, frontend on the same origin, `/api/*` rewritten to the service. **The Git-connected deploy now ships its data** ([PR #30](https://github.com/KF8311/Dubhacks/pull/30), verified 00:15 PT); the 23:00 proof below predates the Git build and is kept as history. Fly (`dubhacks` / `sniff-visa-dubhacks` / `sjc`, D-010, D-012, D-013) remains a second path; Render is backup. |
| Contracts | `docs/contracts.md` carries domain types, `Recommendation`, SSE ordering, and checkout/confirm JSON. `listing.scored` now also carries `allowlisted` so the UI does not render a curated merchant as "0". |
| SerpAPI | **Changed after the Git rebuild.** At 23:00 the Vercel deploy returned `"source": "serpapi"` with real Google Shopping results; at 00:15 on the Git-built deploy the same probe returned `"source": "catalog"` (curated listings, villain included). Most likely `OFFLINE=1` was set in the project — B cannot read Vercel env vars. **Check before saying "live search" on stage.** Locally with no key the app is catalog-only. |
| Tests | Backend **204 passed** (35 files). Frontend **39 passed** (15 files), `npm run build` clean. |
| Offline replay | `backend/.venv/Scripts/python.exe scripts/replay_offline.py` → same numbers as the live run, exit 0. Exits 1 if the demo drifts. |
| Routes | Sessions create/answer/snapshot/events/**explain**, orchestrator fan-out, payability guard and mandates, **checkout/confirm (Task 23)**, **receipts + public share (Task 24)**, **repository swap (Task 27)**. The frontend calls all of them live; `?mock=1` is the fallback. |
| Owners | A: platform + orchestrator + payments + **VEYZL (Task 29, D-020)**. B: trust + data + **Mongo review (Task 27, D-016)** + Devpost. C: frontend. |
| Blockers | **A's deploy is done** (`sykes.select`). Remaining: C's browser click-through and screenshots, the team video, B filling `docs/devpost-form.md`, and a clean VEYZL re-run. **One decision is now on the team:** the public URL serves live search, so it has no villain — see the risk row below. None of these blocks the others. |
| Branches | **`main` carries everything and is pushed** ([PR #20](https://github.com/KF8311/Dubhacks/pull/20)–[PR #25](https://github.com/KF8311/Dubhacks/pull/25) rebase-merged or open; every working branch deleted after its diff against `main` came back empty). Run `git log --oneline origin/main` for the current tip — recording the hash here just goes stale on the next docs commit. Local and remote `main` are the same commit. Every other remote head is contained in `main`. |
| Model | **Gemini 3.5 Flash Lite** writes questions, narration, and check explanations (D-017–D-019), 2.5 s timeout, template fallback. It never scores, selects checks, or touches payability. |

Last updated: 2026-10-18 00:20 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health deployed | Sat 13:15 | 🟡 health live, `Question` shape still open | URL above + `docs/contracts.md` |
| G1 Listings stream to browser | Sat 15:30 | 🟢 server proof + live `EventSource` client wired (browser screenshot still owed) | 9 `listing.found`; `frontend/src/lib/sse.ts` + `useSessionStream` |
| G2 Full investigation, 5 checks, score | Sat 18:00 | 🟢 server proof; cards render `check.completed` | 45 `check.completed`, villain `0 / danger`, 8 trusted |
| G3 Recommendation + best pick | Sat 19:30 | 🟢 server proof; `BestPick` + best-pick ring in the grid | pick `lst_tgt_bsp` $179.99, median $374.49, savings $194.50 |
| G4 Checkout → passkey → receipt | Sat 21:00 | 🟢 **server proof on the public URL** (browser click-through is C's, under G5) | `https://sykes.select`: checkout `201 awaiting_passkey` → confirm `200` → public receipt `200`; refusal shows `MERCHANT_NOT_TRUSTED` |
| G5 Devpost draft submitted | Sat 22:30 | 🟡 **close-out** — text done and the live URL exists; screenshots, video, and a clean VEYZL report pending. The VEYZL finding is already reproduced and fixed | `docs/devpost-form.md` + Devpost confirmation |
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

## Proof of the public deploy (2026-10-17 23:00 PT)

`https://sykes.select`, no headers, over the real internet. Hosted by Vercel:

```
GET  /api/health                     → 200  status "degraded", db "unavailable", version 0.9.0
POST /api/sessions                   → 201
POST /api/sessions/{id}/answers      → 202  stage "ready"
GET  /api/sessions/{id}              → 200  9 listings
POST /api/checkout                   → 201  stage "awaiting_passkey"
POST /api/checkout/{id}/confirm      → 200  receipt_id rcp_Z-Oqv9M-trZ2yOok, receipt_url /r/shr_f4r5vezengss
GET  /r/{share_id}                   → 200  amount 3999, last4 4242, HMAC signature present
```

**The listings come from live SerpAPI, not the catalog.** Measured on a fresh session: 9 real products
(Sony WH-1000XM6, Sennheiser, JBL, …) with hashed ids and `"source": "serpapi"`; recommendation
`Cheapest of 9 trusted options`; **all 9 trusted, no villain.** The catalog's `lst_tgt_bsp` /
`lst_vln_xm5` numbers do not appear on the public URL. One answers call returned a transient `500` on a
cold start and succeeded immediately on retry. **This snapshot describes the CLI-built deployment; it was
later rebuilt from Git and then repaired — see the two sections below for what is true now.**

## Proof after the repair (2026-10-18 00:15 PT)

`https://sykes.select` on the Git-built deployment from `ed4e95b` (Vercel status `success`):

```
GET  /api/health                     → 200
POST /api/sessions                   → 201
POST /api/sessions/{id}/answers      → 202 in 0.47 s, stage "ready", 9 listings
POST /api/checkout  lst_vln_xm5      → 409  MERCHANT_NOT_TRUSTED, verdict "danger"
POST /api/checkout  lst_tgt_bsp      → 201  awaiting_passkey, amount 17999, mandate single-use
POST /api/checkout/{id}/confirm      → 200  "captured", txn approved, mode "sandbox", token last4 4242
GET  /r/{share_id}                   → 200
GET  /api/public/receipts/{share_id} → 200  amount 17999, HMAC signature present, sandbox_label present
```

**The hosted listings are now the curated catalog** (`"source": "catalog"`, `lst_tgt_bsp` recommended at
$179.99, median $374.49, the villain refused). That is the demo's numbers, not live SerpAPI. Something in
the project's environment made the catalog path active — most likely `OFFLINE=1`, which was the
recommended action in the previous revision of this file. Only the Vercel owner can confirm which; do not
claim a live search on stage until the environment is checked.

## The Git deploy shipped no data (2026-10-17 23:40 PT)

The repo was made public and connected to Vercel so anyone on the team can deploy by merging. The first
production build from that connection (`a81bcc4`) succeeded in 15 s, then failed at runtime:

```
POST /api/sessions                    → 201
POST /api/sessions/{id}/answers       → 500  (0.3 s, 3/3 attempts; stage stays "searching")
GET  /api/sessions/{id}               → stage "searching", 0 listings
POST /api/checkout  (lst_tgt_bsp)     → 500
POST /api/checkout  (unknown id)      → 500  (expected 404 LISTING_NOT_FOUND)
GET  /api/health                      → 200
```

**Cause was two bugs, not one.** (a) `.gitignore` excluded `backend/data/`, which `bundle_data.py` copies
from repo `data/` during the build; the old CLI deploy uploaded the working directory where that copy
already existed, a Git build packages tracked files only. (b) Even with the bundle committed, the resolver
in `app/core/paths.py` checked `parents[3]/data` and `parents[2]/data`, which inside a function packaged as
`<root>/app/core` are the parent of the function root and `/data` — never `<root>/data`. Fixing only (a)
would have kept the 500.

**Fix, merged as [PR #30](https://github.com/KF8311/Dubhacks/pull/30) (`ed4e95b`).** `backend/data/` is
committed (`bundle_data.py` still refreshes it every build), and `parents[1]/data` is a resolver
candidate. Two path tests were written first and watched fail. Backend suite **206 passed**.

**Reproduced the failure before the fix and the recovery after it** by copying `backend/` to a temp root —
the exact function layout — and running with `VERCEL=1` and no `SERPAPI_KEY`: answers `500` → `202`, stage
`ready`, 9 listings, unknown listing id `500` → `404`. Production was then re-tested over the internet;
see "Proof after the repair" above.

**Lesson for the next deploy:** a Vercel CLI deploy and a Git deploy are not the same artifact. Anything
the build *generates* has to be tracked, or the code has to find it after packaging.


## In progress

| Owner | Task | Started | Expected | Notes |
|---|---|---|---|---|
| A | Public deploy; smoke the public URL; **VEYZL audit + fix (D-020, D-023)** | 18:25 | 22:30 | ✅ **Deploy is live at `https://sykes.select`** and the full checkout → confirm → receipt path was verified there. ✅ VEYZL audit ran (three reports); finding 1 — no guard on the generative path — is fixed with five tests, merged 22:49 PT. ✅ The VEYZL GitHub App is installed and posts `VEYZL Audit` on PRs. ⬜ That check **fails** on PR #26 and the report has not been read in the portal. ⬜ **Decide the demo source** (next actions #1) |
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
- [x] **The public deploy is live at `https://sykes.select`** (Vercel services). Verified over the internet: health 200, session 201, answers `ready`, checkout `201`, confirm `200`, public receipt 200 with a valid signature. It runs **live SerpAPI**, so all 9 listings are real products and all 9 are trusted — the catalog villain is not on the public URL

## Next three actions

1. **A, two minutes:** decide what the public URL should show. It currently runs live search, so all 9 listings are trusted and **the demo has no villain**. Setting `OFFLINE=1` in the Vercel project forces the curated catalog (villain, $179.99 pick, $374.49 median) — and `OFFLINE=1` also skips the budget filter, which is invisible at the scripted **$300–$600** answer. Leave it as-is if the "live search" story matters more than the villain on the hosted link. Either way, **record the screenshots and video locally**, where the curated numbers are guaranteed.
2. **C, 30 minutes:** `npm run dev` against `uvicorn` on :8000, answer **$300–$600**, click through villain → best pick → Pay → passkey → receipt, and take three screenshots plus one recording.
3. **A, then B:** read the failing `VEYZL Audit` report on PR #26 in the portal, reproduce what it names, and re-run. B fills `docs/devpost-form.md` with `https://sykes.select`, C's images, and the video as they land.

## Demo trap to avoid

The demo run must answer **$300–$600**. Measured on the merged build: `Under $150` → 1 card (the villain, ending in `no_trusted_option`), `$150–$300` → 3 cards, `$300–$600` → all 9. The catalog runs to $549.99, so the lower answers are thinner, not wrong. Under `OFFLINE=1` the budget filter is skipped and all 9 cards appear regardless — do not describe plane mode as budget-filtered. See `docs/checklist.md` §10.

## Risks that are currently live

| Risk | Trigger seen? | Action taken |
|---|---|---|
| **The Git deploy shipped no data** | **yes — fixed 00:15 PT** | Build `a81bcc4` 500'd on answers and checkout: `backend/data/` was gitignored, and `paths.py` never looked at the function root's `data/`. [PR #30](https://github.com/KF8311/Dubhacks/pull/30) fixed both; production re-verified 00:15. Do not repeat the trick: anything the build generates must be tracked or discoverable after packaging |
| Checkout not reachable over HTTP | **cleared** | Tasks 23–26 merged; the public URL completes checkout → confirm → receipt |
| **The public URL has no villain** | **cleared 00:15 PT** | At 23:00 `sykes.select` ran live SerpAPI (9 real listings, all trusted, no villain). At 00:15 the Git-built deploy returned the curated catalog: `lst_tgt_bsp` recommended at $179.99, median $374.49, and `lst_vln_xm5` refused `409 MERCHANT_NOT_TRUSTED`. The hosted link now matches the scripted demo. Confirm the `OFFLINE` setting before describing it on stage |
| Hosted cold start can 500 once | **yes, once** | The first answers call after idle returned 500, then succeeded on retry. Warm the deploy (health + one session) before judging, and rehearse the local path as the primary |
| Fly serves the pre-merge build | **yes** | The Fly app is still stale; **`sykes.select` is the live URL now**. Redeploy Fly only if it is the URL you are putting in the form |
| VEYZL audit produced no usable report | **yes** | Two hosted runs were all-error or wrong response shape; the guard and shape are fixed (D-023). The GitHub App is now installed and posts `VEYZL Audit` on PRs, but its report on PR #26 **failed** and has not been read in the portal. Do not claim the side track, and do not re-add the check as required, until it passes |
| A failed live search silently shows the demo catalog | **changed 22:49** | The orchestrator falls back to `load_catalog()` on a search error and emits `SEARCH_FAILED`, which surfaces as a dismissible error banner. Good for the demo, but do not describe a fallback render as live search |
| ~~`main` protected by a required check nothing reports~~ | **was yes — resolved 20:22** | The `VEYZL Audit` requirement was dropped from the repo ruleset, PR #20 was rebase-merged, and the branch deleted. **Do not re-add the check until the VEYZL GitHub App is installed** — a local run posts nothing, and re-adding it early blocks every merge again. |
| SerpAPI key unavailable | **no longer true on Vercel** | The deploy has a working key and returns `"source": "serpapi"` listings. Locally with no key the app is catalog-only. On stage, say which one you are showing |
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
