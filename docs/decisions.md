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
- **Status:** superseded by D-021
- **Decision:** Ship search on the curated catalog. Re-run `python scripts/serpapi_spike.py` when `SERPAPI_KEY` exists, and only switch to live search if the results carry merchant domains.
- **Why:** The spike could not call SerpAPI because the key was unset. The plan already specifies a catalog fallback, so nothing is blocked.
- **Alternatives considered:** Blocking on the key (rejected: the catalog covers the demo query).
- **Consequences:** The demo is deterministic and offline-safe. Search quality is unchanged until a key appears.

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

## D-016 — Mongo (Task 27) moves from A to B; the Block 6 slot does not move
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Task 27 (`MongoRepository`, TTL indexes, caches, audit, redaction) is owned by **B**. The work stays where it already sits on the calendar — B's 10:30 PM–2:00 AM block, inside Block 6 — so no block, gate, or deliverable changes for anyone else.
- **Why:** A does not want to take on MongoDB, and B already owns persistence-adjacent work: the `Repository` protocol shape, fixture data, redaction rules, and the offline replay that must keep working with `MONGODB_URI` unset. Ownership was the only thing out of place; the schedule was not.
- **Alternatives considered:** Drop Task 27 and stay in-memory only (loses the MLH MongoDB track and the "investigations and receipts are documents" story in D-006); move it to C (C is the critical path on G4/G5); assign it to A anyway (the owner has said no, and a half-owned task is worse than a deferred one).
- **Consequences:** Block 5 is unchanged — nobody starts Mongo work until Block 6. The in-memory adapter remains the default and the cut-order survivor; Mongo stays a swap behind the existing protocol. B owns the Atlas cluster question in `docs/open-questions.md`.

## D-017 — Gemini explains and asks; it never decides
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Wire Gemini into clarifying questions, optional recommendation narration, and on-demand check explanations (model fixed by D-019). Templates remain the fallback. Scoring, checks, payability, and checkout stay Python-only.
- **Why:** The plan already scoped the LLM to those three surfaces. Session create must not fail if the key is missing, the call exceeds 2.5s, or the JSON is invalid.
- **Alternatives considered:** Per-check explanations on the SSE stream (rejected: 8×5 calls would blow quota and the demo); LLM scoring (rejected: D-005).
- **Consequences:** `recommendation.ready` may include `narrative`. `POST /api/sessions/{id}/explain` is additive. `test_no_llm_path.py` allows `llm.py` to read `gemini_api_key`; trust and payment modules still cannot.

## D-018 — Gemini model is `gemini-3.8-flash` for new API keys
- **Date:** 2026-10-17
- **Status:** superseded by D-019
- **Decision:** Default `GEMINI_MODEL` is `gemini-3.8-flash`. New Gemini API keys receive 404 on `gemini-2.5-flash`.
- **Why:** Google's generateContent API returns NOT_FOUND for `models/gemini-2.5-flash` for new users and points at `models/gemini-3.8-flash`.
- **Alternatives considered:** Keep 2.5 (broken for this key); Interactions API (rejected: extra client surface mid-demo).
- **Consequences:** `.env.example` and Settings default follow 3.8. Override with `GEMINI_MODEL` if a key still has 2.5 access.

