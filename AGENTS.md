# Sniff + Visa — Agent Brief

Cross-tool project instructions. Cursor reads this file automatically; Claude Code reads `CLAUDE.md`. Both read `.claude/skills/`. If they disagree, `CLAUDE.md` and the plan are authoritative.

## What we're building

A trust-gated shopping agent for the Visa "Reimagine Shopping" track at DubHacks '26. It searches listings, runs five trust checks per merchant, streams the investigation over SSE, recommends the cheapest **trusted** option, and completes a **sandboxed** Visa mandate → passkey → token → receipt flow. The agent cannot pay a merchant it cannot verify.

## Read before working

1. `docs/status.md` — the current gate, owners, and blockers
2. `docs/INDEX.md` — the document map
3. `docs/superpowers/plans/2026-10-17-sniff-visa.md` — architecture, contracts, and the 30-task list
4. `docs/team-split-3.md` — who owns what

## Non-negotiables

- **Payment is a sandbox.** Every checkout and receipt says "Sandbox — simulated Visa Intelligent Commerce flow." Never claim a production Visa integration.
- **No real PII, no real card numbers.** Synthetic shoppers, synthetic merchants, fictional villain.
- **Hard payability rule.** Checkout is refused unless the verdict is `trusted`, score ≥ 70, and (unless allowlisted) at least 3 checks completed. The server re-validates; the client sends only IDs and a cap.
- **Deterministic scoring.** Failed = `severity × 40`, warning = `severity × 15`, thresholds 70/40, coverage cap 69. The LLM never computes a score.
- **One SSE stream per session**, monotonic `seq`, dedupe on the client, snapshot fallback.
- **Money is integer cents.** Format only at the UI edge.
- **One Uvicorn worker.** `--workers 1`; no global gzip (it buffers SSE).
- **No new infrastructure** without a decision entry: no auth, accounts, Redis, Celery, queues, vector DB, or second database.
- **Do not copy the Sniff repo.** Architecture reference only — no code, layout, copy text, or visual identity.
- **70/30 rule.** At least 70% of code written during the hackathon; commit every 30 minutes per person.

## Skills and agents

Both Cursor and Claude Code auto-load the project skills in `.claude/skills/`. In either tool, type `/` to invoke one. The project agents are in `.claude/agents/`.

- `/test-driven-development` before any feature or bugfix
- `/systematic-debugging` before proposing a fix
- `/verification-before-completion` before claiming a gate passed
- `/handoff` at a shift change — writes `docs/handoffs/`
- Full list and provenance: `docs/SKILLS.md` and `.claude/README.md`

## Working rules

- One owner per task and per file. Contracts change only after a huddle.
- Tests first; every task ends with a passing test and a commit.
- Update `docs/status.md` at every gate. It is the only file that claims to be current.
- Record a decision in `docs/decisions.md` before acting on it.
- Do not change scoring, thresholds, or the API shape without a decision entry and a `scoring_version` bump.

## Cursor specifics

- `.cursor/rules/project.mdc` is always applied and restates the guardrails.
- Cursor ignores `allowed-tools` in `SKILL.md`; that field is Claude Code only.
- If the skills do not appear, enable **Settings → Rules, Skills, Subagents → Include third-party Plugins, Skills, and other configs**.
