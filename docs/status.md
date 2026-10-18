---
title: Status
type: status
updated: 2026-10-18
owner: rotating scribe
---

# Status

This is the only file that claims to be current.

| Field | Value |
|---|---|
| Gate | **Block R — recovery close-out.** The kept build is green; the remaining work is browser proof, the docs scrub, and the Devpost. **Freeze 04:00 PT.** |
| Code | **`96cf47f`** plus the merged `c/web` work, D-025, and the embedded data bundle — live SerpAPI search with an honest failure state (no catalog substitution in live mode), non-audio queries no longer answered with the headphone catalog, product-specific clarifying questions, five checks, deterministic scoring, SSE, recommendation, checkout → passkey → receipt, Gemini copy with template fallback. |
| Branch | **`main` is restored** — [PR #34](https://github.com/KF8311/Dubhacks/pull/34) merged as `2d53ca1`; [#37](https://github.com/KF8311/Dubhacks/pull/37) (timeout) and [#39](https://github.com/KF8311/Dubhacks/pull/39) (D-025) are merged, and the `c/web` + embedded-data updates are integrated. The 20 removed commits stay reachable on `backup/main-post-96cf47f` and the `origin/restore/*` branches. |
| Parked work | Every removed commit with links and a revisit table: [`ideas-after-96cf47f.md`](ideas-after-96cf47f.md). Nothing was deleted. |
| Health | https://sniff-visa-dubhacks.fly.dev/api/health — **serves an older build**. Deploy in the morning from the repo root. Do not submit `sykes.select`; it runs the removed code. |
| Deploy | **Fly.io** org `dubhacks`, app `sniff-visa-dubhacks`, region `sjc`. Vercel Git deploy is broken at this commit (no `data/` shipped); fix is parked as idea A. |
| Contracts | `Question` shape is the last open G0 item ([`contracts.md`](contracts.md#L81)). Everything else is frozen. |
| Search | Live SerpAPI path with a **10 s client timeout inside an 11 s per-attempt budget**, one retry. **Live mode never substitutes the catalog** (D-025): a slow query shows "Searching live listings…" for up to ~22 s, then the `failed` stage with `SEARCH_UNAVAILABLE` and a Start over button. Verified: `noise cancelling headphones` + `$300-$600` → live listings; a bad key → `SEARCH_UNAVAILABLE`, stage `failed`, zero catalog products. Offline mode is unchanged. |
| Tests | Backend **231 passed**. Frontend **49 passed** (15 files), `npm run build` clean. |
| Offline replay | `backend/.venv/Scripts/python.exe scripts/replay_offline.py` → exit 0; 9 listings, 8 trusted, 1 danger, pick `lst_tgt_bsp`, median $374.49, savings $194.50. |
| Run | `.\scripts\dev.cmd` (live) · `.\scripts\dev.cmd offline` · `.\scripts\dev.cmd mock` · `.\scripts\dev.cmd check`. Details: [`RUN.md`](RUN.md). |
| Owners | A: search quality + contracts + deploy. B: docs truth + Devpost. C: browser proof + copy fixes. |
| Blockers | A fixes thin search and signs off `Question`; C clicks the kept build through; B corrects the stale counts and claims before submit. |
| Model | **Gemini 3.5 Flash Lite** writes questions, narration, and check explanations (D-017–D-019), 2.5 s timeout, template fallback. It never scores, selects checks, or touches payability. |

Last updated: 2026-10-18 03:40 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health | Sun 03:00 | 🟡 `Question` shape open | `docs/contracts.md` |
| G1 Listings stream to browser | Sun 03:00 | 🟡 server path proven; browser proof owed on the kept build | 9 `listing.found`; C's screenshot |
| G2 Investigation + score | Sun 03:00 | 🟡 same — villain must be red on screen | 45 `check.completed`; C's screenshot |
| G3 Recommendation | Sun 03:00 | 🟡 same — pick and savings on screen | pick `lst_tgt_bsp`, median $374.49, savings $194.50 |
| G4 Checkout → receipt | Sun 03:15 | 🟡 server path proven; browser click-through owed | live HTTP checkout → confirm → public receipt |
| G5 Devpost draft | Sun 03:45 | 🟡 text written; URL, screenshots, video pending | `docs/devpost-form.md` |
| G6 Freeze | Sun 04:00 | ⬜ | Shared gates in the checklist |
| G7 Submit | Sun 09:50 | ⬜ | Devpost confirmation |

## Proof of the kept build

Offline replay, 2026-10-18 01:51 PT:

```
query          noise cancelling headphones
stage          ready
listings       9
trusted        8
caution        0
danger         1  (lst_vln_xm5)
best pick      lst_tgt_bsp
median trusted $374.49
savings        $194.50
events         check.completed=45, listing.found=9, listing.scored=9,
               recommendation.ready=1, investigation.complete=1
exit           0
```

Suites: **231 backend**, **49 frontend**, build clean. What is not yet proven on this exact commit is the **browser click-through**.

## In progress — Block R, 02:00–04:00 PT

| Owner | Task | Due | Notes |
|---|---|---|---|
| A | Confirm the live-search timeout fix, `Question` sign-off, HTTP proof, VEYZL decision | 03:45 | Timeout fix is in (`serpapi.py` + test). The `<3` guard (`c55ce29`) is optional |
| B | Revert decision entry, claim scrub, Devpost form, MLH claim | 03:45 | Counts are 231/49; the MLH claim goes unless Atlas is actually exercised |
| C | Browser click-through, 3 screenshots, recording, `skipped` copy, D-022 copy | 03:45 | Answer **$300–$600**; use `.\scripts\dev.cmd` |

## Next three actions

1. Click the kept build through at **$300–$600** and capture the grid, receipt, and refusal.
2. Sign off the `Question` contract and mark VEYZL not selected.
3. Docker sanity, then the morning Fly deploy and `smoke_http.py`.

## Demo trap to avoid

The demo run must answer **$300–$600**. Measured: `Under $150` → 1 card (the villain, ending in `no_trusted_option`), `$150–$300` → 3 cards, `$300–$600` → all 9. Under `OFFLINE=1` the budget filter is skipped and all 9 appear for any answer — do not describe plane mode as budget-filtered.

## Risks that are currently live

| Risk | Trigger seen? | Action |
|---|---|---|
| Thin live search | **yes** | Optional: adopt the `<3` guard (idea B) if a query returns one or two cards. |
| Slow SerpAPI query swaps in unrelated products | **fixed 2026-10-18 (D-025)** | Client timeout is 10 s inside an 11 s budget; live mode fails honestly instead of showing the catalog. |
| Slow live query looks stuck | **yes, by design** | Up to ~22 s with skeleton cards, then a retry state. Say "live search is slow" on stage, not "it is broken". |
| Browser never exercised the kept build | **yes** | C's first task; G1–G4 depend on it. |
| Docs claim stale counts | **fixed** | `README.md`, `devpost.md`, `status.md`, and the checklist now say **231/49**. |
| Docs claim removed features | **yes** | B scrubs VEYZL/Vercel/host-aware references before submit. |
| `Question` shape open | **yes** | A signs off at 03:00. |
| Fly serves an older build | **yes** | Morning deploy from repo root; never submit `sykes.select`. |
| Vercel Git deploy broken here | **yes** | Do not attempt; use Fly. Parked fix is idea A. |
| Budget answer changes card count | **yes** | Demo uses $300–$600. |
| Offline skips the budget filter | **yes** | Say "full catalog", never "budget-filtered". |
| Over-budget pick (D-022) | **yes** | C adds the badge or "closest match" copy. |
| Mongo/MLH claim unsupported | **likely** | Drop it unless Atlas is exercised. |
| VEYZL side track ineligible | **yes** | Cut by 03:00 unless a check run is visible on a PR. |
| Public health reads `degraded` | **yes, by design** | With `MONGODB_URI` unset the API is functional but answers `{"status":"degraded","db":"unavailable"}`. Say "optional store off", not "broken". |
| `GEMINI_API_KEY` unset on Fly | likely | Templates are the fallback; the demo still runs. |

## Cut list in effect

Live page fetching → Reddit → SerpAPI → Mongo → page flags. See [`checklist.md`](checklist.md).
