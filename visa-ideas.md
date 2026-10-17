# DubHacks '26 — Visa Track Idea Catalog

**Team profile:** 3–4 people, AI/backend strong  
**Build window:** 12:30 PM Sat → 10:00 AM Sun (21.5 hours)  
**Judging format:** 3-minute recorded video (Visa main track is virtual)  
**Purpose:** A ranked menu of ideas with explicit "why this can win" rationales, so the team can pick one fast and build.

---

## How to use this doc

1. Read the TL;DR and scoring matrix (5 minutes).
2. Pick a direction using the decision tree at the end of §2.
3. Read the full entry for your top 2 choices.
4. At 12:30, lock scope and start building. Do not spend the hacking window debating.

---

## 0. The Visa rubric — and a typo to flag

`visa-rubric.txt` has an internal inconsistency worth confirming with a Visa mentor:

| Criterion | Table says | Bullet says | Sum check |
|---|---|---|---|
| Innovation | 25% | 25% | — |
| Technology Execution | 20% | 20% | — |
| User Experience | **20%** | **25%** | — |
| Commerce Impact | 15% | 15% | — |
| Trust & Responsibility | 15% | 15% | — |

The table sums to **95%**; the bullets sum to **100%** with UX at 25%. This doc assumes **UX = 25%, Tech = 20%**. That matters: UX is the single biggest lever alongside innovation, so a beautiful, intuitive demo is not optional.

**What this rubric rewards:**
- **Innovation (25%)** — a genuinely different interaction or thesis, not another chat wrapper.
- **UX (25%)** — polished, intuitive, seamless under pressure.
- **Tech execution (20%)** — effective use of AI and supporting systems, not just an API call.
- **Commerce impact (15%)** — engagement, conversion, loyalty, speed, or merchant outcomes.
- **Trust & responsibility (15%)** — privacy, transparency, security, responsible AI.

**The winning shape:** a specific user + a visible AI decision + a deterministic trust layer + a real (or convincingly mocked) payment moment + a number.

---

## 1. TL;DR — top five picks

| Rank | Idea | Why it can win | Best for |
|---|---|---|---|
| **1** | **Table Talk** — household decision room | Fills Visa's explicit "collaborating with AI" gap; combines multi-user mediation, passkey-signed spending authority, and tokenized payment. Stacks Visa + T-Mobile Household Mix + SideShift + Cloudforce. | Highest ceiling + best track stack |
| **2** | **Calm Cart** — commerce for neurodivergent shoppers | Highest rubric ceiling: underserved user, UX-first, anti-dark-pattern, strong trust story. Almost nobody builds for this user. | Highest innovation + UX |
| **3** | **Return Radar** — predict returns before checkout | Strongest direct Commerce Impact and least crowded lane; real ML + a quantifiable merchant ROI. | Best ROI story |
| **4** | **Gift Circle** — group gifting with split payment | Fun, social, inherently shareable; strong Cloudforce Most Viral and SideShift angles. | Most viral consumer play |
| **5** | **Mandate** — consent layer for AI shopping agents | Mirrors Visa's actual Intelligent Commerce architecture (tokenization, passkeys, payment instructions). Highest Trust score. | Best Visa-alignment |

**Safest fallback:** **Timekeeper** — simplest to polish, direct T-Mobile hit, high UX.  
**Deepest technical flex:** **Bazaar** (agent-to-agent negotiation) or **Test Kitchen** (commerce simulation).  
**Least crowded lanes:** **Return Radar**, **Fine Print**, **Dispute Desk**, **Calm Cart**.

---

## 2. Scoring matrix

Scores are 1–5 and subjective — use them to argue, not to decide mechanically.  
**Visa score** = Innovation×0.25 + UX×0.25 + Tech×0.20 + Commerce×0.15 + Trust×0.15.

| # | Idea | Innovation 25% | UX 25% | Tech 20% | Commerce 15% | Trust 15% | **Visa score** | Feasibility (21h) | Track stack | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Table Talk** | 5 | 4.5 | 5 | 4 | 5 | **4.73** | 3.5 | 5 | Top pick |
| 2 | **Calm Cart** | 5 | 5 | 4 | 4 | 5 | **4.65** | 4 | 4 | Highest ceiling |
| 3 | **Bazaar** | 5 | 4 | 5 | 5 | 4 | **4.60** | 2 | 4.5 | Ambitious |
| 4 | **Return Radar** | 4 | 4 | 5 | 5 | 4.5 | **4.43** | 3.5 | 4 | Best ROI |
| 5 | **SceneShop** | 4.5 | 4.5 | 4.5 | 3.5 | 5 | **4.43** | 3.5 | 3.5 | Best human story |
| 6 | **Test Kitchen** | 5 | 3.5 | 5 | 5 | 3.5 | **4.40** | 3 | 4 | B2B wildcard |
| 7 | **Gift Circle** | 4.5 | 5 | 3.5 | 4.5 | 4 | **4.35** | 4.5 | 4.5 | Most viral |
| 8 | **Mandate** | 4 | 4 | 5 | 4 | 5 | **4.35** | 3 | 4.5 | Best Visa fit |
| 9 | **Timekeeper** | 4 | 5 | 3.5 | 4 | 5 | **4.30** | 5 | 5 | Safest |
| 10 | **Fine Print** | 5 | 4 | 4 | 3 | 5 | **4.25** | 4 | 4 | Most novel |
| 11 | **Closet** (style twin) | 4 | 5 | 4 | 4 | 4 | **4.25** | 3.5 | 4 | Visual |
| 12 | **Dispute Desk** | 4 | 4 | 4 | 4.5 | 5 | **4.23** | 3 | 4 | Open lane |
| 13 | **Second Life** (resale timing) | 4.5 | 4 | 4 | 4 | 4.5 | **4.20** | 3.5 | 4 | Circular |
| 14 | **Fit** (size translator) | 3.5 | 4.5 | 4 | 4.5 | 4.5 | **4.15** | 4 | 4 | Narrow |
| 15 | **FreshStart** (SNAP/EBT) | 4.5 | 4 | 4 | 3 | 5 | **4.13** | 3 | 3.5 | Social impact |
| 16 | **Recurring** (subscription audit) | 3.5 | 5 | 3 | 4 | 5 | **4.08** | 5 | 4 | Easy win |
| 17 | **True Price** (checkout copilot) | 3 | 5 | 3 | 4.5 | 5 | **4.03** | 5 | 5 | Safe |
| 18 | **Source** (values filter) | 4 | 4 | 4 | 3 | 5 | **4.00** | 3 | 4 | Values |
| 19 | **Upgrade Court** (viral game) | 4 | 5 | 3.5 | 3.5 | 3 | **3.93** | 5 | 4.5 | Viral game |
| 20 | **BNPL Check** | 4 | 4 | 3.5 | 3 | 5 | **3.90** | 4 | 4 | Responsible |

