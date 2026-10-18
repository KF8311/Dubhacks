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
| Gate | **G4 is merged end to end** — checkout → confirm → receipt on the server, and C's sheet and receipt page are wired to the live contract. One browser click-through is all that is left. |
| Health | https://sniff-visa-dubhacks.fly.dev/api/health (serves the pre-merge build; redeploy in Block 5) |
| Deploy | **Fly.io** org `dubhacks`, app `sniff-visa-dubhacks`, region `sjc` (D-010, D-012, D-013). Render is backup. |
| Contracts | `docs/contracts.md` carries domain types, `Recommendation`, SSE ordering, and checkout/confirm JSON. `listing.scored` now also carries `allowlisted` so the UI does not render a curated merchant as "0". |
| SerpAPI | No `SERPAPI_KEY`. Catalog-only until a live query confirms merchant domains (D-011). |
| Tests | Backend **153 passed**. Frontend **9 files / 22 tests passed**, `npm run build` clean. |
| Offline replay | `backend/.venv/Scripts/python.exe scripts/replay_offline.py` → same numbers as the live run, exit 0. Exits 1 if the demo drifts. |
| Routes | Sessions create/answer/snapshot/events, orchestrator fan-out, payability guard and mandates, **checkout/confirm (Task 23)**, **receipts + public share (Task 24)**. The frontend calls all of them live; `?mock=1` is the fallback. |
| Owners | A: platform + orchestrator + payments. B: trust + data. C: frontend. |
| Blockers | Fly serves the pre-merge build; the browser flow has not been clicked through since C's UI merged |
| Branches | **`main` carries everything through Block 4 for A, B, and C** (PRs #1–#14). No branch is ahead of `main`. Branch from `main` for Block 5. |

Last updated: 2026-10-17 18:25 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health deployed | Sat 13:15 | 🟡 health live, `Question` shape still open | URL above + `docs/contracts.md` |
| G1 Listings stream to browser | Sat 15:30 | 🟢 server proof + live `EventSource` client wired (browser screenshot still owed) | 9 `listing.found`; `frontend/src/lib/sse.ts` + `useSessionStream` |
| G2 Full investigation, 5 checks, score | Sat 18:00 | 🟢 server proof; cards render `check.completed` | 45 `check.completed`, villain `0 / danger`, 8 trusted |
| G3 Recommendation + best pick | Sat 19:30 | 🟢 server proof; `BestPick` + best-pick ring in the grid | pick `lst_tgt_bsp` $179.99, median $374.49, savings $194.50 |
| G4 Checkout → passkey → receipt | Sat 21:00 | 🟡 **merged end to end**; browser click-through pending | 153 backend / 22 frontend tests; live HTTP checkout → confirm → public receipt; refusal shows `MERCHANT_NOT_TRUSTED` |
| G5 Devpost draft submitted | Sat 22:30 | ⬜ | Devpost confirmation |
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
| A | Fly redeploy from repo root; free-text budget parsing | 18:25 | 20:00 | Turns commits into a public URL |
| C | Browser click-through + screenshot of the merged checkout sheet and receipt page | 18:25 | 20:00 | Tasks 25–26 merged in PR #14; `?mock=1` remains the fallback |
| B | VEYZL audit, README, Devpost technical section | 18:40 | 21:00 | Block 4 done; Task 29 next |

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

## Next three actions

1. C opens `npm run dev` against `uvicorn` on :8000, jumps on `?mock=1` to prove the fallback, then clicks the live flow once — villain red, best pick `lst_tgt_bsp`, Pay → passkey → receipt — and **screenshots it**.
2. A redeploys Fly from the **repo root** so the live URL carries checkout and receipts, then runs `backend/scripts/smoke_http.py` against it.
3. B starts Task 29 (VEYZL audit + README) and the Devpost technical section.

## Demo trap to avoid

Picking **"Under $150"** filters the catalog to the villain alone and ends in `no_trusted_option`. That is a legitimate refusal path worth showing *after* the happy path, but the demo run should answer with **$150–$300**. See `docs/checklist.md` §9.

## Risks that are currently live

| Risk | Trigger seen? | Action taken |
|---|---|---|
| Checkout not reachable over HTTP | **cleared** | Tasks 23–26 merged; Fly still needs redeploy |
| Fly serves the pre-merge build | **yes** | Redeploy from `main` in Block 5 |
| SerpAPI key unavailable | yes | Catalog-only per D-011 |
| Contracts still open | yes | `Question` shape is the only unresolved item |
| Browser never exercised the live flow | **yes** | Wiring is merged; C must click through it once |

## Cut list in effect

Live page fetching → Reddit → SerpAPI → Mongo → page flags. See `docs/checklist.md` §8.
