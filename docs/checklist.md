---
title: Checklist
type: checklist
updated: 2026-10-18
owner: everyone
---

# Checklist — open items, three owners

Open work only, split A / B / C. Everything proven is in [`status.md`](status.md) and the "Already done" list at the bottom. [`team-split-3.md`](team-split-3.md) is the long-term ownership map; this file is what is left right now.

**Current state:** `main` has the kept build (`96cf47f`), D-025, the `c/web` fixes, and the embedded data bundle. Backend **234 passed**, frontend **49 passed**, `npm run build` clean, replay exit 0. Atlas is connected and proven. A's code and local proofs are done; nothing has been clicked through in a browser on this build, and Fly is not deployed yet.

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
| T1 | Gemini provenance chip | 60 min | not started | none — smallest visible win |
| T2 | Photon text loop | 75 min | blocked on a number | no reply within 10 min of setup → leave slot 3 empty |
| T3 | DEV article | 60 min | not started | trim to 1,200 words; never describe a feature we do not have |
| T4 | Atlas payment-path durability | 90 min | not started | abandon at 90 min — the Atlas claim already stands on D-026 |
| T5 | Slate, SideShift paragraph, project number | 30 min | partly done | none |

#### T0 — Artifacts (blocks the submission)

- [ ] Walk the demo path in a browser (C section below) and capture the three screenshots
- [ ] Record one full run, under 3 minutes, showing: 9 cards → villain red with reasons → purge → pay → receipt
- [ ] Confirm the recording shows the sandbox banner and the `4242` token line

**Done when:** three PNGs in `docs/screenshots/` and one video file handed to B. Nothing else is submission-blocking.

#### T1 — Gemini provenance chip (MLH Gemini)

**Why:** the model writes the explanations, but a judge cannot tell where it wrote one and where the template did. The chip makes the Gemini integration visible in the demo instead of a line on Devpost.

**Files:** `backend/app/services/llm.py`, `backend/app/api/routes_sessions.py`, `backend/tests/unit/test_llm.py`, `frontend/src/lib/api.ts`, `frontend/src/features/results/CheckRow.tsx`, `frontend/src/features/results/CheckRow.test.tsx`, `docs/contracts.md`

- [ ] Write two failing tests: no model → `("…summary…", "template")`; fake completion → `("The certificate is valid for the domain.", "gemini")`
- [ ] Run `cd backend; .\.venv\Scripts\python.exe -m pytest tests/unit/test_llm.py -q` and confirm they fail on the missing name
- [ ] Add `async def explain_check_with_source(check, *, complete=None) -> tuple[str, str]`; keep `explain_check` as a one-line wrapper
- [ ] Return `"source"` from `POST /api/sessions/{id}/explain`
- [ ] Frontend test first: `source: "gemini"` renders `AI-generated`, `source: "template"` renders `From evidence`
- [ ] `api.ts` returns `{ text, source }`; mock mode returns `source: "template"`
- [ ] Add the `text-xs` chip to `CheckRow`
- [ ] Add the field to `docs/contracts.md`

**Done when:** with no API key the chip reads `From evidence`, with a key it reads `AI-generated`, and both suites pass.

#### T2 — Photon text loop (sponsored slot 3, conditional)

**What the number is:** the dashboard binds your phone as a *Spectrum user* — the line only replies to numbers that have texted it first. You need a number you can receive messages on; a teammate's phone is best, a Photon-assigned (shared) number if the dashboard offers one, TextNow/Twilio as fallbacks. **No personal number required, and no slot if none works.**

- [ ] Avatar menu → attach a number; confirm the project leaves `account_phone_missing`
- [ ] `bun create spectrum-project@latest dub --projectId 1afb123e-969b-47e3-b2af-de11d64d6901 --providers imessage --yes`
- [ ] `SPECTRUM_PROJECT_SECRET` lives only in the scaffold's gitignored `.env` — never in this repo or chat
- [ ] `bun start`, text the line, confirm the `echo:` reply — **this is the go/no-go**
- [ ] Replace the echo: text → `POST /api/sessions` → answers → results → reply with the top trusted pick and its one-line reason
- [ ] Capture one real round trip for the video

**Done when:** a text from a phone gets a trust-checked pick computed by our backend. Otherwise mark slot 3 empty, note it in D-027, and stop.

#### T3 — DEV Writing Challenge

- [ ] Draft `docs/devpost-article.md`, 1,200–1,800 words: the problem (agents can pay anyone) → the decision (deterministic scoring, the LLM has no vote) → the honest failure (D-025) → the two bugs only a real database found (naive datetimes, empty idempotency key) → what we would build next
- [ ] Every number traced to `docs/status.md`; no invented feature
- [ ] Publish on DEV, tags `hackathon` `ai` `python` `mongodb`
- [ ] Add the URL to `docs/devpost-form.md` and the Devpost links field

**Done when:** the post is public and linked from the submission.

#### T4 — Make the payment path survive a restart (Atlas)

**Files:** `backend/app/services/repository.py`, `backend/app/sessions/orchestrator.py`, `backend/app/api/routes_checkout.py`, `backend/tests/integration/{test_repositories,test_orchestrator,test_checkout_api}.py`

- [ ] Failing test: `MongoRepository` round-trips a listing through `get_listing`
- [ ] Add `get_listing` to the protocol and both adapters
- [ ] Failing test: the orchestrator leaves a listing and an investigation in the repository
- [ ] Write through after `replace_listings` and `attach_investigation`
- [ ] Add `get_investigation_for(session_id, listing_id)` to both adapters, with its test
- [ ] Make `_get_listing` / `_get_investigation` async with registry → repository → catalog, and update the four call sites
- [ ] Restart-survival test: clear the registry, confirm the checkout, expect a `rcp_` receipt
- [ ] Prove it over HTTP against Atlas and record the ids in `docs/status.md`

**Done when:** a checkout created before a backend restart still confirms after it. **Cut at 90 minutes.**

#### T5 — Slate, startup paragraph, project number

- [ ] Append D-027: title, the three sponsored slots (Photon conditional), non-sponsored list, what was rejected and why
- [ ] Write the SideShift paragraph — who pays, what they pay, how it spreads (also serves DubHacks NEXT)
- [ ] Read the Gemini **project number** from the AI Studio project selector (public id, not the key) and paste it into the Devpost field
- [ ] Tick the sponsored and non-sponsored checkboxes in [`devpost-form.md`](devpost-form.md); VEYZL stays unticked

**Done when:** the slate is recorded, the form's category boxes match it, and no claim in the form lacks evidence in the repo.

---

## A — deploy only

Everything else on A's plate is done (see "Already done"). One item remains:

- [ ] **Deploy to Fly.** The CLI is not installed and there are no credentials on this machine, so this needs an interactive login first:
  ```powershell
  iwr https://fly.io/install.ps1 -useb | iex
  fly auth login
  fly secrets set MONGODB_URI="<the same Atlas URI as backend/.env>" SERPAPI_KEY="<...>" GEMINI_API_KEY="<...>"
  fly deploy
  backend\.venv\Scripts\python.exe backend\scripts\smoke_http.py https://sniff-visa-dubhacks.fly.dev
  ```
  Then warm the app (health + one session) and confirm `search.completed` reports `source: "serpapi"`. The Docker image already builds and serves the whole path locally, so this is a packaging/auth step, not a code step.

**Done when:** the public URL serves this build and `smoke_http.py` passes against it.

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
cd backend;  .\.venv\Scripts\python.exe -m pytest -q            # 234 passed
cd frontend; npx vitest run; npm run build                       # 49 passed, clean
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
