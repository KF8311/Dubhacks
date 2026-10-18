---
title: Devpost technical claims (Person A → Person B)
type: handoff
updated: 2026-10-18
owner: A
---

# Devpost technical claims

> **Superseded in two places since 2026-10-17:** the track slate is now D-028, and the app is deployed on Vercel at `https://sykes.select`. The claim wording below is still the source of truth; the stale lines are corrected inline.

Paste these. Do not strengthen them. Every checkout and receipt line must keep the sandbox disclosure.

## Title / tagline

- **Title:** Sykes + Visa — the trust layer for agentic commerce
- **Tagline:** The AI shopping agent that investigates every listing, then only pays merchants it can verify.

## What is true in this repo

- Guided discovery: 2–3 clarifying questions. Gemini writes them when `GEMINI_API_KEY` is set (`gemini-3.5-flash-lite`); category templates on timeout, offline, or bad JSON. Session create never waits more than 2.5s.
- Search runs live on SerpAPI when `SERPAPI_KEY` is configured (D-021, D-025). In live mode it never falls back to the curated catalog: a failed search reports `SEARCH_UNAVAILABLE` instead. Claim "real Google Shopping listings" only after a deployed query reports `source: "serpapi"`; offline segments use the bundled catalog.
- Five trust checks per listing, run in parallel with timeouts: domain age, SSL, Safe Browsing / denylist, Reddit sentiment, page flags. Allowlisted merchants run the same five checks; the allowlist exempts them from the score floor (D-015, D-043).
- Score is deterministic Python (`failed = severity × 40`, `warning = severity × 15`, thresholds 70 / 40, coverage cap 69). The LLM never computes a score, never picks checks, never fetches URLs.
- Recommendation: cheapest listing with `trusted` and (`score ≥ 70` **or** allowlisted) and `confidence ≥ 0.6`. Demo pick: Target `lst_tgt_bsp` $179.99; median trusted $374.49; savings $194.50. Villain `premium-audio-deals.shop` is cheaper and `danger` (score 0, `LOCAL_DENYLIST`).
- Payability is server-side. Client sends only `session_id`, `listing_id`, and a cap. Checkout is refused unless `trusted`, score ≥ 70 (unless allowlisted), and (unless allowlisted) at least 3 checks completed.
- Checkout is a **sandbox**. Mandate → simulated passkey → one-time token (last4 `4242`) → HMAC-signed receipt. Every checkout and receipt says **“Sandbox — simulated Visa Intelligent Commerce flow.”** Do not claim a production Visa integration.
- No real PII, no real card numbers. Synthetic shoppers and merchants. The villain is fictional.
- SSE: one stream per session, monotonic `seq`, client dedupe, snapshot fallback. One Uvicorn worker; no global gzip.
- Money is integer cents until the UI.
- Gemini also writes the best-pick sentence and an on-demand check explanation. Templates if the call fails.
- Mongo is optional (`MONGODB_URI`). Without it the API still runs (in-memory); health is `200` with `status: degraded`, `db: unavailable`. The submitted deployment has Atlas connected: health returns `status: ok`, `db: ok`.

## Tracks (D-028, current)

- **Title:** Visa Reimagine Shopping
- **Sponsored (up to 3):** SideShift — Best Startup Idea, Cloudforce, Photon 2.0 (conditional on a real text round trip)
- **Non-sponsored:** MLH Gemini, MLH MongoDB Atlas, MLH DEV Writing, DubHacks NEXT, MLH Commit Fellowship
- **Not selected:** VEYZL, T-Mobile, SpaceXAI, Perceptron

## How we built it (stack line)

React, Vite, TypeScript, Tailwind, FastAPI, Python, SSE, Gemini, catalog fixtures, mock Visa Intelligent Commerce, optional MongoDB.

## What’s mocked (say this out loud)

Sandbox Visa Intelligent Commerce. Simulated passkey. Catalog search, not live Google Shopping. Gemini is optional polish; trust and payment decisions are Python.

## Do not claim

- Production Visa Token Service / Payment Passkey
- Live SerpAPI results unless a key is in the deployed env and a query was proven
- That the trust score comes from Gemini
- Real cards, real shoppers, or a real `premium-audio-deals.shop` incident

## Judge one-liners

- **Visa:** The agent can only pay a merchant it can verify.
- **Gemini:** Gemini asks and explains; the score stays deterministic Python.
- **Score vs vibe:** `severity × 40` failed, `severity × 15` warning; identical inputs → identical score.
- **Did you use real Visa APIs?** We prototyped the Intelligent Commerce *flow* in sandbox. We are explicit about that on every checkout and receipt.
