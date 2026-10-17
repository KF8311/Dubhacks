# Visa Track — Round 2: RefundGuard, Sniff, and New Directions

**Additive to:** `visa-ideas.md` (the first catalog)  
**Team:** 3–4 people, AI/backend strong  
**Constraint:** 21.5-hour build, 3-minute video, Visa rubric  
**Purpose:** Keep the ideas you flagged, expand them into full families, and add fresh concepts that are not rehashes of round one.

---

## 0. What was incorporated from your feedback

You added two anchors at the bottom of `visa-ideas.md`:

- **RefundGuard** — the policy-safe refund agent with a real VEYZL audit.
- **Sniff** — the TreeHacks 2026 shopping agent whose five parallel fraud checks make the trust layer the show.

Both are preserved here and expanded:

- **RefundGuard family → 10 ideas** (§3): returns, disputes, refund policy, adversarial testing, and consumer-side refund help.
- **Sniff family → 10 ideas** (§4): trust receipts, review forensics, seller graphs, counterfeit detection, and agent-to-agent trust.
- **Fresh ideas → 18 new concepts** (§5): group buying, regret prediction, caregiver commerce, subscription sharing, privacy vaults, and more.

**Important note on track fit:** RefundGuard was originally a **Cook Smarter** idea, not a Visa title-track idea. If the team is committed to Visa, use the **[Visa-fit]** variants below. If the team is open to switching to Cook Smarter, RefundGuard remains the strongest VEYZL play. Each idea is tagged.

**Tags:** `[Visa-fit]` = can be the Visa title-track submission · `[Cook Smarter]` = fits Cook Smarter better · `[B2B]` = merchant/enterprise-facing · `[Bench]` = shorter entry.

---

## 1. TL;DR — top new picks

| Rank | Idea | Family | Visa score | Why it can win |
|---|---|---|---|---|
| **1** | **Trust Trail** | Sniff | **4.65** | Turns trust from a hidden score into a shareable receipt. High UX + Trust, easy to demo, stacks with any v1 idea. |
| **2** | **ReturnGuard** | RefundGuard | **4.63** | Returns are a massive cost; fraud detection + policy + VEYZL audit gives a clear ROI and a dramatic demo. |
| **3** | **Purchase Regret Predictor** | Fresh | **4.58** | Contrarian, memorable thesis: stop the purchase before it happens. Backboard memory fit; very demoable. |
| **4** | **Review Forensics** | Sniff | **4.63** | Universal pain; fake-review detection is visual, technical, and trust-forward. |
| **5** | **Policy-as-Code Refund Agent** | RefundGuard | **4.55** | The purest "deterministic logic + AI" story; exactly VEYZL's criteria; credible B2B SaaS. |

**Honorable mentions:** Deal Authenticity Scanner (4.58), Agent-to-Agent Trust Handshake (4.68 but low feasibility), Seller Reputation Graph (4.60), Group Buy Agent (4.45), Caregiver Commerce (4.40).

**If you want the safest polished demo:** Trust Trail or Deal Authenticity Scanner.  
**If you want the strongest VEYZL narrative:** ReturnGuard or Policy-as-Code.  
**If you want the most novel consumer idea:** Purchase Regret Predictor.  
**If you want the deepest tech:** Seller Reputation Graph or Agent-to-Agent Trust Handshake.

---

## 2. How to read the scores

Same Visa rubric as round one, using the corrected weights (UX 25%, Tech 20%):

**Visa score** = Innovation×0.25 + UX×0.25 + Tech×0.20 + Commerce×0.15 + Trust×0.15.

Scores are 1–5 and subjective. Use them to argue, not to decide mechanically.

---

## 3. The RefundGuard family — safe AI support, returns, and disputes

**The core thesis:** An AI agent that touches money must be constrained, auditable, and fair. RefundGuard proved the pattern: policy + adversarial resistance + human escalation + a VEYZL audit that visibly changed the build. This family applies that pattern to different commerce moments.

### A1. ReturnGuard — the return fraud + policy agent `[Visa-fit]` `[B2B]`

**One-liner:** An AI returns agent that resolves legitimate returns instantly and catches the abusive ones.

**What it does:**
- Handles return requests end-to-end: eligibility, policy checks, label generation, refund or exchange.
- Detects abuse signals: wardrobing, receipt manipulation, serial returners, empty-box claims, address reuse.
- Explains every decision to the customer and offers a clear appeal path.
- Escalates high-value or ambiguous cases to a human with a summary.
- Runs a VEYZL audit; shows the finding that changed the build (e.g., missing human oversight).

**60-second demo:** A serial returner submits a worn dress with an altered receipt; the agent flags the inconsistencies and offers an appeal. A legitimate customer with a defective item gets an instant refund. The merchant dashboard shows $12k in prevented abuse.

**Why it can win:**
- **Commerce impact (15%):** Returns are one of the largest controllable costs in e-commerce. Fraud and abuse are a direct line item.
- **Trust (15%):** Fair, explainable decisions with an appeal path; the VEYZL audit proves the system is safe.
- **Tech (20%):** Policy engine + fraud signals + LLM explanations + audit trail.
- **UX (25%):** Two-sided flow: a calm customer experience and a clean merchant dashboard.
- **Innovation (25%):** Very few hackathon teams build returns; most build discovery.
- **Gap:** RefundGuard is a support agent. ReturnGuard is returns-specific, with fraud detection and a fairness/audit story.

**Stack:** Visa + VEYZL + SideShift + Cloudforce | NEXT, MongoDB, DEV.

**Risk:** Synthetic data; fairness/bias concerns. Never accuse a real customer in the demo — use clearly fictional personas.

---

### A2. Policy-as-Code Refund Agent `[Visa-fit]` `[B2B]`

**One-liner:** A merchant writes its refund policy in plain English; the agent can only act inside those rules.

**What it does:**
- Merchant writes or uploads a policy ("no refunds after 30 days, except defective; 15% restocking fee on opened electronics").
- The system compiles it into deterministic rules with explicit edge cases.
- The LLM agent handles the conversation but can only take actions the rule engine permits.
- Every decision shows the exact rule it applied; every override requires human approval.
- VEYZL audits the system; the team shows a finding and the fix.

