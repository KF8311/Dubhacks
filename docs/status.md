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
| Gate | G0 met late at 15:32 PT — public health is live; contracts drafted, not frozen |
| Health | https://sniff-visa-dubhacks.fly.dev/api/health |
| Deploy | **Fly.io** org `dubhacks`, app `sniff-visa-dubhacks`, region `sjc` (D-010, D-012, D-013). Render is backup. |
| Contracts | `docs/contracts.md` now carries domain types and SSE ordering. One open shape — `Question` — is marked for A's sign-off, then frozen. |
| SerpAPI | No `SERPAPI_KEY`. Catalog-only until a live query confirms merchant domains (D-011) |
| Owners | A: platform. B: catalog/trust. C: frontend. |
| Blockers | B trust engine in progress; C frontend; contract huddle |

Last updated: 2026-10-17 15:45 PT

## Gate board

| Gate | Due | State | Proof |
|---|---|---|---|
| G0 Contracts frozen + health deployed | Sat 1:15 PM | 🟡 health live late, contracts not frozen | URL above + `docs/contracts.md` |
| G1 Listings stream to browser | Sat 3:30 PM | ⬜ | `curl -N` or screen recording |
| G2 Full investigation, 5 checks, score | Sat 6:00 PM | ⬜ | Browser |
| G3 Recommendation + best pick | Sat 7:30 PM | ⬜ | Browser |
| G4 Checkout → passkey → receipt | Sat 9:00 PM | ⬜ | Browser, real backend |
| G5 Devpost draft submitted | Sat 10:30 PM | ⬜ | Devpost confirmation |
| G6 Feature freeze | Sun 2:00 AM | ⬜ | Team agreement |
| G7 Final submission | Sun 9:50 AM | ⬜ | Devpost confirmation |

## In progress

| Owner | Task | Started | Expected | Notes |
|---|---|---|---|---|
| A | Scaffold + health + Fly deploy | 15:32 | done | `origin/agent_backend` at `9cdd132` |
| B | Task 8 check protocol + runner | 15:20 | done | 3 unit tests passing on `b/trust` |
| B | Task 14 scoring + golden tests | 15:45 | 17:15 | next |
| C | Frontend scaffold | 1:15 | — | `origin/2026-10-17-6c1c` |

## Done since last update

- [x] Repo versioned and pushed; skills and context kit committed
- [x] A: backend scaffold, `GET /api/health` live on Fly.io, `docs/contracts.md` drafted
- [x] B: catalog, allowlist, villain fixtures — 2 tests passing
- [x] B: `TrustCheck` protocol, `get_checks()`, `run_checks()` — 3 tests passing
- [x] B: `b/trust` merged with A's scaffold; stopgap models dropped in favor of A's

## Next three actions

1. Freeze `docs/contracts.md` at the next huddle — A publishes the SSE event names and ordering.
2. B: Task 14 scoring with golden tests (villain ≤31 danger, hero ≥90 trusted).
3. Confirm the Safe Browsing key, or ship the static denylist with `source="unavailable"`.

## Risks that are currently live

| Risk | Trigger seen? | Action taken |
|---|---|---|
| SerpAPI key unavailable | **yes** | Catalog-only per D-011 |
| Backend cold start | no | Fly.io always-on machine |
| Villain not going red | no | Fixtures + golden tests in Task 14 |
| Two branches diverging on `models.py` | **yes** | B merged A's scaffold; A's copy is authoritative |

## Cut list in effect

None yet. See plan §15.3 and `docs/team-split-3.md`.
