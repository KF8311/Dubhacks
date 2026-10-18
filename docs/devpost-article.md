---
title: Your shopping agent can pay anyone. Here is how we stopped it.
published: false
tags: hackathon, ai, python, mongodb
---

*Built at DubHacks '26 for the Visa "Reimagine Shopping" track. The payment flow is a sandbox — no real cards, no real money. Everything below is running code.*

An agent that can check out on your behalf is an agent that can be talked into checking out with the wrong merchant. That is the whole problem, and most demos solve it by trusting the model.

We did the opposite.

## The setup

You type "noise cancelling headphones." The agent asks two or three clarifying questions — budget, where you will wear them, what matters. Then it searches live listings, runs five trust checks against every one of them, streams the results into a grid as they finish, and recommends the cheapest listing that is actually trustworthy. You can then pay that one, through a simulated Visa mandate → passkey → token → receipt flow, with a sandbox banner on every screen and a public receipt you can share.

Nine listings, eight trusted, one not. Forty-five checks, live, in front of you. A median trusted price of $374.49, and a pick at $179.99 that saves $194.50 against that median.

The interesting part is not the search. It is the rule we would not break.

## The model gets no vote

Gemini 3.5 Flash Lite writes three things in this app: the clarifying questions, the one-line narration of the recommendation, and an on-demand explanation of any trust check you click. Every call is capped at 2.5 seconds and falls back to a deterministic template, so the app works with no API key and no network.

The model does not score. It does not select which checks run. It cannot mark a merchant payability.

Scoring is arithmetic, and it lives in Python:

```python
penalties = sum(40 * c.severity for c in failed) + sum(15 * c.severity for c in warned)
score = max(0, min(100, 100 - penalties))

if safe_browsing_failed:                 # fatal overrides, not arithmetic
    score = 0
if completed_checks < 3:
    score = min(score, 69)               # coverage cap: cannot be "trusted"
```

Trusted is 70 and above, caution sits between 40 and 70, danger below that. Some failures are fatal rather than additive: a failed safe-browsing check or a combination of failed page flags and a very young domain zeroes the score outright, because no amount of passing evidence should outvote a merchant being on a malware list.

Checkout refuses unless the verdict is trusted, the score is at least 70, and at least three checks completed — unless the merchant is explicitly allowlisted. The server re-runs that gate on confirm; the client only ever sends ids and a spending cap.

We wrote a test that fails the build if a trust, check, or payment module ever imports the LLM. That is a blunt instrument, and it is the point. A trust score you cannot re-derive from evidence is not a trust score — it is a vibe with a number attached.

The model still earns its place. A failed check explains itself in a sentence a person can read, and the sentence is sanitized and grounded in the check's own evidence, never in raw page text. It just does not decide anything. When the model is unavailable, the explanation falls back to the check's summary — and as of today the UI labels that fallback honestly, with a small `From evidence` chip instead of an `AI-generated` one. A judge can click Explain with no API key and watch the app tell the truth about itself.

## The failure we decided to keep

Live search is the part of this build that hurts.

The SerpAPI path uses a 10-second client timeout inside an 11-second per-attempt budget, with one retry. For a while, it had a fallback: if the live search failed, the app quietly showed the curated catalog instead. That made the demo resilient and it made the app a liar. A shopper asking for $300–$600 travel headphones would see products they did not ask for, presented as results.

We removed the fallback. Now a slow query shows "Searching live listings…" for up to about 22 seconds, then fails honestly with a retry button and no listings at all.

Two 11-second attempts is a bad demo. Unrelated products under someone else's query is a worse product. We chose the demo risk. That decision is written down as D-025 in the repo, along with the alternatives we rejected: keep the catalog but label it loudly (still shows products the user did not ask for), raise only the client timeout (still swaps on failure), or drop the retry entirely (one transient fault ends the demo).

## Two bugs only a real database could find

For most of the build, persistence was an in-memory adapter behind a repository protocol. It passed every test. Then we pointed it at MongoDB Atlas, and the first real checkout failed twice in two different ways.

The first: confirming a checkout raised

```
TypeError: can't compare offset-naive and offset-aware datetimes
```

BSON does not store timezone info. Every datetime came back naive, and the payability check compared it against an aware `now`. A hypothesis: hydrate the domain models with UTC attached to anything naive, at the boundary, once.

The second was subtler. The second checkout of the demo died with

```
E11000 duplicate key error ... idempotency_key: ""
```

`idempotency_key` has a partial unique index — unique among documents where the field is a string, which is how we prevent a client from confirming the same payment twice with the same key. But a freshly created checkout has no client key yet, and the model required a string, so every pending checkout wrote `""`. The first one took the index slot; the second one collided with it.

The in-memory adapter cannot reproduce either bug, because a dict has no BSON encoder and no unique index. Both fixes now have regression tests that strip timezone info from a stored document and assert the hydrated result is aware, and that assert a pending checkout stores `null` rather than an empty string.

The receipt still resolves after a backend restart. That is the only proof that mattered: it is not a cache pretending to be a database.

## What we would build next

The registry still holds sessions and investigations in memory, so the payment path is durable but the investigation is not. Persisting listings and investigations through the orchestrator is the next commit, not a rewrite.

Past that, the honest list is short. Live page fetching and page-flag analysis, so more of the five checks run against the real merchant page rather than the search result. A cost model for the checks, since some are cheap and some are not, and the grid should say which. And a second opinion path: when a check disagrees with the score, show the disagreement instead of resolving it silently.

None of that changes the rule. The model writes sentences. Python writes the score. The agent does not get to pay someone we could not verify.

---

*Code, decisions, and the failing-then-passing tests: [github.com/KF8311/Dubhacks](https://github.com/KF8311/Dubhacks). The decisions log is `docs/decisions.md`; D-025 and D-026 are the two entries in this post.*
