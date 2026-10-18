---
title: Remaining TODO — submission close-out
type: checklist
updated: 2026-10-18
owner: everyone
---

# Remaining TODO — submission close-out

**Deployed URL: <https://sykes.select>** — `/api/health` returns `{"status":"ok","db":"ok","version":"0.9.0","demo_mode":true,"offline":false}`.

This file owns everything left after the merge to `main` (`ee9264b`). The three artifacts that block submission are the **video**, the **screenshots**, and the **Devpost fields**. Everything else is either track evidence or honesty cleanup.

Work top-down. Tick a box only when the "Done when" line is true.

---

## P0 — Blocks submission

### 1. Fix `status.md` before anyone reads it

`docs/status.md` still says Fly is not deployed and "Do not submit `sykes.select`; it runs the removed code." That is now false and is the most dangerous stale claim in the repo.

- [ ] Update the **Health** row to `https://sykes.select/api/health` → `{"status":"ok","db":"ok"}`.
- [ ] Update the **Deploy** row: deployed, URL, commit served (`ee9264b` or later), secrets set.
- [ ] Update **Gate board**: G5 from 🟡 to the actual state; G6/G7 unchanged until submit.
- [ ] Update **Blockers** and **Owners** to the real remaining work (video, screenshots, Devpost).
- [ ] Remove "Fly serves an older build" from **Risks**; keep the honest note that the Spectrum bridge is local-only.

**Done when:** no row in `status.md` says the deployment is blocked, older, or unsafe to submit. `Last updated` is current.

**Owner:** B · **15 min** · **Never cut.**

---

### 2. Verify the deployed build end to end

A health check is not a demo. Walk the submitted URL once, in a browser, and run the HTTP smoke test against it.

- [ ] Confirm the frontend on `sykes.select` is the merged build: landing has **Deal alerts** in the header, the sandbox line is gone from the header, only the best pick is framed, and the Visit/Send footer has a gap.
- [ ] Run the HTTP smoke against the URL (values come from `backend/.env`; never paste secrets):
      `backend\.venv\Scripts\python.exe backend\scripts\smoke_http.py https://sykes.select`
- [ ] One live query on the deployed site reports `source: "serpapi"` and at least one non-allowlisted merchant.
- [ ] The deployed checkout → passkey → receipt path completes, and the receipt shows the exact sandbox sentence with a period: `Sandbox — simulated Visa Intelligent Commerce flow.`
- [ ] Screenshot the deployed results grid and receipt (these can double as Devpost gallery images).

**Done when:** a browser on the public URL has shown search, checks, the best pick, payment, and a receipt with the sandbox line.

**Owner:** A/C · **30 min** · **Never cut.**

---

### 3. Record the video (the locked script)

Use [`video-script-locked.md`](video-script-locked.md) exactly. Two segments: live locally for Beats 1–2, offline locally for Beats 3–6, end card with `sykes.select`.

- [ ] Run `scripts/replay_offline.py` → exit 0 and the frozen numbers (9 / 8 trusted / 1 danger / $179.99 / $374.49 / $194.50).
- [ ] Record the live segment at **1280 px** on `http://localhost:5173/` with answers **$300–$600 / Travel / Noise cancelling**.
- [ ] Record the staged segment with `.\scripts\dev.cmd offline`; villain red, four reasons visible, **Purge danger**, **Pay**, mandate, passkey, receipt with **4242** and the sandbox line.
- [ ] Record the terminal beat: `pytest tests/integration/test_refusal_paths.py -q` → **4 passed** (or the rehearsed `409 MERCHANT_NOT_TRUSTED` curl).
- [ ] Edit to ≤ 3:00, caption the sandbox sentence, hold the end card 4 seconds.
- [ ] Upload unlisted to YouTube; check audio on a phone speaker.
- [ ] Paste the URL into `docs/devpost-form.md` and the Devpost.

**Done when:** a 3:00-or-shorter public/unlisted video exists whose URL is in the Devpost.

**Owner:** C (screen) + A/B (voice) · **90 min** · **Never cut.**

---

### 4. Capture the gallery screenshots

Devpost asks for up to 15 images; the form lists five. **Three is the minimum** for the submission story.

