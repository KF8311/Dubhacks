# Project B — "Test Kitchen": Full Build Rundown

**What this doc is:** A plain-English plan for the Test Kitchen idea from `visa-ideas.md`. It covers what the product is, how the simulation actually works, what each part of the tech stack does, how well it fits the Visa track (honestly), how it stacks with side tracks, and a 21-hour build plan.

**Team:** 3–4 people, AI/backend strong.  
**Track:** Visa "Reimagine Shopping" (title track) — with a caveat, explained in §3.  
**Original idea:** `visa-ideas.md` §3.11 — "Digital clones of your customers test your promotions before you run them."

---

## 0. The one-paragraph version

A merchant uploads a product catalog and a few customer segments. Test Kitchen builds **digital clones** of those customers — not random chatbots, but personas grounded in the merchant's own segment data. The merchant picks two or three offers to test: "20% off bundles," "free shipping," "BNPL at checkout." The system simulates thousands of synthetic shoppers deciding between those offers, then reports conversion lift, revenue, margin impact, cannibalization, and which segment responds. The merchant gets a clear recommendation: **run this offer for this segment, not that one.** The LLM writes the personas and explains the decisions; the math makes the decisions. That split is what makes it credible.

**The one-line pitch:** *A wind tunnel for promotions — test your offer on digital clones of your customers before you spend a dollar.*

---

## 1. What Test Kitchen is (plain English)

Think of a merchant deciding between two promotions:

- **Offer A:** 20% off if you buy a bundle.
- **Offer B:** free shipping.

Today, the merchant guesses, or runs a real A/B test that takes weeks and costs real revenue. Test Kitchen lets them **simulate the test first**.

It works in four steps:

1. **Describe your customers.** The merchant provides segments (e.g., "deal seekers," "loyalists," "convenience shoppers") or a small transaction history. The system turns each segment into a persona with traits: price sensitivity, shipping sensitivity, discount affinity, brand loyalty, payment preference.
2. **Describe the offers.** The merchant enters two or three offers: discount percentage, free shipping, bundle price, payment methods.
3. **Run the simulation.** Each persona "shops" the offers thousands of times. The system counts how many would buy under each offer.
4. **Read the result.** A dashboard shows conversion lift, revenue, margin, cannibalization, and a recommendation.

**What it is not:** It is not a replacement for a real A/B test. It is a **pre-test** — a cheap, fast way to narrow ten possible promotions down to the two worth testing for real.

---

## 2. The user journey (what the demo looks like)

| Step | What the merchant sees | What happens behind the scenes |
|---|---|---|
| 1. Connect | "Import catalog" and "Choose segments" | Loads a mock catalog and 5 customer segments (RFM-based). |
| 2. Build personas | Five persona cards: name, photo, traits, quote | LLM writes the persona's voice; traits come from the segment data. |
| 3. Set offers | Two offer cards: "20% off bundles" vs. "free shipping" | Offers are structured objects with price, shipping, discount, payment terms. |
| 4. Simulate | A progress bar: "Simulating 1,000 shoppers per segment…" | Monte Carlo runs in NumPy — usually under a second. |
| 5. Compare | A results table/chart: conversion, lift, revenue, margin per segment | Aggregates per persona and per offer. |
| 6. Drill down | Click "Deal Seeker Dana" → "I'd buy the bundle because I was already buying two items; free shipping doesn't change my mind." | LLM generates the rationale from the persona's traits and the offer. |
| 7. Decide | Recommendation card: "Run free shipping for Convenience Chris; keep 10% off for Loyalist Lena." | Rule-based ranking + LLM-written explanation. |
| 8. Preview | A consumer checkout preview of the winning offer, with Visa payment options | Static mock of the shopper-facing experience. |

---

## 3. Track fit — the honest assessment

You asked how well this hits the tracks. Here is the candid answer.

### 3.1 Visa fit: medium, not automatic

**Score: ~6.5 / 10 as written.** Here's why.

**What works for Visa:**
- **Commerce Impact (15%)** is explicitly about "customer engagement, conversion, loyalty, speed, or **merchant outcomes**." Test Kitchen is a direct merchant-outcome tool. This is its strongest criterion.
- **Technology Execution (20%)** is strong: multi-agent simulation, Monte Carlo, calibration, LLM narration.
- **Innovation (25%)** is strong: very few student teams build merchant-side simulation, and almost none simulate **payment-linked offers**.
- **Trust (15%)** can be strong if you are transparent about synthetic data and run a bias audit.

**What works against Visa:**
- Visa's theme is **"Reimagine Shopping"** — the consumer shopping experience. Test Kitchen is a **B2B merchant analytics tool**. There is no shopper on screen for most of the demo.
- **UX (25%)** is the weak criterion: B2B dashboards are less emotionally compelling than consumer apps. Judges score what they feel, and a table of conversion rates does not feel like shopping.
- The original idea's score was **4.40**, with UX 3.5 and Trust 3.5. Those are the two criteria to fix.

**How to raise the Visa fit (do these):**
1. **Make the offers payment-linked.** Instead of generic "20% off," test offers that involve Visa: "pay in full vs. BNPL," "card-linked offer," "free shipping over $50," "loyalty multiplier." This puts payments at the center.
2. **Add a consumer preview.** A toggle that shows the winning offer as a shopper would see it at checkout, with a Visa card/token. This gives judges a human moment.
3. **Frame the output as a shopping-experience decision.** "Which checkout experience converts this segment?" not "which discount maximizes margin?"
4. **Show one persona reacting on screen.** A face, a quote, a decision. That is the UX moment.
5. **Use a specific vertical.** Grocery or fashion. A generic "e-commerce" demo feels abstract; a grocery basket feels real.

