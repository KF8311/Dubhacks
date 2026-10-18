---
title: Locked video script — Sykes
type: video
updated: 2026-10-18
owner: C (screen), A (payments), B (trust)
---

# Sykes — locked 3:00 demo script

**This is the take sheet. Record against it, not against memory.** Hard cap 3:00. Target **400–460** spoken words; the timing below assumes ~150 wpm plus deliberate pauses, with room for the dialogue to breathe. If a take runs long, cut the italic line in that beat.

The video now opens with a 16-second skit: a shopper is frustrated, a friend recommends Sykes, and the demo proves the friend's pitch. The slogan in the skit is **"Sykes secures your cart every second."** Say it once, then ground it immediately: every search, every merchant, before every payment. Do not repeat it later as a technical claim.

**Delivery note:** The intro is a conversation, not copy. Let them interrupt each other, leave "um" and "okay" in, and keep the takes where one of them reacts instead of reciting. A slightly messy take sounds real; a clean one sounds like an ad.

One sentence the video must land:

> **A shopping agent that will not pay a merchant it cannot verify.**

Every beat exists to earn one line of the Visa rubric; the rubric map and judge Q&A are at the end. Side-track moments (Gemini, MongoDB Atlas, Photon, SideShift) are woven in and can each be cut in the edit without breaking the Visa story.

---

## Ground truth — what is real

Say this plainly; never apologize for the sandbox.

| Part | Real or simulated | What to say on camera |
|---|---|---|
| Product search | **Real** in live mode | "real Google Shopping listings" (SerpAPI) |
| Clarifying questions | **Real model, template fallback** | "Gemini writes the questions" |
| Check explanations | **Real model with a visible source chip** | "AI-generated" vs "From evidence" |
| Domain age, SSL | **Real** in live mode | Name them as checks |
| Safe Browsing | Real with a key; static list otherwise | Say "threat lists", not "Google Safe Browsing live" |
| Reddit sentiment, page flags | **Fixture-only by default** (`DEMO_MODE=1`) | Name the categories; do **not** say all five ran live |
| Allowlisted retailers | Checks run, merchant exempt from the score floor | "Verified" badge |
| Villain store | **Fictional**, offline catalog only | "our staged catalog … one fictional store" |
| Payment | **Sandbox** | "sandboxed Visa Intelligent Commerce flow" |
| Score and pick | **Deterministic Python** | "arithmetic, not a model" |
| Database | **MongoDB Atlas**, receipt survives a restart | "stored in MongoDB Atlas" |

**Never say:** live Visa charge, production integration, real card, "all five checks ran live", "Gemini found the products", "Gemini scored it", or a hard budget cap (`D-022` is "closest trusted match").

---

## Pre-flight (do not skip)

1. **Reset the demo data.** `python scripts/replay_offline.py` → exit 0; prints **9 listings, 8 trusted, 1 danger, pick Target $179.99, median $374.49, savings $194.50.**
2. **Check the deployed URL.** `https://sykes.select/api/health` → `{"status":"ok","db":"ok", ...}`. Confirm the frontend it serves is the merged build (`ee9264b` or later).
3. **Quota.** Confirm `SERPAPI_KEY` has searches left. Warm the exact query once, then restart the backend so the recorded run is a cache hit if possible. The recorded live run costs at most one uncached search.
4. **Segment 1 — live.** `.\scripts\dev.cmd`. Open **http://localhost:5173/** only. Browser 1280 px wide, notifications off, bookmarks hidden, cursor visible.
5. **Segment 2 — staged.** Close the backend window. `.\scripts\dev.cmd offline`. The replay numbers must match step 1.
6. **Terminal ready.** One tab in `backend/` with this typed:
   `pytest tests/integration/test_refusal_paths.py -q`
   Optional stronger shot: a prepared `curl` to `POST /api/checkout` with the villain id returning `409 MERCHANT_NOT_TRUSTED` (rehearse it; if it is not ready, use the test).