- [ ] `docs/screenshots/01-grid.png` — results grid, villain red, best pick framed, purge visible.
- [ ] `docs/screenshots/02-danger.png` — villain stats panel with the four reasons and Danger badge.
- [ ] `docs/screenshots/03-mandate.png` — checkout sheet with the sandbox sentence and mandate card.
- [ ] `docs/screenshots/04-passkey.png` — passkey dialog (optional).
- [ ] `docs/screenshots/05-receipt.png` — receipt with amount, `4242`, score, share link, sandbox line.
- [ ] Export at 3:2 (1500×1000) where the form requires it.

**Done when:** at least three PNGs exist in `docs/screenshots/` and are attached to the Devpost.

**Owner:** C · **20 min** · **Never cut** (three minimum).

---

### 5. Complete and submit the Devpost

`docs/devpost-form.md` is the field map. Fill text first, attach artifacts as they land, submit once.

- [ ] **Project name:** `Sykes + Visa`; **pitch:** the 150-character line in `devpost-form.md`.
- [ ] **Live demo:** `https://sykes.select`.
- [ ] **Source:** `https://github.com/KF8311/Dubhacks`.
- [ ] **Video:** the YouTube/Vimeo URL.
- [ ] **Gallery:** the screenshots from item 4; **thumbnail** 1500×1000 (grid or receipt, not a logo).
- [ ] **Built with:** the tag list in `devpost-form.md`.
- [ ] **Story:** the required sections (inspiration, what it does, how built, challenges…) plus the exact sandbox disclosure block.
- [ ] **AI disclosure:** **Yes** — Gemini writes questions/narration/explanations; never scores or pays.
- [ ] **Title track:** Visa — Reimagine Shopping. **Not** VEYZL.
- [ ] **Sponsored:** SideShift, Cloudforce; Photon **only** if item 7 passed.
- [ ] **Non-sponsored:** MLH MongoDB Atlas; MLH Gemini **only** with the project number (item 6); DEV Writing **only** with the article URL (item 8); DubHacks NEXT; MLH Commit Fellowship.
- [ ] Preview the public page, read the pitch out loud, then submit.
- [ ] Screenshot the confirmation into `docs/handoffs/`.

**Done when:** Devpost shows the project as submitted and the confirmation is captured.

**Owner:** B · **45 min** · **Never cut.**

---

## P1 — Track evidence

### 6. Gemini project number (MLH Gemini)

- [ ] The key owner opens `aistudio.google.com/apikey` → project selector → copy the **public project number** (~12 digits).
- [ ] Paste it into the Devpost field. Never paste the API key anywhere public.
- [ ] If it cannot be found before submit, **untick the Gemini track** rather than claiming it.

**Owner:** key owner + B · **10 min** · **Cut rule:** untick the track.

---

### 7. Photon text round trip (sponsored slot 3, conditional)

The bridge log proved the blocker: `Target not allowed for this project`. Photon's shared line only messages numbers that are project users or that have texted the line first.

- [ ] Have the friend text the bridge's line once (or add their handle under the Devpost Photon project's **Users**).
- [ ] Run `bun start` in `dub-spectrum/`; confirm `/health` reports `target: "my-phone"` (never print the number).
- [ ] From the site header, enter the number with country code → the friend replies **Y** → the field shows the masked last four.
- [ ] Send a product from a card; confirm the text arrives with the product link.
- [ ] Capture the round trip; add the optional photon line to Beat 7 of the video.
- [ ] Tick **Photon 2.0** in the Devpost.

**Done when:** one real text round trip is shown on camera or in a screenshot.

**Cut rule:** if no reply by 30 minutes before submit, leave the slot empty, record D-028's condition as failed, and **do not tick Photon**.

**Owner:** A + the phone owner · **30 min**.

---

### 8. Publish the DEV Writing Challenge article

- [ ] Publish `docs/devpost-article.md` on DEV with tags `hackathon`, `ai`, `python`, `mongodb`.
- [ ] Add the public URL to `docs/devpost-form.md` and the Devpost links.
- [ ] If no DEV account exists, **untick the track** rather than linking a draft.

**Owner:** B · **20 min** · **Cut rule:** untick the track.

---

### 9. Claim scrub (docs must match the build)