With those changes, Visa fit rises to roughly **7.5–8 / 10** — still below a consumer-native idea like Table Talk or Sniff + Visa, but viable.

### 3.2 Side-track fit

| Track | Fit | Why | What to emphasize |
|---|---|---|---|
| **SideShift — Best Startup Idea** | **9/10** | Classic B2B SaaS with a clear buyer, budget, and ROI. | Pricing, market size, moat, wedge. |
| **VEYZL** | **8/10** | Synthetic personas can encode bias; VEYZL can audit the simulation. | One finding + fix + before/after. |
| **DubHacks NEXT** | **9/10** | Startup/entrepreneurship fit. | 3-slide pitch. |
| **MLH Gemini** | **8/10** | Gemini generates personas and rationales. | Model use visible in the demo. |
| **MongoDB** | **8/10** | Stores catalogs, personas, runs, results. | Data model + persistence. |
| **DEV Writing** | **8/10** | "How we built a credible simulation in 21 hours" is a great post. | Methodology write-up. |
| **Tiger Data** | **6/10** | Time-series of simulation runs; optional. | Only if you store run history. |
| **Cloudforce** | **4/10** | Not viral; B2B dashboards don't spread. | Skip unless going for the raffle. |
| **T-Mobile** | **4/10** | Weak fit unless framed as "Household Mix" segmentation. | Stretch; not recommended. |
| **Photon** | **4/10** | Could add "text the simulator," but it's scope creep. | Optional. |
| **Backboard** | **5/10** | Persona memory across runs; optional. | Nice-to-have. |

### 3.3 Recommended track stack

**Title:** Visa.

**Sponsored (pick 3):**
- **SideShift** — strongest fit; the startup story writes itself.
- **VEYZL** — the bias audit is a real differentiator for a synthetic-persona product.
- **Cloudforce** — weak fit, but every entry is a raffle ticket; low cost to add. Swap for **T-Mobile** only if you build a household-segment feature.

**Non-sponsored:** DubHacks NEXT, MLH Gemini, MongoDB, DEV Writing, Tiger Data.

**Do not** submit to Photon, Perceptron, SpaceXAI, or Solana unless you actually build the integration. Spreading thin hurts the demo.

---

## 4. What you're actually building (scope)

### 4.1 Must-have

- [ ] A mock catalog (20–30 products) and 5 customer segments.
- [ ] Five persona cards with traits and LLM-written descriptions.
- [ ] A utility-based decision model (see §6).
- [ ] Monte Carlo simulation: 1,000 shoppers per segment per offer.
- [ ] Results: conversion, lift, revenue, margin, cannibalization.
- [ ] A dashboard with at least two charts.
- [ ] A persona drill-down with an LLM rationale.
- [ ] A recommendation card.
- [ ] A consumer checkout preview with Visa payment options.
- [ ] A 3-minute video.

### 4.2 Nice-to-have

- [ ] Calibration/backtest on a held-out historical promotion.
- [ ] Confidence intervals on the lift.
- [ ] A tornado chart of assumption sensitivity.
- [ ] VEYZL audit + before/after fix.
- [ ] MongoDB persistence of runs.
- [ ] A "compare runs" history.
- [ ] Export to CSV/PDF.

### 4.3 Cut list (in order)