7. **Backup.** Keep `http://localhost:5173/?mock=1` loaded in a second window. If the API dies mid-take, finish the story in mock and cut the seam.
8. **Bridge.** Send to phone and Deal alerts need the local Spectrum bridge, its `.env` key, and the bridge process. Record where the bridge is known good (local). Do not bet the take on a deployed bridge.
9. **Sketch the skit.** Two people, one laptop, one room, no background music under dialogue. Shoot three takes of the cold open before touching the screen recording.

---

## Script at a glance

| Time | Beat | Speaker | Visa rubric | Side track |
|---|---|---|---|---|
| 0:00–0:16 | Cold open: frustration, friend, slogan | C + B | Commerce Impact, UX, Innovation | — |
| 0:16–0:30 | Thesis: the question payments need | B | Innovation | — |
| 0:30–1:00 | Ask, search, watch the investigation | B + C | UX, Innovation | Gemini (source chip) |
| 1:00–1:28 | Villain and the math | B | Trust & Responsibility, Technical | — |
| 1:28–1:44 | Cheapest *trusted* pick and purge | B + C | Commerce Impact, UX | — |
| 1:44–2:12 | Mandate → passkey → receipt | A | Commerce Impact, Trust | MongoDB Atlas |
| 2:12–2:34 | The server says no | A | Technical, Trust | — |
| 2:34–3:00 | Close, who pays, end card | All | Innovation, Commerce Impact | SideShift, Photon (conditional) |

---

## Beat 1 — Cold open: the frustrated shopper (0:00–0:16) · C + B

**On screen:** live action, handheld or tripod, 16:9. A desk, a laptop, a half-finished coffee. C is scrolling a shopping site, visibly stuck. B enters from frame right.

**Action:**

1. Hold on C's face for two seconds. Let the sigh land.
2. C scrolls, stops, scrolls again, then pushes the laptop back an inch.
3. B walks in already talking, sets down a coffee, sits.

**Dialogue:**

> **C:** "An hour. Every store says 'best deal.' I just want headphones that actually show up."
>
> **B:** "Still doing this by hand? Here — Sykes. Secures your cart every second."
>
> **C:** "That's a slogan."
>
> **B:** "It checks the store before you pay. Can't verify it, no checkout."
>
> **C:** "…Show me."

**Production notes:** Under 16 seconds. B starts on C's last word; don't wait for a clean handoff. C's "That's a slogan" is the audience's thought — keep it, and don't play it for a laugh. No logo shots, no brand names spoken. If it runs long, cut "Here —" and start B on "Sykes."

---

## Beat 2 — Thesis (0:16–0:30) · B

**On screen:** hard cut to the laptop screen, landing hero with the search field, header with Deal alerts and Shop / How it works / About. No sandbox text in the header.

**Action:** B's hands on the keyboard; slow cursor drift toward the search field. Do not type yet.

**Say:**

> "AI agents are about to spend our money. Visa's Intelligent Commerce can hand one a mandate. But somebody has to ask first: should this agent be allowed to pay this store at all? That's Sykes."

**Rubric note:** This is the Innovation beat. Say "Visa's Intelligent Commerce" once, accurately, as the rails — Sykes is the gate before the rails.

---

## Beat 3 — Ask, search, watch (0:30–1:00) · B drives, C reacts

**Action:**

1. Type **noise cancelling headphones**, submit.
2. Answer **$300–$600 → Travel → Noise cancelling → See results**.
3. While cards fill: hover one card so it flips to its safety record. Do not rush.
4. Click a **non-allowlisted** merchant card. The stats panel slides over with five check rows. Point at **Domain age**, **SSL certificate**, **Safe Browsing**, **Reddit**, **Page flags**; point at any **Could not verify**.
5. Click **Explain** on one row. The chip reads **AI-generated** if the key answered, **From evidence** if the template did. Say the line either way.
6. Click **Back to items** once.

**Dialogue:**

