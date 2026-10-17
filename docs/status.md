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
| Gate | G0 partial — health live, contracts not frozen. **G1 server side proven on PR #3** (8 `listing.found` events); the browser half is C's next step. |
| Health | https://sniff-visa-dubhacks.fly.dev/api/health |
| Deploy | **Fly.io** org `dubhacks`, app `sniff-visa-dubhacks`, region `sjc` (D-010, D-012, D-013). Render is backup. |
| Contracts | `docs/contracts.md` carries domain types, `Recommendation`, and SSE ordering. `Question` is the one open shape; `ScoreResult.allowlisted` (D-015) needs A's acknowledgement, then frozen. |
| SerpAPI | No `SERPAPI_KEY`. Catalog-only until a live query confirms merchant domains (D-011) |
| Tests | Backend **56 passed** (46 on `main`, +10 on `b/recommendation`); frontend **3 files / 4 tests passed**, `npm run build` clean |
| Routes | Sessions create/answer/snapshot plus SSE events, all live on `main`. Orchestrator still runs `checks=[]` — no checks or scores emitted yet. |
| Owners | A: platform + orchestrator. B: trust + data. C: frontend. |
| Blockers | Orchestrator still runs `checks=[]`; contracts not frozen; C renders from mock data |
| Branches | `main` `4132b67` — PR #3 merged. `b/recommendation` adds `recommend()` + D-015, unmerged. Existing branches should `git merge origin/main` before continuing. |

Last updated: 2026-10-17 16:45 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health deployed | Sat 13:15 | 🟡 health live, contracts not frozen | URL above + `docs/contracts.md` |
| G1 Listings stream to browser | Sat 15:30 | 🟡 server side proven on PR #3; browser pending | 8 `listing.found` events captured; C's grid still on mock data |
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
- [x] B: Task 4 search service with catalog fallback — 8 tests
- [x] B: Task 14 scoring engine + golden tests — 17 tests; villain `0 danger`, hero `100 trusted`
- [x] B: Task 15 `recommend()` + `Recommendation` + D-015 allowlist exemption — 9 tests

## Next three actions

1. A wires `run_checks()` + `score_investigation()` into the orchestrator — the only thing between us and G2.
2. B writes the five checks, starting with domain age — until three complete, the coverage cap holds every score at 69.
3. C points `api.ts` at the live SSE stream and renders `listing.found`; that closes G1's browser half.

## Risks that are currently live

| Risk | Trigger seen? | Action taken |
|---|---|---|
| G1 missed, later gates compress | **yes** | Blocks re-cut to 45–90 min; proofs unchanged |
| PR #3 unmerged | **yes** | `main` has no session routes, no `search()`, no scoring — nobody should branch from it until this lands |
| Orchestrator emits no checks or scores | **yes** | `checks=[]` — G2 needs A to wire `run_checks` + `score_investigation` |
| SerpAPI key unavailable | yes | Catalog-only per D-011 |
| C building against mock data | **yes** | `?mock=1` fallback so a dead backend never kills the demo |
| Contracts still open | yes | `Question` shape is the only unresolved item |
| Merged state never deployed | **yes** | Fly still serves the platform-branch build; redeploy in Block 5 |

## Cut list in effect

Live page fetching → Reddit → SerpAPI → Mongo → page flags. See `docs/checklist.md` §8.