- [ ] `docs/devpost.md`: test counts are stale (**232/49**). Use the real numbers: backend **264**, frontend **88** (21 files), bridge **29**. Re-run them first; update if they moved.
- [ ] `docs/status.md`: same counts; Cards row should say 21 files / 88 frontend.
- [ ] `README.md`: remove or qualify the old Vercel path and any VEYZL reference; the deploy path is `sykes.select`.
- [ ] Remove "checks are skipped for allowlisted merchants" anywhere it survives — all five run (D-043); allowlisted only changes the score floor.
- [ ] Sandbox wording: keep `Sandbox — simulated Visa Intelligent Commerce flow.` exact on checkout and receipt; the header no longer carries it.
- [ ] Never claim all five checks are live under `DEMO_MODE=1`; Reddit and page flags are fixture-backed.
- [ ] Append a decision entry (**D-047**) recording: `sykes.select` is the submitted URL, the local-only Spectrum bridge is not part of the deployed demo, and the video is recorded locally in two segments.

**Owner:** B · **30 min** · **Never cut** (submission claims).

---

### 10. Deal alerts / Send on the deployed site

The bridge listens at `http://<page host>:8787`; on `sykes.select` there is no such service. A judge who clicks **Send** or **Text me** will see a failure.

- [ ] Decide and record: hide both controls when the page is not `localhost`/LAN, **or** leave them and accept the error copy as the explanation.
- [ ] If kept visible, verify the error is honest and offers the copy-link fallback (no stack trace, no number).
- [ ] Note the choice in D-047 and in `status.md`.

**Owner:** C/A · **20 min** · **Cut rule:** document it; do not ship a broken-looking button silently.

---

## P1 — Demo robustness

### 11. Rehearse the locked script twice

- [ ] Full run with a timer; the voice must finish under **3:00** without cutting a rubric phrase.
- [ ] Check the edit against the **Must-hear phrases** list in `video-script-locked.md`.
- [ ] Confirm no phone number, `.env` value, terminal secret, or browser autofill appears in frame.
- [ ] Record a backup take of the `?mock=1` path.

**Owner:** all · **30 min** · **Never cut.**

---

### 12. Reset and protect the demo environment

- [ ] `scripts/replay_offline.py` exit 0 immediately before recording.
- [ ] One warm live query on the recorded commit; check the SerpAPI quota before and after.
- [ ] Stop the bridge unless the Photon beat is being recorded.
- [ ] Phone-width pass at 390 px; no horizontal scroll.
- [ ] Close personal tabs, notifications, and password managers.

**Owner:** C · **15 min** · **Never cut.**

---

## P2 — Polish, only if P0/P1 are green

- [ ] `checkout` payload still returns `rp_id: "sniff.vercel.app"` (`routes_checkout.py:223`). Change it to the submitted origin (`sykes.select`), update the contract if it is visible, and run the checkout tests. Cosmetic in a sandbox, but it is the old brand in an API response.
- [ ] Public brand sweep: the Devpost, README title, video end card, and page title say **Sykes**. Internal `CLAUDE.md` / `team-split-3.md` may keep Sniff as a codename; do not rename the repo.
- [ ] Thumbnail: export a 1500×1000 frame from the video if no clean grid shot exists.
- [ ] Add `docs/video-script-locked.md` and `docs/remaining-todo.md` to `docs/INDEX.md`.
- [ ] Optional: flip `DEMO_MODE=0` on the deployed backend **only** if Reddit/network checks are proven there; otherwise keep `demo_mode: true` and keep the honest wording.

---

## Final pre-submit gate

Run all of these; every line must pass or be explained in `status.md`.

```powershell
cd backend;  .\.venv\Scripts\python.exe -m pytest -q                 # 264 passed
cd frontend; npx vitest run; npm run build                            # 88 passed, clean
cd dub-spectrum; bun test; bunx tsc --noEmit                         # 29 passed, clean
backend\.venv\Scripts\python.exe scripts\replay_offline.py           # exit 0, frozen numbers
Invoke-RestMethod https://sykes.select/api/health                    # status ok, db ok
git ls-files | Select-String -Pattern "\.env"                        # only .env.example
```

**Submit only when:** video URL exists, three screenshots attached, live URL is `https://sykes.select`, sandbox disclosure is exact, and every ticked track has evidence. Untick anything else.

---

## Cut order (last 30 minutes)

1. Photon — leave the slot empty.
2. Gemini track — if no project number.
3. DEV Writing — if no published URL.
4. Screenshots 4–5 — keep three.
5. Polish items — all P2.

**Do not cut:** the video, the live URL, the sandbox disclosure, the Visa title track, or the final submit.
