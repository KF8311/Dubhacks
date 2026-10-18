---
title: Devpost form map
type: submission
updated: 2026-10-17
owner: B
---

# Devpost form map — DubHacks '26

The submission is five steps. Fields marked **\*** are required. Copy below is the final wording; it is kept in sync with `docs/devpost.md`, which is the long-form source.

**Draft state at capture:** 2/5 steps done.

| Step | Tab | Status |
|---|---|---|
| 1 | Project overview | 2 fields to confirm + thumbnail |
| 2 | Project details | story, tags, links, gallery, video |
| 3 | Additional info | tracks, prizes, team, AI disclosure |
| 4 | Submit | preview + submit |
| 5 | (final review / confirm) | after 4 |

---

## 1. Project overview

**\* Project name** — max 60 characters, editable later.

```
Sykes + Visa
```

**\* Elevator pitch** — max 150 characters, editable later.

```
The AI shopping agent that investigates every listing, then only pays merchants it can verify.
```

**Thumbnail** — JPG/PNG/GIF, 5 MB max, 3:2 ratio. Needs the results grid or the receipt, not a logo.

- [ ] `frontend/public/devpost-thumbnail.png` (1500×1000)

---

## 2. Project details

Everything here is public.

**\* About the project** — Markdown with LaTeX. Devpost explicitly asks for *inspiration, what you learned, how you built it, challenges*. Paste the sections from `docs/devpost.md` in this order, so the required four are obvious:

1. Inspiration
2. What it does
3. How we built it
4. Challenges
5. Accomplishments
6. What we learned
7. What's next

Keep the **Sandbox disclosure** block at the end of the story — it is required copy, not a footnote.

**\* Built with** — up to 25 tags.

```
python, fastapi, pydantic, uvicorn, httpx, beautifulsoup4, python-whois, pytest,
react, typescript, vite, tailwindcss, zustand, vitest, gemini, mongodb
```

**"Try it out" links** — demo site, GitHub repo, video.

| Label | Value |
|---|---|
| Live demo | `https://sykes.select` — live on Vercel, verified 2026-10-17 23:00 PT |
| Source | `https://github.com/KF8311/Dubhacks` |
| Sandbox notice | already in the story; do not add a second link |

**Project media** — up to 15 images, 3:2, 5 MB each.

- [ ] Results grid with the villain red and the best-pick ring
- [ ] Danger detail — four reasons on the villain
- [ ] Checkout mandate card
- [ ] Passkey dialog
- [ ] Receipt page at `/r/{share_id}`

**\* Video demo link** — YouTube or Vimeo URL. Required. The 3-minute path: question → stream → villain → pick → refusal → receipt.

---

## 3. Additional info

Mostly judge-facing.

**Upload a file** — optional, 35 MB. Zip if multiple. Skip unless we add a PDF.

**Sponsor / Special Prizes** — checkboxes. Our selections:

- [ ] **Visa: Reimagine Shopping**
- [ ] **[MLH] Best Use of MongoDB Atlas** — only if the Mongo swap actually lands in Block 6

Note: VEYZL is **not** in this list. It lives in Sponsored Side Tracks below. Do not look for it here.

**\* Title Track** — exactly one, appears in the gallery.

- [ ] **Visa: Reimagine Shopping**

**Sponsored Side Tracks** — at most three, appear in the gallery.

- [ ] **VEYZL** — the $500 + lifetime-pro track; requires the audit PR evidence in `docs/veylz-audit.md`
- [ ] CloudForce — optional; no stated criteria beyond the listing, so skip unless we have a reason

**Non-Sponsored Side Tracks** — unlimited.

- [ ] **MLH: Best Use of MongoDB Atlas** — only if Block 6 lands
- [ ] DubHacks Next — only if eligible

**\* Team Member 1–4 Discord usernames** — double-check spelling and capitalization. Fill from the team, not from memory.

**\* Universities/schools** — one line, everyone's current school.

**GoDaddy Registry domains** — none registered; leave blank.

**Technology feedback** — optional. One or two sentences each on VEYZL, Gemini, and MongoDB. Write it after the audit runs so it describes something real.

**\* AI tools used this weekend** — this asks about *build* tools. Check honestly:

- [ ] **Anthropic** — Claude Code
- [ ] **Gemini** — the Gemini API is implemented in the product
- [ ] anything else the team actually used

**\* Did you implement a generative AI model or API?** — **Yes.** Answer:

> Yes. Gemini 3.5 Flash Lite writes the clarifying questions, the one-line recommendation narration, and on-demand explanations of each trust check. Every call is capped at 2.5 seconds and falls back to a deterministic template, so the demo works with no key and no network. The model never scores, never selects checks, and never touches payability or checkout — those are Python-only, and a build test fails if a trust, check, or payment module imports the LLM. We kept the model out of the decision path deliberately: a trust score you cannot re-derive from evidence is not a trust score.

**Gemini Project Number** — only for the Best Use of Gemini API category. We are not entering it. Leave blank.

---

## 4. Submit

- [ ] Preview the public page and read the elevator pitch out loud
- [ ] Confirm the Visa track and VEYZL side track are both selected
- [ ] Confirm the tax/eligibility fields if Devpost asks
- [ ] Submit

## 5. After submit

- [ ] Screenshot the confirmation, drop it in `docs/handoffs/`
- [ ] Update `docs/status.md` — G5 to 🟢, G7 to in progress
- [ ] Claim VEYZL access if it was granted as a promo, not a purchase

---

## Order of operations

The form is last because every remaining field waits on an artifact:

| Field | Waits on |
|---|---|
| Live URL | A's Fly redeploy |
| Gallery images | C's click-through |
| Video | the team's recording |
| VEYZL selection + audit evidence | the audit and the fix |
| MongoDB selection | Block 6 |

Fill the text first (it is all drafted), attach artifacts as they land, and submit once — not incrementally.
