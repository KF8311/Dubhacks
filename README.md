# Sniff + Visa

A trust-gated shopping agent. It searches listings, runs five trust checks on each merchant, streams the investigation to the browser, recommends the cheapest **trusted** option, and completes a **sandboxed** Visa Intelligent Commerce flow: mandate → passkey → one-time token → transaction → receipt.

Built for the Visa "Reimagine Shopping" track at DubHacks '26.

> **Sandbox notice.** The payment flow is simulated and labeled everywhere. This is a prototype, not a Visa production integration. All shoppers, merchants, and cards are synthetic; no real PII or card numbers are used.

**Status:** see [`docs/status.md`](docs/status.md). VEYZL finding and fix: [`docs/veylz-audit.md`](docs/veylz-audit.md).

## Docs

Start at [`docs/INDEX.md`](docs/INDEX.md).

| Doc | What it's for |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Cross-tool brief — Cursor reads this automatically |
| [`CLAUDE.md`](CLAUDE.md) | Agent context, hard constraints, conventions |
| [`docs/SKILLS.md`](docs/SKILLS.md) | Committed skills and agents, and how to use them |
| [`project-a-sniff-visa.md`](project-a-sniff-visa.md) | Product spec: problem, checks, scoring, Visa flow, video, Devpost |
| [`docs/superpowers/plans/2026-10-17-sniff-visa.md`](docs/superpowers/plans/2026-10-17-sniff-visa.md) | Engineering plan: architecture, API, data model, 30 tasks, schedule |
| [`docs/team-split-3.md`](docs/team-split-3.md) | Ownership, time-boxed checklists, gates, cut list |
| [`docs/status.md`](docs/status.md) | The living state: gate, owners, blockers |
| [`docs/decisions.md`](docs/decisions.md) | Append-only decision log |
| [`docs/open-questions.md`](docs/open-questions.md) | Questions for mentors, judges, and the team |

## Quick start

```bash
# backend
cd backend
copy .env.example .env   # then set GEMINI_API_KEY and SERPAPI_KEY
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\uvicorn.exe app.main:app --reload --workers 1

# frontend
cd frontend
copy .env.example .env   # VITE_API_BASE_URL=http://127.0.0.1:8000 locally
npm install && npm run dev
```

Offline demo without a server: `backend/.venv/Scripts/python.exe scripts/replay_offline.py`.

## Ground rules

- At least 70% of the code is written during the hackathon; commit every 30 minutes per person.
- The Sniff repo is an architecture reference only — no copied code, layout, copy, or visual identity.
- The agent cannot pay a merchant whose verdict is not `trusted`.
- One owner per task and per file. Update `docs/status.md` at every gate.
