---
title: What is actually left
type: checklist
updated: 2026-10-18
owner: B
---

# What is actually left

One page. Everything else in [`docs/checklist.md`](checklist.md) is history or verification.

**The code is done.** 204 backend tests, 39 frontend, `npm run build` clean, the offline replay exits 0, and checkout → confirm → receipt is merged and verified over real HTTP. A's VEYZL finding is already fixed with tests. Nothing below is engineering.

## The list

| # | What | Who | Time | Unlocks |
|---|---|---|---|---|
| 1 | Deploy from the repo root — `fly deploy` **or** the Vercel services path — then `backend/scripts/smoke_http.py` against the public URL | A | 15 min | The Devpost live link — nothing else |
| 2 | Click the flow at **$300–$600**, take three screenshots and one recording | C | 30 min | The gallery images and the video |
| 3 | Record the 3-minute demo video | team | 60 min | **Required by Devpost** |
| 4 | Fill [`docs/devpost-form.md`](devpost-form.md), attach artifacts, submit | B | 60 min | G5 and G7 |
| 5 | *Optional:* re-run VEYZL against the fixed build and capture a clean report | A | 20 min | The VEYZL side track |
| 6 | *Optional:* MongoDB M0 check, **or drop the claim** | B | 30 min / 0 min | The MLH MongoDB checkbox only |

That is the whole remaining project. Two of the six are optional.

## Already delivered

- **A's VEYZL finding is fixed**, not pending: `llm_guard.py` refuses and redacts before Gemini, and the checkout probe path answers in the shape the auditor expects ([D-023](decisions.md), [evidence](veylz-audit.md)). The only thing left is a re-run that produces a report without errors.
- **The Vercel path is merged** alongside Fly. An untested deploy path is still an untested deploy path — smoke it before claiming it.
- Local dev needs no `.env`: `apiBase()` falls back to `localhost:8000` in a dev build and stays same-origin in production.

## The critical path

Item 2 does **not** depend on item 1. Screenshots and the video can be taken against `localhost` with `uvicorn` and `npm run dev`. Nothing in the submission depends on the deploy except the live link itself — so C and the video are not blocked while A is unresponsive.

## If A's deploy does not happen

The submission still goes in.

- **The video is required and does not need a deploy.** Record against `localhost`.
- **The live URL is optional.** "Try it out" links carry no asterisk in the Devpost form. Leave it blank, or point at the repo.
- **Do not fabricate a URL.** A dead link is worse than no link.
- **VEYZL is dropped.** The fix exists, but with no clean report and no check run the side track is not claimable — uncheck it and do not mention it.
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