**60-second demo:** Four edge cases — a defective item at day 45, an opened electronic at day 10, a missing receipt, and a prompt-injection attempt — are handled correctly; the injection is blocked and logged.

**Why it can win:**
- **Tech (20%):** The purest example of "AI proposes, the system disposes."
- **Trust (15%):** Every decision is traceable to a rule; no hallucinated policy.
- **Commerce (15%):** Lower support cost, consistent refunds, fewer escalations.
- **UX (25%):** The policy editor and decision trace are beautiful, legible artifacts.
- **Innovation (25%):** "Policy-as-code for commerce agents" is a fresh, enterprise-credible framing.
- **Gap:** RefundGuard is the agent; this is the safety substrate underneath it.

**Stack:** Visa + VEYZL + SideShift + Cloudforce | Gemini, MongoDB, DEV.

**Risk:** Building a policy DSL can eat time. Keep it to 5–6 rule types and a visual editor.

---

### A3. Adversarial Commerce Red Team `[Visa-fit]` `[B2B]`

**One-liner:** A red-team agent that attacks your own checkout or support bot before a real scammer does.

**What it does:**
- Takes a target agent (refund, support, checkout) and runs adversarial tests: prompt injection, social engineering, policy edge cases, PII extraction, refund manipulation.
- Produces a vulnerability report with severity, reproduction steps, and suggested fixes.
- Re-runs the tests after the fix and shows a before/after scorecard.
- Integrates with VEYZL so the findings become part of the compliance audit.

**60-second demo:** The red-team agent talks a naive refund bot into a $500 refund and extracts a fake customer email. The team patches the prompt and rule engine; the re-run blocks both. The scorecard goes from 4 vulnerabilities to 0.

**Why it can win:**
- **Innovation (25%):** Meta and novel — a security product for commerce agents.
- **Tech (20%):** Adversarial generation, evaluation harness, severity scoring, audit integration.
- **Trust (15%):** Directly improves the safety of AI commerce.
- **UX (25%):** The before/after vulnerability report is a compelling visual.
- **Commerce (15%):** B2B security/QA budget; merchants and platforms need this.
- **Gap:** Nobody in the adjacent set builds an adversarial tester for commerce agents specifically.

**Stack:** Visa + VEYZL + SideShift + Cloudforce | Gemini, DEV.

**Risk:** Could read as a dev tool rather than a commerce product. Frame it as "trust infrastructure for merchants" and show the money at risk.

---

### A4. Consumer Refund Concierge `[Visa-fit]`

**One-liner:** An agent that fights for your refund when a merchant says no.

**What it does:**
- The user describes the problem; the agent gathers order details, photos, and correspondence.
- It reads the merchant's policy and the relevant consumer-protection rules.
- It drafts a clear, firm escalation email or chat message with the evidence.
- It tracks deadlines and escalates to a card dispute if the merchant does not respond.
- It explains the user's options in plain language.

**60-second demo:** A merchant denies a legitimate refund for a broken item. The agent cites the policy's defect clause, attaches photos, drafts an escalation, and gets a resolution (mock). The user sees a timeline and a resolution.

**Why it can win:**
- **Trust (15%):** Consumer advocacy is a strong, memorable trust story.
- **UX (25%):** The timeline and drafted message are satisfying, legible artifacts.
- **Innovation (25%):** Most teams build merchant-side support; consumer-side refund help is rare.
- **Tech (20%):** Document parsing, policy RAG, evidence assembly, drafting.
- **Commerce (15%):** Lower chargeback volume; better merchant-customer outcomes.
- **Gap:** RefundGuard serves the merchant; this serves the consumer. Both are valuable; pick one side.

**Stack:** Visa + SideShift + Cloudforce | Gemini, DEV.

**Risk:** Avoid legal advice. Frame it as policy/evidence assistance, not legal representation.

---

### A5. Chargeback Court `[Visa-fit]`

**One-liner:** A neutral AI mediator that hears both sides of a card dispute and proposes a fair resolution.

**What it does:**
- Cardholder and merchant each submit evidence through a shared case room.
- The AI summarizes both sides, maps the case to the correct dispute reason code, and identifies inconsistencies.
- It proposes a resolution (full refund, partial, or denial) with a written rationale.
- A human arbiter approves the final decision; the audit trail is visible to both sides.

**60-second demo:** A "item not received" dispute has tracking that shows delivery to the wrong address. The AI catches the inconsistency, proposes a refund, and shows both sides the reasoning. A human approves.

**Why it can win:**
- **Trust (15%):** Fairness and transparency are the product.
- **Commerce (15%):** Reduces dispute handling cost and improves outcomes for both sides.
- **Tech (20%):** Evidence parsing, reason-code mapping, two-sided reasoning.
- **UX (25%):** The case room and rationale are compelling artifacts.
- **Innovation (25%):** Very few teams touch disputes; it is unglamorous but high-value.
- **Gap:** No adjacent project covers two-sided dispute mediation.

**Stack:** Visa + SideShift + Cloudforce | MongoDB, DEV.

**Risk:** Domain complexity. Keep to three dispute types and be clear it is a prototype, not a network ruling.

---

### A6. Return-to-Resale Agent `[Visa-fit]`

**One-liner:** Instead of a refund, the agent resells the item and credits the customer.

**What it does:**
- When a customer initiates a return, the agent estimates resale value and condition.
- It offers a choice: full refund minus return shipping, or resale with a higher net credit.
- It lists the item on a resale marketplace, handles buyer questions, and ships it.
- The merchant avoids return processing; the customer gets more money back; the item stays in use.

**60-second demo:** A returned jacket is listed and sold in three minutes; the customer gets 80% back instead of 60%; the merchant avoids the return cost. A dashboard shows the savings.

**Why it can win:**
- **Commerce (15%):** Clear merchant savings and customer value.
- **Innovation (25%):** A fresh alternative to the refund/return binary.
- **Trust (15%):** Transparent condition grading and pricing.
- **UX (25%):** A simple choice screen with two numbers is very demoable.
- **Tech (20%):** Condition assessment, pricing, marketplace listing.
- **Gap:** RefundGuard resolves the refund; this avoids it entirely.