### Decision tree

- **Highest ceiling:** Table Talk or Calm Cart.
- **Safest path to a polished demo:** Timekeeper.
- **Most viral consumer play:** Gift Circle or Upgrade Court.
- **Deepest technical flex:** Bazaar or Test Kitchen.
- **Strongest trust story:** Mandate or Fine Print.
- **Least crowded lane:** Return Radar, Fine Print, Dispute Desk, or Calm Cart.
- **Best T-Mobile stack:** Table Talk (Household Mix) or Timekeeper (Timekeeper).
- **Best SideShift / NEXT story:** Gift Circle, Table Talk, or Test Kitchen.
- **Best accessibility story:** SceneShop or Calm Cart.
- **Best B2B / merchant story:** Return Radar, Test Kitchen, or Dispute Desk.

---

## 3. The ideas — detailed

### 1. Table Talk — the household decision room

**One-liner:** A shared room where a household agrees on a big purchase without the argument.

**Target user:** Families, couples, and roommates making a shared purchase — phones/plans, appliances, furniture, travel.

**Journey stage:** Discovery → decision-making → personalization → checkout.

**What it does:**
- Each person joins a room and states constraints: budget cap, must-haves, dealbreakers, timeline.
- An AI mediator builds a joint shortlist and shows which constraints each option satisfies or violates.
- Members vote; the mediator runs a second round only on contested items.
- The room produces a single cart and a **passkey-signed spending mandate** ("up to $1,200, two phones, one plan, no accessories").
- Checkout uses a tokenized card; the AI cannot pay without the mandate and a final human confirmation.

**60-second demo:** Three browser windows — parent, parent, teen. Each states constraints. The mediator proposes two bundles, shows a tradeoff table, the teen vetoes one, the AI finds a compromise, everyone approves, and the cart is paid with a passkey. A "family savings" tally appears.

**Why it can win:**
- **Innovation (25%):** Visa's brief explicitly says shopping is moving from searching and browsing to "conversing and **collaborating with AI**." Almost every team builds a single-user chatbot. A multi-user decision room is a different interaction model.
- **UX (25%):** The demo is a narrative: argument → mediation → agreement → payment. It is inherently watchable and easy to make beautiful.
- **Tech execution (20%):** Multi-agent mediation, preference elicitation, constraint satisfaction, real-time shared state, passkey/credential flow.
- **Commerce impact (15%):** Larger baskets, higher conversion on considered purchases, fewer abandoned family decisions.
- **Trust (15%):** Signed mandate, explicit approvals, tokenized payment, visible reasons for every recommendation.
- **Gap vs adjacent projects:** Gather, MiyKo, and DecisionMate validate group shopping/decisions, but none combine **Visa payment + a signed spending mandate + a visible agent negotiation** in one build.

**Track stack:** Visa (title) + T-Mobile (Household Mix) + SideShift (Best Startup Idea) + Cloudforce (Most Viral / raffle) | NEXT, Gemini, Backboard, DEV.

**Build scope:** 3 roles, 2 product categories (phones + plans), mock product/plan data, one room, WebSocket or polling, passkey mock, tokenized checkout mock. Feasible for a strong team.

**Risk:** Real-time multi-user demo can be flaky. Pre-record a backup. The AI must not feel like a group chat with a bot — the mediator needs a deterministic constraint engine underneath.

**Kill criteria:** If three browser windows cannot sync reliably by Saturday night, cut to two roles and a scripted third participant.

---

### 2. Calm Cart — commerce for neurodivergent shoppers

**One-liner:** A shopping experience designed for people who find shopping overwhelming.

**Target user:** Adults with ADHD, autism, anxiety, or decision fatigue — also useful for anyone shopping under time pressure.

**Journey stage:** Discovery → decision-making → checkout.

**What it does:**
- Asks a few calm, low-friction questions (budget, must-haves, sensory/dealbreaker constraints).
- Presents **at most three options**, with a plain-language tradeoff table (cost, return policy, delivery, durability).
- Explains *why* each option is shown and *what you give up* with each.
- Detects and removes dark patterns (countdown timers, fake scarcity, confirmshaming) from the experience.
- Offers a "decide later" mode that saves the shortlist without pressure.
- Checkout is a single, explicit confirmation with no upsells.

**60-second demo:** A user overwhelmed by 40 search results gets three calm options, a tradeoff table, and a one-click checkout. A side-by-side shows the "normal" store page versus Calm Cart. The user says: "I actually decided in two minutes."

