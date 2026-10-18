---
title: Running Sniff + Visa locally
type: runbook
updated: 2026-10-18
---

# Running Sniff + Visa

Every supported way to start the product on this machine. The short version is the first section.

## One command

```powershell
.\scripts\dev.cmd
```

That is enough. It starts the backend in its own window, waits until `http://localhost:8000/api/health` answers, then starts the frontend in the current window. Vite prints the URL it chose, normally **http://localhost:5173**.

| Command | What it runs | When to use |
|---|---|---|
| `.\scripts\dev.cmd` | Backend (live search) + frontend | Normal development and the real demo |
| `.\scripts\dev.cmd offline` | Backend pinned to the curated catalog + frontend | Recording, screenshots, a deterministic run |
| `.\scripts\dev.cmd mock` | Frontend only, `?mock=1` data | The API is dead and you still need a demo |
| `.\scripts\dev.cmd check` | Prints prerequisites and what is already running | Something will not start |

What the script checks before starting:

- `backend\.venv\Scripts\python.exe` exists
- `frontend\node_modules` exists
- whether something already answers on `:8000` (if so, it reuses it instead of starting a second backend)

Stopping:

- The frontend runs in the window you launched the script from: **Ctrl+C** stops it.
- The backend runs in the window titled **sniff-visa backend**: close it, or Ctrl+C in it.
- `dev.cmd` reuses a backend that is already on `:8000`, but `dev.cmd offline` refuses when one is running: it cannot know whether that instance is in catalog mode. Close the backend window first, then run offline mode again.

## What "live" and "offline" actually mean

| | Live (`dev.cmd`) | Offline (`dev.cmd offline`) |
|---|---|---|
| Search | SerpAPI on the query you type, catalog fallback | Curated catalog only, query ignored |
| Network | SerpAPI, Gemini, Safe Browsing, WHOIS/DNS | None, all checks are fixture-backed |
| Results | Depends on SerpAPI, can be thin or fall back | Always 9 cards, 8 trusted + `Premium Audio Deals` |
| Use for | Developing discovery and question generation | Recording, screenshots, judging |

Environment is read from `backend/.env`. The current file has `SERPAPI_KEY` and a Gemini key set, so the default is live.

**Live-search timeout:** the SerpAPI client gets `SEARCH_S - 1.0` = **4.0 s** (`backend/app/search/serpapi.py`), inside a 5 s search budget. If a query is slower than that, the search silently falls back to the curated catalog, so you may see headphones instead of what you typed. The fallback is a demo safety net, not an error. If you want to confirm you are getting live results, query something distinctive (`mechanical keyboard`, `airpods pro`) and check the response's `search.completed` event for `source: "serpapi"`.

`DEMO_MODE=1` does **not** force the catalog. Despite the README table, only `OFFLINE` changes search behaviour; `DEMO_MODE` gates `/api/demo/reset` and some page flags.

## Manual two-terminal run

If the script is not an option.

**Terminal 1**

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --workers 1
```

`--workers 1` is mandatory: investigations and sessions are in-memory and SSE comes from the same process. More workers means two separate states.

**Terminal 2**

```powershell
cd frontend
npm run dev
```

`frontend/.env` points `VITE_API_BASE_URL` at `http://localhost:8000`. If you move the backend, change that line, and add the frontend origin to `ALLOWED_ORIGINS` in `backend/.env`.

For offline mode in the manual flow, set the variable for that process only, do not edit `.env`:

```powershell
cd backend
$env:OFFLINE="1"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --workers 1
```

Undo with `Remove-Item Env:\OFFLINE` and restart.

## Frontend only, no backend

```powershell
cd frontend
npm run dev
```

Open **http://localhost:5173/?mock=1** (or set `VITE_USE_MOCK=1` before starting). The full flow runs off `frontend/src/data/mock-session.json`. This is the mid-presentation fallback.

## No server at all: offline replay

```powershell
backend\.venv\Scripts\python.exe scripts\replay_offline.py
```

Runs the real orchestrator end-to-end against the curated catalog and prints the frozen numbers. Exit 0 plus 9 listings / 8 trusted / 1 danger / pick `lst_tgt_bsp` / median $374.49 / savings $194.50 means the contract is intact.

## Tests and build

```powershell
cd backend;  .\.venv\Scripts\python.exe -m pytest -q   # 215 pass
cd frontend; npx vitest run                            # 39 pass
cd frontend; npm run build                             # tsc -b + vite build, must be clean
```

Do not run the suite with `OFFLINE=1` in the environment. `test_ssl_cert.py` and `test_domain_age.py` pass `ctx=None` and read the ambient settings, so 13 tests fail for reasons unrelated to the product. Set `OFFLINE` per-process, never in `.env`.

## Docker

```powershell
docker build -f backend/Dockerfile -t sniff-visa .
docker run --rm -p 8080:8080 --env-file backend/.env sniff-visa
```

The API is on **http://localhost:8080**. The image copies `data/` to `/data`; the frontend is not served from this image, so point `VITE_API_BASE_URL` at `:8080` or serve the static build yourself. This is the same shape Fly.io runs.

## Resetting demo state

Sessions, checkouts, and receipts are in memory: restarting the backend clears them. Without a restart, while `DEMO_MODE=1`:

```powershell
curl -X POST http://localhost:8000/api/demo/reset
```

## The canonical "it works" walkthrough

1. Stack up, open the frontend.
2. Query `noise cancelling headphones`.
3. Answer $300–$600 / Travel / Noise cancelling.
4. Expect 9 cards, 8 trusted, `Premium Audio Deals` red.
5. Best pick is Target at $179.99; median $374.49; savings $194.50.
6. Checkout → passkey → receipt with a public share link.
7. Try to pay the villain; it must refuse.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `WinError 10048` on start | Port 8000 already taken | Let `dev.cmd` reuse it, or stop the old backend window |
| Frontend loads but every call fails | Backend not on 8000, or CORS origin missing | `scripts\dev.cmd check`; confirm `ALLOWED_ORIGINS` lists the frontend origin |
| Query returns headphones you did not ask for | SerpAPI timed out, catalog fallback fired | Retry with a shorter query; see idea B in `ideas-after-96cf47f.md` |
| `?mock=1` shows old-looking data | Mock reads `frontend/src/data/mock-session.json` | That file is the mock; it is not the live flow |
| Backend window flashes and closes | Import or dependency error | Run the manual command to keep the traceback visible |
| `npm run dev` starts a second Vite | 5173 is busy | Vite picks the next port; use the URL it prints |
| Tests fail only sometimes | `OFFLINE=1` leaked into the environment | Start a fresh shell, unset `OFFLINE`, rerun |

## Deploying later

Both paths are documented in `README.md` and `fly.toml`.

- **Fly:** `fly deploy` from the repo root, then `backend\.venv\Scripts\python.exe backend\scripts\smoke_http.py <url>`.
- **Vercel:** do not Git-deploy `96cf47f`. It does not ship `backend/data/`, so answers and checkout return 500. The fix is idea **A** in `ideas-after-96cf47f.md`; apply it first or use Fly.
