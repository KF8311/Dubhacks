# Sykes + Visa — 3-Minute Demo Video Script

DubHacks '26 · Visa "Reimagine Shopping" · Speakers: **A** (platform, payments), **B** (trust, scoring), **C** (frontend, drives the screen)

> **Rule for every line below:** search is real, payment is not. Product listings come from live Google Shopping search (through SerpAPI), not from the AI. The payment flow is a sandbox, the one scam store is a staged fictional merchant, and Gemini never scores or decides anything. Say each plainly and do not apologize for the sandbox.

## What is real and what is simulated

Search and the main trust checks are real in live mode; the payment and the villain store are not. This comes from reading the code, not from running it, so confirm against your `backend/.env` before saying it on camera.

| Part | Real or simulated | Detail |
| --- | --- | --- |
| Product search | Real in live mode | Google Shopping results via SerpAPI for the query typed. Offline mode (`dev.cmd offline`) swaps in a curated 9-listing headphone catalog. |
| Merchant identity | Real, partly inferred | When Google Shopping only names the seller, Sykes maps it to a known domain (Target to target.com). Decision D-021 says to confirm this before claiming it publicly. |
| Gemini | Real, writing only | Writes the questions, the one-line pick narration, and optional check explanations. It never finds products, scores, or pays. |
| Domain age and SSL | Real in live mode | Live RDAP/WHOIS lookup and a live TLS handshake. Offline mode uses fixtures or skips them. |
| Safe Browsing | Real only with a key | Live Google Safe Browsing if `GOOGLE_SAFE_BROWSING_KEY` is set; otherwise a small local denylist. |
| Reddit sentiment and page flags | Fixture-only by default | Live only when `DEMO_MODE=0`. The default is `DEMO_MODE=1`, so for real merchants these two return no evidence. Do not claim all five checks ran live unless you have changed this. |
| Allowlisted retailers | Checks skipped by design | Target, Best Buy and similar show "Verified" and skip the five checks (decision D-015). |
| Villain store | Fictional | `premium-audio-deals.shop` exists only in the offline catalog and its fixtures. |
| Payment | Sandbox | Mock Visa flow: simulated passkey, one-time mock token, card ending 4242, signed receipt. No real card, no Visa network. |
| Score and pick | Real, deterministic | Python arithmetic over the check evidence; no model involved. |

## Before you hit record

- The video has two segments. **Segment 1 (Beats 1–2) is live:** run `.\scripts\dev.cmd` so search returns real Google Shopping listings. **Segment 2 (Beats 3–6) is the staged scenario:** run `.\scripts\dev.cmd offline` so the fictional villain and the frozen numbers appear. Close the backend window between the two, because `dev.cmd offline` refuses to start over a running backend.
- Before the live segment, confirm `SERPAPI_KEY` is set in `backend/.env` and run one live search. The search event should show `source: "serpapi"`. Warm it once first; a cold query can take up to about 22 seconds.
- Answers to use in both segments: **noise cancelling headphones**, then **$300–$600**, **Travel**, **Noise cancelling**. In the live run, check that at least one non-allowlisted merchant appears so the checks visibly stream; allowlisted retailers only show "Verified".
- Before the staged segment, run `python scripts/replay_offline.py`. It must exit 0 and print: 9 listings, 8 trusted, 1 danger, pick Target $179.99, median $374.49, savings $194.50.
- Open `http://localhost:5173/` only (the API allows only that port). Browser at 1280px wide, notifications off.
- Open a terminal in `backend/` with `pytest tests/integration/test_villain_end_to_end.py -q` typed and ready (used in Beat 6).
- Keep `?mock=1` ready as the backup if the API dies mid-take.
- The sandbox sentence must be readable on the checkout sheet and the receipt: "Sandbox — simulated Visa Intelligent Commerce flow."
- **Team decision:** if a live run produces a clean pick and you would rather record everything live, swap that run's numbers into Beats 4–5. The villain beat cannot be live, because no real store will reliably fail on cue.

## Script at a glance

