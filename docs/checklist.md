---
title: Checklist
type: checklist
updated: 2026-10-18
owner: everyone
---

# Checklist — open items, three owners

Open work only, split A / B / C. Everything proven is in [`status.md`](status.md) and the "Already done" list at the bottom. [`team-split-3.md`](team-split-3.md) is the long-term ownership map; this file is what is left right now.

**Blocker (2026-10-18): the SerpAPI key has 0 searches left** (Free Plan, 250 used this month). Live search fails in ~0.2 s with the new `SEARCH_QUOTA_EXHAUSTED` message for any query SerpAPI has not cached. **Get a fresh key before a live rehearsal** — put it in `backend/.env` as `SERPAPI_KEY` (never commit it, never paste it into chat) and restart the backend. Cached queries such as `TUL pens at Office Depot` still resolve; use **Skip questions** so the query stays exact.

**Current state:** `a/atlas-durable` carries the kept build (`96cf47f`), D-025, the `c/web` fixes, the embedded data bundle, and D-034–D-038 (real merchant links, flip cards, phone pay, quota error, skippable questions). Backend **263 passed**, frontend **72 passed** (18 files), `npm run build` clean, replay exit 0. Atlas is connected and proven. A's code and local proofs are done; the live pens demo is proven over HTTP, nothing has been clicked through in a browser on this build, and Fly is not deployed yet.

**Baseline re-run 2026-10-18 05:05 PT** (before starting the track tasks):

| Gate | Result |
|---|---|
| `.venv\Scripts\python.exe -m pytest -q` | 234 passed, 19.6s |
| `npx vitest run` | 54 passed (15 files) — the docs said 49, they were stale |
| `npm run build` | clean after `npm install`; the first run failed on a missing `@fontsource-variable/bricolage-grotesque` because this checkout's `node_modules` predated the restyle |
| `scripts/replay_offline.py` | exit 0, 9 listings / 8 trusted / 1 danger / median $374.49 / savings $194.50 |