**Why it can win:**
- **Innovation (25%):** Almost nobody builds for this user. It reframes shopping from "more choice" to "less cognitive load" — a genuinely different thesis.
- **UX (25%):** Calm design is inherently demo-friendly: whitespace, clear typography, no dark patterns. Judges remember it.
- **Tech (20%):** Preference modeling, constraint filtering, dark-pattern detection, explanation generation.
- **Commerce (15%):** Loyalty and conversion among a large underserved segment; lower returns from better-fit decisions.
- **Trust (15%):** Explicitly anti-manipulation. Privacy-first. No urgency tactics.
- **Gap:** Chaperone targets older adults; Sniff targets fraud. Nobody in the adjacent set targets cognitive accessibility with a calm, choice-reducing UX.

**Track stack:** Visa + SideShift + Cloudforce | NEXT, Gemini, DEV. (If the whole team is freshmen, add the Freshman track.)

**Build scope:** One category (headphones or backpacks), 30–50 mock products, LLM explanations, a polished three-screen flow. Very feasible.

**Risk:** Needs credible user empathy; avoid speaking for a community without research. Cite existing work on choice overload and ADHD shopping behavior, and keep the language respectful. Don't make it feel like a "disability app" — make it a calmer commerce layer.

**Kill criteria:** If the demo feels like a generic recommender with a pastel theme, cut it.

---

### 3. Return Radar — stop the return before it happens

**One-liner:** Predict which purchases will be returned — and recommend the variant that won't.

**Target user:** Online apparel/footwear shoppers and the merchants who pay for returns.

**Journey stage:** Decision-making → post-purchase.

**What it does:**
- At product/checkout, scores return risk from category, size/fit history, review language, and user behavior.
- Recommends the size/variant with the lowest expected return risk and explains why ("runs small," "color differs in photos").
- Shows the shopper the expected cost of a return (time, shipping, restocking).
- Gives the merchant a dashboard: return-risk distribution, top drivers, and the ROI of the intervention.

**60-second demo:** "This jacket has a 38% return risk in your size. The L Tall cuts it to 9%. Here's why." A merchant dashboard shows $18k in avoided returns.

**Why it can win:**
- **Commerce impact (15%):** The most direct ROI story in the field. Returns are a massive cost; a percentage reduction is easy to quantify.
- **Tech (20%):** Real ML (gradient-boosted model on synthetic data), LLM explanations, merchant analytics.
- **Innovation (25%):** Few hackathon teams tackle returns; most build acquisition/discovery. It is a differentiated problem.
- **UX (25%):** The product-page badge and explanation are simple and useful; the merchant dashboard can be beautiful.
- **Trust (15%):** Transparent reasoning, no manipulation, privacy-preserving.
- **Gap:** Sniff and MagiCart optimize price and safety, not returns. This is an open lane.

**Track stack:** Visa + SideShift + Cloudforce + VEYZL (if framed as an AI system and audited) | MongoDB, Tiger Data, DEV.

**Build scope:** Generate a synthetic dataset (~5k purchases with return labels), train XGBoost/logistic regression, add an LLM explanation layer, build a product page + merchant dashboard.

**Risk:** Judges may ask "where's the data?" Be honest: synthetic plus a clear plan for real data. Show a confusion matrix and calibration, not just a demo. Don't overclaim causal lift.

**Kill criteria:** If the model's AUC is barely above random on the synthetic data, reframe as a rules-based risk score with explanations and focus on the UX/ROI story.

---

### 4. Gift Circle — group gifting, solved

**One-liner:** Friends pool money, an AI curates the gift, everyone votes, and payment splits automatically.

**Target user:** Friend groups, families, and coworkers buying a gift for one person.

**Journey stage:** Discovery → decision → checkout → post-purchase.

**What it does:**
- The organizer creates a circle, sets a budget per person, and adds context about the recipient.
- The AI proposes three gift options with rationale and links; members vote or add constraints.
- The circle approves one gift; payments split automatically (mock Visa tokenized checkout).
- The recipient gets a card with messages; the organizer gets a clean receipt.

**60-second demo:** Four friends, $25 each, a recipient who just started climbing. The AI proposes three gifts, the group votes, the gift is bought, and the split payment completes. A shareable card appears.

**Why it can win:**
- **UX (25%):** Fun, social, and inherently shareable. Great video.
- **Innovation (25%):** Group gifting is a real, underserved workflow; most shopping apps are single-user.
- **Commerce (15%):** Higher AOV, group conversion, seasonal virality.
- **Trust (15%):** Transparent splits, explicit approvals, no hidden fees.
- **Tech (20%):** Multi-user state, preference aggregation, split payments, LLM curation — moderate.
- **Gap:** Gather and MiyKo focus on shared carts, not gifting; none combine AI curation + voting + split payment.

**Track stack:** Visa + SideShift + Cloudforce (Most Viral) | NEXT, Gemini, DEV.

**Build scope:** One category (gifts under $100), 3–5 users per circle, mock payment split. Very feasible; the hard part is polish and the viral loop.

**Risk:** It can feel like a feature, not a company. Add a clear business model (affiliate, card fees, group gift concierge) for SideShift/NEXT. The demo needs real people, so pre-seed a circle with teammates.

**Kill criteria:** If the viral loop does not produce a few real users by Saturday night, focus the pitch on conversion/AOV instead of virality.

---

### 5. Mandate — the consent layer for AI shopping agents

**One-liner:** A plain-English spending mandate, signed with a passkey, that tells an AI agent exactly what it may and may not buy.

**Target user:** Anyone who will let an AI agent shop for them — early adopters, busy professionals, people with accessibility needs.

**Journey stage:** Checkout → payments → post-purchase.

