# Decisions

| ID | Decision | Why | Date |
|---|---|---|---|
| D1 | SerpAPI go/no-go: **catalog only** until a live query with `SERPAPI_KEY` confirms product URLs carry merchant domains. Re-run `python scripts/serpapi_spike.py` when the key exists. | Spike could not call SerpAPI (key unset). Plan already specifies catalog fallback. Tell B. | 2026-10-17 |
| D2 | Deploy the API on **Render**, not Fly.io. Frontend stays on Vercel. Mongo stays Atlas M0. Demo backup: local uvicorn + Cloudflare Tunnel. | Fly.io always-on is paid. Plan §9.4 already names Render as the free fallback. | 2026-10-17 |
| D3 | API host is **Fly.io** now that an account exists. App name: `sniff-visa-dubhacks`, region `sea`. Render remains the backup. | User has Fly.io. Plan §11.2 prefers Fly for the always-on API. | 2026-10-17 |
