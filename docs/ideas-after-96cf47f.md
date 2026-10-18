---
title: Ideas after 96cf47f
type: archive
updated: 2026-10-18
status: parked
owner: team
---

# Ideas after `96cf47f` — parked, not in the current code

On 2026-10-18 the team chose **`96cf47f`** ("Merge A's agent_backend: VEYZL guard and Vercel deploy path") as the code to keep. The work built after that commit was removed from `main` but is still in git. This page records what it was, why it existed, and whether it is worth re-implementing later.

**Nothing described here is in the current code.** Treat this as a menu, not a backlog.

The chosen point keeps: live SerpAPI search (`source: "serpapi"`), the curated-catalog fallback, the five trust checks, deterministic scoring, checkout → passkey → receipt, the VEYZL input guard introduced at `96cf47f`, and the localhost + Fly deploy paths.

## Where the removed work still lives

| Ref | Tip | What it is |
|---|---|---|
| `backup/main-post-96cf47f` (local) | `1562772` | `main` immediately before the reset — the full post-`96cf47f` state |
| `origin/main` before PR #34 | `1562772` | The old tip. [PR #34](https://github.com/KF8311/Dubhacks/pull/34) restored `main` to the kept build; the commits stay reachable from the backup refs below |
| `backup/23pm-good-deploy-pre-reset` (local) | `a81bcc4` | The four commits that were on `restore/23pm-good-deploy` |
| `restore/23pm-good-deploy` (local) | `96cf47f` | The point that was kept |
| `origin/restore/23pm-good-deploy` | `a81bcc4` | Remote still has the four later commits |
| `fix/embedded-data` / `origin/fix/embedded-data` | `a9af5a3` | Branch-only alternative deploy fix (see below) |
| `origin/c/web` | `2932c57` | Branch-only merge of the deploy/data/guard work |
| `origin/fix/vercel-data-bundle` | `b11a106` | Earlier attempt at the same data-bundling fix |
| `origin/fix/vercel-include-data` | `b53072f` | Later attempt at the same data-bundling fix |
| `origin/docs/deploy-repair` | `a4208be` | Docs claiming the Vercel deploy was repaired |

Nothing was garbage-collected: `git show <sha>` works for every commit linked below.

## Every commit after `96cf47f` (old `main` history)

Oldest first. The commit messages are not reliable: several commits titled `feat: fix search` actually change `llm_guard.py` / VEYZL probes, and `feat: AI safeguard` is the same workstream. The "actually changed" column is what the diff shows.

