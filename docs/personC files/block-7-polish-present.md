# Block 7 — Polish and present

Sunday. The product is built. This block is proof, pictures, a spoken demo, and the Devpost.

**Do not start new features.** Bugfixes, copy, screenshots, and the form only.

**Where to demo**

| Surface | Use it for | Do not use it for |
|---|---|---|
| `http://localhost:5173` + API on port 8000 | Screenshots, video, judge rehearsal. Catalog has the villain and the frozen numbers. | — |
| `https://sykes.select` | The public link on Devpost. Live search. Warm `/api/health` first. | The villain story. Live search has no `premium-audio-deals.shop`. |
| `http://localhost:5173/?mock=1` | Backup if the API is dead. | Do not call this the live flow on stage. |

Happy-path answers on localhost: **noise cancelling headphones**, then **$300–$600**, **Travel**, **Noise cancelling**. `$150–$300` is thinner. `Under $150` is the villain-only trap.

Keep the API running from `backend`:

```
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --workers 1
```

Frontend: `http://localhost:5173/` only. Other Vite ports cannot call the API.

---

## Shared — before anyone records

- [ ] `git fetch origin && git checkout main && git pull` (or stay on `c/web` if a PR is still open; do not demo unpushed local-only work).
- [ ] Backend: `cd backend && .\.venv\Scripts\python.exe -m pytest -q` — expect the current green count.
- [ ] Frontend: `cd frontend && npm.cmd test -- --run` then `npm.cmd run build`.
- [ ] `backend\.venv\Scripts\python.exe scripts\replay_offline.py` exits 0. Numbers: 9 listings, 8 trusted, 1 danger, pick Target $179.99, median $374.49, savings $194.50.
- [ ] Say out loud once: payment is a sandbox, no real cards, Gemini never scores.

---

## Person C — screens, talk, and the gallery

Owner of the browser. This is the only thing G5 is still waiting on from C.

### Freeze polish (only if it still fits before 2:00 AM)

Skip these if you are already recording. They are nice, not required for submit.

- [x] A listing above the stated budget is labelled, or the pick says "closest match". Do not call the budget a hard cap (D-022).
- [x] A skipped check reads "Could not verify", not a green tick.

### Screenshots (localhost, 3:2, under 5 MB)

Save the files into `docs/personC files/screenshots/` or hand them to B. Devpost still has placeholders.

- [ ] Results grid: best pick Target $179.99, savings visible, villain card still on screen and red.
- [ ] One danger card open: denylist / 12-day domain / Reddit / page flags named.
- [ ] Checkout: sandbox sentence visible, Pay enabled on the trusted pick.
- [ ] Receipt: amount, last4 `4242`, sandbox sentence, Verified or score ring.
- [ ] Thumbnail candidate: 1500×1000 grid or receipt (`docs/devpost-form.md` asks for `frontend/public/devpost-thumbnail.png`).

### Click-through proof

- [x] Full path on localhost: search → 3 questions → stream → best pick → Pay → passkey → receipt.
- [ ] Villain Pay is refused; the sheet shows the server's code (`MERCHANT_NOT_TRUSTED`). Pay stays disabled for danger — see `person-c-sunday-8-to-950.md`.
- [x] `?mock=1` still finishes the story with the API ignored.
- [x] If the API is stopped, Find products shows the red "could not reach the server" line.

### Spoken demo (rehearse twice)

Target 2.5–3 minutes. Do not apologize for the sandbox.

1. Problem: a cheap listing can be a scam. The agent will not pay it.
2. Type **noise cancelling headphones**. If Gemini is slow, the headphone templates are the backup — keep going.
3. Answer **$300–$600**, Travel, Noise cancelling.
4. Point at checks filling in. Skipped ≠ passed.
5. Villain is cheapest and still danger. Score is math, not the model.
6. Best pick is Target $179.99, saves $194.50 vs the trusted median.
7. Purge, then Pay. Read the sandbox sentence.
8. Receipt: `4242`, share link `/r/...`.

Backup if Gemini times out: the questions look like headphones anyway on this query. Backup if the API dies mid-talk: `?mock=1`. Backup if someone asks for shoes on the public URL: that is live search; the villain lives on localhost.