| Time | Beat | Speaker | Rubric criteria hit |
| --- | --- | --- | --- |
| 0:00–0:20 | Hook: the question nobody answers | C | Innovation |
| 0:20–0:50 | Discovery and the live investigation | C | User Experience, Innovation |
| 0:50–1:20 | The villain and the math | B | Trust & Responsibility, Technical Execution |
| 1:20–1:45 | Best pick and purge | B + C | Commerce Impact, User Experience |
| 1:45–2:15 | Mandate, passkey, receipt | A | Commerce Impact, Trust & Responsibility |
| 2:15–2:45 | The server says no, plus the stack | A | Technical Execution, Trust & Responsibility |
| 2:45–3:00 | Close | All | Innovation |

Spoken text is about 430 words, which leaves room for on-screen pauses. If a take runs long, cut the sentence in *italics* in that beat.

## Beat 1 — Hook (0:00–0:20) · C

**On screen:** Sykes home screen, search box, sandbox badge visible in the header.

**Action:** Slow cursor movement toward the search box. Do not type yet.

**Say:**

> "AI agents are about to spend our money. Every shopping-agent demo answers 'what should I buy?' None of them answer the question a payment actually needs: should this agent be allowed to pay this store at all? This is Sykes. It searches real listings, investigates every merchant, and will not pay one it cannot verify."

## Beat 2 — Discovery and the live investigation (0:20–0:50) · C

**Action:**

1. In live mode, type "noise cancelling headphones" and submit. Three questions appear one at a time.
2. Click **$300–$600**, **Travel**, **Noise cancelling**, then **See results**.
3. Let the real listings appear and the check rows fill in. Point at the merchant names (real stores), then at the check rows on a non-allowlisted merchant, then at a "Verified" badge on an established retailer.

**Say:**

> "I type what I want. Sykes asks three short questions, written by Gemini from my query. Then it searches real Google Shopping listings, and for each merchant it runs trust checks: domain age, SSL certificate, threat-list reputation, and more. They stream in live over a single server-sent-event connection, so I watch the investigation happen instead of staring at a spinner. Established retailers on our allowlist show as Verified; everyone else gets checked."

**Why this matters to judges:** this is the UX and the novelty in one shot. The check streaming is the signature moment, so give it a full beat of silence if a take is short.

## Beat 3 — The villain and the math (0:50–1:20) · B

**Action:**

1. Cut to the staged scenario (offline mode, same three answers). Click the red card for `premium-audio-deals.shop` (the cheapest, about $30 below the pick). Expand its checks.
2. Point at each reason in order: denylist, 12-day-old domain, Reddit scam reports, urgency timer and crypto-only checkout.
3. Point at the score and the "danger" badge. Point at any gray "Could not verify" row on another card.

**Say:**

> **Transition:** "Live results rarely contain a scam on cue, so for this part we switch to our staged scenario: a curated catalog of real retailers plus one fictional scam store."
>
> "This is the cheapest listing on the page, and Sykes rates it danger on four independent signals: it is on a threat denylist, the domain is twelve days old, Reddit has scam reports, and the page uses countdown timers and crypto-only checkout. The score is arithmetic, not a model. It starts at a hundred and subtracts severity times forty for every failed check. Same evidence, same score, every time. *And if a check cannot run, it says 'Could not verify.' Missing data is never treated as safe.*"

**If you have 3 extra seconds:** "Gemini writes sentences. It never picks the winner, and a build test fails if the scoring code ever imports it."

## Beat 4 — Best pick and purge (1:20–1:45) · B narrates, C clicks

**Action:**

1. Scroll or cut to the **Best pick** banner: Target, Beats Studio Pro, $179.99, savings line.
2. Click **Purge**. The red wipe removes the danger card; the grid reflows.

**Say (B):**

> "So we do not recommend the cheapest listing. We recommend the cheapest one we would actually pay: Target at $179.99, which is $194.50 under the trusted median."

**Say (C, as you click):**

> "And purge the danger card. Gone."

## Beat 5 — Mandate, passkey, receipt (1:45–2:15) · A

**Action:**

1. Click **Pay** on the best pick. Pause so the sandbox sentence is readable.
2. Show the **mandate card**: merchant, spending cap, expiry. Click approve.
3. Passkey dialog: click confirm. Show the three processing steps (tokenizing, authorizing, capturing).
4. **Receipt:** point at amount, last four `4242`, Verified/score ring, and the share link `/r/...`.

**Say:**

> "The payment is the one simulated part, and we label it that way on every screen: a sandboxed Visa Intelligent Commerce flow. The shopper approves a mandate: this merchant, this spending cap, this expiry. A simulated passkey confirms the human. The server issues a one-time token, authorizes, and returns a signed receipt with a public link that shows what was verified and what was not."

