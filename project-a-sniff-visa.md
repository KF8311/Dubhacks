# Project A — "Sniff + Visa": Full Build Rundown

**What this doc is:** A plain-English plan for the project you said you want to go toward — a Sniff-style shopping agent that investigates every listing, then completes the purchase through a Visa checkout. It covers what to build, the tech stack, how each piece works, how it hits the Visa rubric, which side tracks it stacks with, the 21-hour plan, the video script, and a glossary.

**Team:** 3–4 people, AI/backend strong.  
**Track:** Visa "Reimagine Shopping" (title track).  
**Reference repo:** [github.com/thenerd31/sniff](https://github.com/thenerd31/sniff) — use it for architecture, **not** as a code base. At least 70% of your code must be written during the hackathon.

---

## 0. The one-paragraph version

You type what you want to buy. The agent asks two or three clarifying questions, searches several retailers, and then — for every listing — runs a set of fraud checks in parallel: how old is the domain, is it on a threat list, what does Reddit say, is the brand being impersonated, does the page use scam tactics. Each check streams into the UI live. Every listing gets a trust score from 0–100 and a verdict: **trusted**, **caution**, or **danger**. The agent recommends the cheapest **trusted** option, not the cheapest option. Then comes the Visa moment: a spending mandate with a cap, a passkey confirmation, and a one-time tokenized payment. When the purchase completes, you get a **trust receipt** showing exactly what was verified and what wasn't. The core rule: **the agent is not allowed to pay a merchant it cannot verify.**

That last sentence is the whole project. If you remember nothing else, remember that.

---

## 1. The user journey (what the demo looks like)

| Step | What the user sees | What happens behind the scenes |
|---|---|---|
| 1. Ask | "I need noise-cancelling headphones for travel, under $300." | Query is parsed; the agent asks 2–3 clarifying questions (style, brand, budget). |
| 2. Search | A grid of listings from Amazon, Best Buy, Walmart, Nordstrom, and smaller stores. | Search API returns products; dead links are filtered out. |
| 3. Investigate | Each card shows checks landing one by one: domain age ✓, SSL ✓, Safe Browsing ✓, Reddit ⚠, page flags ✓. | Five checks run in parallel; each result streams over SSE. |
| 4. Score | A trust badge appears: **92 / trusted**, **48 / caution**, **12 / danger**. | Deterministic scoring; fatal flags can force a danger verdict. |
| 5. Purge | Flagged listings are removed with a "PURGE CURSED" animation. | The UI filters out `danger` results. |
| 6. Pick | "Best pick: $249 at Best Buy — the cheapest trusted option. You save $46 vs. the median." | Only `trusted` products are eligible; sorted by trust, then price. |
| 7. Pay | A checkout sheet: mandate cap, merchant, amount, passkey prompt, token. | Mock Visa Intelligent Commerce flow: mandate → passkey → token → transaction. |
| 8. Receipt | A shareable trust receipt: score, checks, what was verified, what wasn't. | Receipt is stored in MongoDB; can be shared as a link. |

---

## 2. What you're actually building (scope)

### 2.1 Must-have (the demo dies without these)

- [ ] Guided discovery: 2–3 questions, not a blank chat box.
- [ ] Multi-retailer search results with real product images and prices.
- [ ] At least **3 real trust checks** and **2 mocked checks**.
- [ ] Live streaming of check results (SSE).
- [ ] Trust score + verdict (trusted / caution / danger).
- [ ] "Cheapest trusted" recommendation.
- [ ] A Visa checkout moment: mandate, passkey, token, result.
- [ ] Trust receipt screen.
- [ ] A polished UI that looks intentional, not default.
- [ ] A 3-minute video.

### 2.2 Nice-to-have (adds points, cut if behind)

- [ ] All 5 checks real.
- [ ] "PURGE CURSED" animation.
- [ ] Shareable receipt link.
- [ ] Merchant badge ("Verified by Sniff").
- [ ] MongoDB persistence of investigations and receipts.
- [ ] VEYZL audit screenshot with before/after fix.
- [ ] Appeal path for a false positive.
- [ ] Chrome-extension mock.

### 2.3 Cut list (in order, if you're behind)

1. Chrome extension.
2. Merchant badge.
3. Share link.
4. Two of the five checks (keep WHOIS, Safe Browsing, page flags).
5. Live search (use a curated catalog).
6. MongoDB (use in-memory).

**Never cut:** the payment moment, the trust score, the streaming investigation, or the polished UI. Those are the project.

---

## 3. Architecture (plain English)

```
┌──────────────────────────────────────────────────────────────┐
│  Browser — React + Vite + Tailwind + shadcn/ui               │
│                                                              │
│  Discovery → Results → Trust cards → Checkout → Receipt      │
│         ▲               ▲               ▲                    │
│         │ SSE           │ SSE           │ REST               │
└─────────┼───────────────┼───────────────┼────────────────────┘
          │               │               │
┌─────────┴───────────────┴───────────────┴────────────────────┐
│  FastAPI backend (Python)                                    │
│                                                              │
│  /api/search      /api/investigate      /api/checkout        │
│      │                  │                    │               │
│      ▼                  ▼                    ▼               │
│  Search service     Trust engine         Visa mock           │
│  (Tavily/SerpAPI)   (5 checks + score)   (mandate + token +  │
│      │                  │                passkey + receipt)  │
│      └──────────────────┴────────────────────┘               │
│                         │                                    │
│                   MongoDB Atlas                              │
│          (investigations, receipts, preferences)             │
└──────────────────────────────────────────────────────────────┘
```

**Why split frontend and backend?** Your team is AI/backend strong. Python is the fastest path for the agent, scraping, and scoring. React/Vite is simpler than Next.js when you're not a frontend team — no server-side rendering to debug. SSE works cleanly across the two.

**Alternative:** all-Next.js (TypeScript). Use it only if the team is comfortable with React and wants one deploy. Do not mix Next.js and FastAPI.

---

## 4. The tech stack

### 4.1 Recommended stack (for your team)

| Layer | Tool | Why |
|---|---|---|
| Frontend | **React 19 + Vite + TypeScript** | Fast dev server, simple build, no SSR complexity. |
| Styling | **Tailwind CSS + shadcn/ui** | Professional components in minutes; consistent design. |
| Animation | **Framer Motion** | Card entrances, score count-up, purge animation. |
| State | **Zustand** (or React state) | Simple global store for products, checks, cart. |
| Backend | **FastAPI + Uvicorn + Pydantic** | Python, async, typed request/response models. |
| Streaming | **SSE** (`sse-starlette` or `StreamingResponse`) | One-way server→client stream; perfect for live checks. |
| AI | **Google Gemini 2.5 Flash** (free tier) or **OpenAI gpt-4o-mini** | Query refinement, explanations, impersonation reasoning. Gemini also hits the MLH Gemini track. |
| Search | **Tavily** (free tier) or **SerpAPI**; fallback: curated JSON | Product search with URLs and prices. |
| Trust checks | Python: `python-whois`, `ssl`, `httpx`, `BeautifulSoup`, `python-Levenshtein` | Mostly free; no paid APIs needed. |
| Safe Browsing | **Google Safe Browsing API** (free key) | Real threat intelligence. |
| Database | **MongoDB Atlas** (free tier) + `motor` | Stores investigations, receipts, preferences; hits the MongoDB track. |
| Payments | **Mock Visa Intelligent Commerce flow** | Real VIC access is unlikely in 21 hours; mock the flow and label it. |
| Deploy | **Vercel** (frontend) + **Render/Fly.io/Railway** (backend) + Atlas | Free tiers; deploy Saturday night. |

### 4.2 What each piece actually does

**React + Vite.** The browser app. One page with four states: discovery, results, checkout, receipt. Vite starts in seconds and hot-reloads.

**Tailwind + shadcn/ui.** Tailwind gives you utility classes; shadcn/ui gives you pre-built buttons, cards, dialogs, badges, and skeletons that already look good. You copy the components into your repo and style them.

**Framer Motion.** Makes the investigation feel alive: cards slide in, scores count up, flagged listings get wiped out. This is a big part of the UX score.

**FastAPI.** Your backend. You define routes like `/api/search` and `/api/investigate`. It handles async work well — important because five checks run at once.

**SSE (Server-Sent Events).** A one-way stream from server to browser. The server keeps the connection open and pushes events: `check`, `score`, `done`. The browser listens with `EventSource`. It's simpler than WebSockets and perfect here because the browser only needs to receive.

**Gemini / OpenAI.** The LLM does three jobs: (1) turn a vague request into a good search query, (2) write human-readable explanations of check results, (3) reason about brand impersonation. **The LLM does not compute the trust score.** The score is deterministic code. This matters for trust and for judging.

**Tavily / SerpAPI.** Search APIs that return product listings with titles, prices, URLs, and images. If they fail or rate-limit, fall back to a curated JSON catalog of 12 products. The demo must never break because of a search API.

**Trust checks.** Small Python modules. Each takes a domain or URL, returns `{name, status, detail, severity}`. They run in parallel with `asyncio.gather`.

**MongoDB Atlas.** Stores each investigation (product, checks, score, verdict) and each receipt. It gives you a "history" screen and hits the MongoDB side track. Use `motor` for async access.

**Mock Visa flow.** You simulate the VIC steps: create a mandate, confirm with a passkey, issue a one-time token, run a test transaction, generate a receipt. The UI should look like a real payment sheet. Label it "prototype" in the Devpost, but make the demo feel real.

### 4.3 What to mock vs. what to make real

| Layer | Real | Mock | Why |
|---|---|---|---|
| Product search | Tavily/SerpAPI for 2 queries | Curated 12-product catalog | Reliability |
| WHOIS | ✅ Real | — | Free, fast, impressive |
| SSL | ✅ Real | — | Free, fast |
| Safe Browsing | ✅ Real (free key) | Static flagged list | API key may be unavailable |
| Reddit sentiment | ✅ Real public JSON | Static quotes | Rate limits |
| Page flags | ✅ Real `httpx` + `BeautifulSoup` | Static flags | Speed |
| Brand impersonation | ✅ Levenshtein + LLM | Static examples | Accuracy |
| Price anomaly | ✅ Median of trusted prices | Mock price table | Data |
| Trust score | ✅ Deterministic code | — | This is the core |
| LLM explanations | ✅ Gemini/OpenAI | Template fallback | API failures |
| Visa token | — | ✅ Mock | No production access |
| Checkout / shipping | — | ✅ Mock | No real merchant |
| Receipt | ✅ Real (stored in Mongo) | — | Easy and valuable |

**Rule of thumb:** make the checks real, make the payment flow convincing and clearly labeled as a prototype.

### 4.4 API contracts (agree on these before you split up)

```
POST /api/search
  body: { "query": "noise cancelling headphones under 300" }
  returns: { "products": [Product] }

GET /api/investigate/{product_id}   → text/event-stream
  event: check   data: { "check": TrustCheck }
  event: score   data: { "score": 92, "verdict": "trusted" }
  event: done    data: { "product_id": "...", "score": 92, "verdict": "trusted" }

POST /api/checkout
  body: { "product_id": "...", "mandate": { "max_amount": 300, "merchant": "..." } }
  returns: { "checkout_id": "...", "token_last4": "4242", "status": "pending_passkey" }

POST /api/confirm
  body: { "checkout_id": "...", "passkey_assertion": "..." }
  returns: { "receipt": Receipt }

GET /api/receipt/{receipt_id}
  returns: { "receipt": Receipt }
```

**Data shapes:**

```ts
type Product = {
  id: string;
  title: string;
  price: number;
  merchant: string;
  domain: string;
  image_url: string;
  product_url: string;
  category: string;
};

type TrustCheck = {
  name: string;                 // "Domain age", "Safe Browsing", ...
  status: "passed" | "warning" | "failed";
  detail: string;               // human-readable evidence
  severity: number;             // 0..1
  evidence_url?: string;
};

type Investigation = {
  id: string;
  product_id: string;
  checks: TrustCheck[];
  score: number;                // 0..100
  verdict: "trusted" | "caution" | "danger";
  created_at: string;
};

type Receipt = {
  id: string;
  product_id: string;
  merchant: string;
  amount: number;
  token_last4: string;
  trust_score: number;
  checks_summary: string;
  created_at: string;
};
```

---

## 5. The trust engine

### 5.1 The five checks

Each check is a small function. Run them with `asyncio.gather` so they overlap.

| # | Check | How it works | What the user sees |
|---|---|---|---|
| 1 | **Domain age** | `python-whois` on the merchant domain. < 90 days is a warning; < 30 days is critical. Also check registrar and TLD. | "Domain registered 12 days ago — high risk." |
| 2 | **SSL certificate** | Python `ssl` / `cryptography`: issuer, age, hostname match. Free certs on a brand-new domain are a warning, not a fail. | "Let's Encrypt certificate issued 9 days ago." |
| 3 | **Safe Browsing** | Google Safe Browsing API lookup. A hit is a **fatal flag**. | "Listed as a phishing/malware site." |
| 4 | **Reddit sentiment** | Search Reddit's public JSON for the domain + "scam"; classify mentions with the LLM or simple keywords. | "3 scam reports in r/Scams in the last year." |
| 5 | **Page flags** | Fetch the product page; look for urgency language ("only 2 left!"), missing return policy, missing contact info, suspicious payment methods, no HTTPS, fake countdowns. | "No return policy; countdown timer; only crypto accepted." |

**Optional stretch checks:** brand impersonation (Levenshtein distance from a brand list + LLM confirmation), price anomaly (50%+ below the trusted median), seller verification (marketplace seller age/rating).

### 5.2 Scoring (copy this logic — it's simple and defensible)

```
For each check:
  failed  → deduct severity × 40
  warning → deduct severity × 15
  passed  → 0

Start at 100, clamp to 0..100.

Fatal flags (override everything):
  Safe Browsing failed        → 0
  Brand impersonation failed  → 5
  Page flags failed + domain failed → 0
  Domain severity ≥ 0.85      → 5

Verdict:
  ≥ 70 → trusted
  ≥ 40 → caution
  < 40 → danger
```

**Known-retailer allowlist.** Keep a list of 150+ trusted domains (Amazon, Best Buy, Walmart, Nordstrom, Target, etc.). If the domain is on the list, score it 0 and skip the expensive checks. This makes the demo fast and reliable, and it mirrors what Sniff does.

**Only `trusted` products are eligible for the best pick.** Sort by trust score descending, then price ascending. Show the savings vs. the median price.

### 5.3 Streaming

When a product is investigated:

1. Backend sends `event: check` for each result as it finishes.
2. Frontend appends a check card to the product.
3. Backend sends `event: score` when all checks are done.
4. Frontend animates the score and verdict.
5. Backend sends `event: done` and closes the stream.

This is the "watch the AI investigate" effect. Do not wait for all checks before showing anything — that kills the magic.

### 5.4 The allowlist trick

Put 10–15 known stores in `known_domains.py`. For those, return all checks passed and score 0 instantly. For unknown stores, run the real checks. This gives you a reliable demo: the known stores look clean, and the one suspicious mock store lights up red.

Create 2–3 **mock suspicious stores** with realistic names (e.g., `premium-audio-deals.shop`) so the demo always has a villain. Your mock catalog should include at least one obviously bad listing.

---

## 6. The Visa payment moment

This is what makes it a **Visa** project instead of a trust tool. Do not skip it.

### 6.1 The flow (what the user sees)

```
[Checkout sheet]
  Merchant: Best Buy
  Product: Sony WH-1000XM5
  Amount: $249.00
  Trust score: 92 / trusted ✅

  Spending mandate
  You authorize Sniff to pay up to $300 at Best Buy
  for this product, valid for 10 minutes.

  [ Confirm with passkey ]   ← biometric prompt

[Passkey confirmed]
  Visa token •••• 4242
  Merchant-specific · one-time use

[Transaction approved]
  Receipt #SNF-8F2A
  $249.00 paid to Best Buy
  Trust checks passed: 5/5
  [ Share trust receipt ]
```

### 6.2 What's real vs. mocked

| Piece | Real? | What to do |
|---|---|---|
| Spending mandate | Mock | Show a clear cap, merchant, product, expiry. Store it. |
| Passkey prompt | Mock or real WebAuthn | A convincing modal is enough; `navigator.credentials` is a bonus. |
| Visa token | Mock | Display a tokenized credential with last-4 and "merchant-specific." |
| Transaction | Mock | Show approved/declined; include a test decline for the demo. |
| Receipt | Real | Store in MongoDB; render a shareable page. |

**Be honest in the Devpost:** "We prototyped the Visa Intelligent Commerce flow — mandate, passkey, tokenization, receipt. In production this would call Visa Token Service and Visa Payment Passkey." Judges reward clarity, not fake claims.

### 6.3 The spending mandate (why it matters)

A mandate is the user's explicit permission: **who** can spend, **how much**, **where**, and **for how long**. It maps to Visa's "payment-instruction controls" and to the Trust & Responsibility criterion. Show it as a human-readable card, not a JSON blob.

### 6.4 The passkey (why it matters)

A passkey is a biometric confirmation (Face ID / fingerprint) that the human — not just the agent — approved the payment. It's the "human in the loop" moment. Even a mock modal earns UX and Trust points because it makes the consent visible.

### 6.5 The trust receipt (the shareable artifact)

The receipt is your differentiator. It contains:

- Merchant and product.
- Amount and token last-4.
- Trust score at the time of purchase.
- The five checks, each with a one-line result.
- What was **not** verified (e.g., "return policy could not be confirmed").
- A share link.

This turns a private checkout into a **public trust signal**. It also gives you a viral artifact for Cloudforce and a clean end-card for the video.

### 6.6 The core rule

> **The agent cannot initiate payment to a merchant it cannot verify.**

If the verdict is `caution` or `danger`, the checkout button is disabled and the agent explains why. This is the single most important sentence in your pitch. It is the difference between "a shopping agent" and "a trust layer for agentic commerce."

---

## 7. How you hit the Visa rubric

**Weights:** Innovation 25% · UX 25% · Tech 20% · Commerce 15% · Trust 15%.  
**Note:** the rubric table lists UX at 20% but the bullets say 25% and sum to 100%. Build as if UX is 25%; confirm with a Visa mentor.

### 7.1 Innovation — 25%

**What judges reward:** a creative recombination of the right "ingredients," not a generic chatbot.

**What you do:**
- Combine **visible trust investigation** (Sniff) with **trust-gated payment** (Visa). Most teams do one or the other.
- The rule "the agent can only pay verified merchants" is a novel product constraint.
- The **trust receipt** turns a private score into a shareable artifact.
- The **purge** interaction makes trust physical and memorable.

**Say this:** "We didn't build another shopping chatbot. We built the trust layer that agentic commerce needs: the agent investigates, scores, and is only allowed to pay merchants it can verify."

### 7.2 UX — 25%

**What judges reward:** intuitive, useful, seamless, polished under pressure.

**What you do:**
- **Guided discovery:** 2–3 questions, not a blank chat. The user never faces an empty box.
- **Live investigation:** checks stream in; the user sees progress instead of a spinner.
- **One-screen verdict:** a big trust badge, a short reason, and a clear next action.
- **Purge animation:** flagged listings disappear; the safe list remains.
- **One-tap checkout:** mandate → passkey → done. No forms.
- **Receipt:** a clean, shareable summary.
- **Polish:** consistent spacing, one accent color, real product images, skeleton loaders, no default browser styles.

**Say this:** "Every second of the demo shows the AI working. The user never waits without seeing why."

### 7.3 Technology Execution — 20%

**What judges reward:** effective use of AI and supporting tech, not just an API call.

**What you do:**
- **Parallel checks** with `asyncio.gather` — real concurrency, not a fake loading bar.
- **SSE streaming** — a real-time protocol, not polling.
- **Deterministic scoring + LLM explanations** — the LLM explains, the code decides.
- **Structured outputs** — typed JSON from the LLM, validated with Pydantic.
- **MongoDB** — persistence for investigations and receipts.
- **Error handling** — every check has a fallback; the demo never hard-fails.
- **Allowlist** — a pragmatic shortcut that improves reliability.
- **Mock VIC flow** — a clear, documented simulation of tokenization and mandates.

**Say this:** "The score is deterministic code, not a vibe from an LLM. The model's job is to explain and to reason about impersonation; the decision is auditable."

### 7.4 Commerce Impact — 15%

**What judges reward:** engagement, conversion, loyalty, speed, or merchant outcomes.

**What you do:**
- **Conversion:** trust is the bottleneck for unfamiliar stores; a verified badge reduces hesitation.
- **Savings:** show the price delta vs. the median ("you save $46").
- **Speed:** guided discovery + best pick = fewer tabs, faster decision.
- **Merchant outcomes:** verified merchants get a badge and more agent traffic.
- **The purchase actually completes** — that's the commerce moment.
- **Numbers to cite:** online fraud losses ($12.5B in 2024), 1 in 5 US adults scammed online, cart abandonment on unfamiliar stores.

**Say this:** "Trust is the conversion problem in agentic commerce. We make trust visible, then we close the sale."

### 7.5 Trust & Responsibility — 15%

**What judges reward:** privacy, transparency, security, responsible AI.

**What you do:**
- **Evidence, not just a score:** every verdict shows the checks and the details.
- **Uncertainty:** explicitly show what could not be verified.
- **Spending mandate:** a hard cap, a merchant, an expiry.
- **Passkey:** human confirmation, not silent agent spending.
- **No PII sharing:** the agent shares only what checkout needs.
- **Audit log:** every investigation and payment is stored.
- **Appeal path:** a flagged merchant can submit evidence; a human reviews.
- **VEYZL audit:** run it on the repo and show one finding that changed the build.

**Say this:** "Trust is not a badge we invented. It's evidence the user can inspect, a mandate they control, and a passkey they approve."

### 7.6 Scorecard summary

| Criterion | Weight | Your evidence | Demo moment |
|---|---|---|---|
| Innovation | 25% | Trust-gated checkout + shareable receipt | The agent refuses to pay a `danger` merchant |
| UX | 25% | Guided discovery, live checks, purge, one-tap pay | The investigation streaming in real time |
| Tech | 20% | Parallel checks, SSE, deterministic score, Mongo | Five checks finishing at different times |
| Commerce | 15% | Cheapest-safe pick, savings, completed purchase | "You save $46" + payment approved |
| Trust | 15% | Evidence, uncertainty, mandate, passkey, audit | The receipt showing what was verified |

---

## 8. How you hit the side tracks

**Rule:** exactly **1 title track** + up to **3 sponsored side tracks** + unlimited non-sponsored. Do not spread thin.

### 8.1 Recommended sponsored picks (choose 3)

| Track | Prize | Why it fits | What to show |
|---|---|---|---|
| **T-Mobile — Cart Whisperer** | Jetson Orin Nano / Plaud NotePin / Claude Pro | Guided discovery understands intent and fills the cart; T-Mobile's "fun track" rewards personality. | The 3-question discovery + the "best pick" cart moment. |
| **SideShift — Best Startup Idea** | $1,500 + work trial | A B2C trust layer with a merchant SaaS upside. | The business model slide: verified badge + affiliate/transaction fee. |
| **VEYZL** | $500 + lifetime pro | The agent handles payments; VEYZL audits AI safety/compliance. | The audit finding + the fix + before/after. |
| *Alternative:* **Cloudforce — Most Viral** | $1,000 / $500 | The purge animation and trust receipt are shareable. | Live engagement at judging; a shareable receipt link. |

**If you can only pick 3:** T-Mobile + SideShift + VEYZL is the most credible. Swap VEYZL for Cloudforce if you want to chase virality.

### 8.2 Non-sponsored picks (unlimited)

| Track | Why it fits | What to do |
|---|---|---|
| **DubHacks NEXT** | Startup/entrepreneurship | 3-slide pitch: problem, product, business model. |
| **MLH Gemini** | You use Gemini | Keep the Gemini calls visible; mention the model in the Devpost. |
| **MongoDB** | You use Atlas | Store investigations + receipts; show the data model. |
| **DEV Writing** | Write a blog post | "How we built a trust-gated shopping agent in 21 hours." |
| **Backboard** | Optional memory | Remember user preferences ("size M, likes Sony"). |

### 8.3 Track-by-track pitch lines

- **Visa:** "The trust layer for agentic commerce — the agent can only pay merchants it can verify."
- **T-Mobile Cart Whisperer:** "Tell it what you want in plain English; it asks the right questions and fills the cart with the cheapest *safe* option."
- **SideShift:** "Trust is the conversion problem. We sell verification to merchants and safety to shoppers."
- **VEYZL:** "We ran the audit, found a missing human-oversight control, and changed the build. Here's the before/after."
- **Cloudforce:** "Watch it purge a scam store in real time. Every purchase comes with a shareable trust receipt."
- **NEXT:** "A B2C trust layer with a B2B verification business underneath."
- **MLH Gemini:** "Gemini powers the explanations and impersonation reasoning; the score stays deterministic."
- **MongoDB:** "Every investigation and receipt is persisted; we can replay any decision."

---

## 9. The 21-hour plan

**Hacking starts:** 12:30 PM Saturday.  
**Devpost draft:** 10:30 PM Saturday (hard).  
**Final submission:** 10:00 AM Sunday (hard lock).  
**Video:** under 3 minutes, required.

### 9.1 Saturday afternoon (12:30–6:00)

| Time | What | Owner |
|---|---|---|
| 12:30–1:15 | Repo, env vars, FastAPI + Vite hello world, design tokens, mock catalog | All |
| 1:15–2:30 | `/api/search` + results grid + product cards | Backend + Frontend |
| 2:30–4:30 | 3 real checks (WHOIS, SSL, Safe Browsing) + scoring function | Backend |
| 4:30–6:00 | SSE `/api/investigate` + live check cards | Backend + Frontend |

### 9.2 Saturday evening (6:00–10:30)

| Time | What | Owner |
|---|---|---|
| 6:00–7:30 | Reddit + page-flags checks; allowlist; mock suspicious store | Backend |
| 7:30–9:00 | Trust badge, score animation, purge animation, best pick | Frontend |
| 9:00–10:00 | Visa checkout mock: mandate → passkey → token → result | Backend + Frontend |
| 10:00–10:30 | Devpost draft + rough screen recording | All |

**Submit the draft at 10:30 PM no matter what.** It can be rough; it must exist.

### 9.3 Saturday night (10:30–2:00)

| Time | What |
|---|---|
| 10:30–12:30 | Receipt screen + MongoDB persistence + share link |
| 12:30–2:00 | VEYZL audit + one finding + fix; merchant badge if time |

### 9.4 Sleep (2:00–6:00)

Sleep in shifts. At least two people should get 4 hours. A tired demo is a bad demo.

### 9.5 Sunday morning (6:00–10:00)

| Time | What |
|---|---|
| 6:00–7:00 | Final polish: spacing, colors, copy, error states |
| 7:00–8:00 | Record the 3-minute video (script in §10) |
| 8:00–9:00 | Devpost final: story, stack, screenshots, video link |
| 9:00–9:30 | Rehearse the live demo twice; test the fallback |
| 9:30–10:00 | Submit + buffer |

### 9.6 Team roles (4 people)

| Role | Owns |
|---|---|
| **Backend / agent** | FastAPI, search, scoring, SSE, LLM calls, error handling |
| **Trust / data** | WHOIS, SSL, Safe Browsing, Reddit, page flags, mock catalog, allowlist |
| **Frontend / UX** | React, Tailwind, shadcn, animations, checkout UI, receipt UI |
| **Payments / demo** | Visa mock flow, MongoDB, VEYZL, video, Devpost, rehearsal |

If you have 3 people: merge Payments/Demo into Backend and Frontend.

---

## 10. The 3-minute video script

Visa judging is **virtual** — the video is what they see. Treat it as the product.

| Time | Visual | Voiceover |
|---|---|---|
| 0:00–0:15 | Title card + a scam-store headline | "One in five Americans has lost money to an online scam. The problem isn't finding products — it's trusting the store." |
| 0:15–0:35 | Discovery screen, 3 questions | "Meet Sniff. Tell it what you want. It asks the right questions, then searches Amazon, Best Buy, Walmart, and Nordstrom." |
| 0:35–1:20 | Results grid; checks streaming into cards | "For every listing, it runs five checks in parallel: domain age, SSL, Safe Browsing, Reddit sentiment, and page red flags. Watch the evidence land in real time." |
| 1:20–1:45 | One listing goes red; PURGE CURSED | "This store was registered twelve days ago and has three scam reports. It's out. The rest get a trust score from zero to one hundred." |
| 1:45–2:10 | Best pick + savings | "Sniff picks the cheapest *trusted* option — not the cheapest option. You save forty-six dollars and avoid the risk." |
| 2:10–2:40 | Checkout: mandate → passkey → token → approved | "Now the Visa moment. A spending mandate caps the amount. A passkey confirms the human. A one-time token pays the merchant. The agent can only pay a store it can verify." |
| 2:40–3:00 | Trust receipt + end card | "Every purchase comes with a trust receipt: what was verified, what wasn't, and why. That's how agentic commerce earns trust." |

**Recording tips:**
- 1080p, clean browser window, no notifications.
- Zoom in on the check cards; the text must be readable.
- Cut dead time; every second should show the product working.
- Record the voiceover separately and lay it over the screen capture.
- End with the repo URL and a one-line tagline.

---

## 11. Devpost draft template

**Title:** Sniff + Visa — the trust layer for agentic commerce

**Tagline:** The AI shopping agent that investigates every listing, then only pays merchants it can verify.

**Inspiration:** Online shopping fraud is massive and invisible. Shoppers can't check WHOIS records or threat databases; they guess. Agentic commerce makes this worse: an AI can now spend your money, but it has no concept of trust.

**What it does:**
- Guided discovery and multi-retailer search.
- Five parallel fraud checks per listing, streamed live.
- A 0–100 trust score and trusted/caution/danger verdict.
- The cheapest **trusted** recommendation.
- A Visa checkout with a spending mandate, passkey, and tokenized payment.
- A shareable trust receipt.

**How we built it:**
- React + Vite + Tailwind + shadcn/ui + Framer Motion.
- FastAPI + Python for the agent, checks, and SSE.
- Gemini/OpenAI for query refinement and explanations.
- `python-whois`, `ssl`, Google Safe Browsing, Reddit public JSON, `httpx` + BeautifulSoup.
- MongoDB Atlas for investigations and receipts.
- Mocked Visa Intelligent Commerce flow: mandate → passkey → token → receipt.

**Challenges:**
- Making five checks fast and reliable in 21 hours.
- Keeping the score deterministic while the LLM writes explanations.
- Designing a payment flow that feels real without production Visa access.
- Avoiding false positives and showing uncertainty honestly.

**Accomplishments:**
- A live investigation the user can watch.
- A trust score that is auditable, not a black box.
- A payment moment that puts the human in the loop.
- A shareable receipt that makes trust visible.

**What we learned:**
- Trust is a UX problem, not just a security problem.
- Deterministic scoring + LLM explanation is the right split.
- The demo needs a villain and a hero: one scam store, one safe pick.

**What's next:**
- Real Visa Intelligent Commerce integration.
- A Chrome extension.
- A merchant verification dashboard.
- More signals: seller history, price history, counterfeit detection.

**Built with:** React, Vite, TypeScript, Tailwind, shadcn/ui, Framer Motion, FastAPI, Python, Gemini, MongoDB, Google Safe Browsing, WHOIS, SSE.

---

## 12. Judge Q&A prep

**"How is this different from Sniff?"**
> Sniff investigates and recommends. We added the missing half of the journey: a Visa checkout with a spending mandate, a passkey, and a tokenized payment — and a hard rule that the agent cannot pay a merchant it cannot verify. We also turned the score into a shareable trust receipt.

**"Is the trust score real, or is it an LLM vibe?"**
> The score is deterministic Python: weighted check severities, fatal flags, and thresholds. The LLM only writes the explanation and reasons about brand impersonation. Every decision is reproducible and stored in MongoDB.

**"What about false positives?"**
> Every verdict shows the evidence and explicitly says what could not be verified. A flagged merchant can submit an appeal; a human reviews it. We block payment, not speech.

**"Did you use real Visa APIs?"**
> We prototyped the Intelligent Commerce flow: mandate, passkey, tokenization, receipt. In production this would call Visa Token Service and Visa Payment Passkey. We're clear about what's mocked.

**"What's the business model?"**
> Two-sided: a merchant verification badge and dashboard (B2B SaaS), plus an affiliate/transaction fee on completed purchases (B2C). The trust layer is the moat.

**"Why now?"**
> Agentic commerce is moving from demo to production. The bottleneck is trust: merchants need to prove they're safe, and users need to approve spending. That's the layer we built.

**"What would you do with another week?"**
> Real VIC integration, a merchant dashboard, a Chrome extension, and more signals — seller history, price history, counterfeit detection.

---

## 13. Risks and fallbacks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Search API fails or rate-limits | High | Curated 12-product catalog + `DEMO_MODE=true` |
| Safe Browsing key unavailable | Medium | Static flagged-domain list; label it |
| Reddit rate-limits | Medium | Cache results; fall back to static quotes |
| Page scraping blocked | Medium | Use a saved HTML fixture for the demo |
| LLM API slow or down | Medium | Template explanations; pre-warm the demo |
| Payment mock looks fake | Medium | Realistic UI, clear labels, explain the real flow |
| Too many tracks | High | Pick 3 sponsored max; don't build track-specific features |
| UI looks default | High | shadcn/ui + one accent color + Framer Motion |
| Running out of time | High | Follow the cut list; protect the payment moment |
| False-positive accusation | Low | Synthetic data; appeal path; no real brand named as fake |

**Demo insurance:** record a full backup video Saturday night. If the live demo breaks, play the video.

---

## 14. Plain-English glossary

| Term | What it means |
|---|---|
| **SSE (Server-Sent Events)** | A one-way stream from server to browser. The server pushes events; the browser listens with `EventSource`. Simpler than WebSockets. |
| **LLM function calling / tool use** | The model returns a structured request to run a function (e.g., `whois_lookup("store.com")`); your code runs it and returns the result. |
| **Agentic commerce** | AI agents that shop and pay on a user's behalf. |
| **Visa Intelligent Commerce (VIC)** | Visa's framework for agentic payments: tokens, mandates, passkeys, and payment controls. |
| **Tokenization (VTS)** | Replacing a card number with a one-time, merchant-specific token. If it leaks, it's useless elsewhere. |
| **Payment mandate** | The user's explicit permission: who can spend, how much, where, and for how long. |
| **Passkey / WebAuthn** | Biometric or device-based confirmation (Face ID, fingerprint) that a human approved an action. |
| **WHOIS** | A public record of who registered a domain and when. A very new domain is a red flag. |
| **Typosquatting** | A lookalike domain (e.g., `arnazon.com`) used to impersonate a brand. |
| **Allowlist** | A list of known-good domains that skip expensive checks. |
| **Weighted score** | A score where each signal counts for a different amount. |
| **Fatal flag** | A single finding that overrides all other signals (e.g., a Safe Browsing hit = 0). |
| **SSE event** | One message in the stream, e.g., `event: check` with a JSON payload. |
| **Pydantic** | Python library for validating data shapes. |
| **Motor** | Async Python driver for MongoDB. |
| **MCP (Model Context Protocol)** | A standard way for AI agents to call tools and data sources. The Visa reference agent uses it. |
| **WebAuthn** | The browser standard behind passkeys. |

---

## 15. Suggested repo structure

```
sniff-visa/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + CORS
│   │   ├── api/
│   │   │   ├── search.py           # POST /api/search
│   │   │   ├── investigate.py      # GET /api/investigate/{id} (SSE)
│   │   │   ├── checkout.py         # POST /api/checkout, /api/confirm
│   │   │   └── receipt.py          # GET /api/receipt/{id}
│   │   ├── services/
│   │   │   ├── search.py           # Tavily/SerpAPI + fallback catalog
│   │   │   ├── scoring.py          # deterministic score + verdict
│   │   │   ├── agent.py            # Gemini/OpenAI calls
│   │   │   └── visa.py             # mock mandate/token/passkey
│   │   ├── checks/
│   │   │   ├── whois.py
│   │   │   ├── ssl.py
│   │   │   ├── safe_browsing.py
│   │   │   ├── reddit.py
│   │   │   └── page_flags.py
│   │   ├── models.py               # Pydantic models
│   │   ├── db.py                   # MongoDB (motor)
│   │   └── known_domains.py        # allowlist
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Discovery.tsx
│   │   │   ├── ResultsGrid.tsx
│   │   │   ├── ProductCard.tsx
│   │   │   ├── TrustBadge.tsx
│   │   │   ├── CheckStream.tsx
│   │   │   ├── PurgeAnimation.tsx
│   │   │   ├── CheckoutSheet.tsx
│   │   │   └── TrustReceipt.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── sse.ts
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.ts
├── data/
│   └── products.json               # fallback catalog + suspicious store
├── README.md
└── .env.example
```

**`.env.example`:**

```text
# AI
GEMINI_API_KEY=
OPENAI_API_KEY=

# Search
TAVILY_API_KEY=
SERPAPI_KEY=

# Safety
GOOGLE_SAFE_BROWSING_KEY=

# Database
MONGODB_URI=

# Demo
DEMO_MODE=true
```

---

## 16. Sources

- [Sniff repo](https://github.com/thenerd31/sniff) — reference architecture, not a code base.
- [Sniff project page](https://yifank.github.io/projects/sniff/)
- [Sniff Devpost](https://devpost.com/software/sniff-l9xk1q)
- [Visa Intelligent Commerce](https://developer.visa.com/capabilities/visa-intelligent-commerce)
- [Visa VIC reference agent](https://github.com/visa/vic-reference-agent)
- [Visa Payment Passkey](https://developer.visa.com/capabilities/visa-payment-passkey)
- [Google Safe Browsing API](https://developers.google.com/safe-browsing)
- [Tavily](https://tavily.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Framer Motion](https://www.framer.com/motion/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)
- [FastAPI](https://fastapi.tiangolo.com/)
- [sse-starlette](https://github.com/sysid/sse-starlette)

---

## 17. The three sentences to remember

1. **The agent investigates every listing, visibly.**
2. **It recommends the cheapest *trusted* option, not the cheapest option.**
3. **It cannot pay a merchant it cannot verify.**

If the demo shows those three things clearly, you have a strong Visa submission.
