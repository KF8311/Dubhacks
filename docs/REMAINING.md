---
title: What is actually left
type: checklist
updated: 2026-10-17
owner: B
---

# What is actually left

One page. Everything else in [`docs/checklist.md`](checklist.md) is history or verification.

**The code is done and the deploy is up at https://sykes.select.** 204 backend tests, 39 frontend, `npm run build` clean, the offline replay exits 0, and checkout → confirm → receipt is verified both locally and on the public URL. A's VEYZL finding is already fixed with tests. Nothing below is engineering.

## The list

| # | What | Who | Time | Unlocks |
|---|---|---|---|---|
| 1 | Click the flow at **$300–$600** against `localhost`, take three screenshots and one recording | C | 30 min | The gallery images and the video |
| 2 | Record the 3-minute demo video | team | 60 min | **Required by Devpost** |
| 3 | Fill [`docs/devpost-form.md`](devpost-form.md), attach artifacts, submit | B | 60 min | G5 and G7 |
| 4 | *Optional:* decide whether `sykes.select` should show live search or the curated catalog (`OFFLINE=1`), then warm it before judging | A | 5 min | A hosted link that matches the demo |
| 5 | *Optional:* read the failing `VEYZL Audit` report on PR #26 in the portal, reproduce what it names, and re-run until the check passes | A | 20–60 min | The VEYZL side track |
| 6 | *Optional:* MongoDB M0 check, **or drop the claim** | B | 30 min / 0 min | The MLH MongoDB checkbox only |

That is the whole remaining project. Three of the six are optional.

## Already delivered

- **The deploy is live at https://sykes.select.** Health 200, and checkout → confirm → public receipt was verified over the internet on 2026-10-17 23:00 PT (`rcp_Z-Oqv9M-trZ2yOok`). It is on Vercel, not Fly.
- **A's VEYZL finding is fixed**, not pending: `llm_guard.py` refuses and redacts before Gemini, and the checkout probe path answers in the shape the auditor expects ([D-023](decisions.md), [evidence](veylz-audit.md)).
- **The VEYZL GitHub App is installed** and posts `VEYZL Audit` on every PR. On PR #26 the check **failed** and the report has not been read yet — so the side track is not claimable, but the tool is finally in the loop.
- Local dev needs no `.env`: `apiBase()` falls back to `localhost:8000` in a dev build and stays same-origin in production.

## The public URL has no villain — read this before recording

`sykes.select` has a working `SERPAPI_KEY`, so it runs **live search**. Measured at 23:00 PT: 9 real
products (Sony, Sennheiser, JBL…), all 9 trusted, recommendation "Cheapest of 9 trusted options". The
catalog's danger merchant, `lst_tgt_bsp` at $179.99, and the $374.49 median **do not appear there.**

- **Take the screenshots and the video against `localhost`.** With no `SERPAPI_KEY` locally the app uses
  the curated catalog and every number in the script holds.
- If the hosted link should match the demo, set **`OFFLINE=1`** in the Vercel project. That pins the
  curated catalog (villain included) and skips the budget filter — invisible at the scripted $300–$600
  answer. Unset it to go back to live search.
- Do not unset `SERPAPI_KEY` as the fix: search then waits out the timeout and falls back with a
  dismissible "Search failed" banner.

## The critical path

The screenshots and the video do **not** depend on the hosted link — take them against `localhost` with
`uvicorn` and `npm run dev`, where the curated catalog is guaranteed. The deploy is already up, but it is
not on the path to submission.

## If the hosted link misbehaves

- **A cold start can 500 once.** Warm it before judging: hit `/api/health`, then create one session.
- **Do not fabricate a URL.** A dead link is worse than no link. The URL in the form is
  `https://sykes.select`.
- **VEYZL is dropped unless the re-run passes.** The fix exists, but with no clean report the side track
  is not claimable — uncheck it and do not mention it.
- **Nothing else changes.** Repo link, story, images, and video are enough.

## If C's click-through does not happen

Use the `?mock=1` path for the screenshots and the recording. It renders the same screens without a backend. Say in the video and the write-up that it is the mock fallback — never present it as the live flow.

## MongoDB

Not required. `MONGODB_URI` is unset by default and the in-memory adapter runs the entire demo. Mongo persists only the payment path; sessions, listings, and investigations stay in-process either way (D-006, D-016). It changes nothing a judge sees. Drop the MLH checkbox unless someone is genuinely idle.

## Do not start

- New features. Nothing the submission needs is missing.
- MongoDB, unless it is free time.
- Anything that needs a required status check on `main`. Keep `VEYZL Audit` off the ruleset until the app actually reports.

## How changes land

Direct pushes to `main` are refused. Use branch → PR → rebase-merge.