| Commit | Message | Actually changed |
|---|---|---|
| [`cc4e7e5`](https://github.com/KF8311/Dubhacks/commit/cc4e7e5577997d34daa2f463b4bceab1042fba16) | docs: record A's merge and update the one-page remaining list | `docs/REMAINING.md` added; status/checklist updates |
| [`d36fd38`](https://github.com/KF8311/Dubhacks/commit/d36fd38f7b073602f1397b1705dc53f760e59298) | Merge PR #26 | Merge of `integration/agent-backend` |
| [`d50bccd`](https://github.com/KF8311/Dubhacks/commit/d50bccd7e44813bc6102e3f0350f6bbb9426d591) | docs: record the VEYZL check run on PR #26 | Docs only |
| [`22f9797`](https://github.com/KF8311/Dubhacks/commit/22f9797a3b381a5a1533bf577c92dbac2d5e4560) | feat: AI safeguard | `llm.py`, `llm_guard.py`, checkout probe handling; D-024 |
| [`74a3818`](https://github.com/KF8311/Dubhacks/commit/74a381845f87e34e44ef5710e35e2d4f1c51b92b) | feat: AI safeguard | Probe path, 12 s `PROBE_LLM_S`, guard tests |
| [`6f3f0f7`](https://github.com/KF8311/Dubhacks/commit/6f3f0f78f9c035e5eb1503b113750a6ba03cc930) | feat: AI safeguard | Probe detection + `test_veyzl_probes.py` |
| [`a3559bb`](https://github.com/KF8311/Dubhacks/commit/a3559bb69a12200e24831a895031509623f8562f) | feat: AI safeguard | Guard/output-enforcement tweaks |
| [`19be652`](https://github.com/KF8311/Dubhacks/commit/19be652fe5dda1fa3ce7cf7ffbfef3e68a789b90) | feat: AI safeguard | Error shapes + guard |
| [`c55ce29`](https://github.com/KF8311/Dubhacks/commit/c55ce290c82719a5a9fe229848e95b5556757c5e) | feat: fix search | **The real search fix**: live results < 3 fall back to catalog; host-aware `apiBase`; `sykes.select` CORS; submit state |
| [`a81bcc4`](https://github.com/KF8311/Dubhacks/commit/a81bcc43dedd485c3672773855c7eb4b3162e3b9) | docs: record the live deploy | Docs only |
| [`fcbcb29`](https://github.com/KF8311/Dubhacks/commit/fcbcb29131a366b52493bd9b304e0437e324933a) | feat: fix search | `.vercelignore`, error handling, guard, orchestrator config fix |
| [`4354a90`](https://github.com/KF8311/Dubhacks/commit/4354a90ba25d56798ae74ec20ec1b8ae19d3315d) | feat: fix search | Guard/probe only |
| [`04d1d2e`](https://github.com/KF8311/Dubhacks/commit/04d1d2e999b28fa33195d9920444fc67d80ad432) | fix(deploy): commit the bundled data | `backend/data/*` committed; `.gitignore` change |
| [`c3cf49c`](https://github.com/KF8311/Dubhacks/commit/c3cf49cabf4d73930673df9d9d0c566f75f95bc0) | docs(status): record the Git-deploy data outage | Docs only |
| [`ed4e95b`](https://github.com/KF8311/Dubhacks/commit/ed4e95b0428e37b30e3bc5f139475a9ef100aac6) | fix(paths): find data/ beside the app package on Vercel | `paths.py` candidate resolution + tests |
| [`e5caac0`](https://github.com/KF8311/Dubhacks/commit/e5caac0eab726e3e272542a939b2c02218cffcb4) | feat: fix search | Guard/probe only |
| [`e163a29`](https://github.com/KF8311/Dubhacks/commit/e163a29fb50e7fa1199a8ad727b2e0f4495cdaca) | Merge branch `agent_backend` | Merge |
| [`7ef096d`](https://github.com/KF8311/Dubhacks/commit/7ef096deb7651f1f14e6c967fbd620d12ffb1b34) | feat: fix search | Guard/probe only (not search) |
| [`ab33e7e`](https://github.com/KF8311/Dubhacks/commit/ab33e7e8968cc6220a57338f4e11f152c3c89653) | fix(deploy): ship data/ in the function | `includeFiles`, `routes_health.py` diagnostics |
| [`1562772`](https://github.com/KF8311/Dubhacks/commit/156277202e4baa7994347811ae3a87db2cb3946b) | feat(health): report the offline flag and whether a search key is set | Health flags + config |

At the removed tip the docs claimed **204 backend tests and 39 frontend tests** (up from 187/34 at `96cf47f`), almost entirely from the VEYZL probe work.

## The ideas, grouped

### A. Vercel data bundling and deploy repair

**Commits:** `04d1d2e`, `c3cf49c`, `ed4e95b`, `ab33e7e`, plus branch-only `a9af5a3`, `b11a106`, `b53072f`.

**What it did:** committed `backend/data/` so a Git-connected Vercel build ships the catalog, allowlist, denylist, and fixtures; added `.vercelignore`; changed `paths.py` to look beside the app package as well as beside the repo; added `includeFiles: ["data/**"]` to `vercel.json`; reported the resolved data directory and every candidate from `/api/health`.

**Why it existed:** the Git deploy built from `a81bcc4` shipped no `data/`, so answers and checkout returned 500 while the CLI-built deployment worked.

**Recommendation: revisit only if the project goes back to a Vercel Git deploy.** It is additive and low risk, but it duplicates `data/` inside `backend/data/` and the local demo does not need it.

**Caveat:** `bundle_data.py` must stay in sync with the committed copy; `fix/embedded-data` (`a9af5a3`) is a different answer to the same problem — embed the bundle as a Python module instead of committing JSON.

### B. Live-search quality guard

**Commit:** `c55ce29` (one line in `backend/app/search/service.py`).

**What it did:** changed `if results:` to `if len(results) >= min(3, limit):`. At `96cf47f`, a live query that returns one or two results shows that thin grid; after the change it falls back to the curated catalog instead.

**Why it matters:** this is the most likely explanation for "it only showed one item" on some live queries.

**Recommendation: test and adopt.** Small, isolated, and has a test. The trade-off is explicit: a thin live result set is replaced by the catalog rather than shown as-is.

### C. Health diagnostics

**Commits:** `ab33e7e`, `1562772`.

**What it did:** `/api/health` now reports:
- `build` — the Vercel commit SHA
- `search.offline` — whether `OFFLINE=1`
- `search.serpapi_key` — **boolean only**, never the key
- `data.dir`, `data.catalog_exists`, `data.candidates`

**Recommendation: adopt if anything is deployed.** It is low risk and makes "live search is off" distinguishable from "the key is missing" without dashboard logs.

### D. CORS for the public origin

**Commit:** `c55ce29`.

**What it did:** added `https://sykes.select` to the default `ALLOWED_ORIGINS`.

**Recommendation: adopt only if that domain stays.** No effect locally.

### E. Host-aware frontend API base and submit state

**Commits:** `c55ce29`, `fcbcb29`.

**What it did:** `apiBase()` now takes the page hostname: a deployed host always uses same-origin `/api` even if `VITE_API_BASE_URL` was baked in; `localhost`/`127.0.0.1` keeps using the env value or `http://localhost:8000`. `DiscoveryFlow` sets a `submitting` phase and resets to `query` on failure.

**Why it matters:** a production build with `VITE_API_BASE_URL` set would otherwise call `localhost:8000` from the browser.

**Recommendation: adopt.** Low risk, with tests. This is the fix that makes one build work both locally and hosted.

### F. VEYZL / LLM probe hardening

**Commits:** `22f9797`, `74a3818`, `6f3f0f7`, `a3559bb`, `19be652`, `fcbcb29`, `4354a90`, `e5caac0`, `7ef096d` (the `AI safeguard` series and most of the mislabeled `feat: fix search` commits).

**What it did** (see decisions D-024, D-025, D-026 in the old `docs/decisions.md`):
- `POST /api/checkout` now treats any body that is not a real `{session_id, listing_id, mandate}` checkout as an LLM probe.
- Harm requests (explosives, self-harm) stay local and never reach Gemini.
- SSN/card/secret payloads are redacted before any model call.
- Other probes are sent to Gemini as plain text with a 12 s budget (`PROBE_LLM_S`).
- Model output is post-processed so refusal language, Paris, or an adverse-action reason is present even if Gemini greets the user.
- `backend/tests/unit/test_veyzl_probes.py` (~406 lines) covers the probe shapes.

**Why it existed:** VEYZL audits of PR #26 failed because probes hit the checkout endpoint and got 422s; later runs failed because canned replies proved nothing about the model.

**Recommendation: park unless the VEYZL side track is revived.** Do not merge it wholesale:
- it turns the payment endpoint into a general LLM probe endpoint;
- it adds a Gemini dependency to probe traffic;
- it is the largest and least product-facing part of the diff.

If it is revived, prefer a separate `/api/audit/probe` route and keep the redaction helpers rather than overloading checkout.

**Note:** the commit messages `feat: fix search` on `fcbcb29`, `4354a90`, `e5caac0`, and `7ef096d` are misleading — those changes are guard/probe work. Only `c55ce29` contains the search change.

### G. Documentation and Devpost updates

**Commits:** `cc4e7e5`, `d50bccd`, `a81bcc4`, `c3cf49c`, plus parts of the `fix search` commits.

**What it did:** added `docs/REMAINING.md` ("what is actually left"), updated `status.md`, `checklist.md`, `devpost*`, `veylz-audit.md`, and `INDEX.md` through 23:10 PT. The old status recorded the live Vercel deploy at `https://sykes.select` and the live-search/villain caveat.

**Recommendation: archive only.** The text is superseded by the reset; follow the commit links if you need it.

## Other branches with related work

- `origin/fix/embedded-data` — `a9af5a3` — embeds the data bundle as a Python module (another answer to the Vercel data problem).
- `origin/c/web` — `2932c57` — merges the partner deploy path, Vercel data, and LLM guard onto `c/web`.
- `origin/fix/vercel-data-bundle` — `b11a106` and `origin/fix/vercel-include-data` — `b53072f` — earlier attempts at the same data-bundling fix.
- `origin/docs/deploy-repair` — `a4208be` — docs only.

These were not merged into `main` at the chosen point. Only investigate them if the Vercel path is revived.

## Bringing any of it back later

```bash
# see the full removed history
git log --oneline 96cf47f..backup/main-post-96cf47f

# inspect one change
git show c55ce29 -- backend/app/search/service.py

# copy a single file from a later commit
git checkout c55ce29 -- backend/app/search/service.py

# or explore the whole removed state on a scratch branch
git switch -c scratch/revisit backup/main-post-96cf47f
```

`backup/main-post-96cf47f` is local; `origin/restore/23pm-good-deploy` still contains the later commits, so the work is recoverable from either machine.

## Decisions to make later

| Idea | Effort | Risk | Worth doing? | Notes |
|---|---|---|---|---|
| A. Vercel data bundling | M | Low | _open_ | Only if deploying on Vercel again; consider `fix/embedded-data` instead |
| B. Live-search < 3 guard | S | Low | _open_ | One line + test; fixes thin live grids |
| C. Health diagnostics | S | Low | _open_ | Useful on any deploy; booleans only |
| D. `sykes.select` CORS | XS | Low | _open_ | Only if the domain stays |
| E. Host-aware `apiBase` | S | Low | _open_ | Needed for any hosted build |
| F. VEYZL probe hardening | L | Medium | _open_ | Only if the VEYZL track is revived; prefer a separate route |
| G. Docs updates | XS | None | no | Archive only |

When a row is decided, replace `_open_` with the date and the decision. Do not silently re-add code from here without a note in `docs/decisions.md`.