**What it does:**
- The user writes or selects a plain-English mandate: "Buy one pair of running shoes under $150; no subscriptions; no marketplace sellers; ask me before any purchase over $100."
- A deterministic rule engine compiles the mandate into hard constraints (budget, category, merchant allowlist, approval thresholds).
- The agent shops; before payment it shows an **intent verification** screen: what it is buying, why, and which mandate clauses it satisfies.
- Payment uses a tokenized card or scoped single-use virtual card; the agent never sees the real credential.
- Every action is logged in a spending journal.

**60-second demo:** The agent finds shoes, tries to add socks (blocked), finds a marketplace seller (blocked), then presents a compliant purchase. The user approves with a passkey. The journal shows every decision.

**Why it can win:**
- **Trust (15%):** The strongest trust story possible: deterministic constraints, passkey consent, scoped credentials, audit log.
- **Tech (20%):** Rule compilation, agent tool use, tokenization, passkey flow, audit logging. Directly mirrors Visa's Intelligent Commerce architecture.
- **Innovation (25%):** The interaction — a signed plain-English mandate — is novel and memorable.
- **UX (25%):** The intent-verification screen *is* the product. If it is beautiful and clear, judges will remember it.
- **Commerce (15%):** Enables agentic commerce safely; merchants get higher-converting agent traffic.
- **Gap:** Argus, Handshake, Omamoris, and Visa's own reference agent cover pieces, but the **plain-English mandate + passkey signature + intent verification** combination is still an open, legible wedge.

**Track stack:** Visa + VEYZL (audit the agent) + SideShift + Cloudforce | NEXT, Gemini, DEV.

**Build scope:** One category (shoes or electronics), a mock merchant API, a rule compiler, an agent loop, a WebAuthn passkey mock, and an audit log.

**Risk:** Crowded space; differentiate on the mandate UX, not just "guardrails." Don't claim a real Visa integration unless you have sandbox access.

**Kill criteria:** If the agent cannot reliably complete a three-step purchase without hand-holding, simplify to a deterministic checkout flow where the agent only proposes.

---

### 6. Timekeeper — the advisor that tells you not to buy

**One-liner:** A buy-now-or-wait advisor that proves when upgrading is a waste of money.

**Target user:** Phone, laptop, and appliance buyers — especially those on family plans.

**Journey stage:** Decision-making → personalization → loyalty.

**What it does:**
- Ingests your current device/plan, usage, and the market (trade-in values, plan math, repair costs, resale curves).
- Produces a verdict: "Wait 7 months," "Upgrade now — here's the cheapest path," or "Buy refurbished."
- Shows a true annual cost breakdown, not just sticker price.
- Generates a shareable verdict card.

**60-second demo:** A judge enters their phone; the app says "wait 7 months — your current device is worth $310 and the next model's battery gains are marginal." A shareable card appears.

**Why it can win:**
- **UX (25%):** One clear verdict, beautiful card, zero friction. Easy to polish.
- **Trust (15%):** Anti-upsell positioning is inherently trustworthy; no dark patterns.
- **Innovation (25%):** The contrarian "don't buy" stance is memorable and directly matches T-Mobile's Timekeeper brief.
- **Commerce (15%):** Drives loyalty and better-timed conversions; carriers reduce churn.
- **Tech (20%):** Lower than others — deterministic TCO engine plus LLM narration.
- **Gap:** MagiCart and Sniff optimize price and safety; nobody owns the "wait" decision.

**Track stack:** Visa + T-Mobile (Timekeeper) + SideShift + Cloudforce | NEXT, Gemini, DEV.

**Build scope:** One category (phones), mock plan/trade-in data, a TCO engine, LLM narration, share card. Very feasible.

**Risk:** Lower technical depth; may lose to a flashier AI demo. The verdict logic must be genuinely smart, not a gimmick.

**Kill criteria:** If the verdict is just "older phone = wait," add real plan/trade-in math and edge cases.

---

### 7. SceneShop — voice-first commerce for blind and low-vision shoppers

**One-liner:** Shop by voice, with a camera that describes what is in front of you and a checkout that reads everything back.

**Target user:** Blind and low-vision shoppers; also useful for hands-busy users.

**Journey stage:** Discovery → decision → checkout.

**What it does:**
- A voice agent helps browse: "Find a black backpack under $80 with a laptop sleeve."
- The camera describes products, labels, and packaging; OCR reads ingredients and sizes.
- The agent reads back the cart, total, delivery date, and return policy before payment.
- Checkout requires an explicit spoken confirmation; no visual-only steps.

**60-second demo:** A user points a phone at a backpack, asks questions, adds it to the cart, and completes checkout entirely by voice. The screen is optional.

