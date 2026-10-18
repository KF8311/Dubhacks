---
title: Devpost form map
type: submission
updated: 2026-10-18
owner: B
---

# Devpost form map — DubHacks '26

The submission is five steps. Fields marked **\*** are required. Copy below is the final wording; it is kept in sync with `docs/devpost.md`, which is the long-form source.

**Draft state at capture:** text ready; live URL, gallery, and video pending.

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
react, typescript, vite, tailwindcss, zustand, vitest, gemini, mongodb, bun, spectrum-ts
```

**"Try it out" links** — demo site, GitHub repo, video.

| Label | Value |
|---|---|
| Live demo | `https://sykes.select` — Vercel; `/api/health` returns `{"status":"ok","db":"ok"}` |
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

- [x] **Visa: Reimagine Shopping**
- [x] **[MLH] Best Use of MongoDB Atlas** — Atlas is connected and proven (D-026)

Note: if the live form lists MLH Atlas under both this section and Non-Sponsored Side Tracks, enter it once under Non-Sponsored Side Tracks (D-028); do not double-enter. VEYZL is **not** in this list. It lives in Sponsored Side Tracks below. Do not look for it here.

**\* Title Track** — exactly one, appears in the gallery.

- [x] **Visa: Reimagine Shopping**

**Sponsored Side Tracks** — at most three, appear in the gallery. The slate is D-028.

- [x] **SideShift — Best Startup Idea** — no build requirement; the pitch is [`devpost.md#who-pays`](devpost.md#who-pays)
- [x] **CloudForce** — entry is a raffle ticket; Most Interesting is a judges' pick
- [ ] **Photon 2.0** — conditional: tick only after a real text round-trips through the deployed bridge and the project's key is set. If it slips, leave this blank.
- [ ] **VEYZL** — the $500 + lifetime-pro track; requires the audit PR evidence in `docs/veylz-audit.md`. **Not selected** (D-028).

**Non-Sponsored Side Tracks** — unlimited.

- [x] **MLH: Best Use of MongoDB Atlas** — Atlas persists the payment path; health reports `db: ok`
- [ ] **MLH: Best Use of Gemini API** — tick once the project number is in the field below
- [ ] **MLH: DEV Writing Challenge** — tick once the article is published and the URL is pasted
- [x] DubHacks Next — eligible; the same startup paragraph serves both
- [x] **MLH Commit Fellowship** — free entry

**\* Team Member 1–4 Discord usernames** — double-check spelling and capitalization. Fill from the team, not from memory.

**\* Universities/schools** — one line, everyone's current school.

**GoDaddy Registry domains** — none registered; leave blank.

**Technology feedback** — optional. One or two sentences each on Gemini and MongoDB. VEYZL is not selected, so do not write VEYZL feedback.

**\* AI tools used this weekend** — this asks about *build* tools. Check honestly:

- [x] **Anthropic** — Claude Code
- [x] **Gemini** — the Gemini API is implemented in the product
- [ ] anything else the team actually used

**\* Did you implement a generative AI model or API?** — **Yes.** Answer:

> Yes. Gemini 3.5 Flash Lite writes the clarifying questions, the one-line recommendation narration, and on-demand explanations of each trust check. Every call is capped at 2.5 seconds and falls back to a deterministic template, so the demo works with no key and no network. The model never scores, never selects checks, and never touches payability or checkout — those are Python-only, and a build test fails if a trust, check, or payment module imports the LLM. We kept the model out of the decision path deliberately: a trust score you cannot re-derive from evidence is not a trust score.

**Gemini Project Number** — required once we tick Best Use of Gemini API. It is the project's **public** identifier (a ~12-digit number), not the API key: MLH uses it to confirm the traffic that hit Gemini this weekend came from this project. The key's owner reads it at `aistudio.google.com/apikey` from the project selector — no rotation needed, and `GEMINI_API_KEY` itself never goes into Devpost, chat, or the repo.

---

## 4. Submit

- [ ] Preview the public page and read the elevator pitch out loud
- [ ] Confirm the Visa title track and the MLH Atlas track are selected, and **VEYZL is not**
- [ ] Confirm the tax/eligibility fields if Devpost asks
- [ ] Submit

## 5. After submit

- [ ] Screenshot the confirmation, drop it in `docs/handoffs/`
- [ ] Update `docs/status.md` — G5 to 🟢, G7 to in progress

---

## Order of operations

The form is last because every remaining field waits on an artifact:

| Field | Waits on |
|---|---|
| Live URL | done — `https://sykes.select` (Vercel) |
| Gallery images | C's click-through |
| Video | the team's recording |
| Gemini Project Number | read from AI Studio's project selector |
| MongoDB selection | done — Atlas connected and proven (D-026) |

Fill the text first (it is all drafted), attach artifacts as they land, and submit once — not incrementally.
