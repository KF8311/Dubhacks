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
| Gate | **G1 server side proven**; **G2 and G3 server side proven** — one real session streams 9 listings, 45 checks, 9 scores, and one recommendation. Browser halves are C's. |
| Health | https://sniff-visa-dubhacks.fly.dev/api/health (serves the pre-merge build; redeploy in Block 5) |
| Deploy | **Fly.io** org `dubhacks`, app `sniff-visa-dubhacks`, region `sjc` (D-010, D-012, D-013). Render is backup. |
| Contracts | `docs/contracts.md` carries domain types, `Recommendation`, SSE ordering, and checkout/confirm JSON. `Question` is the only open shape; `ScoreResult.allowlisted` (D-015) landed with A's block and is acknowledged. |
| SerpAPI | No `SERPAPI_KEY`. Catalog-only until a live query confirms merchant domains (D-011). |
| Tests | Backend **123 passed** on `merge/agent-backend` (122 pre-fix + 1 catalog-limit regression). Frontend **3 files / 4 tests passed**, `npm run build` clean. |
| Routes | Sessions create/answer/snapshot/events, orchestrator fan-out, payability guard and mandates. Checkout/confirm HTTP (Task 23) is not built yet. |
| Owners | A: platform + orchestrator + payments. B: trust + data. C: frontend. |
| Blockers | Task 23 checkout routes; C still renders listings from mock data; Fly serves the pre-merge build |
| Branches | `main` has PRs #1–#8. `merge/agent-backend` carries A's Tasks 16 + 22 on top of `main` — open for review, not yet merged. |

Last updated: 2026-10-17 17:10 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health deployed | Sat 13:15 | 🟡 health live, `Question` shape still open | URL above + `docs/contracts.md` |
| G1 Listings stream to browser | Sat 15:30 | 🟡 server side proven; browser pending | 9 `listing.found` events captured; C's grid still on mock data |
| G2 Full investigation, 5 checks, score | Sat 18:00 | 🟡 server side proven; browser pending | 45 `check.completed`, villain `0 / danger`, 8 trusted |
| G3 Recommendation + best pick | Sat 19:30 | 🟡 server side proven; browser pending | pick `lst_tgt_bsp` $179.99, median $374.49, savings $194.50 |
| G4 Checkout → passkey → receipt | Sat 21:00 | ⬜ | Needs Task 23 (A) and C's checkout sheet |
| G5 Devpost draft submitted | Sat 22:30 | ⬜ | Devpost confirmation |
| G6 Feature freeze | Sun 02:00 | ⬜ | Team agreement |
| G7 Final submission | Sun 09:50 | ⬜ | Devpost confirmation |

## Proof of the server-side pipeline (2026-10-17 17:05 PT)

`SessionOrchestrator(store, bus)` with the real registry, real allowlist, real fixtures, and no network:

```
events: listing.found 9 · check.started 45 · check.completed 45 · listing.scored 9 · recommendation.ready 1
stats:  {'listings': 9, 'trusted': 8, 'caution': 0, 'danger': 1}
stage:  ready
pick:   lst_tgt_bsp (Target, $179.99)
median: $374.49 · savings: $194.50
villain: lst_vln_xm5 → danger, score 0, "Reported by the local threat list: LOCAL_DENYLIST"
```

## In progress

| Owner | Task | Started | Expected | Notes |
|---|---|---|---|---|
| A | Task 23 checkout/confirm HTTP | 18:00 | 19:30 | Block 4 |
| B | Deferred integration golden test + `scripts/replay_offline.py` (Task 28) | 17:10 | 18:00 | After this merge lands |
| C | Live SSE wiring (`api.ts`, `listing.found`, `check.*`, `listing.scored`) | 16:15 | 17:30 | Keep `?mock=1` |

## Done since last update

- [x] B: Tasks 4, 9, 10, 11, 12, 13, 14, 15 merged — five checks, scoring, recommendation, D-015
- [x] A: Tasks 5, 6, 7, 16, 22 merged — session routes, SSE, orchestrator fan-out, payability guard
- [x] Villain-truncation bug fixed: `MAX_LISTINGS` was 8 and dropped the ninth catalog entry, so no session could ever score a `danger`. Raised to 9 with a regression test.
- [x] Real orchestrator run proves 9 listings, 45 checks, 9 scores, and a recommendation end to end

## Next three actions

1. A builds Task 23 — `POST /api/checkout` and `POST /{id}/confirm` — so the payability guard is reachable over HTTP.
2. C points `api.ts` at the live SSE stream and renders `listing.found` / `check.completed` / `listing.scored`; that closes the browser half of G1.
3. B adds the deferred integration golden test (villain through all five checks → `danger` → excluded from the pick) and `scripts/replay_offline.py`.

## Risks that are currently live

| Risk | Trigger seen? | Action taken |
|---|---|---|
| G1 browser half not done | **yes** | C is on the stream wiring now; server side is proven |
| Checkout not reachable over HTTP | **yes** | Task 23 is A's next block; payability logic itself is tested |
| Fly serves the pre-merge build | **yes** | Redeploy from `main` in Block 5 |
| SerpAPI key unavailable | yes | Catalog-only per D-011 |
| Contracts still open | yes | `Question` shape is the only unresolved item |
| Merged state never deployed | **yes** | Fly still serves the platform-branch build; redeploy in Block 5 |

## Cut list in effect

Live page fetching → Reddit → SerpAPI → Mongo → page flags. See `docs/checklist.md` §8.
