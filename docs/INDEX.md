---
title: Project Index
type: index
updated: 2026-10-17
---

# Sniff + Visa — Project Index

One project, one repository, one source of truth. If a fact is not written here or linked from here, it is not agreed.

## Start here

| If you are… | Read, in order |
|---|---|
| **New to the project** | This page → `project-a-sniff-visa.md` → plan §1–§4 |
| **Building a task** | `docs/status.md` → `docs/team-split-3.md` → the task in the plan |
| **Claude / an agent** | `CLAUDE.md` → this page → `docs/status.md` → the plan |
| **On Cursor** | `AGENTS.md` → `.cursor/rules/project.mdc` → `docs/status.md` |
| **Reviewing a decision** | `docs/decisions.md` |
| **Writing the Devpost or video** | `docs/devpost-form.md` (field-by-field) → `docs/devpost.md` (copy) → `project-a-sniff-visa.md` §10–§11 |
| **Debugging the demo** | Plan §9 (fallbacks), §16 (risk register), `docs/status.md` |

## The document set

| Document | What it is | Status |
|---|---|---|
| `AGENTS.md` | Cross-tool brief: read order, non-negotiables, skills. Cursor reads this automatically | Current |
| `CLAUDE.md` | Agent context and hard constraints for Claude Code | Current |
| `.cursor/rules/project.mdc` | Always-applied guardrails for Cursor | Current |
| `project-a-sniff-visa.md` | Product spec: problem, checks, scoring, Visa flow, video, Devpost | Stable |
| `docs/superpowers/plans/2026-10-17-sniff-visa.md` | Engineering plan: architecture, API, data model, 30 TDD tasks, schedule, risks | Current |
| `docs/team-split-3.md` | Three-person ownership map, time-boxed checklists, gates, cuts | Current |
| `docs/checklist.md` | **Shared team checklist** — universal rules plus one block per person, with completed items ticked | **Work from this** |
| `docs/status.md` | The only file that claims to be current: gate, owners, blockers | **Update every 90 min** |
| `docs/decisions.md` | Append-only decision log with rationale and alternatives | Append-only |
| `docs/devpost.md` | Devpost draft: title, copy, tech claims, sandbox disclosure, fill-in list | Draft |
| `docs/devpost-form.md` | The five Devpost steps mapped field by field: limits, required fields, exact copy, which tracks to select | Draft |
| `docs/veylz-audit.md` | VEYZL audit: scope, candidate controls, method, and the finding/fix evidence | Awaiting run |
| `docs/open-questions.md` | Unresolved questions for mentors, judges, or the team | Living |
| `docs/SKILLS.md` | Committed skills and agents, when each fires, who should use it | Current |
| `.claude/` | The vendored skills and agents themselves | Vendored |
| `docs/handoffs/` | Shift handoffs for sleep rotations or owner changes | Per shift |
| `docs/contracts.md` | Frozen API and type contracts | Created at 1:15 PM Sat |

## The one rule

**Update `docs/status.md` at every gate.** A handoff note is a snapshot; `status.md` is the current state. If they disagree, `status.md` wins and the handoff is marked superseded.

## Optional: Obsidian

Open `docs/` as a vault if you want backlinks and graph view. Treat it as a **viewer**:

- Do not commit `.obsidian/workspace.json` (it churns on every machine).
- Do not create a second set of notes outside the repo.
- Do not use Obsidian Sync; git is the sync.
- If the vault and the repo disagree, the repo wins.