**Stack:** Visa + SideShift + Cloudforce | Gemini, MongoDB, DEV.

**Risk:** Resale marketplace integration and condition grading. Mock the marketplace and use a simple condition rubric.

---

### A7. Refund Policy Simulator `[Visa-fit]` `[B2B]` `[Bench]`

Merchants simulate a refund policy against adversarial customer personas to find loopholes and estimate abuse/cost before launch. Demo: a policy fails 12% of abuse cases; patch; re-run; abuse drops to 3%. **Why it can win:** quantifiable, VEYZL-friendly, B2B. **Risk:** simulation credibility. **Stack:** Visa + VEYZL + SideShift + Cloudforce.

### A8. Chargeback Evidence Copilot `[Visa-fit]` `[B2B]` `[Bench]`

Helps merchants assemble evidence to fight illegitimate chargebacks; redacts PII, follows network rules, generates a filing packet. Demo: a "not received" chargeback is rebutted with tracking and a delivery photo. **Why it can win:** direct Visa domain, clear ROI. **Risk:** domain complexity. **Stack:** Visa + SideShift + Cloudforce.

### A9. Refund Escalation with Passkey Approval `[Visa-fit]` `[Bench]`

High-value or high-risk refunds require a human approval signed with a passkey; the agent gathers evidence, proposes a resolution, and logs the approval chain. Demo: a $900 refund triggers an approval request; the manager approves with a passkey. **Why it can win:** trust/consent; ties to Mandate and Table Talk. **Risk:** narrow; could be a feature. **Stack:** Visa + VEYZL + SideShift + Cloudforce.

### A10. Return Reason Intelligence `[Visa-fit]` `[B2B]` `[Bench]`

Analyzes return reasons and reviews to find product/content/sizing issues; recommends fixes and quantifies impact. Demo: "38% of returns cite 'runs small'; updating the size chart could save $22k/quarter." **Why it can win:** B2B ROI, easy to understand. **Risk:** less consumer demo. **Stack:** Visa + SideShift + Cloudforce.

---

## 4. The Sniff family — visible trust and investigation

**The core thesis:** Trust should not be a hidden backend score. It should be a visible, explainable, shareable investigation. Sniff proved that watching the AI check five fraud signals is inherently compelling. This family applies that "visible investigation" pattern to different commerce surfaces.

### B1. Trust Trail — the shareable trust receipt `[Visa-fit]`

**One-liner:** At checkout, the AI runs a visible trust investigation and hands you a receipt showing exactly what it verified.

**What it does:**
- Before payment, the agent checks the merchant: domain age, TLS, WHOIS, review patterns, return policy, contact info, payment methods, social sentiment, and complaint history.
- It produces a **trust receipt**: green/yellow/red, with each check and its evidence.
- It explicitly says what it could **not** verify — no black-box score.
- The receipt is shareable, so a friend can see why a store is safe or risky.
- Merchants can display a verified receipt as a badge.

**60-second demo:** A suspicious store gets a red receipt with three specific red flags; a known store gets a green receipt. The user shares the red receipt to a group chat; a friend avoids the scam.

**Why it can win:**
- **Innovation (25%):** Sniff investigates; Trust Trail makes the *receipt* the product — a shareable trust artifact.
- **UX (25%):** A clean, visual receipt is instantly understandable and beautiful.
- **Trust (15%):** Transparency is the product; it explicitly shows uncertainty.
- **Tech (20%):** Multi-source verification, evidence aggregation, LLM explanation.
- **Commerce (15%):** Trust increases conversion; merchants can display a verified badge.
- **Gap:** No adjacent project turns trust into a shareable, merchant-embeddable artifact.

**Stack:** Visa + SideShift + Cloudforce | Gemini, DEV.

**Risk:** Data sources and false positives. Use a curated mock set and be explicit about what is verified versus inferred.

---

### B2. Review Forensics — the fake-review detector `[Visa-fit]`

**One-liner:** A forensic score that tells you how much of a product's review section is real.

**What it does:**
- Analyzes reviews for AI-generated text, incentivized reviews, review bombing, burst patterns, reviewer overlap, and suspicious timing.
- Produces an **authenticity score** and shows the evidence ("42 reviews posted in 6 minutes; 18 share the same phrasing").
- Separates product quality from review manipulation.
- Offers a "trusted reviews only" view.

**60-second demo:** A 4.9-star product is revealed to have 60% suspicious reviews; the authenticity score drops to 2.8; the "trusted only" view shows a much more honest 3.9.

**Why it can win:**
- **Innovation (25%):** A sharp, memorable wedge; fake reviews are a universal pain.
- **Trust (15%):** Directly addresses deception.
- **UX (25%):** The score and evidence panel are easy to understand.
- **Tech (20%):** NLP stylometry, burst detection, reviewer graph, LLM explanations.
- **Commerce (15%):** Better decisions, fewer returns, more trust.
- **Gap:** Sniff checks stores; Review Forensics checks the reviews themselves.

**Stack:** Visa + SideShift + Cloudforce | Gemini, DEV.

**Risk:** Accuracy and defamation concerns. Use synthetic/mock review data and frame the score as probabilistic.

---

### B3. Seller Reputation Graph `[Visa-fit]` `[B2B]`

**One-liner:** A cross-marketplace identity graph that catches sellers who reinvent themselves after being banned.

**What it does:**
- Aggregates seller signals across marketplaces: names, addresses, payment identifiers, product photos, review patterns, return addresses.
- Detects likely ban evasion, shell stores, and review rings.
- Gives each seller a portable reputation score and a graph of related stores.
- Lets consumers check a seller before buying; lets platforms flag risky sellers.

**60-second demo:** A "new" seller with five-star reviews is linked to a banned store through a shared return address and identical product photos. The graph shows the connection.

**Why it can win:**
- **Innovation (25%):** Deep, novel, and genuinely useful.
- **Tech (20%):** Entity resolution, graph analytics, review fraud detection.
- **Trust (15%):** Directly reduces fraud and ban evasion.
- **Commerce (15%):** Platforms pay for risk reduction; consumers trust the badge.
- **UX (25%):** The graph visualization is compelling.
- **Gap:** Nobody in the adjacent set builds a cross-marketplace reputation graph.

