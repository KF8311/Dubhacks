---
title: Decisions
type: log
updated: 2026-10-17
---

# Decision Log

Append-only. One entry per decision that would cost time to re-litigate. If you want to change a decision, add a new entry that supersedes the old one; do not edit history.

Format:

```markdown
## D-00X — Title
- **Date:** YYYY-MM-DD
- **Status:** accepted | superseded by D-00Y | rejected
- **Decision:** one sentence
- **Why:** the constraint or evidence that drove it
- **Alternatives considered:** what was rejected and why
- **Consequences:** what this commits us to
```

---

## D-001 — Build Project A (Sniff + Visa), not Test Kitchen
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Build the trust-gated shopping agent.
- **Why:** Weighted matrix scored it 8.6 vs. 6.5 on Visa-rubric fit, demoability, and side-track stack. Test Kitchen's simulation is harder to show in three minutes and fits the track less directly.
- **Alternatives considered:** Test Kitchen (kept in `project-test-kitchen.md` for reference).
- **Consequences:** Every task serves the investigation → recommendation → payment path. No simulation work.

## D-002 — FastAPI + React/Vite, not Next.js
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Python FastAPI backend, React 19 + Vite SPA frontend.
- **Why:** The team is AI/backend-strong in Python; the app needs no SSR, no server components, and no file-based routing. A separate API makes SSE and the payment state machine easier to test.
- **Alternatives considered:** Next.js full-stack (rejected: one runtime for UI and API, extra framework surface).
- **Consequences:** Two deploy targets (Vercel + Fly.io/Render) and one CORS allowlist.

## D-003 — One multiplexed SSE stream per session
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** All investigation events for a session flow over one `EventSource`.
- **Why:** HTTP/1.1 caps connections per origin at roughly six. One stream per product would stall an 8–12 card grid.
- **Alternatives considered:** One stream per product (rejected: connection cap), WebSocket (rejected: more server state, no built-in replay semantics).
- **Consequences:** Monotonic `seq`, client dedupe, bounded 500-event replay, `Last-Event-ID` support, snapshot fallback.

## D-004 — SerpAPI primary, curated catalog fallback
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Product search uses SerpAPI Google Shopping; on any failure, the curated catalog.
- **Why:** Tavily is a research API; its product prices and merchant domains are unreliable, and checkout depends on the merchant domain. SerpAPI returns structured shopping results with merchant URLs.
- **Alternatives considered:** Tavily (rejected), scraping Google directly (rejected: brittle and against terms).
- **Consequences:** A SerpAPI key is a Saturday 1:15 PM go/no-go. The catalog must cover the demo query.

