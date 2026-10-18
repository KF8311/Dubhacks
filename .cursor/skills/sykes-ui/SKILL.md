---
name: sykes-ui
description: Restyle Sykes so it does not read as generic AI UI. Use when the user asks for a makeover, visual polish, anti-slop restyle, distinctive branding, or frontend layout/copy that judges will see.
---

# Sykes UI

Read `.claude/skills/frontend-design/SKILL.md` first, then this overlay. After a restyle, run `/web-design-guidelines` on the screens you touched.

## Product

Sykes is a trust-gated shopping agent: search listings, five checks per merchant, cheapest **trusted** pick, sandboxed Visa checkout. Judges watch a laptop in a noisy hall. The UI has to look like a product, not a shadcn template.

## Hard constraints

- Stack stays **React 19 + Vite + Tailwind v4 + existing shadcn/Base UI primitives**. Restyle tokens, type, layout, motion. Do not add a new CSS framework or copy Sniff's layout, copy, or visual identity.
- Sandbox sentence is frozen: `Sandbox — simulated Visa Intelligent Commerce flow.`
- Money stays integer cents in data; format only in the UI.
- Pay stays disabled unless the listing is `trusted`. Do not invent a Pay-on-danger path for the look.
- Do not change scoring, SSE, or API contracts for a visual change.

## Anti-slop for this app

The current canvas (cool gray, teal/cyan, Geist, identical rounded cards, radial gradient washes) is the SaaS-card default. A makeover must pick a direction that belongs to **merchant investigation**, not another dashboard.

Spend boldness on one thing (hero, investigation, or the trusted pick). Keep the other screens quieter. No per-card fade-up, no ALL-CAPS eyebrows, no accent-one-word headlines, no purple-on-white gradient buttons.

## Screens that matter

Landing/search → clarifying chips → live investigation grid → best pick → checkout/passkey → receipt. Villain must stay visually `danger`. Empty and API-down states must stay honest.

## After the restyle

Verify in the browser at `http://localhost:5173/` (not `?mock=1` unless asked). Run `cd frontend && npm.cmd test -- --run` and `npm.cmd run build`.
