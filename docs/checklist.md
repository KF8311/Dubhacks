---
title: Checklist
type: checklist
updated: 2026-10-18
owner: everyone
---

# Checklist — open items, three owners

Open work only, split A / B / C. Everything proven is in [`status.md`](status.md) and the "Already done" list at the bottom. [`team-split-3.md`](team-split-3.md) is the long-term ownership map; this file is what is left right now.

**Current state:** `main` has the kept build (`96cf47f`), D-025, the `c/web` fixes, and the embedded data bundle. Backend **231 passed**, frontend **49 passed**, `npm run build` clean, replay exit 0. Nothing has been clicked through in a browser on this build.

**Run it:** `.\scripts\dev.cmd` → open **http://localhost:5173/**. Offline: `.\scripts\dev.cmd offline`. Details: [`RUN.md`](RUN.md).

**Rules that still apply:** one owner per file (`models.py`, `types.ts`, and `contracts.md` belong to A; docs and Devpost to B; frontend source to C). Tests pass before a task is ticked, and every commit carries your name only.

---

## A — search, contracts, deploy

- [ ] **Give `Question` a backend model.** `backend/app/domain/models.py` has no `Question`; the API returns plain dicts from `questions.py` while `frontend/src/lib/types.ts` and [`contracts.md`](contracts.md#L81) define a shape. Add the pydantic model (including `allow_free_text`) and return typed objects, or freeze the dict shape in the contract — the two must agree. Remove the "Not yet in `models.py`" caveat either way.
- [ ] **Exercise the Mongo repository adapter against Atlas.** Set `MONGODB_URI`, create a session → answer → read the snapshot, and confirm `/api/health` reports the DB as available. This result decides the MLH claim for B. If Atlas cannot be reached, drop the claim.
- [ ] **Remove the live secrets from `frontend/.env`.** Keep only `VITE_API_BASE_URL` and `VITE_USE_MOCK`; delete `SERPAPI_KEY`, `GEMINI_API_KEY`, `RECEIPT_SIGNING_SECRET`, `MONGODB_URI`, and the rest. Vite only exposes `VITE_*`, so nothing leaks today, but a prefix rename would ship a key in the client bundle. Confirm `git ls-files | Select-String "\.env"` shows only `.env.example` files.
- [ ] **Prove live search on the running stack.** Create a session on `dev.cmd` with `noise cancelling headphones` + `$300–$600`; confirm `search.completed` has `source: "serpapi"`. Then point a backend at an invalid `SERPAPI_KEY` and confirm the `failed` stage with `SEARCH_UNAVAILABLE` — never the catalog.
- [ ] **Docker sanity** — this is what Fly runs:
  ```powershell
  docker build -f backend/Dockerfile -t sniff-visa .
  docker run --rm -p 8080:8080 --env-file backend/.env sniff-visa
  ```
- [ ] **Deploy:** `fly deploy` from the repo root, then warm the app and run the smoke script:
  ```powershell
  backend\.venv\Scripts\python.exe backend\scripts\smoke_http.py https://<app>.fly.dev
  ```

**Done when:** the contract and model agree, the Atlas answer is recorded, the env files hold no live keys, live and failed searches are both observed on the running stack, and the public URL serves this build with a passing smoke run.

## B — docs, claims, Devpost

- [ ] **VEYZL: cut it.** The app is not installed and the probe work lives in the parked commits. Mark the side track **not selected** in [`devpost-form.md`](devpost-form.md) and note the decision in [`veylz-audit.md`](veylz-audit.md). Do not claim it.
- [ ] **MLH MongoDB claim follows A's Atlas result.** Keep the checkbox in [`devpost-form.md`](devpost-form.md) only if the adapter ran against Atlas; otherwise remove it. In-memory is the default and `degraded` with Mongo off is expected.
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
cd backend;  .\.venv\Scripts\python.exe -m pytest -q            # 231 passed
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
- [x] Test counts in `README.md`, `devpost.md`, `status.md` updated to 231/49
- [x] Five trust checks, deterministic scoring, recommendation, checkout → passkey → receipt, public share, refusal paths
- [x] Offline replay reproduces the frozen numbers: 9 listings, 8 trusted, 1 danger, pick `lst_tgt_bsp`, median $374.49, savings $194.50