**Why it can win:**
- **Trust (15%):** Accessibility + explicit confirmation + no visual-only traps.
- **UX (25%):** A genuinely different interaction model; judges can close their eyes and follow the demo.
- **Innovation (25%):** Very few commerce projects are built accessibility-first.
- **Tech (20%):** Vision (Perceptron), speech (ElevenLabs), agent orchestration, confidence-aware descriptions.
- **Commerce (15%):** Opens a large underserved market; strong loyalty.
- **Gap:** Chaperone targets older adults with voice; Blindsight (Visa's 2018 challenge winner) shows Visa rewards accessibility + payments. A blind-first commerce experience is still rare.

**Track stack:** Visa + Perceptron (perception) + SideShift + Cloudforce | Gemini, DEV.

**Build scope:** One category, camera + speech, mock checkout. Medium difficulty; latency is the main risk.

**Risk:** Vision/speech latency; must handle uncertainty gracefully ("I'm not sure — there's a label on the left"). Don't overpromise real-time performance.

**Kill criteria:** If voice latency makes the demo painful, pre-record the interaction and present it as a product video with live Q&A.

---

### 8. Fine Print — the dark-pattern detector

**One-liner:** A real-time detector that flags manipulative checkout design and explains what it is doing to you.

**Target user:** Online shoppers, consumer-protection advocates, regulators.

**Journey stage:** Checkout → post-purchase.

**What it does:**
- A browser extension or URL scanner analyzes a checkout page for dark patterns: countdown timers, fake scarcity, confirmshaming, pre-checked add-ons, hidden fees, hard-to-cancel subscriptions.
- Explains each pattern in plain language and shows the "fair" version.
- Estimates the cost of the manipulation ("this pre-checked warranty adds $24").
- Offers a clean summary you can share.

**60-second demo:** A real checkout page lights up with five flags; the extension removes the pre-checked add-on and reveals the true total. A shareable "manipulation report" appears.

**Why it can win:**
- **Innovation (25%):** Timely, novel, and a strong point of view.
- **Trust (15%):** Directly about transparency and responsible commerce.
- **UX (25%):** The visual overlay is instantly understandable.
- **Tech (20%):** Page parsing, LLM classification, rule engine, extension packaging.
- **Commerce (15%):** Weaker direct merchant benefit; frame as consumer trust/loyalty and regulatory compliance for merchants.
- **Gap:** Nobody in the adjacent set does this. It is a genuinely open lane.

**Track stack:** Visa + SideShift + Cloudforce | Gemini, DEV.

**Build scope:** A web app that accepts a URL plus a curated set of mock pages; extension optional. Very feasible.

**Risk:** Commerce impact is the weakest of the five criteria; Visa may see it as anti-merchant. Frame it as "trust infrastructure" that merchants can use to audit their own funnels, not just a consumer weapon.

**Kill criteria:** If you cannot get a reliable score on five or more real checkout pages, use a curated mock set and be transparent.

---

### 9. Bazaar — agent-to-agent negotiation

**One-liner:** Your buying agent negotiates with merchant agents, and Visa closes the payment in-chat.

**Target user:** Price-sensitive shoppers; small merchants who want AI-native storefronts.

**Journey stage:** Discovery → decision → checkout → payments.

**What it does:**
- The buyer states a goal and budget; their agent searches merchant agents.
- Merchant agents make offers (price, bundle, shipping, warranty); the buyer agent negotiates.
- The winning offer is presented with a clear comparison and a "why this is the best deal" explanation.
- Payment is tokenized and confirmed in-chat.

**60-second demo:** Two agents negotiate over a laptop bundle; the merchant agent drops the price and adds a case; the buyer agent accepts; Visa checkout completes. A live negotiation log shows the offers.

**Why it can win:**
- **Innovation (25%):** Agent-to-agent commerce is the frontier; Sherpa validates the concept, but few teams will attempt it.
- **Tech (20%):** Multi-agent orchestration, negotiation protocol, offer evaluation, payment integration.
- **Commerce (15%):** Merchant outcomes, conversion, price discovery.
- **UX (25%):** The negotiation log is inherently watchable; the final comparison is clear.
- **Trust (15%):** Transparent offers, no hidden fees, explicit approval.
- **Gap:** Sherpa is a Visa-challenge project but not a confirmed winner; a polished, narrow version (one category, three merchants) could stand out.

**Track stack:** Visa + SideShift + Cloudforce + VEYZL | Gemini, DEV.

**Build scope:** One category, three mock merchant agents, a negotiation loop, a comparison UI, mock payment. Ambitious; scope tightly.

**Risk:** Can look scripted if the agents are not genuinely reasoning. Build a real offer state machine and show the log. Time risk is high.

**Kill criteria:** If the agents produce incoherent offers by 8 PM Saturday, cut to a deterministic negotiation script with LLM explanations.

---

### 10. Recurring — the subscription auditor

**One-liner:** Find the subscriptions you forgot about, the ones you don't use, and the ones about to renew.

**Target user:** Households and students with too many subscriptions.

**Journey stage:** Post-purchase → loyalty → payments.

**What it does:**
- Ingests mock transaction data (or a CSV) and identifies recurring charges.
- Detects overlapping services (three cloud storage plans), unused subscriptions, and upcoming renewals.
- Suggests cancellations or downgrades and shows annual savings.
- Offers a "cancel concierge" flow with pre-written cancellation scripts.

**60-second demo:** "You're paying for seven subscriptions; three overlap; $412/year recoverable." One click generates a cancellation email.

**Why it can win:**
- **UX (25%):** Universal pain, instantly understandable, satisfying savings number.
- **Trust (15%):** Consumer advocacy; transparent.
- **Commerce (15%):** Loyalty and engagement; potential affiliate revenue for switches.
- **Innovation (25%):** Moderate — the category exists, but a polished hackathon version can stand out.
- **Tech (20%):** Transaction parsing, clustering, LLM explanations.
- **Gap:** Not covered by adjacent winners; easy to demo.

**Track stack:** Visa + SideShift + Cloudforce | Tiger Data (time-series), MongoDB, DEV.

**Build scope:** Mock transaction dataset, clustering, dashboard, cancellation flow. Very feasible.

**Risk:** Low technical depth; may feel like a budgeting app. Differentiate with the cancel concierge and a beautiful savings story.

**Kill criteria:** If it feels like Mint, add the agentic cancellation flow and a household sharing angle.

---

### 11. Test Kitchen — commerce simulation for merchants

**One-liner:** Digital clones of your customers test your promotions before you run them.

**Target user:** E-commerce merchants and marketers.

**Journey stage:** Personalization → loyalty → merchant outcomes.

**What it does:**
- Ingests a merchant's product catalog and customer segments.
- Spins up LLM-powered "digital clones" of customer personas.
- Simulates a promotion, price change, or bundle and predicts conversion/lift.
- Shows which segment responds, which cannibalizes, and what to change.

**60-second demo:** A merchant tests "20% off bundles" versus "free shipping"; the simulation predicts a 14% lift for one segment and cannibalization for another; the merchant picks the better offer.

**Why it can win:**
- **Commerce impact (15%):** Direct, quantifiable merchant outcome — the Waddle/Gentoo playbook.
- **Tech (20%):** Multi-agent simulation, persona modeling, analytics.
- **Innovation (25%):** Few hackathon teams build merchant-side simulation.
- **UX (25%):** Harder — B2B dashboards are less emotionally compelling than consumer apps.
- **Trust (15%):** Must be clear that these are simulations, not real customers.
- **Gap:** Waddle won OpenAI's hackathon with this idea; it is validated but not saturated at student hackathons.

**Track stack:** Visa + SideShift + Cloudforce | Tiger Data, MongoDB, DEV.

**Build scope:** Mock catalog, five personas, a simulation loop, a dashboard. Medium difficulty; the quality of the simulation matters.

**Risk:** B2B UX and "simulation" can feel abstract. The demo needs a crisp before/after number. Waddle already did it; differentiate with a specific vertical (grocery or fashion).

**Kill criteria:** If the simulation outputs feel random, narrow to one decision (discount versus free shipping) and show a clear, explainable model.

---

### 12. Dispute Desk — chargeback copilot

**One-liner:** Turn a confusing chargeback into a clear, evidence-backed dispute in minutes.

**Target user:** Cardholders and small merchants dealing with disputes.

**Journey stage:** Post-purchase → payments → trust.

**What it does:**
- The user describes the problem ("I was charged twice," "the item never arrived").
- The agent gathers evidence (receipts, emails, tracking, screenshots) and maps the case to the right dispute reason code.
- Generates a filing-ready packet and a plain-language timeline.
- For merchants, it generates a rebuttal packet with evidence.

**60-second demo:** A duplicate charge becomes a complete dispute packet with a timeline and the exact reason code; the user submits it in one click.

**Why it can win:**
- **Trust (15%):** Directly Visa's domain; fairness and transparency.
- **Commerce (15%):** Reduces dispute handling cost; improves merchant and cardholder outcomes.
- **Tech (20%):** Document parsing, evidence extraction, reason-code mapping, LLM drafting.
- **Innovation (25%):** Very few hackathon teams touch disputes; unglamorous but high-value.
- **UX (25%):** The "packet" is a satisfying artifact; the timeline is easy to understand.
- **Gap:** No adjacent project covers disputes. Open lane.

**Track stack:** Visa + SideShift + Cloudforce | MongoDB, DEV.

**Build scope:** Mock transaction/email data, reason-code taxonomy, packet generator, simple UI. Feasible.

**Risk:** Domain complexity (reason codes, network rules) can eat time. Focus on the user-facing packet, not a full issuer integration. Avoid legal claims.

**Kill criteria:** If reason-code research takes more than 90 minutes, simplify to three common dispute types.

---

## 4. The bench — shorter entries

### 13. Closet — the style twin
Upload your wardrobe; the AI identifies gaps and only recommends pieces that unlock several new outfits. **Win angle:** visual, personal, high UX; strong social share. **Risk:** crowded, image-heavy. **Stack:** Visa + Perceptron + SideShift + Cloudforce.

### 14. Second Life — resale timing advisor
Tells you when to sell an item for the best price, auto-lists it, and routes proceeds into your next purchase. **Win angle:** circular commerce + loyalty; ties to T-Mobile trade-in timing. **Risk:** price-forecasting data. **Stack:** Visa + T-Mobile + SideShift + Cloudforce.

### 15. Fit — cross-brand size translator
Predicts your size in any brand from purchase and return history. **Win angle:** direct return reduction and conversion lift. **Risk:** narrow; data-dependent. **Stack:** Visa + SideShift + Cloudforce.

### 16. FreshStart — SNAP/EBT grocery optimizer
Budget-constrained meal planning with nutrition, store deals, and substitutions. **Win angle:** strong social impact and trust; a real underserved user. **Risk:** weaker Visa commerce fit; data. **Stack:** Visa + SideShift + Cloudforce.

### 17. True Price — checkout copilot
Shows the true final price (shipping, tax, return fees, warranty), finds coupons, and recommends the best payment method. **Win angle:** practical, polished, clear savings; direct T-Mobile Cart Whisperer fit. **Risk:** low innovation. **Stack:** Visa + T-Mobile + SideShift + Cloudforce.

### 18. Source — values/evidence filter
Shop by ethics and sustainability with cited evidence and a clear tradeoff against price. **Win angle:** trust and transparency. **Risk:** data sourcing and verification. **Stack:** Visa + SideShift + Cloudforce.

### 19. Upgrade Court — the viral AI jury game
Submit your phone; an AI prosecutor, defense, and judge rule on whether you should upgrade; verdicts appear on a public feed. **Win angle:** Cloudforce Most Viral; fun and shareable; T-Mobile fit. **Risk:** gimmick risk; weaker trust/commerce depth. **Stack:** Visa + T-Mobile + Cloudforce + SideShift.

### 20. BNPL Check — the installment reality check
Shows the true cost of buy-now-pay-later, the debt risk, and cheaper alternatives. **Win angle:** responsible finance; Visa trust. **Risk:** potentially anti-conversion; may not appeal to commerce judges. **Stack:** Visa + SideShift + Cloudforce.

---

## 5. What not to build

These are saturated by adjacent projects or explicitly warned against:

- **A generic "AI shopping chatbot."** T-Mobile's brief says everyone will build it; Visa judges will see dozens. If you build a chat interface, the *interaction model* must be different (multi-user, voice-first, negotiation, mandate).
- **A generic fake-store scam detector.** Sniff, Chaperone, Argus, Handshake, Moka Guardian, and Kill Bill already cover this space. Only pursue with a sharp new wedge (live voice social-engineering, agent-to-agent scams).
- **A generic "agent with a spending limit."** Argus, Handshake, Omamoris, and Visa's own reference agent cover pieces. Differentiate with the plain-English mandate + passkey + intent-verification UX.
- **A dashboard-only B2B tool with no consumer moment.** UX is 25% of the Visa rubric; the video needs a human story.
- **A project that covers all seven journey stages shallowly.** Pick two or three stages and go deep.
- **A project that requires real transaction or merchant data you don't have.** Use mock data and be transparent; judges reward a credible demo over an overclaim.
- **A project with no payment moment.** Visa judges expect to see checkout/payment, even if mocked with tokenization and a confirm step.

---

## 6. Patterns from adjacent winners

1. **Full journey, not one step.** The strongest Visa projects cover discover → decide → pay, with a transaction preview and explicit confirmation.
2. **Trust is the product, not a disclaimer.** Tokenization, passkeys, spending rules, human approval, intent verification, scam detection.
3. **Deterministic logic + AI.** The best projects constrain the LLM with rules, permissions, state machines, and budget checks. The AI proposes; the system disposes.
4. **Make the AI's work visible.** Sniff streams fraud checks; Pixel Closet visualizes agents; Sherpa shows agents negotiating. A chat reply alone is not a demo.
5. **A specific user beats "shoppers."** Older adults, families, flatmates, blind users, neurodivergent users, students.
6. **A quantifiable commerce outcome.** Savings, conversion lift, return reduction, fraud loss prevented, false-positive reduction.
7. **Real integrations or convincing mocks.** Visa sandbox APIs, Shopify, Google Shopping, store maps, real baskets. Mock payments with tokenization and test declines still score.
8. **Narrow category, deep demo.** Footwear, fashion, groceries, Target, phones/plans.
9. **Polished UX.** 25% of the Visa rubric. A beautiful, narrative interface beats a deeper backend.
10. **A 3-minute story.** Problem → live "wow" moment → payment/trust step → measurable outcome → track mapping.

**Closest precedents to study:**
- **Conversational Commerce Chatbot** (LifeHack 2026, Visa challenge) — full journey + tokenized mock payment + explicit confirm.
- **Chaperone** (LifeHack 2026, Visa challenge) — specific underserved user + passkey-signed family spending rules + Visa sandbox APIs.
- **Sherpa** (LifeHack 2026, Visa challenge) — agent-to-agent negotiation + Visa payment in-chat.
- **Sniff** (TreeHacks 2026) — visible, streaming trust investigation.
- **Pixel Closet** (ShellHacks 2025 winner) — multi-agent visualization + affiliate revenue.
- **Waddle/Gentoo** (OpenAI GPT-5 Hackathon winner) — quantifiable merchant outcome.
- **Tool Assisted Shopping** (Cal Hacks 11.0 winner) — narrow, concrete, polished utility.
- **MagiCart** (Google Maps Platform Awards winner) — price comparison + route optimization + savings.
- **Visa's own reference agent** (`visa/vic-reference-agent`) — LangGraph + MCP + VTS + Visa Payment Passkey. Mirror this flow even if you mock the credentials.

---

## 7. Recommended pick + 21-hour plan

### Primary recommendation: Table Talk

**Why:** It has the highest Visa score in this catalog, the best track stack (Visa + T-Mobile Household Mix + SideShift + Cloudforce), and a demo that is inherently narrative. It also fills the clearest gap in the adjacent-project landscape: nobody combines group decision + signed spending authority + tokenized payment.

**If the team wants a higher innovation ceiling:** Calm Cart.  
**If the team wants the safest polished demo:** Timekeeper.  
**If the team wants the most viral play:** Gift Circle.

### 21-hour build plan (Table Talk)

| Window | Focus |
|---|---|
| **Now–12:30** | Decide, set up accounts (Gemini, Backboard, MongoDB, Vercel), write the 1-page spec + demo script. **No product code yet.** |
| 12:30–1:30 | Repo, design system (Tailwind + shadcn/ui), mock product/plan data, room state skeleton |
| 1:30–5:30 | Core loop: two participants, constraints, shortlist, tradeoff table |
| 5:30–9:30 | Third participant, voting, mediator compromise, UI polish |
| **9:30–10:30** | **Devpost draft submission (mandatory)** + rough recording |
| 10:30–2:00 | Passkey-signed mandate, tokenized checkout mock, payment confirmation, savings tally |
| 2:00–6:00 | Sleep in shifts. A 4-hour window beats a broken Sunday. |
| 6:00–8:00 | Final polish + record the 3-minute video |
| 8:00–9:30 | Write Devpost, rehearse pitch, **submit early** |
| 9:30–10:00 | Buffer |
| 10:20 | At HUB Ballroom |

### 3-minute video script (Table Talk)

- **0:00–0:20 — Problem:** "A family decides to upgrade three phones. One wants battery, one wants camera, one wants a low bill. They open 14 tabs, argue, and give up."
- **0:20–0:45 — Thesis:** "Table Talk is a shared decision room. Everyone joins, states constraints, and an AI mediator finds the options that satisfy the household."
- **0:45–1:45 — Live demo:** Three windows; constraints; mediator proposes two bundles; tradeoff table; teen vetoes; compromise; vote.
- **1:45–2:20 — Payment:** Passkey-signed mandate, tokenized checkout, explicit confirmation, savings tally.
- **2:20–2:40 — Tech:** Multi-agent mediation, constraint solver, plan math, Visa tokenization/passkey flow.
- **2:40–3:00 — Impact + mapping:** Commerce impact, T-Mobile Household Mix, SideShift, Cloudforce, next steps.

### Presentation tips

- Keep the live demo under 90 seconds; have a recorded backup.
- Put the track mapping on one slide: Visa stages covered, T-Mobile Household Mix, SideShift, Cloudforce.
- Name the user and the number: "A family of three saves $480/year and decides in four minutes."
- Do not demo login, settings, or onboarding. Start at the problem.
- Rehearse the first 15 seconds until it is muscle memory.

---

## 8. Submission checklist

- [ ] Public GitHub repo created at 12:30; commit from the start (proves the 70/30 rule)
- [ ] Devpost draft submitted by **10:30 PM Saturday**
- [ ] Exactly **one title track: Visa**
- [ ] Up to three sponsored side tracks: **T-Mobile, SideShift, Cloudforce** (adjust per idea)
- [ ] Non-sponsored: **NEXT**, **Gemini**, **Backboard**, **DEV**, and **Freshman** if the whole team qualifies
- [ ] 3-minute video recorded and uploaded
- [ ] Final submission by **9:30 AM Sunday** (buffer before the 10:00 AM lock)
- [ ] Laptop, charger, backup recording, QR code to the demo at the table
- [ ] One person owns the pitch; one owns the demo; one owns the Devpost/video
- [ ] Check the hacker profile for the judging schedule

---

## 9. Sources

- [Visa rubric](../info/visa-rubric.txt)
- [Conversational Commerce Chatbot — Devpost](https://devpost.com/software/conversational-commerce-chatbot)
- [Chaperone — Devpost](https://devpost.com/software/chaperone-2rze5w)
- [Sherpa — Devpost](https://devpost.com/software/lh26-qexhxq)
- [Visa VIC reference agent — GitHub](https://github.com/visa/vic-reference-agent)
- [Visa AI toolkit — GitHub](https://github.com/visa/ai)
- [Visa Intelligent Commerce — Visa Developer](https://developer.visa.com/capabilities/visa-intelligent-commerce)
- [Sniff — project page](https://yifank.github.io/projects/sniff/) · [Devpost](https://devpost.com/software/sniff-l9xk1q)
- [Argus — Devpost](https://devpost.com/software/argus-n507tw)
- [Handshake — Devpost](https://devpost.com/software/handshake-wmitzy)
- [Gather — Devpost](https://devpost.com/software/gather-0c1xzt)
- [MiyKo — DEV](https://dev.to/andriishupta/miyko-a-durable-ai-workflow-for-shared-shopping-1bnm)
- [Converge — Devpost](https://devpost.com/software/converge-zn50xd)
- [Moka Guardian — KTU](https://surdurulebilirlik.ktu.edu.tr/en/news/ai-powered-security-shield-brings-first-place-to-our-university)
- [Kill Bill — Money20/20 Hackathon winner](https://blog.killbill.io/blog/kill-bill-among-winners-money2020-hackathon/)
- [Tool Assisted Shopping — University of the Pacific](https://www.pacific.edu/blog/2024/11/20/students-win-first-place-cal-hacks/)
- [MagiCart — Texas State](https://news.txst.edu/accolades-and-achievements/2026/texas-state-students-earn-global-recognition-in-google-maps-platform-awards-hackathon.html)
- [Pixel Closet — GitHub](https://github.com/AaxHamm3r/pixel-closet-shellhacks-2025)
- [Waddle/Gentoo — MK](https://www.mk.co.kr/en/it/11407305)
- [Blindsight — Visa Developer blog](https://community.developer.visa.com/t5/blogs/blogarticleprintpage/blog-id/Developer_Blog/article-id/220)
- [DubHacks '24 winners — Intel](https://community.intel.com/t5/Blogs/Tech-Innovation/Artificial-Intelligence-AI/DubHacks-24-Hackathon-Where-Developers-Innovatively-Utilized/post/1639339)
- [Visa agentic commerce demo — CNBC TV18](https://www.cnbctv18.com/personal-finance/gff-ai-agents-could-soon-shop-pay-for-you-visa-agentic-commerce-demo-19988305.htm)
- [BBVA + Visa agent-initiated payment — The Paypers](https://thepaypers.com/payments/news/bbva-completes-its-first-ai-agent-initiated-payment-together-with-visa)

## 10. Feedbacks
- I want this ideas to be remmebered  we can always add it later.
1. RefundGuard — the refund agent that can prove it's safe.

- Stack: Cook Smarter + VEYZL + SideShift + Cloudforce | NEXT, Gemini, MongoDB, DEV
- What: An AI support agent for e-commerce refunds that follows policy, resists prompt injection and social engineering, and escalates edge cases to a human. Then run a real VEYZL audit on the repo, show it flagged missing human oversight / PII handling, fix it, and demo the before/after.
- 60-sec demo: A judge tries to scam the agent into a $500 refund; it refuses — then you show the audit finding that changed the build.
- Build: Agent + policy docs + adversarial test suite + VEYZL GitHub check.
- Why it scores: VEYZL's own example is exactly this app, and their judging criterion is "evidence the findings changed the build." Cook Smarter = automation. SideShift = B2B SaaS. Strong, credible founder story.
- Risk: Less visually exciting; needs a polished UI and a clear "why care" narrative. VEYZL setup can eat time.

2. Sniff (TreeHacks 2026) — LLM shopping agent across Amazon/Best Buy/Walmart/Nordstrom that runs five parallel fraud checks per listing: WHOIS/domain age, Safe Browsing + ScamAdviser, Reddit sentiment, typosquatting, and page red flags. It assigns a 0–100 trust score, recommends the cheapest among the safest, and streams the investigation live. Flagged listings get removed with a "PURGE CURSED" animation.
Why it matters: The best example of making the trust layer the show. The AI is visibly investigating, which is inherently watchable on video.