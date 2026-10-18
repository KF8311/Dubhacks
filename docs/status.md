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
| Gate | **G4 server-side is in place** — checkout → confirm → receipt. Browser checkout sheet is still C. |
| Health | https://sniff-visa-dubhacks.fly.dev/api/health (serves the pre-merge build; redeploy in Block 5) |
| Deploy | **Fly.io** org `dubhacks`, app `sniff-visa-dubhacks`, region `sjc` (D-010, D-012, D-013). Render is backup. |
| Contracts | `docs/contracts.md` carries domain types, `Recommendation`, SSE ordering, and checkout/confirm JSON. `listing.scored` now also carries `allowlisted` so the UI does not render a curated merchant as "0". |
| SerpAPI | No `SERPAPI_KEY`. Catalog-only until a live query confirms merchant domains (D-011). |
| Tests | Backend **129 passed**. Frontend **6 files / 9 tests passed**, `npm run build` clean. |
| Routes | Sessions, SSE, orchestrator, payability, **checkout/confirm**, **receipts + public share**. |
| Owners | A: platform + orchestrator + payments. B: trust + data. C: frontend. |
| Blockers | Fly serves the pre-merge build; C checkout sheet (Task 25) |
| Branches | **`main` is `fa6c2a7` and fully merged** (PRs #1–#11). No follow-on branch is required; branch from `main` for the next block. |

Last updated: 2026-10-17 17:35 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health deployed | Sat 13:15 | 🟡 health live, `Question` shape still open | URL above + `docs/contracts.md` |
| G1 Listings stream to browser | Sat 15:30 | 🟢 server proof + live `EventSource` client wired (browser screenshot still owed) | 9 `listing.found`; `frontend/src/lib/sse.ts` + `useSessionStream` |
| G2 Full investigation, 5 checks, score | Sat 18:00 | 🟢 server proof; cards render `check.completed` | 45 `check.completed`, villain `0 / danger`, 8 trusted |
| G3 Recommendation + best pick | Sat 19:30 | 🟢 server proof; `BestPick` + best-pick ring in the grid | pick `lst_tgt_bsp` $179.99, median $374.49, savings $194.50 |
| G4 Checkout → passkey → receipt | Sat 21:00 | 🟡 server proof; UI still C | Task 23/24 tests green; `POST /api/checkout` + `/confirm` + receipts |
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
| A | Task 23/24 checkout + receipts | 17:26 | 17:40 | Done locally. Redeploy Fly from repo root. |
| C | Browser verification of the live stream, checkout sheet, receipt page | 17:30 | 19:30 | Tasks 25, 26; `?mock=1` remains the fallback |
| B | Integration golden test + `scripts/replay_offline.py` | 17:30 | 18:30 | Task 28 |

## Done since last update

- [x] C: Tasks 17–21 — discovery, results grid, check rows, best pick, purge, empty/error states (PR #10)
- [x] Hookup: `api.ts` and `useSessionStream` now default to the **live** backend; `?mock=1` is the fallback
- [x] Fixed: discovery submitted answers to a hardcoded `ses_mock`, so the live flow 404'd at the second step
- [x] Fixed: allowlisted merchants rendered as `0 · Trusted`; the badge now reads `Verified · Trusted`
- [x] `listing.scored` carries `allowlisted` end to end
- [x] CORS confirmed for `http://localhost:5173` on both JSON and SSE

## Next three actions

1. C wires the checkout sheet to `POST /api/checkout` and `/confirm` (Tasks 25–26).
2. Redeploy Fly from the **repo root** so G4 is on the public URL.
3. B adds the villain integration golden test and `scripts/replay_offline.py`.

## Demo trap to avoid

Picking **"Under $150"** filters the catalog to the villain alone and ends in `no_trusted_option`. That is a legitimate refusal path worth showing *after* the happy path, but the demo run should answer with **$150–$300**. See `docs/checklist.md` §9.

## Risks that are currently live

| Risk | Trigger seen? | Action taken |
|---|---|---|
| Checkout not reachable over HTTP | **cleared locally** | Tasks 23–24 implemented; Fly still needs redeploy |
| Fly serves the pre-merge build | **yes** | Redeploy from `main` in Block 5 |
| SerpAPI key unavailable | yes | Catalog-only per D-011 |
| Contracts still open | yes | `Question` shape is the only unresolved item |
| Browser never exercised the live stream | **yes** | Wiring is merged; C must click through it once |

## Cut list in effect

Live page fetching → Reddit → SerpAPI → Mongo → page flags. See `docs/checklist.md` §8.