**Stack:** Visa + SideShift + Cloudforce | Neo4j or MongoDB, DEV.

**Risk:** Data access and entity-resolution accuracy. Use a mock graph with 3–4 linked stores.

---

### B4. Deal Authenticity Scanner `[Visa-fit]`

**One-liner:** It tells you whether a "too good to be true" deal is actually real.

**What it does:**
- Checks the deal against price history, MSRP, competitor prices, seller history, product photos, and review patterns.
- Flags fake discounts (inflated "was" prices), counterfeit listings, drop-shipping red flags, and bait-and-switch patterns.
- Gives a simple verdict: **real deal**, **caution**, or **likely fake**.
- Explains the evidence in one screen.

**60-second demo:** A "90% off" luxury watch is flagged as counterfeit with three evidence points; a genuine 30% off deal is verified.

**Why it can win:**
- **Innovation (25%):** A sharp, memorable consumer promise.
- **Trust (15%):** Consumer protection is the product.
- **UX (25%):** The verdict screen is instantly understandable.
- **Tech (20%):** Price history, image checks, seller signals, LLM explanation.
- **Commerce (15%):** Protects conversion and trust; merchants can prove deals are real.
- **Gap:** Sniff checks store trust; this checks the *deal* itself.

**Stack:** Visa + Perceptron (image checks) + SideShift + Cloudforce | Gemini, DEV.

**Risk:** Counterfeit detection accuracy and legal exposure. Use mock listings and avoid naming real brands as fakes.

---

### B5. Agent-to-Agent Trust Handshake `[Visa-fit]`

**One-liner:** Before an AI buyer agent pays a merchant agent, they exchange verifiable trust credentials — and Visa closes the payment.

**What it does:**
- The buyer agent presents a signed intent and spending mandate.
- The merchant agent presents verifiable identity, policy, and fulfillment credentials.
- A trust handshake checks both sides against a shared policy (category, price, return terms, data handling).
- If either side fails, the transaction is blocked or escalated; if both pass, payment completes with a tokenized credential.

**60-second demo:** A buyer agent rejects a merchant agent that cannot prove its return policy; then accepts a verified merchant and completes the purchase. The handshake log shows exactly what was verified.

**Why it can win:**
- **Innovation (25%):** This is the frontier of agentic commerce.
- **Tech (20%):** Verifiable credentials, trust negotiation, tokenized payment.
- **Trust (15%):** Identity + intent + policy verification on both sides.
- **Commerce (15%):** Enables safe agent traffic for merchants.
- **UX (25%):** The handshake log is a watchable, legible artifact.
- **Gap:** Visa's Intelligent Commerce is the rails; this is the trust layer on top.

**Stack:** Visa + VEYZL + SideShift + Cloudforce | Gemini, DEV.

**Risk:** Abstract and ambitious. Feasibility is low for 21 hours; only attempt with a very narrow, scripted demo.

---

### B6. "Why This Store?" Explainer `[Visa-fit]` `[Bench]`

A browser extension that explains who the seller is, where it ships from, its return policy, and the trust signals in plain language. Demo: a side panel explains a store in 10 seconds and flags one red flag. **Why it can win:** simple, useful, polished, fast to build. **Risk:** low innovation; extension permissions. **Stack:** Visa + SideShift + Cloudforce.

### B7. Counterfeit Detector `[Visa-fit]` `[Bench]`

For luxury and collectibles: image analysis + seller history + price anomaly + provenance checks; a trust score and evidence. Demo: a fake watch listing is flagged; a real one passes. **Why it can win:** visual, high-value purchases, trust. **Risk:** accuracy and legal. **Stack:** Visa + Perceptron + SideShift + Cloudforce.

### B8. Merchant Trust Dashboard `[Visa-fit]` `[B2B]` `[Bench]`

Merchants see how their store scores across trust signals and get prioritized fixes. Demo: a store's score rises from 62 to 88 after fixing its return policy and contact info. **Why it can win:** B2B, clear ROI, trust. **Risk:** less consumer story. **Stack:** Visa + SideShift + Cloudforce.

### B9. Scam Signal Screener `[Visa-fit]` `[Bench]`

Detects social-engineering scams during a purchase (fake delivery fee, refund scam, account takeover) in email/SMS/chat and warns the user. Demo: a "your package is held, pay $2.99" message is flagged. **Why it can win:** timely, real losses, trust. **Risk:** Chaperone-adjacent; false positives. **Stack:** Visa + SideShift + Cloudforce.

### B10. Marketplace Watchdog `[Visa-fit]` `[Bench]`

A public, real-time feed of scam sites and fake deals, crowdsourced + AI-verified, searchable and shareable. Demo: a new scam site appears; the watchdog flags it; users report it on a live feed. **Why it can win:** viral, public good, Cloudforce. **Risk:** moderation and legal. **Stack:** Visa + SideShift + Cloudforce.

---

## 5. Fresh ideas — new domains

These are not expansions of RefundGuard or Sniff. They are new theses about commerce.

### C1. Purchase Regret Predictor `[Visa-fit]`

**One-liner:** Before you buy, it tells you whether you will regret it — and gives you a reason to wait.

**What it does:**
- Learns your purchase patterns: late-night buys, impulse categories, items you returned or never used, price-drop regrets.
- At checkout, predicts regret risk and explains the evidence ("you regret 70% of late-night purchases over $100").
- Offers a "wait 48 hours" button that saves the cart and checks the price again later.
- Tracks whether the prediction was right and improves.

**60-second demo:** A user is about to buy a $220 impulse item at 1 AM. The app says "you regret 70% of purchases like this; wait 48 hours?" They wait; the item drops 15%; they buy it later or skip it. A "regret avoided" tally appears.

**Why it can win:**
- **Innovation (25%):** A contrarian, memorable thesis: the best commerce AI sometimes says "don't buy."
- **UX (25%):** One warning + one button; extremely demoable.
- **Tech (20%):** Behavioral memory, regret modeling, explanations.
- **Commerce (15%):** Fewer returns, higher trust, better long-term loyalty.
- **Trust (15%):** Transparent, consent-based, no manipulation.
- **Gap:** Timekeeper does this for phones; this generalizes to any purchase and uses personal history.