> **B:** "Okay. 'Noise cancelling headphones.' Gemini asks three questions — budget, trip, whatever — and I answer. Template fallback if the model's slow."
>
> **C:** "Then what?"
>
> **B:** "Then it searches real Google Shopping listings. Every store gets five checks: domain age, certificate, threat lists, what people are saying, page patterns. It streams in live, so you're watching the investigation instead of a spinner."
>
> **C:** "What's the chip?"
>
> **B:** "Whether Gemini wrote the sentence or the evidence did."
>
> **C:** "Oh — the card flips."
>
> **B:** "Safety record. Click it and all five checks slide over. Established retailers show Verified, but every listing still runs the checks."

**If short on time, cut:** *"Oh — the card flips."* and *"Established retailers show Verified; every listing still runs the checks."*

---

## Beat 4 — The villain and the math (1:00–1:28) · B

**On screen:** staged offline catalog, same query and answers. The red card is `premium-audio-deals.shop`, the cheapest listing.

**Action:**

1. Click the red card. The stats panel slides over; the four reasons are visible in the check rows and the top reason.
2. Point in this order: **denylist**, **12-day-old domain**, **scam reports**, **countdown timer + crypto-only checkout**.
3. Point at the score and the **Danger** badge. Point at one gray **Could not verify** row on another card.

**Say:**

> "This is our staged catalog — real stores plus one fictional one. It's the cheapest listing on the page, and Sykes says danger. Four reasons: a threat denylist, a twelve-day-old domain, scam reports on Reddit, and crypto-only checkout behind a countdown timer. The score is arithmetic, not a model. Start at a hundred, minus forty for every failed check. Same evidence, same score, every time. And if a check can't run, it says 'Could not verify.' It doesn't guess. Missing data is never safe."

---

## Beat 5 — Cheapest trusted pick and purge (1:28–1:44) · B narrates, C clicks

**Action:**

1. Scroll to the **Best pick** banner: Target, Beats Studio Pro, $179.99, savings line.
2. Click **Purge danger**. The red card wipes out; the grid reflows.

**Say (B):**

> "So the cheapest listing isn't the pick. The cheapest one we'd actually pay is. Target — a hundred seventy-nine ninety-nine. That's a hundred ninety-four fifty under the median for trusted stores."

**Say (C, as C clicks):**

> "And the scam card? Gone."

---

## Beat 6 — Mandate, passkey, receipt (1:44–2:12) · A

**Action:**

1. Click **Pay** on the best pick. Hold on the sheet long enough to read **Sandbox — simulated Visa Intelligent Commerce flow.**
2. Show the **mandate card**: merchant, spending cap, expiry. Click approve.
3. Passkey dialog: confirm. Show the processing steps.
4. **Receipt:** point at amount, token ending **4242**, the trust score/ring, and the share link `/r/...`.

**Say:**

> "Payment. This is the one simulated part, and it says so right here: sandboxed Visa Intelligent Commerce flow. You approve a mandate — this store, this cap, this expiry. A passkey confirms it's actually you. The server issues a one-time token and returns a signed receipt with a share link. It's stored in MongoDB Atlas, so the link still works after a restart."

**Do not click** Send to phone or Deal alerts unless the bridge round trip is already proven and the take is a backup.

---

## Beat 7 — The server says no (2:12–2:34) · A

**Action:** cut to the terminal. Run `pytest tests/integration/test_refusal_paths.py -q`. Let **4 passed** sit for a beat. If the prepared `curl` is rehearsed, show `409 MERCHANT_NOT_TRUSTED` instead; the test is the safe fallback.

**Say:**

> "The button isn't the security boundary. The browser sends IDs and a cap — no score, no verdict. The server recomputes everything. Watch." (run the test) "Force the villain through and it comes back four-oh-nine: merchant not trusted. That's FastAPI, one event stream per session with sequence numbers and replay, a React client that dedupes, and tests that have to stay green."

---

## Beat 8 — Close and who pays (2:34–3:00) · all

**Action:** back to the grid and the receipt, then an end card with the Sykes wordmark, `sykes.select`, the repo URL, and **Visa · Reimagine Shopping · DubHacks '26**.

**Say (B):**