## D-019 — Default Gemini model is `gemini-3.5-flash-lite`
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Default `GEMINI_MODEL` is `gemini-3.5-flash-lite`. Lite models omit `thinkingConfig` (they 400 on it). Non-lite models still send `thinkingBudget: 0`.
- **Why:** `gemini-3.8-flash` exceeds the 2.5s session-create budget (timeouts / 503), so questions, narration, and explain always fell back to templates. Lite returned in under 1s on this key.
- **Alternatives considered:** Keep 3.8 and raise the timeout (violates the plan's 2.5s cap); `gemini-flash-lite-latest` (alias, less reproducible).
- **Consequences:** Override with `GEMINI_MODEL` if a judge laptop still has 2.5/3.8 access. Templates remain the fallback.

## D-020 — VEYZL (Task 29) moves to A; B's scoping and reproduction carry over
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Task 29 is owned by **A**. B hands over the scope, the six candidate controls, the Devpost field map, and the reproduced `/api/demo/reset` transcript in `docs/veylz-audit.md`.
- **Why:** VEYZL is a GitHub App that must be installed on `KF8311/Dubhacks` and linked to a project in the vendor portal. That requires repo-admin rights, which A has and B does not. An audit task owned by someone who cannot install the app stalls at step one.
- **Alternatives considered:** B installs the app on a fork (the side track asks for the project repo; a fork weakens the evidence); keep it with B and have A act as installer only (splits one task across two people and leaves the fix PR ownerless).
- **Consequences:** A now owns the audit run, the fix PR, and `docs/veylz-audit.md`. B reviews the final finding and keeps the Devpost. No block or gate moves: the audit still fits Block 5/6, and the Devpost is still B's.

## D-021 — Google Shopping `source` can supply the merchant domain
- **Date:** 2026-10-17
- **Status:** accepted; supersedes D-011
- **Decision:** If the SerpAPI `product_link` is a Google host, map a known `source` (Target, Walmart, eBay, …) to that retailer's domain and keep the listing.
- **Why:** Live Google Shopping results for this key only return `google.com` product links. Dropping them sent every query, including spaced ones like "apple juice", back to the headphone catalog.
- **Alternatives considered:** Keep the D-011 drop-if-Google rule (catalog-only forever); extra SerpAPI product API round-trips (too slow for the 5 s search budget).
- **Consequences:** Unknown sellers are still dropped, and trust checks run on the inferred retailer domain, not on Google. Renumbered from D-019 on merge — that number already belonged to the Gemini model entry.
- **Follow-up:** Re-run `scripts/serpapi_spike.py` with a key and confirm the inferred domains match the retailer's real site before claiming live search in the Devpost. `SERPAPI_KEY` now reads the upper-case env name (also added in this merge).

## D-022 — A budget that matches nothing falls back to the full catalog
- **Date:** 2026-10-17
- **Status:** accepted with a caveat
- **Decision:** `_within_budget()` returns the unfiltered results when the budget filter matches nothing, instead of an empty grid.
- **Why:** Gemini's budget options can be grocery-scale while the demo catalog is headphones; an empty grid is a worse demo than a labelled over-budget listing.
- **Alternatives considered:** Keep the strict filter and show an empty state (honest, but the demo dead-ends on a plausible answer); raise the catalog prices (breaks the fixture numbers).
- **Consequences:** A listing above the stated budget can be recommended and paid, because the payability cap is the listing price, not the user's answer. Say "closest match" on stage, or add an over-budget badge before the demo. Do not describe the budget as a hard cap.
## D-023 — LLM guard on Gemini and on mis-aimed checkout probes
- **Date:** 2026-10-17
- **Status:** accepted
- **Decision:** Free-form prompts that look like jailbreaks, self-harm, explosives, SSNs, or secrets never reach Gemini. `POST /api/checkout` still requires a mandate object for real payments; if `mandate` is a string (VEYZL probe shape), the handler returns HTTP 200 `{refused: true}` instead of 422.
- **Why:** VEYZL audit `7c75aa41-393b-4c38-bdf4-c45263851ea1` failed GDPR Art. 5 / EU AI Act Art. 15 / SAIF because every probe 422'd on checkout. Checkout is not a model. The missing control was input refusal + PII redaction on the actual LLM path (`POST /api/sessions` query).
- **Alternatives considered:** Loosen CheckoutIn so VEYZL can pay with a prompt as `session_id` (breaks the payability contract); point VEYZL only at Gemini and leave checkout 422 (audit stays red).
- **Consequences:** Retarget VEYZL at `POST /api/sessions` (`query`) or keep checkout as the probe URL; both now refuse instead of echoing PII. Renumbered from D-020 on merge — that number already belonged to the VEYZL ownership decision.

## D-024 — Typed budget ranges set a floor and a ceiling
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** Free-text budget answers are parsed. A single number is a ceiling (`under 1200` → max $1200). Two numbers are a range (`1000 to 1200` → min $1000, max $1200). Live search sends `min_price`/`max_price` to SerpAPI. `_within_budget()` drops listings outside the band. D-022 unfilter still applies only to a ceiling-only filter that matches nothing (grocery-scale cap vs the headphone catalog).
- **Why:** Typing "1000 to 1200" was stored as `Answer.text` and ignored (`option_id` only). The remaining filter was max-only, so $200 computers still counted as in budget.
- **Alternatives considered:** Treat the first number as a max (still shows $200); keep D-022 unfilter on ranges (same $200 junk after a miss).
- **Consequences:** `SearchSpec.budget_min_cents` is additive. A typed range that matches nothing can yield an empty grid rather than cheap off-range listings. Preset `Under $150` / `$300–$600` chips are unchanged.

## D-025 — Live search waits, then fails honestly; it never swaps in the catalog
- **Date:** 2026-10-18
- **Status:** accepted; supersedes the catalog half of D-004 and D-011
- **Decision:** In live mode the orchestrator calls `search(..., allow_catalog_fallback=False)`. `SEARCH_S` is 11 s (was 5 s) and the SerpAPI client uses `SEARCH_S - 1` = 10 s. If both attempts fail, the session publishes `session.error` `SEARCH_UNAVAILABLE` (recoverable `false`), moves to the `failed` stage, and shows a retry — no catalog listings. Offline (`OFFLINE=1`) is unchanged and still uses the curated catalog.
- **Why:** A demo answer such as `$300-$600` adds price bounds to the SerpAPI request. When a cold request passed the old 4 s client timeout, the grid silently filled with unrelated headphone-catalog products. A longer spinner followed by "try again" is honest; unrelated products look like a bug on stage.
- **Alternatives considered:** Keep the catalog fallback but label it loudly (still shows products the user did not ask for); raise only the client timeout without changing the fallback (still swaps on failure); remove the retry (one transient SerpAPI fault would end the demo).
- **Consequences:** Worst case is two 11 s attempts (~22 s) before the failure state; warm queries return in under a second. `docs/RUN.md` and `docs/status.md` describe the new failure state. The service default remains `allow_catalog_fallback=True` for offline replay and unit tests.

## D-026 — Atlas round-trips are normalized to UTC and a pending checkout carries no idempotency key
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** `_hydrate()` attaches UTC to any naive datetime read back from Mongo, a freshly created `Checkout` stores `idempotency_key: null` (the model field is `str | None`) until `POST /confirm` supplies the client's key, and the Motor client uses `serverSelectionTimeoutMS=5000`.
- **Why:** The first real Atlas run failed twice. Confirm raised `TypeError: can't compare offset-naive and offset-aware datetimes` because BSON drops `tzinfo`, and the second checkout raised `E11000 duplicate key ... idempotency_key: ""` because the unique index is partial on strings and every pending checkout wrote an empty string. Neither bug can appear with the in-memory adapter.
- **Alternatives considered:** Set `tz_aware=True` on the client only (fixes reads but leaves the hydration contract implicit); change the partial filter to skip empty strings (Mongo rejects `$ne` in a partial filter, and `$gt: ""` would hide the real bug); use the checkout id as a placeholder key (the field would claim a client key that does not exist yet).
- **Consequences:** The partial unique index now matches its stated intent (ignore nulls, reject duplicate client keys). `scripts/smoke_http.py` sends `smoke-<checkout_id>` instead of a constant so repeat runs do not collide. Atlas is exercised end to end: health `db: ok`, checkout → confirm → public receipt, and the receipt still resolves after a backend restart. Sessions, listings, and investigations remain registry-only.

## D-027 — The payment path survives a restart: listings, investigations, and the token id are persisted
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** The orchestrator writes every listing and investigation from `replace_listings` / `attach_investigation` through to the repository. `_get_listing` resolves registry → repository → catalog, and `_get_investigation` resolves registry → repository, both async. `Checkout` carries a `token_id`; confirm reads it when the simulator's in-memory table is empty and calls `ensure_token()` to re-register the token, or refuses with `INVESTIGATION_STALE` when the checkout has no token at all.
- **Why:** With only the mandate, checkout, and receipt persisted, a checkout created before a restart could not be confirmed: the registry was empty, so the listing and investigation were missing, and `store.token_by_checkout[...]` raised `KeyError` and returned a 500. A restart is the exact evidence that the "Atlas-backed" claim is about a database and not a cache, so it must hold for the whole payment path, not half of it.
- **Alternatives considered:** Persist only the listing and investigation and re-issue a token at confirm (issues a second token for a checkout that already had one); keep the token in the `Checkout` document but 409 when the simulator forgot it (the sandbox simulator has no state worth protecting — the checkout record is the source of truth); rebuild the registry from Mongo on boot (a real fix, but a much larger change than the deadline allows, and it still leaves sessions unpersisted).
- **Consequences:** Confirming a checkout now costs up to three reads from Atlas when the registry is cold. Sessions stay registry-only, so you cannot *create* a checkout after a restart — you can only finish one you already started, which is what the demo needs. The in-memory adapter gains `get_listing` and `get_investigation_for` so tests do not silently diverge. Proof: `chk_dzr98nwVykDASG4L` → `rcp_ZSgCEO8uD7hwhCjs` across a real process restart, and an older checkout without a token returns 409 instead of 500.

## D-028 — The track slate: one title, three sponsored, five non-sponsored
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** Enter **Visa: Reimagine Shopping** as the only title track. Sponsored slots go to **SideShift — Best Startup Idea**, **Cloudforce**, and **Photon 2.0** *unless* a text round-trip fails to reach our backend, in which case the third slot stays empty. Non-sponsored: **MLH Best Use of Gemini API**, **MLH Best Use of MongoDB Atlas**, **MLH DEV Writing Challenge**, **DubHacks NEXT**, and the **MLH Commit Fellowship**. **VEYZL is not selected**, and neither are T-Mobile, SpaceXAI, or Perceptron.
- **Why:** Each entered track has evidence in the repo or a path to it inside the deadline. Gemini and Atlas are load-bearing code (D-017–D-019, D-026–D-027); the DEV article is written; SideShift charges nothing to enter and the startup paragraph is the same paragraph DubHacks NEXT asks for. T-Mobile wants wireless commerce we do not have, SpaceXAI requires Cursor and Grok we did not use, Perceptron's workshop closed, and VEYZL needs an installed app and an audit we cannot produce honestly. A conditional Photon slot is the only entry whose criterion is "did it actually work" — we claim it only with a round-trip, not with a project id.
- **Alternatives considered:** Enter VEYZL on the strength of the probe work (no audit, no install — the claim would be false); skip SideShift as "not a startup" (the entry costs nothing and the idea is genuinely monetizable); leave Photon out entirely (it is the only slot we can earn with 75 minutes of honest work).
- **Consequences:** Devpost gets exactly one title track and at most three sponsored. The SideShift paragraph in `docs/devpost.md` is the canonical pitch and doubles as the NEXT entry. If Photon slips, the slate is still complete with two sponsored tracks. Track checkboxes in `docs/devpost-form.md` record this slate; the Gemini and DEV entries stay unticked until the project number and the published URL exist.

## D-029 — Fly is the demo deploy; a personal Vercel account is the fallback
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** Deploy the app to Fly (`fly.toml`, backend + frontend, secrets set with `fly secrets set`) and submit that URL. If Fly cannot be provisioned before the submission window, deploy the existing root [`vercel.json`](../vercel.json) to a **personal** Vercel account — the config declares a `frontend` service and a `backend` service with `/api/(.*)` rewritten to the backend — or, if the services build fails, deploy `frontend/` alone with `VITE_API_BASE_URL` pointed at a reachable backend.
- **Why:** This machine has no Fly credentials, and the team's Vercel project is not accessible to the person holding the submission. The repo already carries a working Vercel config and `apiBase()` returns same-origin `/api` in production, so a personal account can host the same commit without code changes. Deploy is the last blocked gate; a fallback that is written down beats an undocumented improvisation at 09:00.
- **Alternatives considered:** Submit the existing (stale) Fly app (it serves removed code — not acceptable); run the demo from localhost only (Devpost requires a URL, and judges open it without us); spend the window fixing team Vercel access (not in our hands).
- **Consequences:** Whichever URL goes in the Devpost must serve this commit and pass `smoke_http.py`; `docs/status.md` names the live one. Vercel Services is a newer config shape and may reject the file, the FastAPI function is capped at 60 s, and SSE over serverless may buffer — the checklist marks those risks and T7 degrades to frontend-only. Fly stays the preferred target because the Docker image is already proven to serve the full path.

## D-030 — `product_url` is not a unique key; a store write can never freeze a session
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** Drop the unique index on `listings.product_url` and recreate it as a plain index; listings are keyed by `_id`. Both persistence writes in the orchestrator (`save_listing`, `save_investigation`) are best-effort: a failure is logged and the session continues from the registry.
- **Why:** Once every Google-hosted result pointed at the same Shopping results page (`/search?ibp=oshop&q=…`), the second `replace_one(..., upsert=True)` on a new `_id` hit `E11000 duplicate key ... product_url_1`. That exception propagated out of the fire-and-forget `_run` task, so the stage stayed `searching` forever with nine cards already in the registry — the UI looked like a load failure. Reproduced twice: create → answers → `searching` at 8 s, no progress at 170 s. Measured after the fix: **ready at 10.8 s**.
- **Alternatives considered:** Keep the unique index and store a per-listing token in the URL (re-introduces the `prds` token the user asked to drop, and it can resolve to a different product); catch only `DuplicateKeyError` in the orchestrator (the index stays a trap for the next shared-URL field); make the orchestrator await persistence before publishing listings (slower first paint and still dies).
- **Consequences:** `ensure_indexes` inspects `index_information()` on boot and drops a unique `product_url` index if an older build created one, so existing Atlas deployments migrate without manual steps. Losing a durable listing no longer loses the session, but a Mongo outage now degrades D-027's restart durability silently apart from a warning log — acceptable: the demo path is the registry, and an outage must not hang the screen.

## D-031 — Search is localized to Seattle
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** Every SerpAPI search sends `location=Seattle, Washington, United States`, `gl=us`, `hl=en`. The market is configurable with `SERPAPI_LOCATION`, `SERPAPI_GL`, and `SERPAPI_HL`.
- **Why:** Google Shopping prices and availability vary by market; a demo in Seattle that searches the default (often East Coast) market can show products nobody local can buy at that price. The user asked for a Seattle ZIP area.
- **Alternatives considered:** Append "Seattle" to the query string (changes what Google matches, not where it looks — worse results); use a raw ZIP (`uule` encoded) for street-level accuracy (precise location is not useful for shopping results and cannot be verified on stage).
- **Consequences:** Results now reflect Seattle-area stock and pricing. `location` is a SerpAPI parameter on `google_shopping`, verified live (`HTTP 200`, 9 listings, ready in 10.9 s). A slow or unavailable location lookup degrades into the existing honest `SEARCH_UNAVAILABLE`, not the catalog.

## D-032 — Google-hosted links use `udm=28`, not the legacy `ibp=oshop`
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** `_google_product_url` builds `https://www.google.com/search?udm=28&q=<query>`. The legacy `?ibp=oshop&q=…` form is no longer emitted.
- **Why:** The user reported the links "don't even load" in a browser. `ibp=oshop` is the parameter SerpAPI returns, but Google's shopping vertical is `udm=28` (a `tbm=shop` request redirects to it). Both answer `HTTP 200`, but only `udm=28` renders the results page.
- **Alternatives considered:** Keep `ibp=oshop` (blank page); use `tbm=shop` (Google immediately redirects it to `udm=28`, so it is the same destination with an extra hop); link straight to the retailer's search page (Walmart and Target bot-block requests we cannot verify, and per-merchant URL patterns are guesses).
- **Consequences:** Every Google-hosted result opens the current Shopping results page for the query, which lands on the top result for that listing's price. The `prds` token stays out of the URL. Verified live after a backend restart; the SerpAPI tests assert the new shape.

## D-033 — The texting agent answers with a pick first, then a refinement menu
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** In `dub-spectrum/src/index.ts` a text is a search: it is cleaned of polite framing, the session is created, answers are submitted empty (`skip_remaining: true`), and the reply is the top trusted pick plus a menu — 1 cheaper, 2 better quality, 3 something else, or `new: <product>`. Later texts refine the previous query unless they start with `new:`.
- **Why:** The first live text was a sentence ("hey can you find me …"), and the budget-first flow put that whole sentence into the Google query, so the results were unrelated. A shopper texting a line wants an answer, not a questionnaire; questions belong after a bad answer.
- **Alternatives considered:** Keep the clarifying question first (the user rejected it; it also doubles the round trips); run Gemini to extract a query (extra latency and a new failure mode for a job a regex does); treat every later text as a new search (loses the natural "cheaper" follow-up).
- **Consequences:** One text now produces a useful reply in ~10–15 s. A greeting ("hi", "test") is answered with "What are you shopping for?" instead of being searched. Refinements are appended to the query (`… cheaper`), so they stay inside the SerpAPI budget-in-query behavior that already works. 15 unit tests cover cleaning, greetings, and reply shapes.

## D-034 — Listings link to the merchant's own product page when SerpAPI names it
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** Each Google Shopping result carries a `serpapi_immersive_product_api` lookup. `SerpAPIProvider._enrich` fetches those concurrently (one per listing, capped at `IMMERSIVE_STORE_S = 3.5`), and `store_url_for_listing` swaps in a store's link only when the link's host equals the listing's `merchant_domain` after stripping `www.`. Anything else — a Google-hosted link, a marketplace reselling the item, a slow lookup — keeps the `udm=28` Google Shopping link.
- **Why:** The user asked whether a real product link was possible. It is: the immersive response lists every store selling that item with real URLs (for `TUL pens at Office Depot`, 8 of 9 listings got their own `officedepot.com`/`ebay.com` page, and the best pick linked straight to `https://www.officedepot.com/a/products/1310454/…`). Matching by merchant *name* would not do: a DoorDash store labelled "DoorDash - Office Depot" matched the Office Depot listing through `domain_from_source`'s substring loop and produced a doordash.com link under a merchant called Office Depot. Exact host equality is the only match that cannot mislabel a listing.
- **Alternatives considered:** Use the first store in the list (relabels every listing as whatever store Google ranks first); fuzzy-match names (the DoorDash bug above); fetch immersive for every result serially (5 s+ on cold lookups, measured); skip enrichment (honest Google links, no real product pages).
- **Consequences:** Search latency is bounded by the shopping call plus at most 3.5 s of concurrent lookups; measured **ready in 3.2–5.1 s** for `TUL pens at Office Depot` and warm lookups at 0.04–0.15 s each. `KNOWN_SOURCES` gains `office depot`, `staples`, and `jetpens` so those listings survive parsing in the first place. A listing whose merchant cannot be matched is still clickable — it just opens Google Shopping. Regression tests pin the DoorDash case and the unmatched-merchant fallback.

## D-035 — Product cards flip to their site stats
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** `ProductCard` renders a CSS 3D flip (`.flip-card` / `.flip-inner` / `.flip-face` in `index.css`) on hover or keyboard focus. The front is the existing listing card; the back shows the merchant and domain, the `TrustBadge`, `passed · warning · failed` counts, and the top reason — or "Checks are still running." while the investigation has not landed.
- **Why:** The user asked for each card to "turn over to show their site stats." The score and verdict already existed but were only legible inside the detail view or from the badge colour; the flip puts the tally on the grid without spending another click.
- **Alternatives considered:** A tooltip (unreachable on touch, no counts visible at a glance); a permanent second row (doubles card height and shrinks the grid); a modal (a click through to the detail view already exists).
- **Consequences:** The flip is disabled under `prefers-reduced-motion` and on `hover: none` devices, where both faces stay readable in normal flow. Focus-within makes it keyboard-reachable without a separate control. The back face is `pointer-events: none` until flipped so it cannot steal the card's click.

## D-036 — A checkout can be paid on a phone through its own link
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** `GET /api/checkout/{checkout_id}` returns a read-only summary (stage, amount, merchant, listing, trust snapshot, sandbox label, expiry, receipt URL). The mandate step of the checkout sheet shows `PhonePayLink`, which copies or shares `<origin>/pay/<checkout_id>`; `PayPage` reads that summary on the phone and calls the existing `POST /api/checkout/{id}/confirm`. The checkout id is the capability: no account, no second secret.
- **Why:** The user wanted to buy something found on a computer but pay on their phone without typing a card into the desktop. The browser never stores a card in either flow — the sandbox passkey is the only approval — so the phone becomes the trusted device and the desktop is just the catalog.
- **Alternatives considered:** QR code (new dependency; a copyable link is one line and works in a text message); e-mail the link (a mail service we do not have and do not want); a separate phone checkout session (duplicates the mandate and checkout the desktop already created).
- **Consequences:** In dev, `apiBase()` now uses `window.location.hostname` instead of hardcoding `localhost`, so a phone on the LAN reaches Uvicorn — Vite must run with `--host` and Uvicorn must bind `0.0.0.0`. The link expires with the mandate and the passkey is still required on the phone. Confirm is idempotent per checkout, so a double tap on the phone returns the same receipt.

## D-037 — An exhausted search plan is its own failure, and store lookups are cached
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** `SerpAPIProvider` raises `SearchQuotaExhausted` when a 429 body says the account is out of searches. `app.search.service` re-raises it instead of falling back to the catalog, and the orchestrator publishes `SEARCH_QUOTA_EXHAUSTED` on the first attempt without retrying. A successful merchant-page lookup is cached per listing id for the process lifetime; a miss is not cached.
- **Why:** The user reported that a search "ends that quick" with a failure. The log showed `429 Too Many Requests` and SerpAPI's body, "Your account has run out of searches." Both retry attempts came back in under a second because the provider rejects immediately — no amount of waiting produces results. The old path reported `SEARCH_UNAVAILABLE` ("taking too long"), which hid the one cause the user could fix. Separately, every immersive lookup is a priced SerpAPI search; the free plan (250/month) is spent by roughly 25 live queries at 10 searches each, so rehearing the demo must not repeat lookups.
- **Alternatives considered:** Retry the 429 a few times (a quota error never clears by waiting, and it delays the honest message); treat every 429 as quota (a rate limit is transient and should stay retryable); cache misses too (a later lookup may succeed, and a test double can produce a spurious empty response).
- **Consequences:** The failed state now reads "Live search quota is used up. Add a fresh search key, then start over." and arrives in ~0.2 s — the right speed for a permanent error. A repeated query that resolves all nine listings on the first run costs one search instead of ten while the process lives. The current key is at 0 searches (250 used in October), so live search fails for any query SerpAPI has not cached; a fresh key is required.

## D-038 — The questions can be skipped
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** The question screen gains a **Skip questions** action that submits the answers collected so far with `skip_remaining: true`. The backend already supported this flag; the UI did not expose it.
- **Why:** A budget answer rewrites the query (`TUL pens at Office Depot` becomes `… under $25`), which is a different SerpAPI search. With the free plan exhausted, only the exact cached query resolves, so the demo could not reach it through the UI. More broadly, a shopper who already knows what they want should not be forced through a questionnaire.
- **Alternatives considered:** Auto-skip when the provider is out of quota (the UI should not guess the provider's state); hide the budget question for Office Depot queries (a product-specific hack); default to skipping always (the questions genuinely improve matching and the text bridge already picks first).
- **Consequences:** The demo path is: type `TUL pens at Office Depot`, click **Skip questions**, and the cached live results arrive in ~2–3 s even with the quota exhausted. With a fresh key, both paths work.

## D-039 — The whole ticket flips, one card owns the marigold edge
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** The flip container now wraps the entire product ticket, merchant link included; the expanded detail card does not flip. Only the best pick (and only in the list, not the detail card) wears `ticket-best`; a selected non-best row gets a neutral `ticket-selected` ring, and `shelf-row:hover` lifts with a soft shadow instead of a marigold offset. Card rows shrink to a `size-12` thumbnail and tighter type. The checkout review gains a **Send to phone** action beside **Pay**; both create the same checkout, and the intended path puts `PhonePayLink` above the mandate card with the marigold wash. Buttons become pills and tickets move to `rounded-2xl`.
- **Why:** The user reported that the flip only turned the card body, that the top pick's orange edge also appeared on the two rows beneath it, and that there was no visible way to get the payment link to a phone. The marigold edge is the one bit of emphasis the grid has; spending it on the default-selected row and on every hovered row made the recommendation unclear. The phone link existed only after clicking Pay, below the mandate card, where it was easy to miss.
- **Alternatives considered:** Keep the flip on the body only (the link and checks live outside it, so the card never feels like one object); keep `isBest || selected` and differentiate with opacity (two visual languages for the same edge); put the phone link inside the mandate card (it is a different action from continuing the desktop passkey, and the mandate card is already dense); a QR code (a dependency and a camera step; the copy/share link is enough).
- **Consequences:** The merchant link is rendered on both faces — the back copy is `aria-hidden` and removed from the tab order — because a whole-card hover flip would otherwise hide the link the moment the pointer reached it. The flip turns on hover only; focus no longer flips the card, so the select button and link never rotate away from the keyboard user. On touch the flip stays disabled and the front face, link included, is the whole card. `PhonePayLink`'s URL still uses the page origin, so a phone on the LAN needs Vite `--host` and Uvicorn `0.0.0.0` (D-036).

## D-040 — Hover stays still, the verdict carries the color, and the pay text sends itself
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** Compact the product ticket (`size-10` thumbnail, `text-sm` title, `text-base` price, `p-2.5`, `rounded-3xl`). `.product-card` keeps a 3px left edge colored by verdict and a background tinted from the same verdict; hover swaps the background to the marigold wash and darkens the border, with **no transform, rotation, or lift**. The header brand, nav links, and buttons become pills. **Send to phone** creates the checkout and then posts the pay text to the local Spectrum bridge (`POST http://<page host>:8787/send`), which texts `Sykes checkout: … Approve with your passkey: <origin>/pay/<id>` to the conversation the shopper already texted (or `MY_PHONE` when set). The phone copy link appears only when sending fails, alongside the bridge's reason.
- **Why:** The user rejected the first restyle: cards still felt large, "every hover" made them move, the palette had not become more colorful, and copying a link from a computer to a phone is unrealistic when the bridge already has permission to message their number. Hover motion competed with the one deliberate motion in the grid (the flip), the verdict was legible only through a badge, and the send action still required the shopper to move a link across devices by hand.
- **Alternatives considered:** Keep a restrained lift on hover (the user asked explicitly for highlight or border instead); tint every card the same (loses the verdict information the left edge now carries); require the shopper to type a number into the browser (that would put PII in the page state and duplicate `MY_PHONE`); ask the bridge to guess the owner's number (the Spectrum SDK exposes no such lookup).
- **Consequences:** The bridge texts the last inbound conversation, so it is a single-shopper demo, not a general notifier. The target lives in `dub-spectrum/.last-space.json` (gitignored) or in `MY_PHONE` in `dub-spectrum/.env`; the number never enters the repo or the browser. With no linked phone the bridge returns 502 and the sheet says so and shows the copyable link. The frontend reads the bridge at `http://<page host>:8787`, so it works over the LAN the same way the phone pay link does (D-036). Touch devices keep the card flat and the front face is the whole card.

## D-041 — The grid stops flipping; color does the hover work instead
- **Date:** 2026-10-18
- **Status:** accepted
- **Decision:** Remove the hover flip from `ProductCard` and the `.flip-card` / `.flip-inner` / `.flip-face` rules. A collapsed row is one compact line-group: `size-10` thumb, single-line title, merchant · domain, `TrustBadge` plus the `passed · warning · failed` tally, the price at the right edge, and a circular `↗` link button. The expanded "On the counter" card keeps the five check rows and the text link. Hover is the marigold wash plus a darker border, with no transform. The color pass adds `--sky` / `--berry` tokens with washes, turns the three landing pillars and starter chips into tinted pills and cards, gives the best pick a marigold label, and washes the best row in marigold.
- **Why:** The user reported that the cards still felt the same size and that "navigating the site is still kind of annoying with all the flips," and repeated that the palette was not more colorful or bubbly. The flip was an earlier request, but on every row it made the pointer feel unsafe and hid the tally behind an interaction. The tally fits on the row in one line; the full checks were always in the counter card. Color now carries verdict on the edge and tint, and the hover only answers with a wash and border.
- **Alternatives considered:** Keep the flip only on the best pick (still turns under the pointer on the row people are most likely to click); keep the flip but slow it down (the problem is the movement, not the speed); move the stats into a tooltip (unreachable on touch and hidden from the keyboard); tint each merchant a different hue (the verdict is the information that matters).
- **Consequences:** Nothing about a listing is hidden behind hover anymore; the row, its link, its badge, and its tally are all on one face. The tally line is the only place the pass/warning/fail counts appear in the list; the check names and evidence stay in the expanded counter. The flip CSS, its touch and reduced-motion overrides, and the mirrored back-face link are gone, and the tests assert the row never renders `.flip-card`.