1. Export.
2. Compare runs.
3. Tornado chart.
4. Calibration/backtest.
5. MongoDB (use in-memory).
6. Consumer preview (last resort — it's your Visa fit).
7. Two of the five personas.

**Never cut:** the simulation, the lift number, the persona drill-down, the recommendation.

---

## 5. Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Browser — React + Vite + Tailwind + shadcn/ui + Recharts    │
│                                                              │
│  Segments → Personas → Offers → Results → Drill-down →       │
│  Recommendation → Consumer Preview                           │
│         ▲                    ▲                               │
│         │ REST               │ REST                          │
└─────────┼────────────────────┼───────────────────────────────┘
          │                    │
┌─────────┴────────────────────┴───────────────────────────────┐
│  FastAPI backend (Python)                                    │
│                                                              │
│  /api/personas      /api/simulate      /api/recommend        │
│       │                   │                  │               │
│       ▼                   ▼                  ▼               │
│  Persona service     Simulation engine    LLM narration      │
│  (segments + LLM)    (NumPy Monte Carlo)  (rationales)       │
│       │                   │                  │               │
│       └───────────────────┴──────────────────┘               │
│                           │                                  │
│                     MongoDB Atlas                            │
│              (catalogs, personas, runs, results)             │
└──────────────────────────────────────────────────────────────┘
```

**Key architectural decision:** the simulation is **synchronous and fast**. One thousand shoppers × five personas × three offers is about 15,000 draws — NumPy does that in milliseconds. You do **not** need a queue, a worker, or SSE for the simulation itself. The only slow part is the LLM generating persona descriptions and rationales; call it once per persona (5–8 calls), not once per shopper.

---

## 6. The simulation — the part you're unsure about

This is the heart of the project. Read this section twice.

### 6.1 What "simulation" means here

A simulation is just **running a model many times with slightly different inputs** and looking at the distribution of outcomes.

Two analogies:

- **A focus group, but synthetic.** You create five representative customers and ask each one, "Would you buy at this price, with this shipping, with this payment option?" Then you ask the question 1,000 times with small variations.
- **A weather forecast.** One run gives you a number; 1,000 runs give you a range and a confidence level. You report "14% lift, 90% CI [9%, 19%]," not "14%."

**What it is not:**
- It is not 1,000 LLM calls. That would be slow, expensive, and random.
- It is not a random number generator. The decisions are structured.
- It is not a guarantee. It is a decision aid.

### 6.2 The three layers

The simulation has three layers. Keep them separate in your code and in your explanation.

| Layer | What it is | Who computes it |
|---|---|---|
| **1. Personas** | Five customer archetypes with traits and a baseline conversion rate. | Segment data + LLM narration. |
| **2. Decision model** | A formula that turns an offer into a purchase probability for each persona. | Python math. |
| **3. Market simulation** | Thousands of draws per persona, aggregated into conversion, lift, revenue, margin. | NumPy Monte Carlo. |

### 6.3 Layer 1 — personas (grounded, not random)

Do **not** ask the LLM to invent customers from nothing. Ground them in data.

**Step 1: Create a mock transaction dataset.** 500–1,000 rows with:
- customer_id
- age
- income bracket
- last_purchase_days_ago (recency)
- purchases_last_year (frequency)
- average_order_value (monetary)
- preferred_category
- preferred_payment (card / BNPL / wallet)
- price_sensitivity (derived or assigned)

**Step 2: Segment with RFM.** Use recency, frequency, and monetary value to create 5 segments. Simple rules are fine:
- **Loyalists:** recent, frequent, high AOV.
- **Deal Seekers:** frequent, high price sensitivity.
- **Convenience Shoppers:** medium frequency, high shipping sensitivity.
- **Budget Buyers:** low AOV, high price sensitivity, BNPL preference.
- **Premium Patrons:** low frequency, high AOV, low price sensitivity.

**Step 3: Compute segment traits.** For each segment, average the traits:
- `price_sensitivity` (0–1)
- `shipping_sensitivity` (0–1)
- `discount_affinity` (0–1)
- `brand_loyalty` (0–1)
- `base_conversion` (historical conversion rate)
- `aov` (average order value)
- `margin_pct` (gross margin)

**Step 4: Let the LLM write the persona.** Give it the traits and ask for a name, a one-paragraph description, and a quote. Example:

> **Deal Seeker Dana, 29.** "I never pay full price. I keep a cart open for a week waiting for a code. If the discount is real, I'll buy two."
> Traits: price sensitivity 0.9 · shipping sensitivity 0.2 · discount affinity 0.9 · brand loyalty 0.3 · base conversion 6% · AOV $62 · margin 38%.

The LLM writes the **voice**, not the **numbers**. This is the same principle as Sniff: deterministic data, LLM explanation.

### 6.4 Layer 2 — the decision model

This is the part that makes the simulation credible. Do not ask the LLM "would you buy?" Use a **utility model**.

Each offer is converted into a set of value scores (0–1):

```
price_value      = 1 - (offer_price / reference_price)     # cheaper is better
shipping_value   = 1.0 if free_shipping else 0.2
discount_value   = min(discount_pct / 0.30, 1.0)           # 30%+ = max
bundle_value     = 1.0 if bundle else 0.5
payment_value    = 1.0 if offer supports preferred_payment else 0.6
```

Each persona has traits (weights). The utility of an offer for a persona is:

```
utility =
    2.0 * price_sensitivity  * price_value
  + 1.5 * shipping_sensitivity * shipping_value
  + 1.8 * discount_affinity  * discount_value
  + 1.0 * brand_loyalty      * bundle_value
  + 0.8 * payment_value
  + intercept
  + noise
```

- The **weights** (2.0, 1.5, 1.8, 1.0, 0.8) are global assumptions. Put them in a config file so you can tune them.
- The **traits** are per persona.
- The **intercept** is calibrated so the persona's baseline conversion matches the historical rate.
- The **noise** is a random draw from a normal distribution (e.g., σ = 0.5). This is what makes it a simulation rather than a single calculation.

Convert utility to a purchase probability with the **logistic function**:

```
probability = 1 / (1 + exp(-utility))
```

Then draw a random number and decide: buy if `random() < probability`.

**Why this is credible:** every decision is explainable. You can point to the exact term that drove it: "Dana bought because her price sensitivity (0.9) multiplied by the discount value (0.67) contributed 1.08 utility." That is a sentence a judge can trust. "The LLM said so" is not.

**Why this is fast:** the math is a few multiplications. You can run 15,000 draws in milliseconds. You only call the LLM five times, for the personas.

### 6.5 Layer 3 — Monte Carlo

For each persona and each offer:

1. Set the offer's value scores.
2. Compute the persona's utility.
3. Convert to probability.
4. Draw 1,000 random shoppers (noise).
5. Count how many buy.
6. Repeat for the control offer.

**Pseudo-code:**

```python
import numpy as np

def simulate(persona, offer, control, n=1000, seed=42):
    rng = np.random.default_rng(seed)
    p_treat = purchase_probability(persona, offer)
    p_ctrl  = purchase_probability(persona, control)

    treat_buys = rng.random(n) < p_treat
    ctrl_buys  = rng.random(n) < p_ctrl

    treat_rate = treat_buys.mean()
    ctrl_rate  = ctrl_buys.mean()
    lift = (treat_rate - ctrl_rate) / ctrl_rate

    return {
        "treatment_rate": treat_rate,
        "control_rate": ctrl_rate,
        "lift": lift,
        "incremental_buyers": (treat_buys & ~ctrl_buys).sum(),
    }
```

Run it per persona and aggregate. Use the same seed for reproducibility.

### 6.6 Metrics — what the dashboard shows

| Metric | Formula | Why it matters |
|---|---|---|
| **Conversion rate** | buyers / shoppers | The basic outcome. |
| **Lift** | (treatment − control) / control | The headline number. |
| **Revenue** | buyers × AOV | Top line. |
| **Gross margin** | revenue × margin% − discount cost − shipping cost | The number that stops bad promotions. |
| **Cannibalization** | buyers who would have bought anyway | Discounts that don't create new demand. |
| **Incremental margin** | incremental buyers × margin − cannibalized margin loss | The real ROI. |
| **Confidence interval** | bootstrap or normal approximation | Shows uncertainty. |
| **Best segment** | highest lift with positive incremental margin | The recommendation. |

**Cannibalization model (simple and defensible):**

Each persona has a `base_intent` — the probability they would buy at full price. For a treatment offer:

```
incremental  = max(0, treatment_rate - base_intent)
cannibalized = min(treatment_rate, base_intent)

incremental_margin = incremental * aov * margin_pct
cannibalized_loss  = cannibalized * aov * (margin_pct - discounted_margin_pct)

net_margin = incremental_margin - cannibalized_loss - shipping_cost
```

A good demo shows a case where the offer **lifts conversion but destroys margin** — that is the insight that makes the tool feel smart.

### 6.7 Calibration / backtest (the credibility trick)

Before you predict a new offer, prove the model can reproduce a known result.

1. Hold out a historical promotion: "Last month we ran 15% off and saw a 12% lift."
2. Run the simulation on that offer with the same personas.
3. Compare predicted lift to actual lift.
4. Show the error: "Predicted 11.8%, actual 12.4%."

For the hackathon, use a **synthetic historical result** that your model reproduces. Be transparent: "This is a synthetic backtest to demonstrate the method." Judges care that you thought about calibration, not that you have real merchant data.

### 6.8 What the LLM does vs. what the math does

| Job | LLM | Math |
|---|---|---|
| Persona name, description, quote | ✅ | — |
| Persona traits | — | ✅ (from data) |
| Offer value scores | — | ✅ |
| Utility and probability | — | ✅ |
| Buy/no-buy draws | — | ✅ |
| Aggregation, lift, margin | — | ✅ |
| Why a persona responded | ✅ (from the math) | — |
| Merchant recommendation | ✅ (from the results) | — |
| Bias check | ✅ (review) | ✅ (distributions) |

**Rule:** the LLM never invents a number. It only narrates numbers the math produced. If you say this in the demo, you will sound like a real team.

### 6.9 A worked example

**Merchant:** a grocery/meal-kit store.  
**Control:** 10% off first order.  
**Treatment:** free shipping over $50.

**Personas:**

| Persona | Price sens. | Ship sens. | Discount aff. | Loyalty | Base conv. | AOV | Margin |
|---|---|---|---|---|---|---|---|
| Deal Seeker Dana | 0.9 | 0.2 | 0.9 | 0.3 | 6% | $62 | 38% |
| Convenience Chris | 0.3 | 0.9 | 0.4 | 0.6 | 8% | $74 | 35% |
| Loyalist Lena | 0.2 | 0.4 | 0.2 | 0.95 | 14% | $88 | 40% |
| Budget Bri | 0.8 | 0.7 | 0.7 | 0.2 | 5% | $48 | 30% |
| Premium Pat | 0.1 | 0.3 | 0.1 | 0.8 | 11% | $110 | 42% |

**Offer values (free shipping over $50):**

```
price_value    = 1 - (50 / 62)  ≈ 0.19   (for Dana's AOV)
shipping_value = 1.0
discount_value = 0.0
bundle_value   = 0.5
payment_value  = 0.6
```

**Dana's utility:**

```
2.0 * 0.9 * 0.19 = 0.34
1.5 * 0.2 * 1.00 = 0.30
1.8 * 0.9 * 0.00 = 0.00
1.0 * 0.3 * 0.50 = 0.15
0.8 * 0.60       = 0.48
+ intercept (calibrated)
+ noise
```

The intercept is set so the control offer reproduces Dana's 6% baseline. The treatment utility is compared to the control utility; the difference drives the lift.

**Result (illustrative):**

- Convenience Chris: +14% lift, positive incremental margin → **best segment for free shipping.**
- Deal Seeker Dana: +6% lift but heavy cannibalization → **discount already converts her; free shipping doesn't add much.**
- Loyalist Lena: +1% lift, mostly cannibalization → **do not offer her a discount.**
- Budget Bri: +9% lift, positive margin → **second-best segment.**
- Premium Pat: +2% lift → **indifferent; keep full price.**

**Recommendation:** "Run free shipping over $50 for Convenience Chris and Budget Bri. Keep the 10% offer for Dana. Do not discount Lena or Pat."

That is the demo. One screen, one clear decision.

### 6.10 How to explain it to a judge in 20 seconds

> "We don't ask an LLM to guess whether someone will buy. We build five personas from the merchant's own segments, give each a simple utility model, and simulate a thousand shoppers per offer. The LLM writes the persona and explains the decision; the math makes it. That's why we can show a confidence interval and a backtest."

---

## 7. The tech stack — what each part does

### 7.1 Recommended stack

| Layer | Tool | Why |
|---|---|---|
| Frontend | **React 19 + Vite + TypeScript** | Fast, simple, no SSR. |
| Styling | **Tailwind CSS + shadcn/ui** | Polished components quickly. |
| Charts | **Recharts** | Bar, line, funnel, tornado charts. |
| Animation | **Framer Motion** | Count-up numbers, persona cards, transitions. |
| State | **Zustand** | Simple store for the run and results. |
| Backend | **FastAPI + Uvicorn + Pydantic** | Python, async, typed models. |
| Simulation | **NumPy + pandas** | Monte Carlo and aggregation. |
| Stats | **SciPy** (optional) | Confidence intervals. |
| LLM | **Gemini 2.5 Flash** (free tier) or **OpenAI gpt-4o-mini** | Personas, rationales, recommendation. |
| Data | **JSON/CSV mock** | Catalog, transactions, segments. |
| Database | **MongoDB Atlas** + `motor` | Stores runs, personas, results. |
| Deploy | **Vercel + Render** | Free tiers. |

### 7.2 What each piece is supposed to do

**React + Vite.** The dashboard. Four screens: setup, personas, simulation, results. Vite gives you a fast dev loop.

**Tailwind + shadcn/ui.** Tailwind for layout and spacing; shadcn/ui for cards, tables, tabs, badges, dialogs, and tooltips. Copy the components in and style them. This is how you make a B2B dashboard look designed instead of default.

**Recharts.** The charts that carry the demo:
- **Bar chart:** conversion by segment, control vs. treatment.
- **Funnel:** audience → reached → engaged → converted.
- **Tornado chart:** which assumption changes the result most.
- **Line chart:** run history / sensitivity.

**Framer Motion.** Numbers count up; bars grow; persona cards flip. Small animations make the results feel alive and raise the UX score.

**FastAPI.** The API. Routes for personas, simulation, recommendation. It also serves the static frontend build in production if you want one deploy.

**NumPy + pandas.** The simulation engine. NumPy does the draws; pandas aggregates by persona and offer. This is where the credibility lives.

**SciPy.** Optional. Use it for a bootstrap confidence interval or a normal approximation. If SciPy is a hassle, compute the interval manually from the standard error.

**Gemini / OpenAI.** Three jobs:
1. Turn segment traits into a persona description and quote.
2. Explain why a persona responded the way it did.
3. Write the merchant recommendation.

It does **not** generate the numbers. One call per persona, plus one call for the recommendation. Cache the results.

**JSON/CSV mock data.** Your catalog and transaction history. Keep it realistic: 20–30 products, 500–1,000 transactions, five segments. Put it in `data/` and load it at startup.

**MongoDB Atlas.** Store each run: personas, offers, seed, results, recommendation. This gives you a history screen and hits the MongoDB track. If time is short, use in-memory and add Mongo later.

**Vercel + Render.** Deploy the frontend and backend Saturday night. Do not wait until Sunday. A deployed link in the Devpost is worth points.

### 7.3 What to mock vs. what to make real

| Layer | Real | Mock | Why |
|---|---|---|---|
| Catalog | — | ✅ 20–30 products | No merchant access |
| Transactions | — | ✅ 500–1,000 rows | No real data |
| Segments | ✅ RFM on mock data | — | Real method |
| Personas | ✅ LLM-grounded | — | Core demo |
| Utility model | ✅ Real | — | Core credibility |
| Monte Carlo | ✅ Real | — | Core demo |
| Backtest | — | ✅ Synthetic historical result | No real history |
| Recommendation | ✅ Real (rule + LLM) | — | Core demo |
| Consumer preview | — | ✅ Static mock | Visa fit |
| Payments | — | ✅ Mock Visa checkout | No production access |

### 7.4 API contracts and data shapes

```
POST /api/personas
  body: { "segment_id": "deal_seekers" }
  returns: { "persona": Persona }

POST /api/simulate
  body: {
    "catalog_id": "grocery_v1",
    "offers": [Offer, Offer],
    "control": Offer,
    "personas": [Persona],
    "trials": 1000,
    "seed": 42
  }
  returns: { "run_id": "...", "results": [PersonaResult], "summary": RunSummary }

GET /api/run/{run_id}
  returns: { "run": Run }

POST /api/recommend
  body: { "run_id": "..." }
  returns: { "recommendation": string, "best_segment": string }
```

**Data shapes:**

```ts
type Persona = {
  id: string;
  name: string;
  segment: string;
  price_sensitivity: number;    // 0..1
  shipping_sensitivity: number; // 0..1
  discount_affinity: number;    // 0..1
  brand_loyalty: number;        // 0..1
  base_conversion: number;      // 0..1
  aov: number;
  margin_pct: number;
  preferred_payment: "card" | "bnpl" | "wallet";
  description: string;
  quote: string;
};

type Offer = {
  id: string;
  name: string;
  price: number;
  discount_pct: number;
  free_shipping: boolean;
  bundle: boolean;
  payment_methods: string[];
};

type PersonaResult = {
  persona_id: string;
  control_conversion: number;
  treatment_conversion: number;
  lift: number;
  revenue: number;
  gross_margin: number;
  incremental_margin: number;
  cannibalization: number;
  confidence_interval: [number, number];
};

type RunSummary = {
  best_segment: string;
  best_offer: string;
  total_lift: number;
  total_incremental_margin: number;
  recommendation: string;
};
```

---

## 8. How you hit the Visa rubric

**Weights:** Innovation 25% · UX 25% · Tech 20% · Commerce 15% · Trust 15%.  
(UX is listed as 20% in the table but 25% in the bullets; build as if 25%.)

### 8.1 Innovation — 25%

**What judges reward:** a creative recombination of the right ingredients.

**What you do:**
- Simulate **payment-linked offers** (BNPL vs. pay-in-full, card-linked offers, free shipping) — not generic discounts.
- Use **grounded personas + a utility model + Monte Carlo**, not "ChatGPT roleplay."
- Show **cannibalization and margin**, not just conversion. Most hackathon analytics stop at the happy number.
- Add a **backtest** to prove the model can reproduce a known result.

**Say this:** "Most promotion tools predict a click. We predict incremental margin — and we show you which segment to avoid."

### 8.2 UX — 25% (your weak point — invest here)

**What judges reward:** intuitive, useful, seamless, polished under pressure.

**What you do:**
- **Persona cards with faces and quotes.** Make the synthetic customers feel like people.
- **A single headline number:** "+14% lift for Convenience Chris."
- **Charts, not tables.** Bar chart by segment; funnel; tornado.
- **Drill-down:** click a persona, see the reasoning in plain English.
- **A recommendation card** with a clear action: "Run free shipping for Segment B."
- **A consumer preview** of the winning offer at checkout, with a Visa card.
- **Animations:** count-up numbers, growing bars, persona card flip.
- **One accent color, generous whitespace, no dense grids.**

**Say this:** "The merchant sees one number, one reason, and one action."

### 8.3 Technology Execution — 20%

**What judges reward:** effective use of AI and supporting tech.

**What you do:**
- **Grounded personas:** RFM segmentation on a mock transaction dataset.
- **Utility model + logistic conversion:** deterministic, explainable.
- **Monte Carlo:** 1,000 draws per persona per offer; confidence intervals.
- **Calibration/backtest:** predicted vs. actual on a held-out promotion.
- **LLM narration:** personas, rationales, recommendation — not numbers.
- **MongoDB:** persistence of runs and results.
- **Reproducibility:** a seed and a config file for the weights.

**Say this:** "The LLM narrates; the math decides. Every number is reproducible from a seed."

### 8.4 Commerce Impact — 15%

**What judges reward:** engagement, conversion, loyalty, speed, merchant outcomes.

**What you do:**
- **Conversion lift:** the headline.
- **Incremental margin:** the number that matters.
- **Cannibalization:** protects against discounts that destroy margin.
- **Segment targeting:** the merchant knows who to offer what.
- **Speed:** a simulation in seconds vs. a weeks-long A/B test.
- **Merchant outcome:** a clear ROI story for a B2B buyer.

**Say this:** "A 14% lift on the right segment is worth more than a 20% discount on the wrong one."

### 8.5 Trust & Responsibility — 15%

**What judges reward:** privacy, transparency, security, responsible AI.

**What you do:**
- **Synthetic data label:** every screen says "simulated customers, not real people."
- **Assumptions visible:** a panel showing the utility weights and the persona traits.
- **Confidence intervals:** no single-point false precision.
- **Backtest:** prove the model on a known result.
- **Bias audit (VEYZL):** check that persona distributions don't skew unfairly; show a finding and a fix.
- **No PII:** the mock data is synthetic; the merchant's real data would be aggregated.
- **Human decision:** the tool recommends; the merchant decides.

**Say this:** "We show the assumptions, the uncertainty, and the bias audit. This is a decision aid, not an oracle."

### 8.6 Scorecard summary

| Criterion | Weight | Your evidence | Demo moment |
|---|---|---|---|
| Innovation | 25% | Payment-offer simulation + incremental margin | "We predict margin, not clicks" |
| UX | 25% | Persona cards, one headline, charts, preview | The persona drill-down quote |
| Tech | 20% | RFM + utility + Monte Carlo + backtest | The confidence interval and seed |
| Commerce | 15% | Lift, margin, cannibalization, segment targeting | "+14% for Chris, −2% for Lena" |
| Trust | 15% | Synthetic labels, assumptions, CI, VEYZL audit | The assumptions panel |

---

## 9. The 21-hour plan

**Hacking starts:** 12:30 PM Saturday.  
**Devpost draft:** 10:30 PM Saturday.  
**Final submission:** 10:00 AM Sunday.  
**Video:** under 3 minutes.

### 9.1 Saturday afternoon (12:30–6:00)

| Time | What | Owner |
|---|---|---|
| 12:30–1:15 | Repo, env, FastAPI + Vite hello world, design tokens | All |
| 1:15–2:30 | Mock catalog + 500 transactions + RFM segments | Data |
| 2:30–4:30 | Utility model + Monte Carlo + metrics | Simulation |
| 4:30–6:00 | `/api/simulate` + results data shape | Backend |

### 9.2 Saturday evening (6:00–10:30)

| Time | What | Owner |
|---|---|---|
| 6:00–7:30 | Dashboard: offer setup + persona cards | Frontend |
| 7:30–9:00 | Results: bar chart, funnel, metric cards | Frontend |
| 9:00–10:00 | Persona drill-down + LLM rationales + recommendation | Backend + Frontend |
| 10:00–10:30 | Devpost draft + rough video | All |

**Submit the draft at 10:30 PM.** It can be rough.

### 9.3 Saturday night (10:30–2:00)

| Time | What |
|---|---|
| 10:30–12:00 | Consumer preview + Visa payment options |
| 12:00–1:00 | Calibration/backtest screen |
| 1:00–2:00 | VEYZL audit + one finding + fix |

### 9.4 Sleep (2:00–6:00)

Sleep in shifts. At least two people get four hours.

### 9.5 Sunday morning (6:00–10:00)

| Time | What |
|---|---|
| 6:00–7:00 | Polish: spacing, colors, copy, empty states |
| 7:00–8:00 | Record the 3-minute video |
| 8:00–9:00 | Devpost final: story, stack, screenshots, video |
| 9:00–9:30 | Rehearse the live demo twice; test fallback |
| 9:30–10:00 | Submit + buffer |

### 9.6 Team roles (4 people)

| Role | Owns |
|---|---|
| **Simulation** | RFM, utility model, Monte Carlo, metrics, backtest |
| **Backend / data** | FastAPI, mock data, MongoDB, API contracts |
| **Frontend / UX** | React, Tailwind, shadcn, Recharts, animations |
| **LLM / demo** | Personas, rationales, recommendation, VEYZL, video, Devpost |

If 3 people: merge LLM/demo into simulation and frontend.

---

## 10. The 3-minute video script

Visa judging is virtual — the video is the product.

| Time | Visual | Voiceover |
|---|---|---|
| 0:00–0:15 | A merchant staring at a promotion spreadsheet | "Merchants spend billions on promotions they never tested. A bad discount doesn't just fail — it destroys margin." |
| 0:15–0:35 | Persona cards appearing | "Test Kitchen builds digital clones of your customers — grounded in your own segments, not random chatbots." |
| 0:35–1:15 | Offer setup; simulation running | "Pick two offers: twenty percent off bundles, or free shipping. A thousand synthetic shoppers per segment decide." |
| 1:15–1:50 | Results: bar chart + lift + margin | "Free shipping lifts Convenience Chris by fourteen percent. But for Loyalist Lena, it's pure cannibalization — she would have bought anyway." |
| 1:50–2:20 | Persona drill-down quote | "Click a persona and see why. The LLM explains the decision; the math made it. Every number is reproducible." |
| 2:20–2:45 | Recommendation + consumer preview | "The recommendation: run free shipping for Segment B, keep the discount for Segment A. Here's the offer as a shopper sees it — with Visa payment options." |
| 2:45–3:00 | Trust panel + end card | "Synthetic data, visible assumptions, confidence intervals, and a bias audit. Test before you spend." |

**Recording tips:** 1080p, clean browser, zoom on the numbers, cut dead time, separate voiceover.

---

## 11. Devpost draft template

**Title:** Test Kitchen — a wind tunnel for promotions

**Tagline:** Digital clones of your customers test your offers before you spend a dollar.

**Inspiration:** Merchants guess which promotion will work, or run slow, expensive A/B tests. A bad discount can lift conversion while destroying margin. We wanted a fast, explainable pre-test.

**What it does:**
- Builds grounded customer personas from merchant segments.
- Simulates thousands of synthetic shoppers across offers.
- Predicts conversion lift, revenue, margin, and cannibalization.
- Recommends which offer to run for which segment.
- Shows a consumer checkout preview with Visa payment options.

**How we built it:**
- React + Vite + Tailwind + shadcn/ui + Recharts + Framer Motion.
- FastAPI + Python + NumPy + pandas.
- RFM segmentation on a mock transaction dataset.
- Utility model + logistic conversion + Monte Carlo.
- Gemini/OpenAI for persona narration and recommendations.
- MongoDB Atlas for run persistence.
- VEYZL for a bias/safety audit of the synthetic personas.

**Challenges:**
- Making a simulation feel credible, not random.
- Keeping the LLM out of the numbers.
- Designing a B2B dashboard that is emotionally compelling.
- Calibrating the model to a known result.

**Accomplishments:**
- A reproducible simulation with confidence intervals.
- A clear incremental-margin story, not just conversion.
- A backtest that shows the method works.
- A persona drill-down that explains every decision.

**What we learned:**
- The LLM should narrate, not decide.
- Cannibalization is the number merchants actually care about.
- B2B UX needs a human face — the persona cards are the emotional hook.

**What's next:**
- Real merchant data integration.
- Live A/B test calibration.
- Multi-touch attribution.
- More offer types: loyalty multipliers, card-linked offers, BNPL.

**Built with:** React, Vite, TypeScript, Tailwind, shadcn/ui, Recharts, Framer Motion, FastAPI, Python, NumPy, pandas, Gemini, MongoDB, VEYZL.

---

## 12. Judge Q&A prep

**"Isn't this just ChatGPT with personas?"**
> No. The personas are grounded in RFM segments from transaction data. The decision is a utility model with a logistic conversion function. The LLM writes the persona and explains the result; it never invents a number. We can reproduce any run from a seed.

**"How accurate is the simulation?"**
> It's a pre-test, not a guarantee. We backtest on a held-out historical promotion and report the error, and we show a confidence interval on every lift. It narrows the option set before a real A/B test.

**"Why not just run an A/B test?"**
> A/B tests are slow and expensive, and you can't test ten offers at once. Test Kitchen is a cheap filter: simulate ten, test the best two for real.

**"How does this fit Visa?"**
> We simulate payment-linked offers — BNPL vs. pay-in-full, card-linked offers, free shipping thresholds — and recommend the offer that maximizes conversion and margin. The consumer preview shows the checkout with Visa payment options.

**"What about bias in the personas?"**
> We audit the persona distributions against the segment data with VEYZL, show the assumptions, and use synthetic data with no PII. The tool recommends; the merchant decides.

**"What's the business model?"**
> SaaS subscription plus per-simulation pricing. The buyer is the growth or CRM team; the ROI is measured in incremental margin.

**"What would you do with another week?"**
> Real merchant data, live A/B calibration, multi-touch attribution, and more offer types.

---

## 13. Risks and fallbacks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Simulation feels random | High | Utility model + calibration + confidence intervals + seed |
| B2B UX feels boring | High | Persona cards, one headline number, charts, consumer preview |
| LLM cost/latency | Medium | One call per persona; cache; template fallback |
| Mock data looks fake | Medium | Realistic distributions, real product names, believable AOVs |
| Backtest is unconvincing | Medium | Label it synthetic; show the method, not a false claim |
| Visa fit feels weak | Medium | Payment-linked offers + consumer preview + shopping narrative |
| Waddle already did it | Medium | Differentiate with payment offers, margin, calibration, bias audit |
| Too many tracks | High | SideShift + VEYZL + one raffle; don't spread thin |
| Running out of time | High | Follow the cut list; protect the simulation and the headline number |

**Demo insurance:** record a backup video Saturday night.

---

## 14. Plain-English glossary

| Term | What it means |
|---|---|
| **Digital clone / synthetic persona** | A simulated customer with traits and a decision model. |
| **RFM segmentation** | Grouping customers by Recency, Frequency, and Monetary value. |
| **Utility model** | A formula that scores how appealing an offer is to a persona. |
| **Logistic function** | Turns a utility score into a probability between 0 and 1. |
| **Monte Carlo** | Running a model many times with random variation to get a distribution. |
| **Lift** | The percentage change in conversion from control to treatment. |
| **Cannibalization** | Sales to customers who would have bought anyway, so the discount didn't create new demand. |
| **Incremental margin** | Profit from new buyers minus the margin lost on cannibalized buyers. |
| **Confidence interval** | A range that shows how uncertain an estimate is. |
| **Backtest / calibration** | Checking the model against a known historical result. |
| **Counterfactual** | What would have happened under the other offer. |
| **A/B test** | A real-world experiment with a control and a treatment group. |
| **Synthetic data** | Data generated to look real but containing no real people. |
| **PII** | Personally identifiable information. |
| **Tornado chart** | A bar chart showing which assumptions matter most. |
| **Treatment / control** | The new offer vs. the current offer. |

---

## 15. Suggested repo structure

```
test-kitchen/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── personas.py
│   │   │   ├── simulate.py
│   │   │   └── recommend.py
│   │   ├── services/
│   │   │   ├── segmentation.py     # RFM
│   │   │   ├── personas.py         # LLM narration
│   │   │   ├── utility.py          # decision model
│   │   │   ├── simulation.py       # Monte Carlo
│   │   │   ├── metrics.py          # lift, margin, cannibalization
│   │   │   ├── backtest.py         # calibration
│   │   │   └── recommend.py        # rule + LLM
│   │   ├── models.py
│   │   ├── config.py               # utility weights
│   │   └── db.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── SegmentPicker.tsx
│   │   │   ├── PersonaCard.tsx
│   │   │   ├── OfferBuilder.tsx
│   │   │   ├── SimulationProgress.tsx
│   │   │   ├── ResultsChart.tsx
│   │   │   ├── PersonaDrilldown.tsx
│   │   │   ├── RecommendationCard.tsx
│   │   │   └── ConsumerPreview.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── format.ts
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.ts
├── data/
│   ├── catalog.json
│   ├── transactions.csv
│   └── historical_promo.json
├── README.md
└── .env.example
```

**`.env.example`:**

```text
GEMINI_API_KEY=
OPENAI_API_KEY=
MONGODB_URI=
DEMO_MODE=true
```

---

## 16. Sources

- `visa-ideas.md` §3.11 — original Test Kitchen entry.
- [Visa Intelligent Commerce](https://developer.visa.com/capabilities/visa-intelligent-commerce)
- [Visa rubric](../info/visa-rubric.txt)
- [Waddle — OpenAI hackathon winner](https://www.mk.co.kr/en/it/11407305) — the validated reference; differentiate with payment offers, margin, and calibration.
- [Recharts](https://recharts.org/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Framer Motion](https://www.framer.com/motion/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [NumPy](https://numpy.org/)
- [pandas](https://pandas.pydata.org/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)
- [RFM segmentation primer](https://en.wikipedia.org/wiki/RFM_(market_research))

---

## 17. The three sentences to remember

1. **The personas come from the merchant's segments; the LLM only gives them a voice.**
2. **The math makes the decision — utility, probability, Monte Carlo — so every number is reproducible.**
3. **The output is incremental margin by segment, not just conversion.**

If the demo shows those three things clearly, Test Kitchen is credible. If it shows a chatbot guessing, it isn't.