> "Gemini writes the sentences. Math decides who's trusted. A human approves the money."

**Say (A):**

> "And for whoever's running the agent, it's a few cents per gated checkout. Not the shopper. Not the store."

**Say (C, or all):**

> "Sykes. The trust layer for agentic commerce. It's at sykes dot select."

**Optional Photon line, only if the round trip is proven:**

> "The same agent answers a text message with a trust-checked pick."

**Cut first if long:** the Photon line, then "never the shopper, never the merchant."

---

## Visa rubric coverage — where each point is earned

The source image disagrees with itself: the table says UX 20% (weights total 95%), the bullets say 25% (total 100%). This script assumes **25%**; ask an organizer if it matters.

| Criterion | Weight | Beat | The exact thing judges should remember |
|---|---|---|---|
| **Innovation** | 25% | 1, 2, 3, 8 | Reframes agentic shopping around *should it pay?*; the trust gate is the product, not a feature; Visa mandate is the rail, Sykes is the gate |
| **User Experience** | 25% | 1, 3, 5, 6 | Frustrated-shopper story, live check stream, hover-flip cards, slide-over stats, one-click purge, four-step checkout |
| **Technical Execution** | 20% | 4, 7 | Deterministic scoring; SSE with seq/replay; server-side refusal; Atlas-backed receipt; tests |
| **Commerce Impact** | 15% | 1, 5, 6, 8 | Cheapest **trusted** pick, $194.50 savings, mandate-to-receipt path, per-checkout business model |
| **Trust & Responsibility** | 15% | 4, 6, 7 | No model in the decision path; skipped ≠ safe; sandbox labelled; spending cap; human passkey; 409 |

### What judges must see (tick before upload)

- [ ] A real user with a real frustration in the first 15 seconds
- [ ] The one-sentence thesis: will not pay a merchant it cannot verify
- [ ] The slogan **"secures your cart every second"**, immediately grounded
- [ ] Live search + the investigation stream, uncut for 4–5 seconds
- [ ] All five checks named on screen
- [ ] Deterministic score explained as arithmetic, with the formula audible
- [ ] The fictional villain and its four signals
- [ ] "Could not verify" and "missing data is never treated as safe"
- [ ] The cheapest **trusted** pick, with the $194.50 savings number
- [ ] Mandate: merchant, cap, expiry
- [ ] Passkey confirmation by a human
- [ ] Receipt with token, share link, and Atlas persistence
- [ ] The frozen sandbox sentence readable for 2 seconds
- [ ] Terminal: 4 passed or `409 MERCHANT_NOT_TRUSTED`
- [ ] Business model: few cents per gated checkout
- [ ] End card: Sykes, `sykes.select`, repo, track line
- [ ] Captions on every spoken line (judges may watch muted)

### Claims audit

| Claim on camera | Evidence on screen | Do not say |
|---|---|---|
| "real Google Shopping listings" | live search results | "Google Shopping API" if it is SerpAPI |
| "Gemini writes the questions / sentences" | clarifying questions, **AI-generated** chip | "Gemini scores it" |
| "arithmetic, not a model" | score panel + formula line | "AI decides who is trusted" |
| "all five checks" | five rows in the stats panel | "all five ran live" |
| "stored in MongoDB Atlas" | health `db: ok`, receipt reload | "our database" without naming it |
| "sandboxed Visa Intelligent Commerce flow" | frozen sentence on sheet + receipt | "real Visa charge" |
| "merchant not trusted" | `409 MERCHANT_NOT_TRUSTED` | "the client blocks it" |

---

## Side-track coverage

Tick a side track only if the video (or its Devpost link) actually shows the evidence.