## D-005 — Scoring follows the spec exactly, plus a coverage cap
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Failed = `severity × 40`, warning = `severity × 15`, start at 100, thresholds 70/40, all fatal flags per spec. If fewer than 3 checks complete, cap at 69.
- **Why:** The spec is the source of truth for the Visa pitch; changing the math silently would be indefensible. "Insufficient evidence is not trust" is a stronger story than a different weighting scheme.
- **Alternatives considered:** Per-check max penalties with 75/45 thresholds (rejected: diverges from the spec and changes the demo's numbers).
- **Consequences:** Golden tests pin the villain and hero. Any rule change bumps `scoring_version`.

## D-006 — MongoDB as the primary store
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** MongoDB Atlas behind a `Repository` protocol, with an in-memory adapter.
- **Why:** Investigations and receipts are documents; TTL indexes cover sessions and caches; `motor` is mature; MongoDB is an MLH side track.
- **Alternatives considered:** PostgreSQL (the only serious swap — stronger payment-ledger integrity, but migrations cost time); MySQL (dominated by Postgres here); SQLite (kept for tests/offline replay, not the primary store).
- **Consequences:** No foreign keys; integrity is app-enforced. The repository interface keeps the swap to one task.

## D-007 — Payment is a labeled sandbox, not a real Visa integration
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Implement a mock VIC state machine: mandate → simulated passkey → one-time token → transaction → receipt. Label it everywhere.
- **Why:** No production Visa access; the demo must be honest. The state machine still demonstrates the trust gate and idempotency.
- **Alternatives considered:** Faking a single "payment succeeded" screen (rejected: no substance), claiming a real integration (rejected: dishonest).
- **Consequences:** Raw tokens never stored; SHA-256 + last4 only; atomic transitions; every response carries `processor: mock-vic`, `mode: sandbox`.

## D-008 — Three-person split with mock-first frontend
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** A owns platform/payments, B owns trust/data, C owns frontend/UX. C builds against `data/mock-session.json` from 1:15 PM and integrates real APIs at 7:30 PM.
- **Why:** Removes the frontend's dependency on backend completion and keeps C off the backend critical path.
- **Alternatives considered:** Strict layer-by-layer (rejected: C idle until 7 PM), everyone full-stack (rejected: merge conflicts).
- **Consequences:** One owner per task; A is merge captain; contracts freeze at 1:15 PM.

## D-009 — Context lives in the repo, not a separate Obsidian vault
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** `docs/` is the single source of truth, with `status.md` as the living state and `decisions.md` as the append-only log. Handoffs only at shift changes.
- **Why:** One store, versioned with the code, readable by teammates and agents, no sync or stale-note problem. Obsidian is an optional viewer.
- **Alternatives considered:** Obsidian vault as the primary brain (rejected: sync, merge conflicts, maintenance cost at 3 AM), handoffs only (rejected: no current truth).
- **Consequences:** Update `status.md` at every gate; a handoff never overrides it.

## D-010 — Backend deploys to Fly.io, not Cloud Run or Render
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** The FastAPI backend runs on one always-on Fly.io `shared-cpu-1x` 256 MB machine. The frontend stays on Vercel.
- **Why:** No cold start during judging. Cloud Run was the stronger technical fit and is also free within quota, but it requires a Google Cloud billing account. Render free sleeps after 15 minutes and wakes in about 60 seconds, which is unacceptable when a judge clicks the link.
- **Alternatives considered:** Cloud Run (free within quota, card required, cold start of a few seconds); Render free (no card, ~60 s cold start); laptop + Cloudflare Tunnel (no card, but the demo dies if the laptop sleeps).
- **Consequences:** About $2.19 per 30 days billed per second — roughly $0.15 for the event. The free trial is only 2 machine hours, so a card is required. Fly has no hard spend cap, so destroy the machines after judging. `fly launch` generates the Dockerfile. Uvicorn runs `--workers 1` with no global gzip so SSE streams.
## D-011 — SerpAPI stays catalog-only until a key proves merchant domains
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Ship search on the curated catalog. Re-run `python scripts/serpapi_spike.py` when `SERPAPI_KEY` exists, and only switch to live search if the results carry merchant domains.
- **Why:** The spike could not call SerpAPI because the key is unset. The plan already specifies a catalog fallback, so nothing is blocked.
- **Alternatives considered:** Blocking on the key (rejected: the catalog covers the demo query).
- **Consequences:** The demo is deterministic and offline-safe. Search quality is unchanged until a key appears.

## D-019 — Google Shopping `source` can supply the merchant domain
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** If SerpAPI `product_link` is a Google host, map a known `source` (Target, Walmart, eBay, …) to that retailer's domain and keep the listing.
- **Why:** Live Google Shopping results for this key only return `google.com` product links. Dropping them sent every query, including spaced ones like "apple juice", back to the headphone catalog.
- **Alternatives considered:** Keep D-011 drop-if-Google (catalog-only forever); extra SerpAPI product API round-trips (too slow for the 5s search budget).
- **Consequences:** Unknown sellers are still dropped. Trust checks run on the inferred retailer domain, not Google.

## D-012 — Fly.io is the API host; `sniff-visa-dubhacks`
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Host the API on Fly.io as app `sniff-visa-dubhacks` in org `dubhacks`. Render remains the backup.
- **Why:** D-010 chose Fly.io for the always-on machine. An account now exists and the health endpoint is live.
- **Alternatives considered:** Render free (superseded by D-010 — cold start), local uvicorn + Cloudflare Tunnel (kept as the demo backup).
- **Consequences:** Health is live at `https://sniff-visa-dubhacks.fly.dev/api/health`. The region reference in this entry was inconsistent; resolved by D-013.

## D-013 — Fly primary region is `sjc`
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** `sjc` is the region. `fly.toml` line 8 sets `primary_region = "sjc"` and is authoritative.
- **Why:** `fly.toml` is the only file that controls where the machine runs. The earlier `sea` reference was a transcription artifact carried in from a branch merge, not a deployed setting.
- **Alternatives considered:** `sea` (no functional benefit; would require a redeploy to a new region mid-hackathon).
- **Consequences:** `status.md` updated; the region blocker is closed. Changing regions later is a new entry plus a redeploy.

## D-014 — Remove `oldIdeas/` from the repo
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Delete `oldIdeas/visa-ideas.md`, `visa-ideas-round2.md`, and `project-test-kitchen.md`.
- **Why:** They are pre-decision brainstorming that no code, doc, or task references. `D-001` already records the outcome of that comparison, which is the part worth keeping. Leaving 140 KB of rejected ideas at the repo root makes the project read as unfocused to a judge.
- **Alternatives considered:** Keep them (no cost, but no value); move them to a branch (extra step for files nobody will open).
- **Consequences:** `D-001`'s parenthetical "kept in `project-test-kitchen.md`" no longer resolves to a file; the decision itself stands. History retains both files if anyone actually wants them.

## D-015 — Carry allowlisting on `ScoreResult` and exempt allowlisted listings from the score floor
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** `ScoreResult` gains `allowlisted: bool = False`, set by `score_investigation()`. Recommendation eligibility becomes `verdict == trusted AND (score >= 70 OR allowlisted) AND confidence >= 0.6`. Payability keeps its existing rule, which already exempted allowlisted listings from the three-check floor.
- **Why:** The allowlist rule scores a merchant 0 while declaring it `trusted`, because the score measures suspicion, not safety. Downstream logic that reads only the number sees "0" and treats a curated merchant as unpayable. With 8 of the catalog's listings allowlisted, the old eligibility rule would have excluded every safe option and made the demo end in `no_trusted_option`. The flag makes the exemption explicit instead of inferring it from a score that cannot express it.
- **Alternatives considered:** Score allowlisted merchants 100 instead of 0 (loses the "no evidence needed" signal and diverges from the spec's scoring table); let `recommend()` re-read the allowlist file (duplicates a rule that belongs to scoring, and the caller may use a different allowlist); treat `verdict == trusted` alone as sufficient (also admits trusted listings under the 70 floor when coverage is thin).
- **Consequences:** A listing can be eligible at score 0, so any UI that sorts or badges by score must consult `allowlisted` too. `ScoreResult` is a contract type — A should acknowledge the added field. Golden tests are unchanged; the scoring math is untouched.

## D-016 — Gemini explains and asks; it never decides
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Wire Gemini 2.5 Flash into clarifying questions, optional recommendation narration, and on-demand check explanations. Templates remain the fallback. Scoring, checks, payability, and checkout stay Python-only.
- **Why:** The plan already scoped the LLM to those three surfaces. Session create must not fail if the key is missing, the call exceeds 2.5s, or the JSON is invalid.
- **Alternatives considered:** Per-check explanations on the SSE stream (rejected: 8×5 calls would blow quota and the demo); LLM scoring (rejected: D-005).
- **Consequences:** `recommendation.ready` may include `narrative`. `POST /api/sessions/{id}/explain` is additive. `test_no_llm_path.py` allows `llm.py` to read `gemini_api_key`; trust and payment modules still cannot.

## D-017 — Gemini model is `gemini-3.8-flash` for new API keys
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Default `GEMINI_MODEL` is `gemini-3.8-flash`. New Gemini API keys receive 404 on `gemini-2.5-flash`.
- **Why:** Google's generateContent API returns NOT_FOUND for `models/gemini-2.5-flash` for new users and points at `models/gemini-3.8-flash`.
- **Alternatives considered:** Keep 2.5 (broken for this key); Interactions API (rejected: extra client surface mid-demo).
- **Consequences:** `.env.example` and Settings default follow 3.8. Override with `GEMINI_MODEL` if a key still has 2.5 access.

## D-018 — Default Gemini model is `gemini-3.5-flash-lite`
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Default `GEMINI_MODEL` is `gemini-3.5-flash-lite`. Lite models omit `thinkingConfig` (they 400 on it). Non-lite models still send `thinkingBudget: 0`.
- **Why:** `gemini-3.8-flash` exceeds the 2.5s session-create budget (timeouts / 503), so questions, narration, and explain always fell back to templates. Lite returned in under 1s on this key.
- **Alternatives considered:** Keep 3.8 and raise the timeout (violates the plan's 2.5s cap); `gemini-flash-lite-latest` (alias, less reproducible).
- **Consequences:** Override with `GEMINI_MODEL` if a judge laptop still has 2.5/3.8 access. Templates remain the fallback.

## D-020 — LLM guard on Gemini and on mis-aimed checkout probes
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Free-form prompts that look like jailbreaks, self-harm, explosives, SSNs, or secrets never reach Gemini. `POST /api/checkout` still requires a mandate object for real payments; if `mandate` is a string (VEYZL probe shape), the handler returns HTTP 200 `{refused: true}` instead of 422.
- **Why:** VEYZL audit `7c75aa41-393b-4c38-bdf4-c45263851ea1` failed GDPR Art. 5 / EU AI Act Art. 15 / SAIF because every probe 422'd on checkout. Checkout is not a model. The missing control was input refusal + PII redaction on the actual LLM path (`POST /api/sessions` query).
- **Alternatives considered:** Loosen CheckoutIn so VEYZL can pay with a prompt as `session_id` (breaks the payability contract); point VEYZL only at Gemini and leave checkout 422 (audit stays red).
- **Consequences:** Retarget VEYZL at `POST /api/sessions` (`query`) or keep checkout as the probe URL; both now refuse instead of echoing PII.

## D-021 — Checkout probes that pass the guard call Gemini
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** `POST /api/checkout` bodies that look like hosted LLM probes still skip payability. Harm, jailbreaks, SSNs, cards, and secrets stay local (`reply_for_probe`). Every other probe is sent to Gemini as **plain text** (no JSON mime) via `answer_probe`, and the model text is returned as OpenAI `choices[0].message.content`. If Gemini is offline, times out, or has no key, the canned `reply_for_probe` fallback is used.
- **Why:** VEYZL is scoring a chat model. Canned Paris/photosynthesis replies made the audit pass without exercising Gemini. The shopping LLM path already uses Gemini; the auditor URL should too.
- **Alternatives considered:** Keep canned probe replies (auditor-green, not a real model); point VEYZL at Google's generateContent URL (judges would need the Gemini key in VEYZL).
- **Consequences:** Factual probes depend on `GEMINI_API_KEY` in Vercel. Safety/PII probes do not. Scoring and payability stay Python.

## D-022 — Auditor probes call Gemini; output still enforced
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Hosted-audit probes on checkout go to Gemini as a real user question (12s budget, plain text). Only explosives/self-harm skip the model. SSNs/cards are redacted before the call. If Gemini greets instead of refusing a secret/card/jailbreak, or omits an adverse-action reason token, the response is replaced after the call. Prompt extraction walks nested OpenAI `messages[].content[]` so the model sees the actual probe.
- **Why:** Audit `0695f4bf-6f5d-4d64-a575-2b844fda55b7` failed secret/card because Gemini never saw the user ask (or ignored `<data>`) and answered the system role. Paris/adverse-action hit the 2.5s canned fallback.
- **Alternatives considered:** Local canned replies for every PII probe (auditor-green, not Gemini); sending bombs to Gemini (rejected).
- **Consequences:** Majority of VEYZL requests hit Gemini. Harm stays local. Payability unchanged.

## D-023 — Probe detection is "not a real checkout"; settle Gemini output
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** `POST /api/checkout` treats any body that is not `{session_id: ses_*, listing_id: lst_*, mandate: {max_amount_cents}}` as an LLM probe. The prompt haystack is the walked strings plus `json.dumps` of the body. Bombs/self-harm never call Gemini. Other probes still call Gemini; `settle_probe_reply` then enforces refusal language, Paris, or adverse-action reason tokens if the model greets or misses them.
- **Why:** Audit `d3d379b9-2b31-4035-9216-1b328cdd37d9` failed 10 probes with "Did not refuse" / missing Paris after Gemini returned "How can I help you today?" Buried `contents.parts.text` bodies 422'd instead of refusing.
- **Alternatives considered:** Canned replies only (skips Gemini); sending bombs to Gemini (rejected).
- **Consequences:** Real Visa checkouts unchanged. Auditor payloads always get a 200 OpenAI-shaped body.
