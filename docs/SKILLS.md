---
title: Skills and Agents
type: reference
updated: 2026-10-17
---

# Skills and Agents

The team's Claude Code setup is committed under `.claude/`, so a fresh clone gets the same workflows.

- **Skills** live in `.claude/skills/<name>/SKILL.md` and load automatically when Claude Code starts in `Dubhacks/`.
- **Agents** live in `.claude/agents/<name>.md`.
- Provenance, licenses, and the exact local changes are in `.claude/README.md`.

Invoke a skill by typing `/` and its name, or just describe the situation — each skill's description tells Claude when it should fire.

## Fresh clone setup

There is nothing to install — the skills are vendored, not referenced from the marketplace.

1. Open **`Dubhacks/`** as the working directory, not `Desktop/dubhacks/`. Project skills load from `.claude/skills/` in the folder the session starts in. Starting one level up means they load late or not at all.
2. Accept the workspace trust prompt the first time.
3. Type `/` in the prompt to confirm the skills are listed.

Optional: if you want the maintained upstream versions instead, run `claude plugin install superpowers@claude-plugins-official --scope project` once. The marketplace copy is namespaced (`/superpowers:writing-plans`) and lives alongside the flat vendored ones (`/writing-plans`), so nothing breaks — you just see both. We vendor so the team works offline and from a fresh clone with no setup.

## Cursor

Cursor 2.x supports the Agent Skills standard and **loads `.claude/skills/` automatically** for Claude Code compatibility. Teammates on Cursor do not need to copy anything or tell it where to look.

| Thing | How Cursor handles it |
|---|---|
| `.claude/skills/<name>/SKILL.md` | Auto-discovered at startup; offered to the agent by description; `/` invokes one |
| `AGENTS.md` | Read automatically as project instructions |
| `.cursor/rules/project.mdc` | Applied to every chat (`alwaysApply: true`) |
| `CLAUDE.md` | **Not** read automatically — that is why `AGENTS.md` exists |
| `allowed-tools` in frontmatter | Ignored; Claude Code only |

One-time check if the skills don't appear: **Cursor Settings → Rules, Skills, Subagents → enable "Include third-party Plugins, Skills, and other configs."** Cursor labels skills found outside `.cursor/skills/` as third-party, and that toggle controls them.

To hold a skill for a whole session instead of one message, open it with `Option+Enter` (Mac) or `Alt+Enter` (Windows) to make it a Custom Mode.


## The skills

| Skill | Fires when | Use it for | Best for |
|---|---|---|---|
| `/brainstorming` | Before any new feature or scope change | Turning a vague idea into an agreed design | All |
| `/writing-plans` | A design is agreed and needs implementation tasks | Producing a task-by-task TDD plan | A, B |
| `/executing-plans` | Implementing a written plan in this session | Working tasks in order with checkpoints | All |
| `/subagent-driven-development` | A plan has independent tasks | Fresh subagent per task, review between tasks | A |
| `/test-driven-development` | Writing any feature or bugfix | Red → green → refactor, no exceptions | A, B |
| `/systematic-debugging` | Any bug, failing test, or "it worked a second ago" | Root cause before fixes; no shotgun patching | All |
| `/verification-before-completion` | About to say "done" or claim a gate passed | Runs the command and shows the evidence first | All |
| `/requesting-code-review` | A task is finished, before merge | Self-review against the requirements | A (merge captain) |
| `/receiving-code-review` | Someone reviews your work | Evaluates feedback instead of blindly applying it | All |
| `/dispatching-parallel-agents` | 2+ tasks with no shared state | Fan-out without collisions | A |
| `/using-git-worktrees` | You need isolation from the current workspace | Separate worktree per feature | Optional |
| `/finishing-a-development-branch` | Work is complete and tests pass | Merge, clean up, or hand off | A |
| `/handoff` | End of shift, or before a long compaction | Writes `docs/handoffs/YYYY-MM-DD-HHMM-name.md` | All |

`/handoff` is the explicit, durable one. Automatic compaction is not a substitute — see below.

## The agents

| Agent | Use it for |
|---|---|
| `code-architect` | Design a component before building it; produces files, interfaces, and a build sequence |
| `code-explorer` | Trace how an existing feature works across files before changing it |
| `code-reviewer` | Review a diff for bugs, security, and convention violations |

Agents are read-only where it matters. Give one a narrow question and a file path.

## Compaction vs. handoff

These are different mechanisms:

- **Automatic compaction** happens by itself when the context window fills. Claude Code summarizes the session and keeps going. You do not need to ask, and the summary is not written to the repo.
- **`/compact`** forces it. You can steer it: `/compact focus on the SSE contract and what is left in Task 23`.
- **`/handoff`** writes a durable note for a teammate or a fresh session. Ask for it at shift changes or before you close the laptop.
- **`docs/status.md`** is the durable current state either way. It survives compaction, new sessions, and reboots.

Durable context belongs in files (`CLAUDE.md`, `docs/status.md`, the plan), never only in the conversation. That is why the repo, not the chat, is the source of truth.

## Suggested set per person

| Owner | Default skills |
|---|---|
| **A — Platform/Agent** | `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `subagent-driven-development`, `requesting-code-review` |
| **B — Trust/Data** | `test-driven-development`, `systematic-debugging`, `code-explorer` agent, `verification-before-completion` |
| **C — Frontend/UX** | `verification-before-completion`, `code-reviewer` agent, `brainstorming`, `systematic-debugging` |
| **Everyone** | `handoff` at shift changes, `executing-plans` while working the task list |

## Adding a skill

1. Create `.claude/skills/<name>/SKILL.md` with `name:` and `description:` frontmatter.
2. Write the description as "Use when…" so it fires at the right moment.
3. Add a row to the table above.
4. Do not modify a vendored skill to fit a project need; add a new one.
