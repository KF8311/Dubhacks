# Status

This is the only file that claims to be current.

| Field | Value |
|---|---|
| Gate | 3:30 — sessions/SSE/orchestrator skeleton local-green; Fly still on health-only until `fly deploy` |
| Health | Public: https://sniff-visa-dubhacks.fly.dev/api/health |
| Deploy | **Fly.io** org `dubhacks`, app `sniff-visa-dubhacks`, region `sjc` (D3). Render is backup. |
| Contracts | Drafted in `docs/contracts.md`; freeze at the 1:15 huddle |
| SerpAPI | No `SERPAPI_KEY` in the environment. Spike script is `scripts/serpapi_spike.py`. Default: catalog-only until a live query confirms merchant domains. |
| Owners | A: platform. B: catalog/trust. C: frontend. |
| Blockers | Redeploy Fly for sessions; Task 16 checks; B catalog; C frontend |

Last updated: 2026-10-17 15:40 PT (Person A, Tasks 5–7).