| Track | What the video shows | Gate |
|---|---|---|
| **MLH: Best Use of Gemini API** | Beat 3: Gemini-written questions + the **AI-generated / From evidence** chip | Project number in the Devpost field; never claim Gemini scores |
| **MLH: Best Use of MongoDB Atlas** | Beat 6: receipt persisted in Atlas, share link survives a restart | Health `db: ok` on the submitted URL |
| **Photon 2.0** | Beat 8 optional line + a real text round trip | **Only if** a phone text reaches the bridge and gets a reply before recording; otherwise cut the line and leave the track unticked |
| **SideShift — Best Startup Idea** | Beat 8: who pays, a few cents per gated checkout | Form-only; no build requirement |
| **Cloudforce** | Nothing on camera (raffle entry) | Form-only |
| **DubHacks NEXT** | Same business line as SideShift | Form-only |
| **MLH: DEV Writing Challenge** | Nothing on camera; link the published article | Article URL in the Devpost |

---

## Judge Q&A cheat sheet (not on camera)

Rehearse these; the answers are the rubric in spoken form.

| Question | Answer |
|---|---|
| **Is this a real Visa integration?** | No — the checkout is a sandboxed simulation of the Visa Intelligent Commerce flow. Every screen says so. No real card, charge, or token. |
| **What is actually live?** | Search, domain age, SSL, and Gemini are live in live mode. Reddit sentiment and page flags are fixture-only by default. We say "threat lists," not "Safe Browsing live." |
| **How is the score computed?** | Deterministic Python: start at 100, subtract 40 per failed check and 15 per warning; thresholds 70/40; a coverage cap prevents a partially checked merchant from scoring trusted. The model never computes it. |
| **What happens when a check cannot run?** | It stays "Could not verify," counts against coverage, and never counts as a pass. Missing data is not safety. |
| **Can the browser bypass the gate?** | No. The client sends only listing/merchant IDs and a cap. The server re-derives the verdict and refuses with `409 MERCHANT_NOT_TRUSTED`. |
| **Why not just read reviews?** | Reviews are one signal. We combine domain age, certificate, threat lists, community reports, and page patterns, and show which evidence drove each row. |
| **Why Gemini?** | It turns an ambiguous request into useful clarifying questions and writes explanations, with a visible chip separating model prose from evidence. It is not in the decision path. |
| **Why MongoDB Atlas?** | The receipt and share link survive a restart, which is what makes the receipt a durable artifact rather than a UI state. |
| **How do you make money?** | A few cents per gated checkout to the operator of a shopping agent. Never the shopper, never the merchant. |
| **What would production need?** | Real Visa Intelligent Commerce credentials, production merchant data sources, more check providers, rate limits, and an audit trail. The current build is the trust layer, not the payment rail. |
| **What did you build during the hackathon?** | The search-to-receipt product, five-check engine, deterministic scorer, SSE client, sandbox checkout, and the Spectrum bridge. Answer with the 70/30 rule in mind; do not claim vendored code. |

---

## Edit plan

- Shoot the cold open first, separately from the screen capture. Get clean audio; do not record dialogue through the laptop mic across the room.
- Record the screen cleanly twice: **live segment** (Beats 2–3) and **staged segment** (Beats 4–7). Record voiceover separately over the chosen take; never rush a click to match narration.
- Keep the live check stream uncut for at least 4–5 seconds. That silence is the signature moment.
- Caption the sandbox sentence on Beat 6 for 2 full seconds. Judges may watch muted.
- End card holds 4 seconds: Sykes, `sykes.select`, repo, track line.
- Upload unlisted to YouTube; title **Sykes — the trust layer for agentic commerce**; paste the URL into the Devpost and `docs/devpost-form.md`.

## If it breaks on the day

| Failure | Do this | Say |
|---|---|---|
| Cold-open take is stiff | Shoot it again before touching the screen; do not settle | — |
| Live search slow (up to ~22 s) | Cut the wait in the edit; keep the skeletons | "Live search is slow" |
| Live search fails (`SEARCH_UNAVAILABLE`) | Use `?mock=1` and finish; cut the seam | Nothing; do not explain a broken take |
| Backend dies | `?mock=1` finishes the story | Nothing |
| Gemini key missing | The chip reads **From evidence** | "a template fallback when the model is slow" |
| Bridge down | Cut Send / Deal alerts / Photon line | — |
| Offline numbers drift | Stop. Re-run replay; do not record | — |
