# Person C — Sunday 8:00–9:50 checklist

Done when the 3-minute video exists, the final screenshots are in the folder B can upload, and C can run the spoken demo twice without notes. Submit itself is B with A on the URL.

**C does not fill Devpost fields or deploy Fly.** Hand files to B.

## Screenshots (localhost, 3:2, under 5 MB)

Save into `docs/personC files/screenshots/`. Devpost still has placeholders until B uploads.

Use `.\scripts\dev.cmd offline` so the catalog villain and Target $179.99 are on screen. Do not use a live SerpAPI run for these stills.

- [ ] Results grid: best pick Target $179.99, savings visible, villain card still on screen and red.
- [ ] One danger card open: denylist / 12-day domain / Reddit / page flags named.
- [ ] Checkout: sandbox sentence visible, Pay enabled on the trusted pick.
- [ ] Receipt: amount, last4 `4242`, sandbox sentence, Verified or score ring.
- [ ] Thumbnail candidate: 1500×1000 grid or receipt → `frontend/public/devpost-thumbnail.png`.

## Click-through proof (before recording)

- [x] Full path on live search: search → 3 questions → stream → best pick → Pay → passkey → receipt (2:21 AM, typed `300 to 600`).
- [ ] Catalog path on `OFFLINE=1`: 9 cards, villain red, Target $179.99, savings $194.50. Server replay matches those numbers; browser stills for Devpost are not in the folder yet.
- [ ] Villain Pay is refused; the sheet shows the server's code (`MERCHANT_NOT_TRUSTED`). Pay is disabled for danger in the UI — C needs a call: is a disabled Pay enough, or should a click still POST and show the 409?
- [x] `?mock=1` still finishes the story with the API ignored (Best Buy $249, villain $79 / 12-day domain / crypto, Pay → mandate → passkey dialog).
- [x] If the API is stopped, Find products shows the red “could not reach the server” line. Verified in the browser at 2:30 AM; PNG not yet saved into `docs/personC files/screenshots/`.

## Spoken demo (rehearse twice)

Target 2.5–3 minutes. Do not apologize for the sandbox.

1. Problem: a cheap listing can be a scam. The agent will not pay it.
2. Type **noise cancelling headphones**. If Gemini is slow, the headphone templates are the backup — keep going.
3. Answer **$300–$600**, Travel, Noise cancelling.
4. Point at checks filling in. Skipped ≠ passed.
5. Villain is cheapest and still danger. Score is math, not the model.
6. Best pick is Target $179.99, saves $194.50 vs the trusted median.
7. Purge, then Pay. Read the sandbox sentence.
8. Receipt: `4242`, share link `/r/...`.

Backup if Gemini times out: questions still look like headphones on this query. Backup if the API dies: `?mock=1`. Backup if someone asks for shoes on the public URL: that is live search; the villain lives on localhost.

- [ ] Rehearse once.
- [ ] Rehearse twice.

## Video

- [ ] Record the 3-minute path above. No face required. Sandbox line must be readable.
- [ ] Hand the file to B for Devpost gallery + video.

## Submit window

- [ ] Files are with B before **09:50**.
- [ ] C is at the laptop for the live demo, not still exporting video.

## Not this block

Mongo claims, Fly deploy, VEYZL, rewriting scoring, a second router.
