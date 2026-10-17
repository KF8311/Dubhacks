# Person C — 1:15–3:30 PM

Frontend / UX. You build against mocks. Do not wait for the backend.

**Branch:** `c/web`  
**Done when:** discovery → results works in the browser with no API running. Fake checks are on the cards.  
**Proof:** screen recording or a live localhost walkthrough at the 3:30 gate.  
**Commits:** one per task below, and at least one every 30 minutes. Each commit has a passing test. A merges to `main`. You do not.

**Out of this block:** SSE, best-pick highlight, purge animation, checkout, receipt. Those start at 3:30.

Read `docs/superpowers/plans/2026-10-17-sniff-visa.md` §5 (models), §6.2–6.4 (session API), and Tasks 17–19 while `npm install` runs.

---

## Install before you write UI

You need Node.js 20 or newer. Check with `node -v`. If it is missing or below 20, install the LTS from [https://nodejs.org](https://nodejs.org).

On this machine PowerShell blocks `npm.ps1` (`running scripts is disabled`). Do not change the execution policy. Call the `.cmd` shims instead: `npm.cmd` and `npx.cmd`. They skip the PowerShell script and work in this terminal.

From the repo root:

```powershell
npm.cmd create vite@latest frontend -- --template react-ts
cd frontend
npm.cmd install
npm.cmd install zustand
npm.cmd install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
npx.cmd shadcn@latest init
npx.cmd shadcn@latest add button card badge input skeleton
```

When `shadcn` asks:

- Framework: Vite
- TypeScript: yes
- Path alias: `@/`
- Tailwind: yes, let the CLI set it up

Add this to `frontend/package.json` scripts if the Vite template did not:

```json
"test": "vitest",
"typecheck": "tsc -b --noEmit"
```

`frontend/vite.config.ts` needs the Vitest + React plugin and the `@` alias. A working shape:

```ts
/// <reference types="vitest/config" />
import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
  },
});
```

`frontend/src/test/setup.ts`:

```ts
import "@testing-library/jest-dom/vitest";
```

If `@tailwindcss/vite` is not already a dependency after `shadcn` init, install it: `npm.cmd install -D @tailwindcss/vite`. If the CLI generated Tailwind v3 (`tailwind.config.ts` + `postcss.config.js`) instead, keep that setup and do not also add the v4 plugin.

Create `frontend/.env.example` (commit this) and `frontend/.env.local` (do not commit):

```
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=1
```

`VITE_API_BASE_URL` is the only frontend env var in the plan. `VITE_USE_MOCK=1` is how this block stays offline until 7:30 PM.

**Do not install yet:** Framer Motion, Playwright, a chart library, an icon pack beyond what shadcn pulls in (`lucide-react`). Motion is the 3:30–6:00 block.

**Do not copy** code, layout, copy, or visuals from [github.com/thenerd31/sniff](https://github.com/thenerd31/sniff). It is an architecture reference only.

---

## Suggested clock

| Time | Work | Commit message |
|---|---|---|
| 1:15–1:45 | Bullet 1 — shell, types, API client, store | `feat: add frontend shell, types, and api client` |
| 1:45–2:30 | Bullet 2 — discovery flow | `feat: add guided discovery flow` |
| 2:30–3:10 | Bullets 3–5 — tokens, mock JSON, results grid | `feat: add results grid and trust ui` |
| 3:10–3:30 | Click the whole flow with the API off. Fix whatever breaks. | only if something changed |

If install eats the first 20 minutes, cut polish, not the three screens. The 3:30 gate is "listings on screen," even if they are still the mock.

---

## Bullet 1 — Task 17: shell, `types.ts`, `api.ts`, Zustand store

**Files you own**

- Create `frontend/src/lib/types.ts`
- Create `frontend/src/lib/api.ts`
- Create `frontend/src/lib/format.ts`
- Create `frontend/src/store/sessionStore.ts`
- Modify `frontend/src/App.tsx`
- Create `frontend/src/App.test.tsx`

`types.ts` is a contract file. Person A owns it after the 1:15 freeze. If A already committed it, import it and do not rewrite it. If it does not exist yet, you write it now to match the plan exactly, then tell the channel what you committed. After that, any field change is announced before you commit it.

### What to put in `types.ts`

Mirror plan §5. Money is `number` cents. Timestamps are `string` (ISO-8601). Use string-literal unions, not TypeScript enums.

```ts
export type CheckId =
  | "domain_age"
  | "ssl_cert"
  | "safe_browsing"
  | "reddit_sentiment"
  | "page_flags";

export type TrustStatus = "passed" | "warning" | "failed" | "skipped";

export type Verdict = "trusted" | "caution" | "danger";

export type SessionStage =
  | "clarifying"
  | "searching"
  | "investigating"
  | "ready"
  | "no_trusted_option"
  | "failed";

export type CheckoutStage =
  | "awaiting_passkey"
  | "authorized"
  | "captured"
  | "declined"
  | "expired"
  | "cancelled";

export type CheckSource =
  | "live"
  | "cache"
  | "allowlist"
  | "fixture"
  | "timeout"
  | "unavailable";

export interface Evidence {
  label: string;
  value: string;
  url?: string | null;
}

export interface TrustCheckResult {
  id: CheckId;
  name: string;
  status: TrustStatus;
  severity: number;
  summary: string;
  evidence: Evidence[];
  source: CheckSource;
  duration_ms: number;
}

export interface Listing {
  id: string;
  title: string;
  price_cents: number;
  currency: string;
  merchant_name: string;
  merchant_domain: string;
  image_url: string;
  product_url: string;
  category?: string | null;
  source: "serpapi" | "catalog" | "fixture";
}

export interface Penalty {
  check_id: CheckId;
  points: number;
  reason: string;
}

export interface ScoreResult {
  score: number;
  verdict: Verdict;
  confidence: number;
  penalties: Penalty[];
  fatal_flags: string[];
  top_reason: string;
  scoring_version: string;
}

export interface QuestionOption {
  id: string;
  label: string;
}

export interface Question {
  id: string;
  prompt: string;
  kind: "single_select";
  options: QuestionOption[];
  allow_free_text: boolean;
}

export interface Answer {
  question_id: string;
  option_id?: string | null;
  text?: string | null;
}

export interface SearchSpec {
  query: string;
  budget_max_cents?: number | null;
  category?: string | null;
  merchants_preferred: string[];
}

export interface Recommendation {
  recommended_listing_id: string | null;
  median_trusted_cents: number | null;
  savings_cents: number | null;
  eligible_ids: string[];
  reason: string;
  no_trusted_option: boolean;
}

export interface SessionSnapshot {
  session_id: string;
  stage: SessionStage;
  query: string;
  listings: Listing[];
  checks: Record<string, TrustCheckResult[]>;
  scores: Record<string, ScoreResult>;
  recommendation: Recommendation | null;
  last_seq: number;
  stats: {
    listings: number;
    trusted: number;
    caution: number;
    danger: number;
    duration_ms: number;
  };
}
```

Also add `CreateSessionResponse` and `SubmitAnswersResponse` matching plan §6.2 and §6.3 (`session_id`, `stage`, `questions`, `expires_at`, `events_url`, `search_spec`). Add `Checkout` and `Receipt` as thin interfaces so `api.ts` typechecks; you will not render them until 6:00.

### What to put in `api.ts`

Base URL: `import.meta.env.VITE_API_BASE_URL`. Throw on non-2xx with the error envelope `{ error: { code, message, details, request_id } }`.

| Function | Call | Used this block? |
|---|---|---|
| `createSession({ query, client_id })` | `POST /api/sessions` | Mocked |
| `submitAnswers(sessionId, { answers, skip_remaining })` | `POST /api/sessions/{id}/answers` | Mocked |
| `getSnapshot(sessionId)` | `GET /api/sessions/{id}` | Mocked |
| `createCheckout(...)` | `POST /api/checkout` | Stub only |
| `confirmCheckout(checkoutId, body)` | `POST /api/checkout/{id}/confirm` | Stub only |
| `getReceipt(receiptId)` | `GET /api/receipts/{id}` | Stub only |

When `import.meta.env.VITE_USE_MOCK === "1"`, `createSession`, `submitAnswers`, and `getSnapshot` return the JSON in bullet 5 after a short `setTimeout` (~400ms) so the submitting state is visible. Do not call `fetch`.

### What to put in `format.ts`

One function: `formatCents(cents: number, currency = "USD")` using `Intl.NumberFormat`. `24900` → `$249.00`. Never divide in a component.

### What to put in `sessionStore.ts`

Zustand store. Fields from Task 17:

- `sessionId: string | null`
- `stage: SessionStage | "discovery"`
- `query: string`
- `questions: Question[]`
- `listings: Listing[]`
- `checks: Record<string, TrustCheckResult[]>`
- `scores: Record<string, ScoreResult>`
- `recommendation: Recommendation | null`
- `checkout: null` (typed, unused)
- `receipt: null` (typed, unused)

Actions you need today: `setQuery`, `setQuestions`, `startSession(snapshot)`, `reset`. `reset` returns the app to the discovery screen.

### What the shell looks like

`App.tsx` is one page, two stages:

1. `discovery` — renders `<DiscoveryFlow />` (placeholder text is fine until bullet 2).
2. `results` — renders `<ResultsGrid />` once a snapshot is in the store.

The header shows:

- The word **Sniff** (the Task 17 test looks for `/sniff/i`).
- A sandbox badge that stays visible: `Sandbox — simulated Visa flow`. Use the shadcn `Badge`.

No router. No login. No chat box.

### Test, then commit

`frontend/src/App.test.tsx` — copy from plan Task 17:

```tsx
import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders the app shell", () => {
  render(<App />);
  expect(screen.getByText(/sniff/i)).toBeInTheDocument();
});
```

```powershell
cd frontend
npm.cmd test -- --run
git add frontend/src frontend/package.json frontend/vite.config.ts frontend/.env.example
git commit -m "feat: add frontend shell, types, and api client"
```

---

## Bullet 2 — Task 18: discovery flow (query → 2–3 questions → submit)

**Files**

- Create `frontend/src/features/discovery/DiscoveryFlow.tsx`
- Create `frontend/src/features/discovery/DiscoveryFlow.test.tsx`
- Modify `frontend/src/App.tsx` so the shell mounts `<DiscoveryFlow onStarted={...} />`

**Component contract:** `<DiscoveryFlow onStarted={(sessionId) => void} />`

### The three states

1. **Query.** One text field. Placeholder must be `What are you looking for?` so the test matches. Primary button label: `Find products`. Disabled while the field is empty.
2. **Questions.** After the query, show 2–3 questions. Each question is single-select pills (`<button type="button">`, not a `<select>`). If `allow_free_text` is true, show a text input under the pills. One question on screen at a time is fine; a short stack is also fine. The user can answer with a pill or with free text, not both.
3. **Submitting.** Button shows a busy label, inputs lock, and a `Skeleton` stands in for the results grid. Then call `submitAnswers`. On success, write the snapshot into the store and call `onStarted(sessionId)`. `App` switches to the results stage.

### Questions to hardcode in the mock

These match the contract in plan §6.2. The real API will replace them at 7:30. Until then, `createSession` returns this list:

| id | prompt | options |
|---|---|---|
| `q_budget` | What's your ceiling? | Under $150 · $150–$300 · $300–$600 |
| `q_priority` | What matters more? | Lowest trusted price · Brand I already like · Fast shipping |
| `q_use` | Where will you use them? | Travel · Desk · Gym |

`q_budget` has `allow_free_text: true`. The other two can be pills only.

Map the budget pill to cents when you build `SearchSpec`: `150 → 15000`, `300 → 30000`, `600 → 60000`. Free text that contains a number is parsed once; if parsing fails, leave `budget_max_cents` null. Do not block submit on a perfect parse.

### Keyboard and focus

- Enter in the query field clicks Find products.
- Pills are real buttons. Arrow keys are optional. A visible focus ring is required (shadcn `ring` is enough; do not remove it).
- After submit, move focus to the results heading.

### Test, then commit

Copy from plan Task 18. The test only covers query → first question, not the grid:

```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { DiscoveryFlow } from "./DiscoveryFlow";

test("renders questions and submits", async () => {
  render(<DiscoveryFlow onStarted={() => {}} />);
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "headphones" },
  });
  fireEvent.click(screen.getByRole("button", { name: /find products/i }));
  expect(await screen.findByText(/what's your ceiling/i)).toBeInTheDocument();
});
```

```powershell
npm.cmd test -- --run
git add frontend/src/features/discovery frontend/src/App.tsx
git commit -m "feat: add guided discovery flow"
```

---

## Bullet 3 — Task 19: results grid, product cards, `TrustBadge`, `CheckRow`

**Files**

- Create `frontend/src/features/results/ResultsGrid.tsx`
- Create `frontend/src/features/results/ProductCard.tsx`
- Create `frontend/src/features/results/TrustBadge.tsx`
- Create `frontend/src/features/results/CheckRow.tsx`
- Create `frontend/src/features/results/ResultsGrid.test.tsx`

**Props**

- `<ResultsGrid listings checks scores recommendation />`
- `<ProductCard listing checks score isBest />`
- `<TrustBadge score verdict />` — `score` and `verdict` may both be missing while a card is still pending
- `<CheckRow check />` — `check` may be a started-but-not-finished placeholder

### `ResultsGrid`

- Read listings from the store (filled by the mock snapshot).
- If `recommendation.recommended_listing_id` is set, render that card first. Do not draw the savings callout yet. That is Task 21 at 3:30.
- Responsive grid: 1 column under 768px, 2 at 768px, 3–4 at 1024px and up. No horizontal page scroll.
- Heading includes the query, for example `Results for “headphones”`.

### `ProductCard`

Show, top to bottom:

1. Image. If `image_url` is empty or the image errors, show a gradient block using the merchant initial. Do not use a broken-image icon.
2. Title. Clamp to 2 lines.
3. Merchant name and domain.
4. Price from `formatCents(price_cents)`.
5. `TrustBadge`.
6. The five `CheckRow`s.

Empty `image_url` must still look intentional. Several mock listings should have `image_url: ""` so you see the fallback.

### `TrustBadge`

| State | Label | Colors |
|---|---|---|
| No score yet | `Checking` | pending gray |
| `trusted` | `92 · Trusted` | green |
| `caution` | `61 · Caution` | amber |
| `danger` | `12 · Danger` | red |

Use the CSS variables from bullet 4. Text is the colored token; the badge background is the matching tint. Do not rely on Tailwind `green-500` / `red-500` — those fail WCAG AA as small text on white.

### `CheckRow`

One row per check. Left: check name. Right: status word.

| status | What the row shows |
|---|---|
| `passed` | name, “Passed”, one-line `summary` |
| `warning` | name, “Warning”, summary |
| `failed` | name, “Failed”, summary |
| `skipped` | name, “Skipped”, summary. Skipped is not a pass. Do not use a checkmark. |
| started, no result yet | shadcn `Skeleton` the height of one row. No fake status. |

Check display names:

| id | name |
|---|---|
| `domain_age` | Domain age |
| `ssl_cert` | SSL certificate |
| `safe_browsing` | Safe Browsing |
| `reddit_sentiment` | Reddit |
| `page_flags` | Page flags |

Every card in the mock should show all five rows. Mix finished rows and one skeleton on one card so you can see the pending state. The other cards can be fully scored.

### Test, then commit

Copy from plan Task 19:

```tsx
import { render, screen } from "@testing-library/react";
import { ResultsGrid } from "./ResultsGrid";

test("renders title, merchant, and formatted price", () => {
  render(
    <ResultsGrid
      listings={[
        {
          id: "lst_1",
          title: "Sony XM5",
          price_cents: 24900,
          currency: "USD",
          merchant_name: "Best Buy",
          merchant_domain: "bestbuy.com",
          image_url: "",
          product_url: "",
          source: "catalog",
        },
      ]}
      checks={{}}
      scores={{}}
    />,
  );
  expect(screen.getByText("Sony XM5")).toBeInTheDocument();
  expect(screen.getByText("Best Buy")).toBeInTheDocument();
  expect(screen.getByText(/\$249\.00/)).toBeInTheDocument();
});
```

```powershell
npm.cmd test -- --run
git add frontend/src/features/results
git commit -m "feat: add results grid and trust ui"
```

---

## Bullet 4 — Design tokens and WCAG AA

Put these in `frontend/src/index.css` under `:root` (and wire them through Tailwind if you want utilities like `text-trusted`). These pairs are AA for normal-size text (4.5:1) and for the badge as a UI component (3:1).

| Token | Text | Background tint | Use |
|---|---|---|---|
| trusted | `#14532d` | `#dcfce7` | verdict `trusted` |
| caution | `#78350f` | `#fef3c7` | verdict `caution` |
| danger | `#7f1d1d` | `#fee2e2` | verdict `danger` |
| pending | `#374151` | `#f3f4f6` | no score yet, skeletons, skipped |

```css
:root {
  --trust-trusted: #14532d;
  --trust-trusted-bg: #dcfce7;
  --trust-caution: #78350f;
  --trust-caution-bg: #fef3c7;
  --trust-danger: #7f1d1d;
  --trust-danger-bg: #fee2e2;
  --trust-pending: #374151;
  --trust-pending-bg: #f3f4f6;
}
```

Rules:

- Badge text uses the text token on the tint. Body text on the page background uses the text token or `foreground`, never the tint.
- Focus rings stay visible on the query field, pills, and any later button. Do not set `outline: none` without a replacement ring.
- Status is not color alone. The badge and the check row both include the word (Trusted, Caution, Danger, Passed, Skipped).
- Before 3:30, spot-check one trusted badge and one danger badge in the browser. If the text looks light, you used a 400/500 Tailwind color. Switch to the tokens above.

This work lands in the Task 19 commit. It does not need its own commit unless the clock hits a 30-minute mark with nothing else to commit.

---

## Bullet 5 — `data/mock-session.json` so the UI renders with no API

**File:** `data/mock-session.json` at the repo root (same folder as `data/catalog.json`, which Person B owns — do not edit the catalog).

Import it from the frontend:

```ts
import mockSession from "../../../data/mock-session.json";
```

Vite bundles that import. You do not need the backend, and you do not need to serve the file.

### Shape

One object with two pieces the UI reads:

```json
{
  "create_session": {
    "session_id": "ses_mock",
    "stage": "clarifying",
    "questions": [],
    "expires_at": "2026-10-17T20:30:00Z"
  },
  "snapshot": {
    "session_id": "ses_mock",
    "stage": "ready",
    "query": "noise cancelling headphones for travel",
    "listings": [],
    "checks": {},
    "scores": {},
    "recommendation": {
      "recommended_listing_id": "lst_bestbuy_xm5",
      "median_trusted_cents": 27900,
      "savings_cents": 3000,
      "eligible_ids": ["lst_bestbuy_xm5"],
      "reason": "cheapest trusted",
      "no_trusted_option": false
    },
    "last_seq": 40,
    "stats": { "listings": 8, "trusted": 5, "caution": 2, "danger": 1, "duration_ms": 4200 }
  }
}
```

Fill `questions` with the three questions from bullet 2. Fill `listings` with these eight. Prices are cents.

| id | title | merchant | domain | price_cents | verdict | score | notes |
|---|---|---|---|---|---|---|---|
| `lst_bestbuy_xm5` | Sony WH-1000XM5 | Best Buy | `bestbuy.com` | 24900 | trusted | 92 | best pick, all 5 passed |
| `lst_amazon_bose` | Bose QuietComfort Ultra | Amazon | `amazon.com` | 32900 | trusted | 88 | all passed |
| `lst_walmart_xm5` | Sony WH-1000XM5 | Walmart | `walmart.com` | 27900 | trusted | 85 | all passed |
| `lst_nordstrom_at` | Audio-Technica ATH-M50x | Nordstrom | `nordstrom.com` | 19900 | trusted | 90 | all passed. Not eligible if you want the story to be “cheapest trusted is $249”; either drop its score under 70 or leave it trusted and set the recommendation to it. Pick one and make the JSON agree. |
| `lst_target_bose` | Bose QC Headphones | Target | `target.com` | 29900 | caution | 61 | Reddit `warning`, others passed |
| `lst_amazon_budget` | Generic ANC Headphones | Amazon | `amazon.com` | 8900 | caution | 48 | page flags `warning` |
| `lst_bb_xm4` | Sony WH-1000XM4 | Best Buy | `bestbuy.com` | 22800 | trusted | 86 | all passed |
| `lst_villain` | XM5 Pro — Flash Deal | Premium Audio Deals | `premium-audio-deals.shop` | 7900 | danger | 12 | domain age `failed`, page flags `failed`, Reddit `failed` |

The Nordstrom row is the one to decide on purpose: the demo line is “cheapest trusted, not cheapest.” If Nordstrom at $199 is trusted, it is the best pick. Simplest fix: make Nordstrom `caution` / 64 so Best Buy at $249 stays the cheapest trusted. Then `eligible_ids` lists only the trusted rows, `median_trusted_cents` is the median of those prices, and `savings_cents` is `median - 24900`.

Each listing object:

```json
{
  "id": "lst_bestbuy_xm5",
  "title": "Sony WH-1000XM5",
  "price_cents": 24900,
  "currency": "USD",
  "merchant_name": "Best Buy",
  "merchant_domain": "bestbuy.com",
  "image_url": "",
  "product_url": "https://www.bestbuy.com/",
  "category": "audio",
  "source": "catalog"
}
```

Leave `image_url` empty on at least three listings, including the villain. You can paste real public product-image URLs on the others if they load. If they do not, the gradient fallback from bullet 3 has to carry the card. Do not hotlink anything that requires a cookie.

Each check object:

```json
{
  "id": "domain_age",
  "name": "Domain age",
  "status": "passed",
  "severity": 0,
  "summary": "Registered for 28 years.",
  "evidence": [{ "label": "Created", "value": "1998" }],
  "source": "fixture",
  "duration_ms": 180
}
```

`checks` is keyed by listing id → array of five `TrustCheckResult`s. `scores` is keyed by listing id → `ScoreResult`. For the danger listing, set `fatal_flags` to `["domain_age"]` and `top_reason` to the domain-age summary. For a trusted listing, `penalties` is `[]` and `top_reason` is `"All checks passed."` `scoring_version` is `"1.0"`. `confidence` is `1` when all five checks finished, otherwise `completed / 5`.

On one trusted card, omit the `page_flags` result and have the card render a skeleton for that row. That is the only pending state you need today.

### How the mock is wired

In `api.ts`, when `VITE_USE_MOCK=1`:

- `createSession` returns `create_session` and ignores the network.
- `submitAnswers` returns `{ session_id, stage: "searching", events_url: "/api/sessions/ses_mock/events", search_spec }` built from the answers.
- `getSnapshot` returns `snapshot`.

`DiscoveryFlow` calls `createSession` on “Find products”, then `submitAnswers` + `getSnapshot` on the last answer, then `onStarted`. With the dev server running and the API stopped, that path still reaches the grid.

```powershell
cd frontend
npm.cmd run dev
```

Open the printed localhost URL. API stays down.

---

## 3:25 checklist

Click this once, with `VITE_USE_MOCK=1` and no backend:

1. Header says Sniff and shows the sandbox badge.
2. Type “noise cancelling headphones”, press Find products.
3. Answer the budget question with a pill. Answer the next two.
4. A short skeleton shows, then eight cards.
5. Best Buy XM5 is first. Price reads `$249.00`.
6. You can see a green Trusted badge, an amber Caution badge, and a red Danger badge.
7. The villain card shows failed checks in words, not only red.
8. One card has a skeleton check row.
9. Empty images show the gradient fallback, not a broken icon.
10. `npm.cmd test -- --run` passes.

If step 4 fails, the bug is the mock import or the store, not the API. Do not start the SSE hook to “unblock” it.

---

## What you are waiting on, and what you do if it is late

| From | What | When you need it |
|---|---|---|
| A | Frozen `types.ts` / `docs/contracts.md` | Now, if they already wrote it. If not, you write `types.ts` to §5 and say so. |
| A | SSE event schema and a live `/events` URL | 3:30, for the next block. Not this one. |
| B | `data/catalog.json` merchant names | Nice to match, not blocking. Your mock is the source of truth until 7:30. |

If A’s types differ from this file, their file wins. Update your mock and components to match, and do not invent fields.
