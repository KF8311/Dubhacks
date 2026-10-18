# `.claude/` — Team Skills and Agents

Committed to the repo so every teammate, and every Claude Code session started here, behaves the same way.

## What loads automatically

| Path | What it is | Discovery |
|---|---|---|
| `.claude/skills/<name>/SKILL.md` | Project skills | Loaded when Claude Code starts in this folder |
| `.claude/agents/<name>.md` | Project subagents | Available to the Agent tool |

**Open `Dubhacks/` as the working directory**, not `Desktop/dubhacks/`. `.claude/` is discovered relative to the folder Claude Code starts in, so starting one level up means none of this loads.

There is no `.claude/settings.json` on purpose. Committing `enabledPlugins` does not download the plugin on a teammate's machine; it produces an "enabled in project settings but isn't installed here" error instead. Vendoring the skill folders avoids that entirely — a fresh clone needs no install step and no network.

## Provenance and local changes

| Source | License | What we vendored | Changes |
|---|---|---|---|
| [superpowers](https://github.com/obra/superpowers) 7.0.0, Jesse Vincent | MIT | 13 process skills | Removed the `superpowers:` namespace prefix from cross-references, because project skills are flat (`writing-plans`, not `superpowers:writing-plans`) |
| [mattpocock-skills](https://github.com/mattpocock/skills) 1.3.1, Matt Pocock | MIT | the `handoff` skill only | Saves to `docs/handoffs/` instead of the OS temp directory, so the team can read it |
| [feature-dev](https://github.com/anthropics/claude-code), Anthropic | Apache-2.0 | `code-architect`, `code-explorer`, `code-reviewer` agents | None, verbatim |
| [anthropics/skills](https://github.com/anthropics/skills) `frontend-design` | Apache-2.0 | `.claude/skills/frontend-design/` (mirrored to `.cursor/skills/`) | None, verbatim |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) `web-design-guidelines` | MIT | `.claude/skills/web-design-guidelines/` (mirrored to `.cursor/skills/`) | None, verbatim |
| project | — | `sykes-ui` skill, `ui-designer` agent | Sykes overlay: no Sniff copy, frozen sandbox sentence |

License texts are beside the skills: `skills/LICENSE-superpowers-MIT.txt`, `skills/LICENSE-mattpocock-skills-MIT.txt`, `agents/LICENSE-feature-dev-Apache-2.0.txt`.

## Rules

- **Do not edit vendored skills.** If the team needs different behavior, add a new project skill next to them and say why in `docs/SKILLS.md`.
- **Do not add a skill for something the plan already covers.** A skill is a workflow; the plan is the design. They are not substitutes.
- These are docs and agent definitions, not product code. Vendoring them does not affect the 70/30 rule.
- If you update a vendored skill, bump the version in the table above and note the diff.