### Video

- [ ] One screen recording of the path above. No face required. Sandbox line must be readable.
- [ ] Hand the file to B for Devpost (step 2, gallery + video).

### Not this block

Mongo, Fly, VEYZL portal, rewriting scoring, a second router, new pages.

---

## Person A — hosted link, warm start, VEYZL close-out

Owner of deploy and the audit tool.

### Public URL

- [ ] `https://sykes.select/api/health` returns 200. `degraded` with db unavailable is correct if Mongo is unset.
- [ ] Team decision, one line in `docs/status.md`: keep live SerpAPI on the public URL, **or** set `OFFLINE=1` on Vercel so the hosted site matches the localhost villain demo. Do not unset `SERPAPI_KEY` as the fix.
- [ ] If Git deploys still 500 on answers/checkout, land the data-bundle fix (PR #30) before judging.
- [ ] Warm before any judge hits the link: health, then one session. A cold start can 500 once.

### Freeze proof

- [ ] `pytest -q` green with no `GEMINI_API_KEY` and `OFFLINE=1` (templates, catalog).
- [ ] One Uvicorn worker locally; no global gzip.

### VEYZL (optional, side track only)

- [ ] Read the failing report on PR #26 in the portal.
- [ ] If it names something already fixed (`llm_guard`, demo reset), re-run until the check is green and link it from `docs/veylz-audit.md`.
- [ ] If it will not go green before submit: uncheck the side track. Do not mention VEYZL on Devpost.

### Not this block

New payment features, a second database, raising the 2.5s Gemini cap without a decision.

---

## Person B — Devpost, numbers, claims

Owner of the story and every number a judge can quote.

### Form (`docs/devpost-form.md`)

- [ ] Project name: Sykes + Visa.
- [ ] Elevator pitch from the form map (150 characters).
- [ ] About the project pasted from `docs/devpost.md` in the listed order, sandbox disclosure at the end.
- [ ] Built-with tags match the stack that actually shipped.
- [ ] Demo URL: `https://sykes.select`. If it is dead, say so in the team channel — do not invent a URL.
- [ ] Repo link.
- [ ] Gallery: C's three images + thumbnail. 3:2, 5 MB.
- [ ] Video: C's recording, or the team recut.
- [ ] Visa track selected. Sponsored tracks only if the proof exists (VEYZL only with a green check; Mongo only if Atlas was actually used).
- [ ] Generative AI: **Yes**. Wording: Gemini writes questions, narration, and optional explanations. It never scores, never picks a merchant, never pays.
- [ ] Team members complete.

### Honesty pass

- [ ] `scripts/replay_offline.py` numbers copied into `docs/status.md`.
- [ ] README and `docs/devpost.md` still match the merged code (sandbox, synthetic data, no production Visa, live search vs catalog).
- [ ] No `.env` or key in git (`git ls-files` should not list secrets).
- [ ] Drop the MLH Mongo checkbox unless Atlas is in the demo.

### Submit

- [ ] Preview the Devpost. Read the sandbox sentence on a screenshot.
- [ ] Submit by **Sunday 09:50**. Capture the confirmation.

### Not this block

Rewriting checks. New scoring. Claiming live Visa.

---

## Sunday morning — 08:00–09:50 (all three)

- [ ] Wake the public URL; hit `/api/health` until 200.
- [ ] One localhost rehearsal of the 8-step script. C talks, A watches the API, B watches the claims.
- [ ] One refusal: try to pay the villain.
- [ ] Confirm every spoken claim: sandbox, synthetic, model does not decide, cheapest trusted not cheapest overall.
- [ ] Submit. Screenshot the confirmation page.

---

## Cut order if time runs out

1. Optional polish (budget badge, skipped copy).
2. Mongo claim.
3. VEYZL track.
4. Hosted-site villain (demo localhost instead).
5. Never cut: screenshots, video, sandbox sentence, payability refusal, Devpost story.

## Proof this block is done

Devpost has a URL, at least three screenshots, a video, and the sandbox disclosure. One person can run the 8-step script without notes. The villain cannot be paid.