**Stack:** Visa + SideShift + Cloudforce | Backboard (memory), Gemini, DEV.

**Risk:** Can feel creepy. Make consent explicit, show only aggregated patterns, and let the user delete their history.

---

### C2. Group Buy Agent `[Visa-fit]`

**One-liner:** It finds strangers who want the same thing, forms a buying group, and negotiates a group discount.

**What it does:**
- Users post a desired product and a target price.
- The agent matches them with other buyers who want the same item in the same window.
- It negotiates a group price with merchants (mock in the demo).
- It splits the payment, tracks commitments, and coordinates delivery.

**60-second demo:** Eight people want the same standing desk. The agent forms a group, unlocks a 25% discount, and splits the payment. The group converges in a live room.

**Why it can win:**
- **Innovation (25%):** Social commerce + group negotiation is a fresh interaction.
- **Commerce (15%):** Higher AOV and conversion; merchants get volume.
- **UX (25%):** Watching a group form and a discount unlock is a great demo.
- **Tech (20%):** Matching, group formation, negotiation, split payment.
- **Trust (15%):** Transparent pricing and group approval.
- **Gap:** Gather and MiyKo are group carts, not group buying with merchant negotiation.

**Stack:** Visa + SideShift + Cloudforce | Gemini, MongoDB, DEV.

**Risk:** Marketplace liquidity. Simulate the other buyers in the demo and focus on the negotiation and payment mechanics.

---

### C3. Subscription Sharing Marketplace `[Visa-fit]`

**One-liner:** Legally match households to share family plans and subscriptions, split payments, and manage access.

**What it does:**
- Users list subscriptions with unused seats (streaming, music, cloud storage, family phone plans).
- The agent matches compatible households, verifies eligibility, and sets up cost sharing.
- It splits payments, tracks renewals, and handles access changes.
- It optimizes the plan mix to reduce total cost.

**60-second demo:** Two households share a family plan; each saves $18/month; access is managed in one dashboard. A price-hike alert suggests a better plan.

**Why it can win:**
- **Innovation (25%):** A fresh, practical marketplace thesis.
- **Commerce (15%):** Recurring payments, loyalty, clear savings.
- **UX (25%):** Simple savings math and a clean shared dashboard.
- **Trust (15%):** Eligibility checks, transparent splits, no account sharing beyond terms.
- **Tech (20%):** Matching, payment splitting, access management.
- **Gap:** None in the adjacent set.

**Stack:** Visa + T-Mobile (family plans) + SideShift + Cloudforce | Gemini, DEV.

**Risk:** Terms-of-service legality and trust/safety. Frame it as "eligible family-plan sharing," not credential sharing.

---

### C4. Caregiver Commerce `[Visa-fit]`

**One-liner:** A trusted commerce agent for family caregivers managing purchases for someone else.

**What it does:**
- The caregiver sets budgets, approved categories, and delivery addresses for a dependent.
- The agent handles recurring purchases (medication, groceries, supplies) and checks for duplicate or conflicting orders.
- It asks for approval on unusual purchases and logs every action.
- It coordinates delivery and returns with the dependent's schedule.

**60-second demo:** A caregiver approves a medication refill; the agent checks the price, avoids a duplicate order, and schedules delivery. The family sees a clean log.

**Why it can win:**
- **Innovation (25%):** A specific, underserved user with real recurring needs.
- **Trust (15%):** Budgets, approvals, logs, and privacy.
- **UX (25%):** A calm, supervised commerce flow.
- **Commerce (15%):** Recurring purchases and loyalty.
- **Tech (20%):** Preference modeling, approval workflows, delivery coordination.
- **Gap:** Chaperone targets older adults; this targets the caregiver managing for someone else.

**Stack:** Visa + SideShift + Cloudforce | Backboard, Gemini, DEV.

**Risk:** Health claims and privacy. Avoid medical advice; focus on logistics and budgeting.

---

### C5. Commerce Accessibility Auditor `[Visa-fit]` `[B2B]`

**One-liner:** It audits online stores for accessibility and tells merchants how much revenue they are leaving behind.

**What it does:**
- Scans a store's product, cart, and checkout flow for accessibility issues: screen-reader labels, contrast, keyboard navigation, focus order, error messages, timeouts.
- Gives a "shopability" score with prioritized fixes.
- Estimates the revenue at stake from disabled shoppers.
- Offers a fixed version of the checkout flow as a demo.

**60-second demo:** A store's checkout fails seven accessibility checks; the tool shows the fixes and the estimated revenue at stake; the fixed flow passes.

**Why it can win:**
- **UX (25%):** Accessibility is a UX story with a clear human impact.
- **Trust (15%):** Inclusion and fairness.
- **Innovation (25%):** Very few commerce teams build accessibility audits.
- **Commerce (15%):** Merchants unlock revenue from an underserved market.
- **Tech (20%):** Automated accessibility testing, LLM explanations.
- **Gap:** No adjacent project.

**Stack:** Visa + SideShift + Cloudforce | Gemini, DEV.

**Risk:** B2B and less consumer-facing; the demo needs a strong before/after.

---

### C6. AI Layaway — price-lock savings `[Visa-fit]`

**One-liner:** Save toward a purchase, lock the price, and complete it when you are ready.

**What it does:**
- The user picks an item and a target date.
- The app locks the current price, finds coupons, and auto-saves in small increments.
- It checks for price drops and negotiates a better deal if possible.
- When the goal is met, it completes the purchase with a tokenized payment.

**60-second demo:** A $400 jacket is locked at $360 with a coupon; the user saves $40/week; the purchase completes in 10 weeks. A price-drop alert saves another $20.

**Why it can win:**
- **Innovation (25%):** A fresh alternative to BNPL and credit.
- **Commerce (15%):** Conversion, loyalty, no debt trap.
- **UX (25%):** A clear progress bar and a satisfying completion.
- **Trust (15%):** Transparent, no interest, no hidden fees.
- **Tech (20%):** Price tracking, savings automation, payment scheduling.
- **Gap:** BNPL alternatives are rare in hackathons.

**Stack:** Visa + SideShift + Cloudforce | Gemini, DEV.

