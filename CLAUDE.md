# Sniff + Visa — Agent Context

Read this first, then `docs/INDEX.md`.

## What we're building

A trust-gated shopping agent for the Visa "Reimagine Shopping" track at DubHacks '26. It searches listings, runs five trust checks per listing, streams the investigation over SSE, recommends the cheapest **trusted** option, and completes a **sandboxed** Visa mandate → passkey → token → receipt flow. The agent cannot pay a merchant it cannot verify.

## Read order

1. `docs/INDEX.md` — the map
2. `docs/status.md` — what is true right now
3. `docs/superpowers/plans/2026-10-17-sniff-visa.md` — architecture, contracts, 30 tasks
4. `docs/team-split-3.md` — ownership and the time-boxed checklist
5. `docs/decisions.md` — decisions already made; do not re-litigate without a new entry
6. `docs/SKILLS.md` — the skills and agents committed under `.claude/`

## Skills and agents

The team's Claude Code skills are vendored in `.claude/skills/` and load automatically when a session starts in `Dubhacks/`. Cursor loads the same folder for compatibility. The three project agents are in `.claude/agents/`. Use them:

- `/test-driven-development` before writing any feature or bugfix.
- `/systematic-debugging` before proposing a fix for a failing test or a stuck demo.
- `/verification-before-completion` before claiming a gate passed.
- `/handoff` at a shift change; it writes `docs/handoffs/`.
- `code-architect`, `code-explorer`, `code-reviewer` when the question is "how should this be shaped" or "how does this work."

Do not edit vendored skills; add a project skill instead. Full list and provenance: `docs/SKILLS.md` and `.claude/README.md`.


## Hard constraints

- **70/30 rule.** At least 70% of code written during the hackathon. First commit by 12:45 PM Saturday; commit every 30 minutes per person.
- **Do not copy the Sniff repo.** `thenerd31/sniff` is an architecture reference only. No code, file layout, copy text, or visual identity.
- **Payment is a sandbox.** Never claim production Visa integration. Every checkout and receipt shows "Sandbox — simulated Visa Intelligent Commerce flow."
- **No real PII, no real card numbers.** Synthetic shoppers and merchants. The villain is fictional (`premium-audio-deals.shop`).
- **Hard payability rule.** Checkout is refused unless the verdict is `trusted`, score ≥ 70, and (unless allowlisted) at least 3 checks completed. The server re-validates; the client sends only IDs and a cap.
- **One SSE stream per session**, monotonic `seq`, dedupe on the client, snapshot fallback.
- **Deterministic scoring.** `severity × 40` failed, `severity × 15` warning, thresholds 70/40, coverage cap 69. The LLM never computes a score.
- **Money is integer cents.** Format only at the UI edge.
- **One Uvicorn worker.** `--workers 1` is mandatory; no global gzip (it buffers SSE).
- **No new infrastructure** without a decision entry: no Redis, Celery, queues, auth, accounts, vector DB, or second database.

## Commands (once scaffolded)

```bash
# backend
cd backend && pytest -q
cd backend && uvicorn app.main:app --reload --workers 1

# frontend
cd frontend && npm test -- --run
cd frontend && npm run dev

# full demo path without network
python scripts/replay_offline.py
```

## Where things live

| Path | Purpose |
|---|---|
| `docs/INDEX.md` | Entry point and doc map |
| `docs/status.md` | Current gate, owners, blockers — update every 90 minutes |
| `docs/decisions.md` | Append-only decision log |
| `docs/open-questions.md` | Unresolved product/technical questions |
| `docs/handoffs/` | Shift handoff notes (sleep rotations, owner changes) |
| `docs/SKILLS.md` | Skills, agents, and when to use them |
| `.claude/` | Vendored team skills and agents — see `.claude/README.md` |
| `docs/contracts.md` | Frozen API/type contracts after 1:15 PM Saturday |
| `docs/team-split-3.md` | Task ownership and per-person checklist |
| `data/` | Catalog, allowlist, villain fixtures — not a database |

## Conventions

- One owner per task and per file. Contract files change only after a huddle.
- Tests first; every task ends with a passing test and a commit.
- Record a decision in `docs/decisions.md` before acting on it. Do not silently change scoring, thresholds, or the API shape.
- Update `docs/status.md` at every gate. It is the only file that claims to be current.
- Handoffs are for shift changes; they do not replace `status.md`.

## Do not

- Do not add auth, accounts, Redis, workers, or a second database.
- Do not send raw HTML or Reddit text to the LLM.
- Do not let a real brand render as `danger` in the demo.
- Do not store raw payment tokens, card data, or PII.
- Do not make the browser talk to MongoDB directly.
- Do not change the scoring math without bumping `scoring_version` and updating the golden tests.
