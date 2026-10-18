---
title: Devpost draft
type: submission
updated: 2026-10-17
owner: B
---

# Devpost — Sykes + Visa

> **Status:** draft. Placeholders in `[BRACKETS]` are filled after the live URL, screenshots, and video land. Nothing in this document may claim a Visa production integration, real card data, or a model-authored score.

## Title

**Sykes + Visa — the trust layer for agentic commerce**

## Tagline

The AI shopping agent that investigates every listing, then only pays merchants it can verify.

## Track

Visa — **Reimagine Shopping**

## Inspiration

Online shopping fraud is massive and invisible. Shoppers cannot check WHOIS records or threat databases; they guess from a photo and a price. Agentic commerce makes the problem worse, not better: an AI can now spend your money, and it has no concept of trust.

Every shopping agent demo we had seen optimised for *finding* the product. None of them answered the question a payment actually requires: **should this agent be allowed to pay this merchant at all?**

## What it does

- **Guided discovery.** Three questions (budget, use, priority) become a structured search.
- **Multi-listing search.** Nine listings across eight merchants, including one deliberately hostile store.
- **Five parallel fraud checks per listing, streamed live.** Domain age via RDAP/WHOIS, TLS certificate validity, threat-list reputation, community sentiment, and scam-pattern page analysis.
- **A 0–100 trust score** and a `trusted` / `caution` / `danger` verdict, computed by observable arithmetic — not a model.
- **The cheapest trusted recommendation**, with the median trusted price and the saving so the user can see the trade-off.
- **A Visa checkout** with a human-readable spending mandate, a passkey confirmation, a one-time token, and a signed receipt.
- **A shareable trust receipt** at `/r/{share_id}` that carries the score, the checks, and what could *not* be verified.

The closing beat: the agent reaches for the cheapest listing, refuses it, and explains why. In the demo, the villain is $30 cheaper than the pick and is disqualified on four independent signals.

## How we built it

**Frontend** — React 19 + TypeScript + Vite, Tailwind, shadcn-style components, Zustand for session state, and a native `EventSource` client with sequence-number dedupe and snapshot fallback. The checkout sheet is a four-step flow (review → mandate → passkey → receipt).

**Backend** — FastAPI + Pydantic v2, one Uvicorn worker (SSE forbids more), one SSE stream per session with monotonic `seq` and `Last-Event-ID` replay.

**The checks** are ordinary Python with hard timeouts and bounded concurrency (8 at a time, 14-second budget per session):

| Check | Implementation |
|---|---|
| Domain age | RDAP first, WHOIS fallback; a 12-day domain is a fatal signal |
| SSL | Live TLS handshake, hostname match, issuer, expiry |
| Safe Browsing | Google Safe Browsing when a key exists; a static denylist otherwise, always labelled `unavailable` when it is the static list |
| Reddit sentiment | Public JSON, classified into scam report / neutral / positive |
| Page flags | Server-side fetch, parsed for urgency copy, crypto-only payment, missing return policy, and countdown language |

**The scoring is arithmetic, deliberately.**

```
score = 100 − Σ penalties
  failed  → round(severity × 40)
  warning → round(severity × 15)
trusted ≥ 70 · caution ≥ 40 · danger < 40
fewer than 3 completed checks → score capped at 69
```

**The score is deterministic, and a model never decides anything.** Gemini Flash Lite writes the clarifying questions, the recommendation narration, and on-demand check explanations — each call capped at 2.5 seconds and falling back to a template. It never scores, never selects checks, and never sees a verdict it can change. Scoring, checks, payability, and checkout are Python-only, and a build test fails if any trust, check, or payment module imports the LLM. This was a deliberate trade: a trust score you cannot re-derive from evidence is not a trust score, and judges — like users — should be able to check the math.

**The payment is a sandboxed Visa Intelligent Commerce flow.** Mandate → passkey → token → transaction → receipt, with the same state machine and idempotency a real integration needs, and visible honesty about what is simulated.

## The trust gate (the core of the product)

Checkout is refused server-side — not just disabled in the UI — unless the listing is `trusted`, scores ≥ 70, has at least three completed checks, matches the mandate's merchant, stays under the cap, and has an investigation less than 30 minutes old. Every refusal carries a machine-readable code and a human reason.

The client sends **only** a session id, a listing id, and a cap. It never sends a verdict, a score, or a price. The server re-derives all of them.

## Challenges

- **Making five network-dependent checks fast and reliable in 21 hours.** The answer was per-check timeouts, bounded concurrency, and a rule that a check that cannot run is `skipped`, never `passed`.
- **Keeping skipped from looking safe.** The UI renders `skipped` as "Could not verify", and missing checks cap the score below the payability floor. Insufficient evidence is not trust.
- **A deterministic score with honest explanation.** We dropped the LLM from the scoring path entirely and wrote the reasons from the evidence the checks emitted.
- **A payment flow that feels real without production access.** We mocked the network and kept the controls: mandates, idempotency, single-use tokens, signed receipts, and a visible sandbox label on every surface.
- **A demo that cannot drift.** A replay script runs the whole session in-process with no server and no network and exits non-zero if the numbers change.

## Accomplishments

- A live investigation the user watches happen, rather than a loading spinner.
- A score anyone can audit: every deduction names the check and the evidence.
- A payment moment that puts the human in the loop with a passkey.
- A receipt that turns a private checkout into a public trust signal.
- A test suite that treats the demo script as a contract: **231 backend and 49 frontend tests**, plus an offline replay that must reproduce the live numbers exactly.

## What we learned

- **Trust is a UX problem, not only a security problem.** The valuable output is not "score 0" — it is "here is the four-item reason, and here is what we could not check."
- **Deterministic scoring plus evidence beats a model that sounds confident.** Judges and users both asked "how do you know?" — and we could show them.
- **The demo needs a villain and a hero.** One scam store and one safe pick turn an abstract trust system into a story with a decision in it.
- **Skipped is the hard case.** Most trust products quietly treat missing data as neutral. Ours refuses to.

## What's next

- Real Visa Intelligent Commerce integration against the Token Service and Payment Passkey APIs.
- A browser extension that scores the page you are already on.
- A merchant verification dashboard for the allowlist.
- More signals: seller history, price history, counterfeit detection, and a persisted audit trail.

## Built with

`python` · `fastapi` · `pydantic` · `uvicorn` · `httpx` · `beautifulsoup4` · `python-whois` · `pytest`
`react` · `typescript` · `vite` · `tailwindcss` · `zustand` · `vitest`
`gemini` · `mongodb`

## Sandbox disclosure (required copy — keep it visible)

> **Sandbox — simulated Visa Intelligent Commerce flow.** This is a prototype. The payment is mocked; there is no Visa production integration, no real merchant, and no real card data. All shoppers, merchants, and card numbers are synthetic. The score is computed deterministically from public evidence, not by a language model.

## Fill before submitting

- [ ] `[LIVE URL]` — the Fly app after A's redeploy
- [ ] `[REPO URL]`
- [ ] `[VIDEO]` — the 3-minute path: question → stream → villain → pick → refusal → receipt
- [ ] `[SCREENSHOT: results grid]`, `[SCREENSHOT: danger detail]`, `[SCREENSHOT: receipt]`
- [ ] A's review pass on every technical claim
- [ ] Confirm the numbers still match `scripts/replay_offline.py`