**Risk:** Financial regulation and trust. Keep it a prototype; avoid holding real money.

---

### C7. Cross-Border Landed Cost `[Visa-fit]` `[Bench]`

Shows the true landed cost (duties, taxes, fees, currency) before checkout and suggests alternatives. Demo: a $120 item actually costs $178 landed; the app suggests a local alternative at $140. **Why it can win:** Visa cross-border, clear savings, no surprise fees. **Risk:** duty data. **Stack:** Visa + SideShift + Cloudforce.

### C8. Commerce Identity Vault `[Visa-fit]` `[Bench]`

A privacy-preserving identity/payment profile that shares verified attributes (age, address) without raw PII; merchants get what they need, users keep control. Demo: checkout requests age and address; the vault shares proofs, not raw data. **Why it can win:** privacy/trust, Visa tokenization, deep tech. **Risk:** complexity and abstraction. **Stack:** Visa + VEYZL + SideShift + Cloudforce.

### C9. Purchase Recall Alert `[Visa-fit]` `[Bench]`

Monitors recalls for products you bought; alerts you and helps with refunds, returns, or replacements. Demo: a recalled appliance triggers an alert; the agent files a replacement. **Why it can win:** trust, safety, post-purchase loyalty. **Risk:** data sources. **Stack:** Visa + SideShift + Cloudforce.

### C10. Dynamic Budget Basket `[Visa-fit]` `[Bench]`

A grocery basket that re-optimizes in real time as prices change, keeping nutrition and budget constraints; auto-substitutes. Demo: prices spike; the basket swaps items and stays under $80 with the same nutrition. **Why it can win:** practical, clear savings. **Risk:** MagiCart-adjacent; data. **Stack:** Visa + SideShift + Cloudforce.

### C11. Second-Hand First `[Visa-fit]` `[Bench]`

A "buy used first" agent that checks resale marketplaces before new, verifies authenticity/condition, and compares total cost. Demo: a new $300 headset vs. a verified used $180 one; the agent recommends used with a warranty. **Why it can win:** sustainability, savings, trust. **Risk:** marketplace data. **Stack:** Visa + SideShift + Cloudforce.

### C12. Inclusive Sizing Commerce `[Visa-fit]` `[Bench]`

A size-inclusive shopping layer: real fit data from diverse body types, brand size transparency, virtual try-on, and fit confidence. Demo: a user finds a brand that actually fits; return risk drops. **Why it can win:** UX, return reduction, underserved users. **Risk:** data and body-image sensitivity. **Stack:** Visa + Perceptron + SideShift + Cloudforce.

### C13. Commerce Language Bridge `[Visa-fit]` `[Bench]`

Real-time translation and cultural adaptation for cross-border shopping; explains sizing, returns, and payment norms. Demo: a Japanese store is translated; the agent explains sizing and returns; checkout completes. **Why it can win:** Visa cross-border, global. **Risk:** translation quality. **Stack:** Visa + SideShift + Cloudforce.

### C14. Commerce Coach for First-Time Buyers `[Visa-fit]` `[Bench]`

Teaches young adults how to shop safely: credit vs. debit, returns, scams, budgeting, subscription traps; interactive simulations. Demo: a first-time buyer faces a scam checkout; the coach warns and explains. **Why it can win:** trust/education, social impact. **Risk:** weaker commerce impact. **Stack:** Visa + SideShift + Cloudforce.

### C15. Merchant Policy Translator `[Visa-fit]` `[Bench]`

Turns confusing return/shipping/warranty policies into plain language, compares across merchants, and flags unfair terms. Demo: a 4,000-word policy becomes three bullets; a hidden restocking fee is flagged. **Why it can win:** trust/UX, easy to build. **Risk:** low innovation. **Stack:** Visa + SideShift + Cloudforce.

### C16. Small Merchant AI Storefront `[Visa-fit]` `[Bench]`

Turns a merchant's WhatsApp/Instagram catalog into an AI-native storefront with product Q&A, checkout, and order tracking. Demo: a bakery's WhatsApp menu becomes a storefront; a customer orders and pays in-chat. **Why it can win:** SMB commerce, Visa payments. **Risk:** Sherpa-adjacent. **Stack:** Visa + SideShift + Cloudforce.

### C17. AI Negotiated Shipping `[Visa-fit]` `[Bench]`

An agent that negotiates shipping costs and delivery windows at checkout. Demo: shipping drops from $12 to $6 with a slower window; the user chooses. **Why it can win:** checkout optimization, clear savings. **Risk:** carrier integration. **Stack:** Visa + SideShift + Cloudforce.

### C18. Family Subscription & Bill Splitter `[Visa-fit]` `[Bench]`

Manages shared family bills/subscriptions, optimizes plans, splits payments, and alerts on price hikes. Demo: a family saves $64/month by switching plans and splitting. **Why it can win:** T-Mobile Household Mix, payments, clear savings. **Risk:** data access. **Stack:** Visa + T-Mobile + SideShift + Cloudforce.

---

## 6. New scoring matrix

Top 20 new ideas. **Visa score** = Innovation×0.25 + UX×0.25 + Tech×0.20 + Commerce×0.15 + Trust×0.15.

