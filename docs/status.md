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
| Code | **`96cf47f`** plus the merged `c/web` work, D-025, the embedded data bundle, and D-034–D-040 — live SerpAPI search with an honest failure state (no catalog substitution in live mode), non-audio queries no longer answered with the headphone catalog, product-specific clarifying questions, five checks, deterministic scoring, SSE, recommendation, checkout → passkey → receipt, Gemini copy with template fallback, **real merchant product links**, **whole-card flips to site stats**, **one marigold edge for the pick alone**, **verdict-tinted compact cards that answer hover without moving**, and a **pay-on-your-phone text the bridge sends automatically**. |
| Branch | **`main` is restored** — [PR #34](https://github.com/KF8311/Dubhacks/pull/34) merged as `2d53ca1`; [#37](https://github.com/KF8311/Dubhacks/pull/37) (timeout) and [#39](https://github.com/KF8311/Dubhacks/pull/39) (D-025) are merged, and the `c/web` + embedded-data updates are integrated. The 20 removed commits stay reachable on `backup/main-post-96cf47f` and the `origin/restore/*` branches. |
| Parked work | Every removed commit with links and a revisit table: [`ideas-after-96cf47f.md`](ideas-after-96cf47f.md). Nothing was deleted. |
| Health | https://sniff-visa-dubhacks.fly.dev/api/health — **serves an older build**. The image now builds and runs locally (see Deploy), but the Fly CLI and credentials are not on this machine. Do not submit `sykes.select`; it runs the removed code. |
| Deploy | **Docker proven:** `docker build -f backend/Dockerfile -t sniff-visa .` builds and the container serves health, a live search (`source: "serpapi"`), and the full checkout → confirm → public receipt path. **Fly is blocked on `flyctl` + `fly auth login`** on this machine. The embedded data bundle means a packaged function no longer needs an on-disk `data/`. |
| Contracts | `Question` is now a backend model (`Question`, `QuestionOption` in `models.py`, `allow_free_text` included); [`contracts.md`](contracts.md#L81) matches the code. Everything is frozen. |
| Data | **Atlas is connected and load-bearing.** Health returns `db: ok`; checkout → confirm → public receipt works against Atlas (Mongo 8.0.34, `sniff` database, indexes created on boot), and a **pending checkout still confirms after a backend restart** — the listing and investigation are read back from Atlas and the token id is persisted on the checkout (D-027). Two adapter bugs surfaced first and were fixed under D-026. Sessions remain registry-only. |
| Search | **Real merchant links** (D-034): each listing's immersive lookup is fetched concurrently inside a 3.5 s cap, and a store's URL replaces the Google link only when its host equals the listing's merchant host exactly. Measured `TUL pens at Office Depot` → ready in 3.2–5.1 s, **8 of 9 listings on their merchant's own product page** (best pick: Office Depot TUL BP Series, $12.49, `https://www.officedepot.com/a/products/1310454/…`). Unmatched listings still link to `google.com/search?udm=28&q=…` (the legacy `ibp=oshop` page renders empty). Live SerpAPI path **localized to Seattle, Washington, United States** (`SERPAPI_LOCATION`, `gl=us`, `hl=en`; the market is a SerpAPI parameter, not part of the query), with a **10 s client timeout inside an 11 s per-attempt budget**, one retry. **Live mode never substitutes the catalog** (D-025): a slow query shows "Searching live listings…" for up to ~22 s, then the `failed` stage with `SEARCH_UNAVAILABLE` and a Start over button. Offline mode is unchanged. |
| Cards | The whole ticket flips on hover — merchant link included — to show the merchant, the trust badge, `passed · warning · failed` counts, and the top reason, or "Checks are still running." until the investigation lands (D-035, D-039). Only the best pick in the list wears the marigold offset; a selected row gets a neutral ring (D-039). Rows are compact (`size-10` thumbnail, `text-sm` title, `text-base` price, `p-2.5`, `rounded-3xl`). A 3px verdict-colored left edge and a faint verdict tint give every card its color; hover swaps to the marigold wash and darkens the border with **no movement** (D-040). The flip is off on touch and turns instantly under reduced motion; both faces stay readable, and the link is rendered on the back so the hover flip never hides it. |
| Phone pay | The review step offers **Pay** and **Send to phone**; either creates the checkout, and the mandate step leads with a copy/share link to `<origin>/pay/<checkout_id>` above the mandate card (D-036, D-039). **Send to phone texts the link itself** (D-040): the browser posts to the local Spectrum bridge at `http://<page host>:8787/send`, which messages the conversation the shopper already texted (or `MY_PHONE`). The sheet shows "Sent to your phone." and hides the copy link; if the bridge fails it shows the bridge's reason and the copyable link as a fallback. **The bridge currently reports `target: none` — no phone has texted it since the restart**, so a send returns 502 until the shopper texts the bridge once or sets `MY_PHONE` in the gitignored `dub-spectrum/.env`. `GET /api/checkout/{id}` returns a read-only summary, and `PayPage` approves with the sandbox passkey on the phone, then lands on `/r/<share_id>`. Verified over HTTP: checkout `201` → `GET /api/checkout/{id}` `200` with `stage: awaiting_passkey` and `trust_snapshot: {score: 0, verdict: "trusted", allowlisted: true}`. On a LAN, Vite needs `--host` and Uvicorn `0.0.0.0`; `apiBase()` follows the page hostname. |
| Tests | Backend **263 passed**. Frontend **77 passed** (18 files), `npm run build` clean. Photon bridge: **15** (`bun test` in `dub-spectrum/`), `bunx tsc --noEmit` clean. |
| Text agent | `dub-spectrum/` (in-repo). A text is a search: polite framing is stripped, the session runs with no clarifying answers, and the reply is the top trusted pick, its price and merchant, one reason, and the `product_url`, followed by a refinement menu (1 cheaper, 2 better quality, 3 something else, `new: <product>`). The same process serves `POST /send` on `127.0.0.1:8787` for the website's automatic pay-link text (D-040); `/health` reports whether a target phone is known. Live text still unproven, and no inbound text has been recorded since the restart. |
| Offline replay | `backend/.venv/Scripts/python.exe scripts/replay_offline.py` → exit 0; 9 listings, 8 trusted, 1 danger, pick `lst_tgt_bsp`, median $374.49, savings $194.50. |
| Run | `.\scripts\dev.cmd` (live) · `.\scripts\dev.cmd offline` · `.\scripts\dev.cmd mock` · `.\scripts\dev.cmd check`. `/api/health` now reports `offline`, and `dev.cmd` refuses to reuse an offline backend for a live run (that trap served the catalog demo with no warning). Details: [`RUN.md`](RUN.md). |
| Owners | A: search quality + contracts + deploy. B: docs truth + Devpost. C: browser proof + copy fixes. |
| Blockers | Fly deploy needs the CLI and login; C has not clicked the kept build through in a browser; B corrects the remaining claims and fills the Devpost. |
| Model | **Gemini 3.5 Flash Lite** writes questions, narration, and check explanations (D-017–D-019), 2.5 s timeout, template fallback. It never scores, selects checks, or touches payability. |

Last updated: 2026-10-18 07:25 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health | Sun 03:00 | 🟢 | `docs/contracts.md` |
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

Suites: **243 backend**, **55 frontend**, build clean. What is not yet proven on this exact commit is the **browser click-through**.

Atlas, 2026-10-18 04:25 PT:

```
health          {"status": "ok", "db": "ok"}
create          201  ses_-9jNqX5oj1Pfc40B
answers         202
checkout        201  chk_KrBFjhzVK6DOZLiC
confirm         200  rcp_g09DRcJ5ykNO_KJO  /r/shr_rmnvwebawdch
public receipt  200  4242  Sandbox — simulated Visa Intelligent Commerce flow.
confirm again   200  same receipt
after restart   200  the public receipt still resolves (Mongo, not memory)
collections     mandates 3 · checkouts 2 · transactions 1 · receipts 1 · audit_events 3
```

Atlas payment-path durability, 2026-10-18 05:20 PT — the checkout itself survives the restart:

```
create          201  ses_SsOQrDPm5geV0z9O  lst_tgt_bsp
checkout        201  chk_dzr98nwVykDASG4L   awaiting_passkey
--- backend killed and restarted ---
confirm         200  rcp_ZSgCEO8uD7hwhCjs  /r/shr_y4zjob7ty3nb  17999¢  token 4242
                     (listing and investigation read back from Atlas; the registry was empty)
stale checkout  409  INVESTIGATION_STALE, not a 500
```

The confirm above needed three things the process no longer had: the listing, the investigation, and the payment token. Listings and investigations are now written through by the orchestrator and read back by `_get_listing` / `_get_investigation`; the token id is persisted on the checkout and re-registered in the simulator (D-027).

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
| **Search quota exhausted** | **yes, 2026-10-18** | The exhausted key was replaced at 06:55 PT and the account reports **250 searches left**. A 429 still reports `SEARCH_QUOTA_EXHAUSTED` in ~0.2 s instead of the old misleading timeout (D-037); the UI says "Live search quota is used up. Add a fresh search key, then start over." Each new query costs 1 search plus up to 9 immersive lookups, a repeat in the same process costs 1 (D-037), and **Skip questions** (D-038) reaches cached queries. |
| Thin live search | **yes** | Optional: adopt the `<3` guard (idea B) if a query returns one or two cards. |
| Slow SerpAPI query swaps in unrelated products | **fixed 2026-10-18 (D-025)** | Client timeout is 10 s inside an 11 s budget; live mode fails honestly instead of showing the catalog. |
| Slow live query looks stuck | **yes, by design** | Up to ~22 s with skeleton cards, then a retry state. Say "live search is slow" on stage, not "it is broken". |
| Session stuck on "searching" with cards visible | **fixed 2026-10-18 (D-030)** | A unique `product_url` index made the second Google-hosted listing fail with `E11000`, killing the orchestrator task before `investigating`. Index is now non-unique; store writes are best-effort. Measured ready in 10.8 s. |
| Browser never exercised the kept build | **yes** | C's first task; G1–G4 depend on it. |
| Docs claim stale counts | **fixed** | `README.md`, `devpost.md`, `status.md`, and the checklist now say **231/49**. |
| Docs claim removed features | **yes** | B scrubs VEYZL/Vercel/host-aware references before submit. |
| `Question` shape open | **yes** | A signs off at 03:00. |
| Fly serves an older build | **yes** | Morning deploy from repo root; never submit `sykes.select`. |
| Vercel Git deploy broken here | **yes** | Do not attempt; use Fly. Parked fix is idea A. |
| Budget answer changes card count | **yes** | Demo uses $300–$600. |
| Offline skips the budget filter | **yes** | Say "full catalog", never "budget-filtered". |
| Over-budget pick (D-022) | **yes** | C adds the badge or "closest match" copy. |
| Mongo/MLH claim unsupported | **fixed 2026-10-18** | Atlas is connected and proven; the claim is now supported. Fly still needs `MONGODB_URI` set as a secret or the deployed app reports `db: unavailable`. |
| VEYZL side track ineligible | **yes** | Cut by 03:00 unless a check run is visible on a PR. |
| Public health reads `degraded` | **no longer on this machine** | Locally the API answers `{"status":"ok","db":"ok"}`. The Fly app will answer `degraded` until `MONGODB_URI` is set as a secret there. Say "optional store off", not "broken". |
| `GEMINI_API_KEY` unset on Fly | likely | Templates are the fallback; the demo still runs. |

## Cut list in effect

Live page fetching → Reddit → SerpAPI → Mongo → page flags. See [`checklist.md`](checklist.md).
