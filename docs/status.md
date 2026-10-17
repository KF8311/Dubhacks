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
| Gate | G0 partial — health live, contracts drafted but not frozen. **G1 missed at 15:30**; Block 1 of `docs/checklist.md` recovers it by 17:00. |
| Health | https://sniff-visa-dubhacks.fly.dev/api/health |
| Deploy | **Fly.io** org `dubhacks`, app `sniff-visa-dubhacks`, region `sjc` (D-010, D-012, D-013). Render is backup. |
| Contracts | `docs/contracts.md` carries domain types and SSE ordering. One open shape — `Question` — needs A's sign-off, then frozen. |
| SerpAPI | No `SERPAPI_KEY`. Catalog-only until a live query confirms merchant domains (D-011) |
| Tests | Backend **15 passed**; frontend **3 files / 4 tests passed**, `npm run build` clean |
| Routes | Only `GET /api/health` and `POST /api/demo/reset` exist. No session routes yet — that is the G1 blocker. |
| Owners | A: platform + orchestrator. B: trust + data. C: frontend. |
| Blockers | No session/SSE routes; contracts not frozen; C renders from mock data |
| Branches | `main` `58e4427`. `c/web` `88dcee5` = `main` + frontend, **PR #2 open**. `b/trust`, `richard-dev`, `agent_backend` fully merged; `2026-10-17-6c1c` is an ancestor of `c/web`. |

Last updated: 2026-10-17 16:10 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health deployed | Sat 13:15 | 🟡 health live, contracts not frozen | URL above + `docs/contracts.md` |
| G1 Listings stream to browser | Sat 15:30 | 🔴 missed — recovering in Block 1 | `curl -N` showing `listing.found` + cards in browser |
| G2 Full investigation, 5 checks, score | Sat 18:00 | ⬜ | Browser: villain red with named reasons |
| G3 Recommendation + best pick | Sat 19:30 | ⬜ | Browser: cheapest trusted listing picked |
| G4 Checkout → passkey → receipt | Sat 21:00 | ⬜ | Browser, real backend, refusal path shown |
| G5 Devpost draft submitted | Sat 22:30 | ⬜ | Devpost confirmation |
| G6 Feature freeze | Sun 02:00 | ⬜ | Team agreement |
| G7 Final submission | Sun 09:50 | ⬜ | Devpost confirmation |

## In progress

| Owner | Task | Started | Expected | Notes |
|---|---|---|---|---|
| A | Session routes + SSE (`listing.found`) | 16:15 | 17:00 | Block 1 |
| B | Task 4 search service, then Task 14 scoring | 16:15 | 17:00 | Block 1 |
| C | Wire `api.ts` to live SSE, keep `?mock=1` | 16:15 | 17:00 | Block 1 |

## Done since last update

- [x] PR #1 merged — backend scaffold, trust foundation, data, docs on `main`
- [x] Frontend branch reconciled with `main` and pushed; PR #2 open
- [x] Region resolved as `sjc` from `fly.toml` (D-013)
- [x] `oldIdeas/` removed (D-014)
- [x] `docs/contracts.md` gained domain types and the SSE ordering guarantee
- [x] Both suites verified on merged code: 15 backend, 4 frontend, build clean

## Next three actions

1. Merge PR #2 so `main` carries the frontend — one click, blocks nobody but keeps one source of truth.
2. A signs off the `Question` shape in `contracts.md`; then G0 is genuinely closed.
3. Start Block 1 at 16:15 — the session routes are the single thing gating every remaining gate.

## Risks that are currently live

| Risk | Trigger seen? | Action taken |
|---|---|---|
| G1 missed, later gates compress | **yes** | Blocks re-cut to 45–90 min; proofs unchanged |
| No session routes | **yes** | Block 1 is A's only task |
| SerpAPI key unavailable | yes | Catalog-only per D-011 |
| C building against mock data | **yes** | `?mock=1` fallback so a dead backend never kills the demo |
| Contracts still open | yes | `Question` shape is the only unresolved item |
| Merged state never deployed | **yes** | Fly still serves the platform-branch build; redeploy in Block 5 |

## Cut list in effect

Live page fetching → Reddit → SerpAPI → Mongo → page flags. See `docs/checklist.md` §8.