| # | Idea | Family | Inn 25% | UX 25% | Tech 20% | Com 15% | Trust 15% | **Visa score** | Feasibility | Stack |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Agent-to-Agent Trust Handshake** | Sniff | 5 | 4 | 5 | 4.5 | 5 | **4.68** | 2.5 | 4.5 |
| 2 | **Trust Trail** | Sniff | 5 | 5 | 4 | 4 | 5 | **4.65** | 4 | 4.5 |
| 3 | **ReturnGuard** | RefundGuard | 4.5 | 4 | 5 | 5 | 5 | **4.63** | 3.5 | 4.5 |
| 4 | **Review Forensics** | Sniff | 5 | 4.5 | 4.5 | 4 | 5 | **4.63** | 4 | 4 |
| 5 | **Seller Reputation Graph** | Sniff | 5 | 4 | 5 | 4 | 5 | **4.60** | 3 | 4 |
| 6 | **Purchase Regret Predictor** | Fresh | 5 | 5 | 4 | 4 | 4.5 | **4.58** | 4 | 4 |
| 7 | **Deal Authenticity Scanner** | Sniff | 4.5 | 4.5 | 4.5 | 4.5 | 5 | **4.58** | 4 | 4 |
| 8 | **Policy-as-Code Refund Agent** | RefundGuard | 4.5 | 4 | 5 | 4.5 | 5 | **4.55** | 3.5 | 4.5 |
| 9 | **Commerce Identity Vault** | Fresh | 5 | 4 | 5 | 3.5 | 5 | **4.53** | 2.5 | 4.5 |
| 10 | **Adversarial Commerce Red Team** | RefundGuard | 5 | 4 | 5 | 3.5 | 5 | **4.53** | 3.5 | 4.5 |
| 11 | **Group Buy Agent** | Fresh | 5 | 4.5 | 4 | 4.5 | 4 | **4.45** | 3 | 4.5 |
| 12 | **Inclusive Sizing Commerce** | Fresh | 4.5 | 5 | 4 | 4.5 | 4 | **4.45** | 3 | 4 |
| 13 | **Caregiver Commerce** | Fresh | 4.5 | 4.5 | 4 | 4 | 5 | **4.40** | 3.5 | 4 |
| 14 | **Counterfeit Detector** | Sniff | 4.5 | 4 | 4.5 | 4 | 5 | **4.38** | 3 | 4 |
| 15 | **Chargeback Court** | RefundGuard | 4.5 | 4 | 4.5 | 4 | 5 | **4.38** | 3 | 4 |
| 16 | **Consumer Refund Concierge** | RefundGuard | 4.5 | 4.5 | 4 | 3.5 | 5 | **4.33** | 4 | 4 |
| 17 | **Subscription Sharing Marketplace** | Fresh | 4.5 | 4.5 | 3.5 | 4.5 | 4 | **4.23** | 4 | 4.5 |
| 18 | **Chargeback Evidence Copilot** | RefundGuard | 4 | 4 | 4 | 4.5 | 5 | **4.23** | 3 | 4 |
| 19 | **Second-Hand First** | Fresh | 4.5 | 4 | 4 | 4 | 4.5 | **4.20** | 3.5 | 4 |
| 20 | **Family Subscription & Bill Splitter** | Fresh | 4 | 4.5 | 3.5 | 4.5 | 4 | **4.10** | 4 | 4.5 |

---

## 7. Top five new picks — deep dive

### Pick 1: Trust Trail — the shareable trust receipt

**Why it wins:** It takes the most watchable part of Sniff — the trust investigation — and turns the output into a **shareable artifact** that any consumer or merchant can use. It scores high on UX (25%) and Trust (15%), is feasible in 21 hours, and stacks with almost any other idea as a trust layer.

**The wedge:** Sniff is an agent; Trust Trail is infrastructure. A merchant can embed the badge; a consumer can share the receipt; a group chat can warn a friend.

**What to build:** A checkout page for a mock store, a trust investigation panel with 5–6 checks, a green/yellow/red receipt, and a share link. Use a curated set of 10 mock stores (5 safe, 5 risky) so the demo is reliable.

**Risk:** False positives. Be explicit about what was verified, what was inferred, and what could not be checked.

---

### Pick 2: ReturnGuard — the return fraud + policy agent

**Why it wins:** It has the strongest Commerce Impact (15%) story in the batch: returns are a huge, measurable cost, and fraud is a clear line item. The VEYZL audit gives it a compelling Trust (15%) and Tech (20%) narrative. It is also a natural B2B SaaS story for SideShift/NEXT.

**The wedge:** RefundGuard handles refunds; ReturnGuard handles the entire return lifecycle, including abuse detection and a fair appeal path.

**What to build:** A customer return flow, a merchant dashboard, a policy engine with 4–5 rules, a fraud-signal panel, an appeal path, and a VEYZL audit screenshot with a before/after fix.

**Risk:** Never accuse a real customer. Use fictional personas and be clear that the fraud signals are probabilistic.

---

### Pick 3: Purchase Regret Predictor

**Why it wins:** It is the most memorable consumer thesis in the batch: "the AI that stops you from buying." It scores high on Innovation (25%) and UX (25%), is easy to demo, and fits Backboard's persistent memory. It also gives Visa a responsible-commerce story: fewer returns, less impulse debt, more trust.

**The wedge:** Timekeeper does this for phones; this generalizes to any purchase and uses the user's own history. It is a "shopping therapist," not a recommender.

**What to build:** A checkout mock, a regret-risk panel with 3–4 evidence points, a "wait 48 hours" flow, and a "regret avoided" tally. Seed the history with 4–5 synthetic past purchases.

**Risk:** Privacy and creepiness. Make consent explicit; show aggregated patterns, not raw surveillance.

---

### Pick 4: Review Forensics

**Why it wins:** Fake reviews are a universal pain, and the demo is instantly legible: a 4.9-star product becomes a 2.8-star product when the manipulation is exposed. It scores high on Innovation (25%), Trust (15%), and Tech (20%), and it is feasible with mock data.

**The wedge:** Sniff checks the store; this checks the reviews. It can be a standalone product or a layer inside Trust Trail.

**What to build:** A product page with 20–30 mock reviews, an authenticity score, an evidence panel (burst timing, repeated phrasing, reviewer overlap), and a "trusted reviews only" toggle.

**Risk:** Accuracy and defamation. Use synthetic reviews and frame the score as probabilistic.

---

### Pick 5: Policy-as-Code Refund Agent

**Why it wins:** It is the purest expression of the pattern judges reward: **deterministic rules + LLM conversation**. Every decision is traceable; the VEYZL audit has real teeth; and the B2B SaaS story is credible. It scores highest on Tech (20%) and Trust (15%) among the RefundGuard family.

**The wedge:** RefundGuard is the agent; this is the safety substrate that makes any refund agent auditable.

**What to build:** A policy editor, a rule compiler for 5–6 rule types, a customer chat, a decision trace, a prompt-injection test, and a VEYZL audit screenshot.

**Risk:** A policy DSL can eat time. Keep the rule set small and visual.

---

## 8. How these combine with the round-one picks

If you want to combine ideas, use the **"one spine + one trust layer"** rule. Do not build three products.

