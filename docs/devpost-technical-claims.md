---
title: Devpost technical claims (Person A → Person B)
type: handoff
updated: 2026-10-17
owner: A
---

# Devpost technical claims

Paste these. Do not strengthen them. Every checkout and receipt line must keep the sandbox disclosure.

## Title / tagline

- **Title:** Sniff + Visa — the trust layer for agentic commerce
- **Tagline:** The AI shopping agent that investigates every listing, then only pays merchants it can verify.

## What is true in this repo

- Guided discovery: 2–3 clarifying questions. Gemini writes them when `GEMINI_API_KEY` is set (`gemini-3.5-flash-lite`); category templates on timeout, offline, or bad JSON. Session create never waits more than 2.5s.
- Search is catalog-only in the demo: no `SERPAPI_KEY` is set on the deploy (D-011). D-021 adds a live SerpAPI path that infers the merchant domain from Google Shopping's `source`; it is untested against a real key, so do not claim live search unless the spike has been run.
- Five trust checks per listing, run in parallel with timeouts: domain age, SSL, Safe Browsing / denylist, Reddit sentiment, page flags. Allowlisted merchants skip checks and score `0` with verdict `trusted`.
- Score is deterministic Python (`failed = severity × 40`, `warning = severity × 15`, thresholds 70 / 40, coverage cap 69). The LLM never computes a score, never picks checks, never fetches URLs.
- Recommendation: cheapest listing with `trusted` and (`score ≥ 70` **or** allowlisted) and `confidence ≥ 0.6`. Demo pick: Target `lst_tgt_bsp` $179.99; median trusted $374.49; savings $194.50. Villain `premium-audio-deals.shop` is cheaper and `danger` (score 0, `LOCAL_DENYLIST`).
- Payability is server-side. Client sends only `session_id`, `listing_id`, and a cap. Checkout is refused unless `trusted`, score ≥ 70 (unless allowlisted), and (unless allowlisted) at least 3 checks completed.
- Checkout is a **sandbox**. Mandate → simulated passkey → one-time token (last4 `4242`) → HMAC-signed receipt. Every checkout and receipt says **“Sandbox — simulated Visa Intelligent Commerce flow.”** Do not claim a production Visa integration.
- No real PII, no real card numbers. Synthetic shoppers and merchants. The villain is fictional.
- SSE: one stream per session, monotonic `seq`, client dedupe, snapshot fallback. One Uvicorn worker; no global gzip.
- Money is integer cents until the UI.
- Gemini also writes the best-pick sentence and an on-demand check explanation. Templates if the call fails.
- Mongo is optional (`MONGODB_URI`). Without it the API still runs (in-memory); health is `200` with `status: degraded`, `db: unavailable`.

## Tracks (recommended)

- **Title:** Visa Reimagine Shopping
- **Sponsored (up to 3):** T-Mobile Cart Whisperer, SideShift, VEYZL
- **Non-sponsored:** DubHacks NEXT, MLH Gemini, MongoDB (only if Atlas is actually used in the demo)

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