**Finding to carry forward:** a machine that has not run `npm install` since [`index.css:4`](../frontend/src/index.css#L4) gained the Bricolage import builds the app fine in dev but fails `npm run build`. Anyone picking this up on a fresh clone needs `cd frontend; npm install` first. Add it to [`RUN.md`](RUN.md).

**Run it:** `.\scripts\dev.cmd` → open **http://localhost:5173/**. Offline: `.\scripts\dev.cmd offline`. Details: [`RUN.md`](RUN.md).

**Rules that still apply:** one owner per file (`models.py`, `types.ts`, and `contracts.md` belong to A; docs and Devpost to B; frontend source to C). Tests pass before a task is ticked, and every commit carries your name only.

---

## Tracks — one title, three sponsored, unlimited non-sponsored

Implementation plan: [`superpowers/plans/2026-10-18-track-submissions.md`](superpowers/plans/2026-10-18-track-submissions.md). This section is the working copy — tick a box only when its check actually passes.

### The slate

| Slot | Track | State |
|---|---|---|
| **Title** | Visa: Reimagine Shopping | Locked. The build is the pitch. |
| Sponsored 1 | **SideShift — Best Startup Idea** | Enter. No build requirement, any stack, $1,500 first. |
| Sponsored 2 | **Cloudforce** | Enter. Every entry is a raffle ticket; Most Interesting is a judges' pick. |
| Sponsored 3 | **Photon 2.0** — project `1afb123e` exists, blocked on `account_phone_missing` | Conditional. Claim only after a real text round-trips through our backend. **VEYZL** stays unselected. |
| Non-sponsored | **MLH: Best Use of Gemini API** | T1 + the public project number. |
| Non-sponsored | **MLH: Best Use of MongoDB Atlas** | Proven (D-026); T4 makes it load-bearing. |
| Non-sponsored | **MLH: DEV Writing Challenge** | T3 — publish, then link it. |
| Non-sponsored | **DubHacks NEXT**, **MLH Commit Fellowship** | Free entries; the startup paragraph doubles as the NEXT pitch. |
| Not selected | T-Mobile, SpaceXAI, Perceptron | Wireless-commerce mismatch; Cursor + Grok required; workshop closed. |

### Execution order

| # | Task | Time box | Status | Cut rule |
|---|---|---|---|---|
| **T0** | **Video + three screenshots** | must exist by 08:30 PT | not started | **never cut** — the only artifact that blocks submission outright |
| T1 | Gemini provenance chip | 60 min | ✅ done 05:10 | none — smallest visible win |
| T2 | Photon text loop | 75 min | blocked on a number | no reply within 10 min of setup → leave slot 3 empty |
| T3 | DEV article | 60 min | ✅ drafted; publish pending a DEV account | trim to 1,200 words; never describe a feature we do not have |
| T4 | Atlas payment-path durability | 90 min | ✅ done 05:30 | abandon at 90 min — the Atlas claim already stands on D-026 |
| T5 | Slate, SideShift paragraph, project number | 30 min | ✅ 05:25 — D-028 + paragraph done; project number still needs the AI Studio owner | none |
| T6 | **Fly deploy** (backend + frontend) | 45 min | blocked on `flyctl` + `fly auth login` | if Fly will not deploy by 08:15, use T7 and say "personal Vercel" on stage |
| T7 | **Personal Vercel deploy** (fallback) | 30 min | not started | frontend-only if the services build fails; point it at the Fly or local backend |

#### T0 — Artifacts (blocks the submission)

- [ ] Walk the demo path in a browser (C section below) and capture the three screenshots
- [ ] Record one full run, under 3 minutes, showing: 9 cards → villain red with reasons → purge → pay → receipt
- [ ] Confirm the recording shows the sandbox banner and the `4242` token line

**Done when:** three PNGs in `docs/screenshots/` and one video file handed to B. Nothing else is submission-blocking.

#### T1 — Gemini provenance chip (MLH Gemini)

**Why:** the model writes the explanations, but a judge cannot tell where it wrote one and where the template did. The chip makes the Gemini integration visible in the demo instead of a line on Devpost.

**Files:**
[`llm.py:220`](../backend/app/services/llm.py#L220) ·
[`routes_sessions.py:87`](../backend/app/api/routes_sessions.py#L87) ·
[`test_llm.py`](../backend/tests/unit/test_llm.py) ·
[`api.ts:133`](../frontend/src/lib/api.ts#L133) ·
[`CheckRow.tsx:30`](../frontend/src/features/results/CheckRow.tsx#L30) ·
[`CheckRow.test.tsx`](../frontend/src/features/results/CheckRow.test.tsx) ·
[`contracts.md`](contracts.md)

**Read first:** the explain route currently hides which path answered — [`routes_sessions.py:95-101`](../backend/app/api/routes_sessions.py#L95-L101) imports `explain_check` and returns only `explanation`.

- [x] Write three failing tests: no model → `("ok", "template")`; fake completion → `("The certificate is valid for the domain.", "gemini")`; unusable answer → `("ok", "template")`
- [x] Run `cd backend; .\.venv\Scripts\python.exe -m pytest tests/unit/test_llm.py -q` and confirm they fail on the missing name
- [x] Add `async def explain_check_with_source(check, *, complete=None) -> tuple[str, str]`; keep `explain_check` as a one-line wrapper
- [x] Return `"source"` from `POST /api/sessions/{id}/explain`; update `test_explain_route_uses_llm` to patch the new name
- [x] Frontend test first: `source: "gemini"` renders `AI-generated`, `source: "template"` renders `From evidence`
- [x] `api.ts` returns `{ text, source }`; mock mode and a missing field both return `source: "template"`
- [x] Add the `text-xs` chip to `CheckRow`
- [x] Add the field to `docs/contracts.md`

**Done when:** with no API key the chip reads `From evidence`, with a key it reads `AI-generated`, and both suites pass. ✅ 2026-10-18 05:20 PT — backend 237, frontend 55, build clean.

#### T2 — Photon text loop (sponsored slot 3, conditional)

**What the number is:** the dashboard binds your phone as a *Spectrum user* — the line only replies to numbers that have texted it first. **Using your own phone is fine and is the simplest path**; the only cost is that the agent can message that number while the line exists. Alternatives if that changes: a teammate's phone, a Photon-assigned (shared) number if the dashboard offers one, TextNow or a Twilio trial number.

**Read first:** [Spectrum quickstart](https://photon.codes/docs/spectrum-ts/introduction) · [iMessage provider](https://photon.codes/docs/spectrum-ts/providers/imessage) · [create-user / shared numbers](https://photon.codes/docs/api-reference/users/create-user) · dashboard at [photon.co/beta](https://photon.co/beta)

- [ ] Avatar menu → attach a number; confirm the project leaves `account_phone_missing`
- [x] Scaffolded at `../dub-spectrum` with `bun create spectrum-project@latest dub-spectrum --projectId 1afb123e-969b-47e3-b2af-de11d64d6901 --platforms imessage --yes`. The flag is `--platforms` now, not `--providers`. **The Cloud step in the scaffolder fails on Windows** (`spawn npx ENOENT` — Bun cannot start the `.cmd` shim), so the project id is written by hand and the secret is fetched with `bunx @photon-ai/cli@latest projects secret --project …` after `login`.
- [x] `PROJECT_SECRET` lives only in the scaffold's gitignored `.env` — never in this repo or chat
- [x] Authenticated (`bunx @photon-ai/cli@latest login`, user's account) and fetched the secret with `projects secret --project 1afb123e-969b-47e3-b2af-de11d64d6901 --json` into the gitignored `.env` — no secret in the repo or chat.
- [ ] `bun start` is running (`Spectrum started`, provider `imessage`). **The go/no-go is now a real text**: the echo loop is gone, so the line should answer with the budget question, then the pick. Any reply within 10 minutes of the first text counts as a pass; silence after a text fails slot 3.
- [x] Bridge lives at **`Dubhacks/dub-spectrum`** (moved inside the repo; `.env`, `node_modules`, and logs stay gitignored). Flow is **pick first, questions after**: text → strip the polite framing ("hey can you find me …" becomes "…") → create session → submit empty answers → poll until `ready`/`no_trusted_option`/`failed` → reply with the top trusted pick, price, merchant, one-line reason, **and `listing.product_url`** → then a refinement menu (1 cheaper, 2 better quality, 3 something else, or `new: <product>`). A greeting alone asks what to shop for instead of searching for "hi". 15 unit tests; `bun simulate.ts` proved the network path end to end against the real backend. Only the live text is unproven.
- [ ] Capture one real round trip for the video

**Done when:** a text from a phone gets a trust-checked pick computed by our backend. Otherwise mark slot 3 empty, note it in D-028, and stop.

#### T3 — DEV Writing Challenge

- [x] Draft [`devpost-article.md`](devpost-article.md) — 1,214 words, every number checked against the replay and the code: the problem (agents can pay anyone) → the decision (deterministic scoring, the LLM has no vote) → the honest failure ([D-025](decisions.md#L216)) → the two bugs only a real database found ([D-026](decisions.md#L224): naive datetimes, empty idempotency key) → what we would build next
- [x] Every number traced to [`status.md`](status.md) and [`scoring.py`](../backend/app/trust/scoring.py); no invented feature
- [ ] Publish on DEV, tags `hackathon` `ai` `python` `mongodb`
- [ ] Add the URL to `docs/devpost-form.md` and the Devpost links field

**Done when:** the post is public and linked from the submission.

#### T4 — Make the payment path survive a restart (Atlas)

**Files:**
[`repository.py:73`](../backend/app/services/repository.py#L73) (protocol, then both adapters at [:135](../backend/app/services/repository.py#L135) and [:229](../backend/app/services/repository.py#L229)) ·
[`orchestrator.py:147`](../backend/app/sessions/orchestrator.py#L147) (`replace_listings`) ·
[`orchestrator.py:303`](../backend/app/sessions/orchestrator.py#L303) (`attach_investigation`) ·
[`routes_checkout.py:53`](../backend/app/api/routes_checkout.py#L53) (`_get_listing`, `_get_investigation`; call sites at [:131](../backend/app/api/routes_checkout.py#L131), [:134](../backend/app/api/routes_checkout.py#L134), [:232](../backend/app/api/routes_checkout.py#L232), [:233](../backend/app/api/routes_checkout.py#L233)) ·
[`test_repositories.py`](../backend/tests/integration/test_repositories.py) ·
[`test_orchestrator.py`](../backend/tests/integration/test_orchestrator.py) ·
[`test_checkout_api.py`](../backend/tests/integration/test_checkout_api.py)

**Read first:** [`status.md:21`](status.md#L21) — sessions, listings and investigations are still registry-only. That sentence is what this task deletes.

- [x] Failing test: `MongoRepository` round-trips a listing through `get_listing`
- [x] Add `get_listing` to the protocol and both adapters
- [x] Failing test: the orchestrator leaves a listing and an investigation in the repository
- [x] Write through after `replace_listings` and `attach_investigation`
- [x] Add `get_investigation_for(session_id, listing_id)` to both adapters, with its test
- [x] Make `_get_listing` / `_get_investigation` async with registry → repository → catalog, and update the four call sites
- [x] Restart-survival test: clear the registry, reset the token simulator, confirm the checkout, expect a `rcp_` receipt
- [x] **Found a second gap:** the real restart returned a 500 — `store.token_by_checkout[...]` raised `KeyError` because the simulator's token table is in memory. `Checkout` now carries `token_id`, confirm re-registers it, and a checkout with no token refuses with 409 (D-027)
- [x] Prove it over HTTP against Atlas and record the ids in [`status.md`](status.md): `chk_dzr98nwVykDASG4L` → `rcp_ZSgCEO8uD7hwhCjs` across a real process restart

**Done when:** a checkout created before a backend restart still confirms after it. ✅ 2026-10-18 05:30 PT

#### T5 — Slate, startup paragraph, project number

- [x] Append D-028 to [`decisions.md`](decisions.md) (after D-027): title, the three sponsored slots (Photon conditional), non-sponsored list, what was rejected and why
- [x] Write the SideShift paragraph — who pays, what they pay, how it spreads (also serves DubHacks NEXT). Canonical copy: [`devpost.md`](devpost.md#who-pays)
- [ ] Read the Gemini **project number** from the [AI Studio project selector](https://aistudio.google.com/apikey) (public id, not the key) and paste it into the Devpost field at [`devpost-form.md:132`](devpost-form.md#L132)
- [ ] Tick the sponsored and non-sponsored checkboxes in [`devpost-form.md`](devpost-form.md); VEYZL stays unticked

**Done when:** the slate is recorded, the form's category boxes match it, and no claim in the form lacks evidence in the repo.

#### T6 — Fly deploy (the real demo URL)

- [ ] Install the CLI and log in — **interactive; the user runs these in their own terminal**:
  ```powershell
  iwr https://fly.io/install.ps1 -useb | iex
  fly auth login
  ```
- [ ] Set the secrets (values come from `backend/.env`; never paste them into chat or the repo):
  ```powershell
  fly secrets set MONGODB_URI="<atlas uri>" SERPAPI_KEY="<key>" GEMINI_API_KEY="<key>"
  ```
- [ ] `fly deploy` from the repo root, then warm it:
  `backend\.venv\Scripts\python.exe backend\scripts\smoke_http.py https://sniff-visa-dubhacks.fly.dev`
- [ ] Confirm `GET /api/health` reports `{"status":"ok","db":"ok"}` and one live query reports `source: "serpapi"`.

**Done when:** the public URL serves this build and `smoke_http.py` passes against it.

#### T7 — Personal Vercel deploy (fallback, frontend + `/api` in one project)

The repo already carries a [`vercel.json`](../vercel.json) with two services — `frontend` (Vite) and `backend` (FastAPI) — and a `/api/(.*)` rewrite to the backend. It targets **Vercel Services**, which is the part most likely to fail; treat this as a fallback, not the demo URL.

- [ ] Log in with the user's own account: `npx vercel login` (or import `KF8311/Dubhacks` in the Vercel dashboard).
- [ ] Deploy from the **repo root**, not `frontend/`: `npx vercel --prod`
- [ ] Add the env vars in the project settings for **Production and Preview**: `MONGODB_URI`, `SERPAPI_KEY`, `GEMINI_API_KEY`.
- [ ] Open the deployment and check `https://<deploy>/api/health` → `db: "ok"`.
- [ ] If the services build fails: deploy **frontend only** (`npx vercel --prod frontend`), set `VITE_API_BASE_URL` to the Fly backend, and rebuild.
- [ ] Walk the full path on the deployed URL: query → grid → villain → pick → checkout → receipt.

**Done when:** either the combined deployment serves `/api/health` with `db: "ok"`, or the frontend-only deployment works against a reachable backend — and `docs/status.md` says which one is live.

**Known risks:** Vercel Services is a newer config shape and may reject this file; the FastAPI function has a 60 s cap and SSE over serverless can buffer, so the search stream may arrive in one burst; cold starts add seconds the demo cannot afford. None of this blocks T6.

---

## A — deploy only

Everything else on A's plate is done (see "Already done"). Two items remain:

- [ ] **Deploy to Fly — full steps in [T6](#t6--fly-deploy-the-real-demo-url).** The CLI is not installed and there are no credentials on this machine, so this needs an interactive login first. The Docker image already builds and serves the whole path locally, so this is a packaging/auth step, not a code step.
- [ ] **Personal Vercel deploy — full steps in [T7](#t7--personal-vercel-deploy-fallback-frontend--api-in-one-project).** Only if Fly slips; `vercel.json` is already in the repo and the frontend falls back to same-origin `/api`.

**Done when:** the public URL serves this build and `smoke_http.py` passes against it (or T7's Vercel URL does).

## B — docs, claims, Devpost

- [ ] **VEYZL: cut it.** The app is not installed and the probe work lives in the parked commits. Mark the side track **not selected** in [`devpost-form.md`](devpost-form.md) and note the decision in [`veylz-audit.md`](veylz-audit.md). Do not claim it.
- [ ] **Support the MLH MongoDB claim.** Atlas is connected and proven (D-026), so keep the checkbox in [`devpost-form.md`](devpost-form.md) and make sure the deployed app gets `MONGODB_URI` as a Fly secret — otherwise the public health reads `degraded` and the claim looks thin.
- [ ] **Claim scrub.** `README.md` describes the Vercel path and the embedded bundle makes it plausible again — verify it against a real deploy before claiming it, or reword it to "Fly is the deploy path". Remove or qualify the VEYZL reference in `README.md`.
- [ ] **Pre-fill the Devpost.** [`devpost.md`](devpost.md) and [`devpost-form.md`](devpost-form.md) are drafted; fill every field that does not need the URL, screenshots, or video. The generative-AI answer is **Yes**.
- [ ] **Fill the artifacts and submit.** URL from A, three screenshots and the video from C, then the final submit and the confirmation capture.

**Done when:** no doc claims a cut feature, the form is complete except artifacts, and the submission is confirmed.

## C — browser proof

- [ ] **Click the demo path through in a real browser.** Start `.\scripts\dev.cmd`, query `noise cancelling headphones`, answer **$300–$600 / Travel / Noise cancelling**. Confirm:
  - 9 cards, 8 trusted, `Premium Audio Deals` red with its reasons
  - Best pick Target $179.99, median $374.49, savings $194.50
  - the villain disappears after Purge
  - **screenshot the grid** → `docs/screenshots/`
- [ ] **Pay → passkey → receipt** on the best pick. Confirm score, `4242`, and the sandbox line on the receipt. **Screenshot.**
- [ ] **Try to pay the villain.** It must refuse with the server's code. **Screenshot.**
- [ ] **Watch the live search.** The page must show "Searching live listings…" skeletons while it waits, and on a slow query the retry state — never a headphone catalog for a different query.
- [ ] **Mock fallback.** Stop the backend, run `.\scripts\dev.cmd mock`, open `http://localhost:5173/?mock=1`, confirm the whole flow renders.
- [ ] **Phone width.** Re-check the flow at 390 px; fix any overflow before the recording.
- [ ] **Record one full run** of the demo path and hand the file to B.

**Done when:** three screenshots and one recording exist, and the browser has shown 9 cards, the receipt, the refusal, and the loading/retry states.

---

## Shared gates — run before calling anything done

```powershell
cd backend;  .\.venv\Scripts\python.exe -m pytest -q            # 263 passed
cd frontend; npx vitest run; npm run build                       # 72 passed (18 files), clean
backend\.venv\Scripts\python.exe scripts\replay_offline.py       # exit 0, frozen numbers
git ls-files | Select-String -Pattern "\.env"                    # only .env.example
```

Do **not** run the suite with `OFFLINE=1` exported; 13 tests read ambient settings and fail for unrelated reasons.

## Demo script

| Step | Action | Expected |
|---|---|---|
| 1 | Query "noise cancelling headphones" | Questions appear (audio-specific) |
| 2 | Answer **$300–$600**, **Travel**, **Noise cancelling** | 9 cards: 8 trusted + 1 danger |
| 3 | Watch the stream | 45 checks fill in, villain turns red |
| 4 | Read the villain reason | `LOCAL_DENYLIST`, 12-day domain, 3 Reddit reports, 4 page flags |
| 5 | Point at the pick | Target $179.99, saves $194.50 vs median $374.49 |
| 6 | Purge danger | villain card disappears |
| 7 | Checkout | sandbox banner, passkey, receipt |
| 8 | Optional refusal | try the villain; server refuses with a code |

## Live pens demo (the one to show off)

The demo query is **`TUL pens at Office Depot`** (D-034). Measured over HTTP on `a/atlas-durable`: **ready in 3.2–5.1 s**, 9 listings (5 Office Depot + 4 eBay), **8 of 9 on the merchant's own product page**, best pick the Office Depot TUL BP Series Retractable Ballpoint Pens at **$12.49**, checkout `201`, `GET /api/checkout/{id}` `200`. If the flow asks a budget question, answer above **$12.49** (or skip); a lower cap filters the pen out. A bare `pens` query does not surface Office Depot in the top 9 — say "at Office Depot".

| Step | Action | Expected |
|---|---|---|
| 1 | Query `TUL pens at Office Depot`, then click **Skip questions** | 9 cards; most labelled `officedepot.com`. Skipping keeps the query exact, so SerpAPI's cache (and the quota budget) is used; answering a budget appends `under $X` and needs a live search. |
| 2 | Hover or tab to a card | It **flips**; the back shows the merchant, badge, `N passed · N warning · N failed` |
| 3 | Click the best pick's link | Opens the real product page on officedepot.com |
| 4 | Checkout | Sandbox banner, mandate, then the **"Pay on your phone"** link |
| 5 | Copy the link, open it on the phone | `/pay/<checkout_id>` shows merchant, amount, trust badge, `Approve with passkey` |
| 6 | Approve on the phone | Lands on `/r/<share_id>`, the same receipt the desktop would have produced |

**Phone on the LAN:** start Vite with `--host` (`npx vite --host`) and Uvicorn with `--host 0.0.0.0`; open the **LAN IP** (`http://192.168.x.x:5173/`) on the computer too, because `apiBase()` uses `window.location.hostname` (D-036). Opening via `localhost` on the desktop and then the raw IP on the phone means the phone's page still calls the right API, but the copied link inherits whichever host is in the address bar — use the IP so both devices agree.

## Cut list

Live page fetching → Reddit → SerpAPI → Mongo → page flags.

**Never cut:** scoring, the fixtures, the golden tests, the sandbox label, the payability gate, the refusal demo, offline replay.

## Already done — do not redo

- [x] Kept build restored on `main`; post-`96cf47f` work archived in [`ideas-after-96cf47f.md`](ideas-after-96cf47f.md)
- [x] Live search waits, then fails honestly (D-025) — no catalog substitution in live mode; skeletons and a retry state in the UI
- [x] Non-audio queries no longer answered with the headphone catalog; clarifying questions are product-specific (`c/web`)
- [x] SerpAPI client honours the configured timeout
- [x] Frontend pinned to 5173 via `scripts/dev.cmd`
- [x] `skipped` copy reads "Could not verify"
- [x] Over-budget pick is labelled "closest trusted match above that budget" (D-022)
- [x] Embedded data bundle: a deploy no longer needs an on-disk `data/` directory
- [x] Test counts in `README.md`, `devpost.md`, `status.md` updated to 232/49
- [x] `Question` / `QuestionOption` are backend models and the contract matches (`allow_free_text` included)
- [x] `frontend/.env` holds only `VITE_API_BASE_URL` and `VITE_USE_MOCK`; only `.env.example` files are tracked
- [x] Live search proven over HTTP: `noise cancelling headphones` + `$300–$600` → `source: "serpapi"`; invalid key → `SEARCH_UNAVAILABLE`, stage `failed`, zero listings
- [x] Docker image builds and the container serves health, live search, and checkout → confirm → public receipt (`smoke_http.py` passes)
- [x] Atlas connected and proven: health `db: ok`, checkout → confirm → public receipt, and the receipt survives a backend restart (D-026)
- [x] Two Mongo-only bugs fixed — naive datetimes on hydrate, and an empty `idempotency_key` colliding on the unique index — with regression tests (backend now 234)
- [x] Five trust checks, deterministic scoring, recommendation, checkout → passkey → receipt, public share, refusal paths
- [x] Offline replay reproduces the frozen numbers: 9 listings, 8 trusted, 1 danger, pick `lst_tgt_bsp`, median $374.49, savings $194.50
- [x] Every listing is clickable: the card, the best pick, and the public receipt link to the real `product_url`; a Google-hosted result opens the Google Shopping results page for the query (the top result, no `prds` catalog token) and is labelled "View on Google Shopping". The URL uses the current shopping vertical `?udm=28&q=…`; the legacy `?ibp=oshop&q=…` that SerpAPI returns renders an empty page in a browser; merchant URLs are labelled with the domain. Spaces are encoded so a text message keeps the whole link, listing ids stay distinct when results share a URL, and SerpAPI no longer invents `https://<retailer>/item/…` 404s.
- [x] `/api/health` reports `offline`, and `dev.cmd` refuses to reuse an offline backend for a live run — the trap that made a live demo silently serve the catalog
- [x] Search is localized to **Seattle, Washington, United States** (`SERPAPI_LOCATION`, override with `SERPAPI_GL` / `SERPAPI_HL`). The market goes in SerpAPI's `location` parameter, never appended to `q`. Verified live: `location=Seattle%2C+Washington%2C+United+States` on the request, ready in 10.9 s.
- [x] A bodyless text bridge exists (`dub-spectrum/src/agent.ts`): numbered budget question → answers → poll → pick, price, merchant, reason, `product_url`. 9 unit tests; not yet exercised by a real text.
- [x] **Real merchant links** (D-034): one immersive lookup per listing, concurrent, 3.5 s cap; a store's URL is used only when its host exactly equals the listing's merchant host, so a marketplace reselling the item (the DoorDash case) cannot relabel a listing. `office depot`, `staples`, and `jetpens` are known sources. Verified: `TUL pens at Office Depot` → 8/9 real links, best pick's `officedepot.com` URL.
- [x] **Cards flip to site stats** (D-035): hover/focus reveals merchant, badge, `passed · warning · failed`, and the top reason (or "Checks are still running."). Off on touch and under reduced motion.
- [x] **Pay on your phone** (D-036): `GET /api/checkout/{id}` read-only summary + `/pay/<id>` page; the mandate step copies/shares the link. `apiBase()` follows the page hostname so a LAN phone reaches Uvicorn.
- [x] **Out of searches is its own failure** (D-037): a 429 whose body says "run out of searches" raises `SearchQuotaExhausted`, is not retried, and reaches the UI as `SEARCH_QUOTA_EXHAUSTED` in ~0.2 s. A rate-limit 429 stays retryable. Resolved merchant links are cached per listing id for the process, so a re-run costs one search instead of ten.
- [x] **Questions can be skipped** (D-038): a **Skip questions** action submits `skip_remaining: true`, keeping the query exact — required to reach SerpAPI's cached results while the key is exhausted.