## Beat 6 — The server says no, plus the stack (2:15–2:45) · A

**Action:** Switch to the terminal. Run `pytest tests/integration/test_villain_end_to_end.py -q`. Let the green result sit for a second. *(Optional upgrade if you have rehearsed it: a prepared `curl` to `POST /api/checkout` with the villain's listing id that returns `409 MERCHANT_NOT_TRUSTED`.)* Then briefly show the repo tree or `docs/contracts.md`.

**Say:**

> "The button is not the security boundary. The browser only ever sends IDs and a spending cap. It never sends a score or a verdict. The server re-derives everything, and when we force the villain through, it refuses with a 409, merchant not trusted. Under the hood: FastAPI, one event stream per session with sequence numbers and replay, a React 19 client that dedupes events, and about 280 automated tests, plus an offline replay that fails if the demo numbers drift."

## Beat 7 — Close (2:45–3:00) · All

**Action:** Back to the results grid, or an end card with the Sykes logo, repo link, and "Visa · Reimagine Shopping · DubHacks '26".

**Say (C, then A and B on the last line):**

> "Gemini writes the sentences. Math decides who is trusted. A human approves the money."
>
> **All:** "Sykes: the trust layer for agentic commerce."

## Rubric coverage check

The image lists weights in two places that disagree: the table gives User Experience 20% (the weights add to 95%), while the bullets give it 25% (adding to 100%). This script treats the bullets as correct. It is worth asking an organizer if you want to be sure.

| Criterion | Weight | Where the video earns it | One line to make sure lands |
| --- | --- | --- | --- |
| Innovation | 25% | Beat 1 reframes agentic commerce around "should it pay?" instead of "what should it buy?"; Beat 2 shows live trust checks; Beat 7 closes on it | "A shopping agent that will not pay a merchant it cannot verify." |
| User Experience | 25% | Beat 2 (three questions, live stream, skeleton rows), Beat 4 (purge), Beat 5 (mandate card, passkey, receipt) | Show the grid filling in without cuts. Keep the cursor slow and deliberate. |
| Technical Execution | 20% | Beat 3 (deterministic scoring), Beat 6 (SSE, server-side payability gate, tests, offline replay) | "Same evidence, same score, every time." |
| Commerce Impact | 15% | Beat 4 ($194.50 savings, cheapest *trusted*), Beat 5 (full mandate-to-receipt path, shareable receipt) | Say the savings number out loud. |
| Trust & Responsibility | 15% | Beat 3 (no model scoring, skipped is not safe), Beat 5 (sandbox label, spending cap, human passkey), Beat 6 (server refusal, no PII) | Say "sandbox" (payment only), "fictional" (the villain store), and "the model never scores" at least once each. |

## Production notes

- **Roles on screen:** C drives the browser for Beats 1, 2, 4, 5 and the final shot. B and A narrate over C's screen. Record voice separately if you can and sync it, so the clicks are never rushed by the talking.
- **Two takes of the UI, one take of the voice:** record the screen cleanly once at a comfortable speed, then record voiceover while watching it. Trim to 3:00.
- **Name the staged part out loud:** the transition line in Beat 3 tells judges the villain is a staged fictional store. Teams that name what is staged are trusted more on everything else.
- **Name check before you publish:** the README and Devpost say **Sykes + Visa**, while `CLAUDE.md`, `team-split-3.md`, and Fly say **Sniff**. Pick one for the video and the end card. This script uses Sykes.
- **Do not say or show:** a live Visa charge or production integration; "real cards"; that Gemini found the products (SerpAPI did); that all five checks ran live (see the real-vs-simulated table); a hosted URL (the Fly deployment serves an older build); MongoDB or VEYZL; "budget-filtered" in offline mode (it shows all nine for any answer); or a hard budget cap (D-022 says "closest match").
- **Keep the status line honest:** your `status.md` notes the villain-refusal click-through is not yet proven in the browser. That is why Beat 6 uses the passing test rather than a UI click. If you try the refusal in the UI before recording and it works, swap it in.
- **If something breaks mid-take:** live search can take up to about 22 seconds, then fails with `SEARCH_UNAVAILABLE` and a Start over button. Cut the wait in the edit, or say "live search is slow", not "it is broken". If the API dies, append `?mock=1` and the whole story finishes without it.