| Spine (round one) | Trust layer (round two) | What it becomes |
|---|---|---|
| **Table Talk** | **Trust Trail** | A household decision room where every merchant gets a visible trust receipt before the family votes. |
| **Table Talk** | **Policy-as-Code** | A household spending mandate compiled into deterministic rules; the AI cannot pay outside them. |
| **Return Radar** | **ReturnGuard** | A full returns OS: predict the return, then resolve it safely. |
| **Sniff** | **Mandate** | A trust layer that verifies the merchant and a consent layer that verifies the buyer's intent. |
| **Gift Circle** | **Trust Trail** | Group gifting with verified merchants and a shareable trust receipt. |
| **Timekeeper** | **Purchase Regret Predictor** | A buy/wait advisor that also learns your personal regret patterns. |
| **RefundGuard** | **VEYZL** | The original Cook Smarter play: a policy-safe refund agent with a real audit and a before/after fix. |

**Best combined concept for Visa:** **Table Talk + Trust Trail**. It combines collaboration (Visa's explicit "collaborating with AI" language) with visible trust, has a full payment moment, and stacks Visa + T-Mobile Household Mix + SideShift + Cloudforce.

**Best combined concept for Cook Smarter:** **RefundGuard + Policy-as-Code + VEYZL**. It is the strongest safety/audit narrative and a credible B2B SaaS story.

---

## 9. Build notes for the new picks

### What to mock (and how to make it credible)
- **Merchant data:** 10 mock stores with names, domains, policies, reviews, and trust signals. Make 5 clearly safe and 5 clearly risky.
- **Payments:** A tokenized checkout mock with a transaction preview, explicit confirmation, and a test decline. You do not need real Visa credentials to score well.
- **Policy engine:** 5–6 rule types (time window, condition, category, receipt, restocking fee, human approval). Keep the DSL visual.
- **Fraud signals:** Use a rules + scoring approach on synthetic data. Show the evidence, not just a score.
- **Audit (VEYZL):** Connect the GitHub repo, run the check, and capture the finding + fix. If access is unavailable, document the intended audit and show a mock report — but be transparent.

### What to avoid
- Do not build a generic chatbot. The interaction model must be distinct.
- Do not claim real fraud detection without data. Say "synthetic data, rules + model."
- Do not build a dashboard-only B2B tool. The Visa video needs a human moment.
- Do not combine more than one spine. Pick one.
- Do not skip the payment moment. Visa judges expect to see checkout.

### 21-hour scope for Trust Trail (the safest new pick)
- **12:30–1:30:** Repo, design system, 10 mock stores, trust-check data model.
- **1:30–5:30:** Trust investigation pipeline (5 checks), receipt UI, green/yellow/red logic.
- **5:30–9:30:** Checkout flow, share link, polish.
- **9:30–10:30:** Devpost draft + rough recording.
- **10:30–2:00:** Merchant badge, edge cases, second store category.
- **2:00–6:00:** Sleep in shifts.
- **6:00–8:00:** Final polish + 3-minute video.
- **8:00–9:30:** Devpost + rehearsal + submit.
- **9:30–10:00:** Buffer.

### 21-hour scope for ReturnGuard (the strongest commerce pick)
- **12:30–1:30:** Repo, design system, mock orders/returns, policy rules.
- **1:30–5:30:** Customer return flow + policy engine + decision trace.
- **5:30–9:30:** Fraud-signal panel, appeal path, merchant dashboard.
- **9:30–10:30:** Devpost draft + rough recording.
- **10:30–2:00:** VEYZL audit, before/after fix, polish.
- **2:00–6:00:** Sleep in shifts.
- **6:00–8:00:** Final polish + 3-minute video.
- **8:00–9:30:** Devpost + rehearsal + submit.
- **9:30–10:00:** Buffer.

---

## 10. Sources and references

- `visa-ideas.md` — round-one catalog, scoring, and recommendations.
- [Visa rubric](../info/visa-rubric.txt)
- [Visa VIC reference agent — GitHub](https://github.com/visa/vic-reference-agent)
- [Visa Intelligent Commerce — Visa Developer](https://developer.visa.com/capabilities/visa-intelligent-commerce)
- [Sniff — project page](https://yifank.github.io/projects/sniff/) · [Devpost](https://devpost.com/software/sniff-l9xk1q)
- [Conversational Commerce Chatbot — Devpost](https://devpost.com/software/conversational-commerce-chatbot)
- [Chaperone — Devpost](https://devpost.com/software/chaperone-2rze5w)
- [Sherpa — Devpost](https://devpost.com/software/lh26-qexhxq)
- [Argus — Devpost](https://devpost.com/software/argus-n507tw)
- [Handshake — Devpost](https://devpost.com/software/handshake-wmitzy)
- [Gather — Devpost](https://devpost.com/software/gather-0c1xzt)
- [MiyKo — DEV](https://dev.to/andriishupta/miyko-a-durable-ai-workflow-for-shared-shopping-1bnm)
- [Moka Guardian — KTU](https://surdurulebilirlik.ktu.edu.tr/en/news/ai-powered-security-shield-brings-first-place-to-our-university)
- [Kill Bill — Money20/20 Hackathon winner](https://blog.killbill.io/blog/kill-bill-among-winners-money2020-hackathon/)
- [Pixel Closet — GitHub](https://github.com/AaxHamm3r/pixel-closet-shellhacks-2025)
- [Waddle/Gentoo — MK](https://www.mk.co.kr/en/it/11407305)
- [Tool Assisted Shopping — University of the Pacific](https://www.pacific.edu/blog/2024/11/20/students-win-first-place-cal-hacks/)
- [MagiCart — Texas State](https://news.txst.edu/accolades-and-achievements/2026/texas-state-students-earn-global-recognition-in-google-maps-platform-awards-hackathon.html)
- [Blindsight — Visa Developer blog](https://community.developer.visa.com/t5/blogs/blogarticleprintpage/blog-id/Developer_Blog/article-id/220)
- [BBVA + Visa agent-initiated payment — The Paypers](https://thepaypers.com/payments/news/bbva-completes-its-first-ai-agent-initiated-payment-together-with-visa)
