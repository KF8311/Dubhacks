# Person C — do this from top to bottom

This is your instruction sheet for **1:15–3:30 PM**. Follow it in order. Do not skip a step because it looks optional.

You are the frontend person. You build what people see and click. Your two teammates build the server. You do **not** need their server for this block. The screen will use a fake shopping session saved in a file.

When this block is finished, you can open the site on your computer, type what you want to buy, answer three questions, and see eight product cards. Each card has a price, a trust label (Trusted, Caution, or Danger), and five check rows. No server is running.

---

## What the app is

The product is called **Sniff**. A person types something they want to buy. Sniff asks a few short questions, then shows products from different stores. Each product is checked for scams. A store Sniff does not trust cannot be paid. Payment itself is later today. Right now you only build the first two screens:

1. **Discovery** — the question screen.
2. **Results** — the product cards.

Leave these for the next time block: live updates, the big “you save $30” banner, the purge animation, checkout, and the receipt.

---

## Words used in this file

| Word | What it means |
|---|---|
| Terminal | The text panel in Cursor where you type commands. Open it with **Ctrl+`** (the key under Escape). |
| Command | One line you type in the terminal, then press Enter. Wait until the terminal is ready again before you type the next one. |
| `frontend` folder | The website project. It already exists. Do not create it again. |
| Component | One piece of the screen, saved as its own file. A card is a component. A badge is a component. |
| Mock | Fake data in a file. The screen reads the file instead of asking the server. |
| Cents | Prices are whole numbers of cents, never dollars with a dot, until the moment they are shown. `24900` is displayed as `$249.00`. |
| Commit | A saved checkpoint in git, with a message. You make three of them today. |
| Branch | Your own line of work, named `c/web`. You do not put your work straight on `main`. |

---

## Where you are right now

- The folder `frontend` already exists. The `npm create vite` step is done. **Do not run it again.**
- Libraries are not installed yet. The site will not open until Step 1 finishes.
- You are on the git branch `main`. You will move to `c/web` in Step 4, before the first commit.
- PowerShell on this computer blocks `npm`. Every command below uses `npm.cmd` or `npx.cmd`. If you type `npm` by itself, you get the “running scripts is disabled” error. That is the same error you already saw. Use the `.cmd` version.

Every command starts with `cd`, so it does not matter which folder the terminal was in before.

---

## Step 1 — Install the website’s libraries

**Why:** The `frontend` folder is only a starter. This downloads React and the other packages it needs. It creates a `frontend/node_modules` folder. You never edit that folder.

In the terminal, paste this and press Enter:

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks\frontend
npm.cmd install
```

**It worked if** the terminal finishes and you see a line like `added N packages`. A few yellow `npm warn` lines are fine. A red `npm ERR!` is not. If you see `running scripts is disabled`, you typed `npm` instead of `npm.cmd`.

---

## Step 2 — Install the extra libraries this block needs

**Why each one is here:**

| Package | What you use it for |
|---|---|
| `zustand` | Remembers the query, the product list, and the scores while the person clicks around. |
| `tailwindcss` and `@tailwindcss/vite` | The styling system. You write class names like `text-xl` instead of a separate CSS file for every screen. |
| `vitest`, `jsdom`, Testing Library | Runs the three tests that prove the screen renders. Each commit needs a passing test. |

Paste this:

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks\frontend
npm.cmd install zustand
npm.cmd install -D tailwindcss @tailwindcss/vite vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

**It worked if** both commands finish without `npm ERR!`.

---

## Step 3 — Turn on Tailwind, the `@` import shortcut, and tests

**Why:** Later files import code as `@/lib/types`. That `@` means “the `src` folder.” Tailwind has to be plugged into the dev server. Tests need a setup file. You are editing config, not building a screen yet.

### 3a. Replace `frontend/vite.config.ts`

Open that file. Select all (Ctrl+A). Delete it. Paste this. Save (Ctrl+S).

```ts
import path from "node:path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vitest/config"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
  },
})
```

### 3b. Edit `frontend/tsconfig.app.json`

Open it. Inside `"compilerOptions"`, you already have a `"types"` line. Replace that one line with:

```json
"types": ["vite/client", "vitest/globals"],
```

Then, still inside `"compilerOptions"`, add these three lines after `"jsx": "react-jsx",`:

```json
"baseUrl": ".",
"paths": {
  "@/*": ["./src/*"]
},
"resolveJsonModule": true,
```

Leave every other line alone. Save. JSON does not allow a trailing comma after the last item in a list. If you already have a comma after `"jsx": "react-jsx"`, do not add a second one.

### 3c. Add the test script to `frontend/package.json`

Open `package.json`. The `"scripts"` section looks like this:

```json
"scripts": {
  "dev": "vite",
  "build": "tsc -b && vite build",
  "lint": "oxlint",
  "preview": "vite preview"
},
```

Add a `"test"` line so it becomes:

```json
"scripts": {
  "dev": "vite",
  "build": "tsc -b && vite build",
  "lint": "oxlint",
  "preview": "vite preview",
  "test": "vitest"
},
```

Save.

### 3d. Create `frontend/src/test/setup.ts`

In the left sidebar, right-click `frontend/src` → **New Folder** → name it `test`.

Right-click `test` → **New File** → name it `setup.ts`.

Paste this and save:

```ts
import "@testing-library/jest-dom/vitest"
```

**Why:** This teaches the tests extra matchers such as `toBeInTheDocument()`.

---

## Step 4 — Create your git branch

**Why:** The team rule is that your work lives on a branch named `c/web`. Person A is the only one who merges into `main`. A branch is a separate save-line. Your commits will sit there until A pulls them in.

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks
git checkout -b c/web
```

**It worked if** the terminal says `Switched to a new branch 'c/web'`.

If it says the branch already exists, use this instead:

```powershell
git checkout c/web
```

---

## Step 5 — Install the pre-built UI pieces (shadcn)

**Why:** shadcn copies a Button, a Card, a Badge, an Input, and a Skeleton into your project. You use those instead of styling raw HTML from scratch. The files land in `frontend/src/components/ui`. Do not edit those files today.

This command asks questions **in the terminal**. You answer with the keyboard, not the mouse. Arrow keys move. Enter confirms.

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks\frontend
npx.cmd shadcn@latest init
```

If a question is not in this list, press Enter to take the default.

| If it asks | You answer |
|---|---|
| Ok to proceed / install | `y`, then Enter |
| Which style, preset, or component library | The first option, usually **New York** or **Radix** |
| Base color | **Neutral** |
| CSS variables | **Yes** |
| Global CSS file | `src/index.css` (press Enter if that is already filled in) |
| Import alias / components alias | `@` or `@/components` (press Enter if already filled in) |
| Use TypeScript | **Yes** |

Wait until the prompt comes back and there is no spinner.

Then install the five pieces. This one should not ask questions:

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks\frontend
npx.cmd shadcn@latest add button card badge input skeleton -y
```

**It worked if** these files exist:

- `frontend/src/components/ui/button.tsx`
- `frontend/src/components/ui/card.tsx`
- `frontend/src/components/ui/badge.tsx`
- `frontend/src/components/ui/input.tsx`
- `frontend/src/components/ui/skeleton.tsx`

shadcn rewrites `frontend/src/index.css`. That is expected. Do the next step after it, not before.

---

## Step 6 — Add the trust colors

**Why:** Trusted, caution, danger, and “still checking” each have a color. The text color on the tinted background has to be dark enough to read (the WCAG AA rule). Do not use bright Tailwind greens and reds for the words. Those fail the contrast check.

Open `frontend/src/index.css`. Leave whatever shadcn wrote. Scroll to the very bottom and paste this. Save.

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

| Name | Text | Background | Meaning |
|---|---|---|---|
| trusted | dark green `#14532d` | light green `#dcfce7` | Safe to recommend |
| caution | dark amber `#78350f` | light amber `#fef3c7` | Something was off |
| danger | dark red `#7f1d1d` | light red `#fee2e2` | Do not pay this store |
| pending | dark gray `#374151` | light gray `#f3f4f6` | Check has not finished |

The word is always on the badge too. Color is not the only signal.

---

## Step 7 — Tell the app to use fake data

**Why:** The real server address will be `http://localhost:8000`. Today the app must not call it. `VITE_USE_MOCK=1` is the switch. Vite only exposes variables whose names start with `VITE_`.

### 7a. Create `frontend/.env.example`

This one **is** committed, so teammates can see which variables exist. New File in the `frontend` folder, name it `.env.example`. If Cursor hides the name because it starts with a dot, create it anyway. Paste:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=1
```

### 7b. Create `frontend/.env.local`

Same folder, name it `.env.local`. Same two lines:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=1
```

`.env.local` is the file your computer actually reads. It is gitignored (the starter ignore rule `*.local` covers it). Do not commit it. Do not put passwords in it. This block has no passwords.

---

## Step 8 — The data types (`frontend/src/lib/types.ts`)

**Why:** TypeScript is a spell-checker for data. These types are the contract with the server. Person A owns this file after 1:15. If A already wrote `frontend/src/lib/types.ts`, do not replace it. Tell them in the channel, and use their file. If the file does not exist, you create it now, matching the plan exactly, and you say so in the channel.

**What “cents as a number” means:** `price_cents: 24900`, not `price: 249.00`.

**What you are not doing:** you are not writing the server. These are only the shapes the screen expects.

Create the folder `frontend/src/lib`. Create `types.ts` inside it. Paste this whole file. Save.

```ts
export type CheckId =
  | "domain_age"
  | "ssl_cert"
  | "safe_browsing"
  | "reddit_sentiment"
  | "page_flags"

export type TrustStatus = "passed" | "warning" | "failed" | "skipped"

export type Verdict = "trusted" | "caution" | "danger"

export type SessionStage =
  | "clarifying"
  | "searching"
  | "investigating"
  | "ready"
  | "no_trusted_option"
  | "failed"

export type CheckoutStage =
  | "awaiting_passkey"
  | "authorized"
  | "captured"
  | "declined"
  | "expired"
  | "cancelled"

export type CheckSource =
  | "live"
  | "cache"
  | "allowlist"
  | "fixture"
  | "timeout"
  | "unavailable"

export interface Evidence {
  label: string
  value: string
  url?: string | null
}

export interface TrustCheckResult {
  id: CheckId
  name: string
  status: TrustStatus
  severity: number
  summary: string
  evidence: Evidence[]
  source: CheckSource
  duration_ms: number
}

export interface Listing {
  id: string
  title: string
  price_cents: number
  currency: string
  merchant_name: string
  merchant_domain: string
  image_url: string
  product_url: string
  category?: string | null
  source: "serpapi" | "catalog" | "fixture"
}

export interface Penalty {
  check_id: CheckId
  points: number
  reason: string
}

export interface ScoreResult {
  score: number
  verdict: Verdict
  confidence: number
  penalties: Penalty[]
  fatal_flags: string[]
  top_reason: string
  scoring_version: string
}

export interface QuestionOption {
  id: string
  label: string
}

export interface Question {
  id: string
  prompt: string
  kind: "single_select"
  options: QuestionOption[]
  allow_free_text: boolean
}

export interface Answer {
  question_id: string
  option_id?: string | null
  text?: string | null
}

export interface SearchSpec {
  query: string
  budget_max_cents?: number | null
  category?: string | null
  merchants_preferred: string[]
}

export interface Recommendation {
  recommended_listing_id: string | null
  median_trusted_cents: number | null
  savings_cents: number | null
  eligible_ids: string[]
  reason: string
  no_trusted_option: boolean
}

export interface SessionStats {
  listings: number
  trusted: number
  caution: number
  danger: number
  duration_ms: number
}

export interface SessionSnapshot {
  session_id: string
  stage: SessionStage
  query: string
  listings: Listing[]
  checks: Record<string, TrustCheckResult[]>
  scores: Record<string, ScoreResult>
  recommendation: Recommendation | null
  last_seq: number
  stats: SessionStats
}

export interface CreateSessionResponse {
  session_id: string
  stage: SessionStage
  questions: Question[]
  expires_at: string
}

export interface SubmitAnswersResponse {
  session_id: string
  stage: SessionStage
  events_url: string
  search_spec: SearchSpec
}
```

The five checks, in the order they appear on a card:

| id | What it means | Name on the card |
|---|---|---|
| `domain_age` | How long the store’s website has existed | Domain age |
| `ssl_cert` | Whether the connection certificate looks normal | SSL certificate |
| `safe_browsing` | Whether Google’s threat list knows this site | Safe Browsing |
| `reddit_sentiment` | Whether Reddit posts call it a scam | Reddit |
| `page_flags` | Whether the product page uses pressure tactics | Page flags |

A **skipped** check is not a pass. The card must say “Skipped.”

---

## Step 9 — Turn cents into a dollar string (`frontend/src/lib/format.ts`)

**Why:** `24900` must become `$249.00` in exactly one place. The test looks for `$249.00`. Forcing `en-US` means a Windows laptop set to another region still prints the format the test expects.

Create `frontend/src/lib/format.ts`. Paste and save.

```ts
export function formatCents(cents: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(cents / 100)
}
```

---

## Step 10 — The fake shopping session

**Why:** This is the file the screen reads instead of the server. It has the three questions and eight products. The story the cards tell:

- The cheapest listing is a scam, so it is **not** the recommendation.
- A couple of cheaper listings are only **caution**.
- The cheapest listing that is actually **trusted** is the Sony headphones at Best Buy for $249.

That is the product rule: cheapest trusted, not cheapest.

Trusted prices are $249, $279, and $329. The middle one is $279. Savings versus that middle price are $30. You will not draw the savings banner yet. The number is in the file so the next block can read it.

Create the folder `frontend/src/data`. Create `mock-session.json` inside it. Paste this whole file. Save.

```json
{
  "create_session": {
    "session_id": "ses_mock",
    "stage": "clarifying",
    "expires_at": "2026-10-17T20:30:00Z",
    "questions": [
      {
        "id": "q_budget",
        "prompt": "What's your ceiling?",
        "kind": "single_select",
        "allow_free_text": true,
        "options": [
          { "id": "150", "label": "Under $150" },
          { "id": "300", "label": "$150–$300" },
          { "id": "600", "label": "$300–$600" }
        ]
      },
      {
        "id": "q_priority",
        "prompt": "What matters more?",
        "kind": "single_select",
        "allow_free_text": false,
        "options": [
          { "id": "price", "label": "Lowest trusted price" },
          { "id": "brand", "label": "Brand I already like" },
          { "id": "shipping", "label": "Fast shipping" }
        ]
      },
      {
        "id": "q_use",
        "prompt": "Where will you use them?",
        "kind": "single_select",
        "allow_free_text": false,
        "options": [
          { "id": "travel", "label": "Travel" },
          { "id": "desk", "label": "Desk" },
          { "id": "gym", "label": "Gym" }
        ]
      }
    ]
  },
  "snapshot": {
    "session_id": "ses_mock",
    "stage": "ready",
    "query": "noise cancelling headphones for travel",
    "last_seq": 40,
    "stats": {
      "listings": 8,
      "trusted": 3,
      "caution": 4,
      "danger": 1,
      "duration_ms": 4200
    },
    "recommendation": {
      "recommended_listing_id": "lst_bestbuy_xm5",
      "median_trusted_cents": 27900,
      "savings_cents": 3000,
      "eligible_ids": ["lst_bestbuy_xm5", "lst_walmart_xm5", "lst_amazon_bose"],
      "reason": "cheapest trusted",
      "no_trusted_option": false
    },
    "listings": [
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
      },
      {
        "id": "lst_walmart_xm5",
        "title": "Sony WH-1000XM5",
        "price_cents": 27900,
        "currency": "USD",
        "merchant_name": "Walmart",
        "merchant_domain": "walmart.com",
        "image_url": "",
        "product_url": "https://www.walmart.com/",
        "category": "audio",
        "source": "catalog"
      },
      {
        "id": "lst_amazon_bose",
        "title": "Bose QuietComfort Ultra",
        "price_cents": 32900,
        "currency": "USD",
        "merchant_name": "Amazon",
        "merchant_domain": "amazon.com",
        "image_url": "",
        "product_url": "https://www.amazon.com/",
        "category": "audio",
        "source": "catalog"
      },
      {
        "id": "lst_bb_xm4",
        "title": "Sony WH-1000XM4",
        "price_cents": 22800,
        "currency": "USD",
        "merchant_name": "Best Buy",
        "merchant_domain": "bestbuy.com",
        "image_url": "",
        "product_url": "https://www.bestbuy.com/",
        "category": "audio",
        "source": "catalog"
      },
      {
        "id": "lst_nordstrom_at",
        "title": "Audio-Technica ATH-M50x",
        "price_cents": 19900,
        "currency": "USD",
        "merchant_name": "Nordstrom",
        "merchant_domain": "nordstrom.com",
        "image_url": "",
        "product_url": "https://www.nordstrom.com/",
        "category": "audio",
        "source": "catalog"
      },
      {
        "id": "lst_target_bose",
        "title": "Bose QC Headphones",
        "price_cents": 29900,
        "currency": "USD",
        "merchant_name": "Target",
        "merchant_domain": "target.com",
        "image_url": "",
        "product_url": "https://www.target.com/",
        "category": "audio",
        "source": "catalog"
      },
      {
        "id": "lst_amazon_budget",
        "title": "Generic ANC Headphones",
        "price_cents": 8900,
        "currency": "USD",
        "merchant_name": "Amazon",
        "merchant_domain": "amazon.com",
        "image_url": "",
        "product_url": "https://www.amazon.com/",
        "category": "audio",
        "source": "catalog"
      },
      {
        "id": "lst_villain",
        "title": "XM5 Pro — Flash Deal",
        "price_cents": 7900,
        "currency": "USD",
        "merchant_name": "Premium Audio Deals",
        "merchant_domain": "premium-audio-deals.shop",
        "image_url": "",
        "product_url": "https://premium-audio-deals.shop/",
        "category": "audio",
        "source": "fixture"
      }
    ],
    "checks": {
      "lst_bestbuy_xm5": [
        { "id": "domain_age", "name": "Domain age", "status": "passed", "severity": 0, "summary": "Registered for 28 years.", "evidence": [{ "label": "Created", "value": "1998" }], "source": "fixture", "duration_ms": 180 },
        { "id": "ssl_cert", "name": "SSL certificate", "status": "passed", "severity": 0, "summary": "Certificate is valid.", "evidence": [], "source": "fixture", "duration_ms": 90 },
        { "id": "safe_browsing", "name": "Safe Browsing", "status": "passed", "severity": 0, "summary": "No threats found.", "evidence": [], "source": "fixture", "duration_ms": 210 },
        { "id": "reddit_sentiment", "name": "Reddit", "status": "passed", "severity": 0, "summary": "No scam reports.", "evidence": [], "source": "fixture", "duration_ms": 240 },
        { "id": "page_flags", "name": "Page flags", "status": "passed", "severity": 0, "summary": "No pressure tactics.", "evidence": [], "source": "fixture", "duration_ms": 160 }
      ],
      "lst_walmart_xm5": [
        { "id": "domain_age", "name": "Domain age", "status": "passed", "severity": 0, "summary": "Registered for 25 years.", "evidence": [], "source": "fixture", "duration_ms": 180 },
        { "id": "ssl_cert", "name": "SSL certificate", "status": "passed", "severity": 0, "summary": "Certificate is valid.", "evidence": [], "source": "fixture", "duration_ms": 90 },
        { "id": "safe_browsing", "name": "Safe Browsing", "status": "passed", "severity": 0, "summary": "No threats found.", "evidence": [], "source": "fixture", "duration_ms": 200 },
        { "id": "reddit_sentiment", "name": "Reddit", "status": "passed", "severity": 0, "summary": "No scam reports.", "evidence": [], "source": "fixture", "duration_ms": 220 }
      ],
      "lst_amazon_bose": [
        { "id": "domain_age", "name": "Domain age", "status": "passed", "severity": 0, "summary": "Registered for 30 years.", "evidence": [], "source": "fixture", "duration_ms": 180 },
        { "id": "ssl_cert", "name": "SSL certificate", "status": "passed", "severity": 0, "summary": "Certificate is valid.", "evidence": [], "source": "fixture", "duration_ms": 90 },
        { "id": "safe_browsing", "name": "Safe Browsing", "status": "passed", "severity": 0, "summary": "No threats found.", "evidence": [], "source": "fixture", "duration_ms": 200 },
        { "id": "reddit_sentiment", "name": "Reddit", "status": "passed", "severity": 0, "summary": "No scam reports.", "evidence": [], "source": "fixture", "duration_ms": 220 },
        { "id": "page_flags", "name": "Page flags", "status": "passed", "severity": 0, "summary": "No pressure tactics.", "evidence": [], "source": "fixture", "duration_ms": 160 }
      ],
      "lst_bb_xm4": [
        { "id": "domain_age", "name": "Domain age", "status": "passed", "severity": 0, "summary": "Registered for 28 years.", "evidence": [], "source": "fixture", "duration_ms": 180 },
        { "id": "ssl_cert", "name": "SSL certificate", "status": "passed", "severity": 0, "summary": "Certificate is valid.", "evidence": [], "source": "fixture", "duration_ms": 90 },
        { "id": "safe_browsing", "name": "Safe Browsing", "status": "passed", "severity": 0, "summary": "No threats found.", "evidence": [], "source": "fixture", "duration_ms": 200 },
        { "id": "reddit_sentiment", "name": "Reddit", "status": "warning", "severity": 0.4, "summary": "A few shipping complaints. Not a scam pattern.", "evidence": [], "source": "fixture", "duration_ms": 260 },
        { "id": "page_flags", "name": "Page flags", "status": "passed", "severity": 0, "summary": "No pressure tactics.", "evidence": [], "source": "fixture", "duration_ms": 160 }
      ],
      "lst_nordstrom_at": [
        { "id": "domain_age", "name": "Domain age", "status": "passed", "severity": 0, "summary": "Long-established retailer.", "evidence": [], "source": "fixture", "duration_ms": 180 },
        { "id": "ssl_cert", "name": "SSL certificate", "status": "passed", "severity": 0, "summary": "Certificate is valid.", "evidence": [], "source": "fixture", "duration_ms": 90 },
        { "id": "safe_browsing", "name": "Safe Browsing", "status": "passed", "severity": 0, "summary": "No threats found.", "evidence": [], "source": "fixture", "duration_ms": 200 },
        { "id": "reddit_sentiment", "name": "Reddit", "status": "warning", "severity": 0.5, "summary": "Mixed reviews about this listing.", "evidence": [], "source": "fixture", "duration_ms": 260 },
        { "id": "page_flags", "name": "Page flags", "status": "warning", "severity": 0.4, "summary": "One urgency banner.", "evidence": [], "source": "fixture", "duration_ms": 160 }
      ],
      "lst_target_bose": [
        { "id": "domain_age", "name": "Domain age", "status": "passed", "severity": 0, "summary": "Long-established retailer.", "evidence": [], "source": "fixture", "duration_ms": 180 },
        { "id": "ssl_cert", "name": "SSL certificate", "status": "passed", "severity": 0, "summary": "Certificate is valid.", "evidence": [], "source": "fixture", "duration_ms": 90 },
        { "id": "safe_browsing", "name": "Safe Browsing", "status": "passed", "severity": 0, "summary": "No threats found.", "evidence": [], "source": "fixture", "duration_ms": 200 },
        { "id": "reddit_sentiment", "name": "Reddit", "status": "warning", "severity": 0.45, "summary": "A few buyers could not match the seller name.", "evidence": [], "source": "fixture", "duration_ms": 260 },
        { "id": "page_flags", "name": "Page flags", "status": "passed", "severity": 0, "summary": "No pressure tactics.", "evidence": [], "source": "fixture", "duration_ms": 160 }
      ],
      "lst_amazon_budget": [
        { "id": "domain_age", "name": "Domain age", "status": "passed", "severity": 0, "summary": "Amazon is an established domain.", "evidence": [], "source": "fixture", "duration_ms": 180 },
        { "id": "ssl_cert", "name": "SSL certificate", "status": "passed", "severity": 0, "summary": "Certificate is valid.", "evidence": [], "source": "fixture", "duration_ms": 90 },
        { "id": "safe_browsing", "name": "Safe Browsing", "status": "passed", "severity": 0, "summary": "No threats found.", "evidence": [], "source": "fixture", "duration_ms": 200 },
        { "id": "reddit_sentiment", "name": "Reddit", "status": "warning", "severity": 0.5, "summary": "Buyers report a no-name brand.", "evidence": [], "source": "fixture", "duration_ms": 260 },
        { "id": "page_flags", "name": "Page flags", "status": "warning", "severity": 0.6, "summary": "Countdown timer and stock warning.", "evidence": [], "source": "fixture", "duration_ms": 160 }
      ],
      "lst_villain": [
        { "id": "domain_age", "name": "Domain age", "status": "failed", "severity": 0.95, "summary": "Domain registered 12 days ago.", "evidence": [{ "label": "Age", "value": "12 days" }], "source": "fixture", "duration_ms": 180 },
        { "id": "ssl_cert", "name": "SSL certificate", "status": "warning", "severity": 0.7, "summary": "Certificate issued this week.", "evidence": [], "source": "fixture", "duration_ms": 90 },
        { "id": "safe_browsing", "name": "Safe Browsing", "status": "passed", "severity": 0, "summary": "Not on the threat list yet.", "evidence": [], "source": "fixture", "duration_ms": 200 },
        { "id": "reddit_sentiment", "name": "Reddit", "status": "failed", "severity": 0.9, "summary": "Three scam reports this week.", "evidence": [], "source": "fixture", "duration_ms": 260 },
        { "id": "page_flags", "name": "Page flags", "status": "failed", "severity": 0.9, "summary": "Only crypto accepted. No return policy.", "evidence": [], "source": "fixture", "duration_ms": 160 }
      ]
    },
    "scores": {
      "lst_bestbuy_xm5": { "score": 92, "verdict": "trusted", "confidence": 1, "penalties": [], "fatal_flags": [], "top_reason": "All checks passed.", "scoring_version": "1.0" },
      "lst_walmart_xm5": { "score": 85, "verdict": "trusted", "confidence": 0.8, "penalties": [], "fatal_flags": [], "top_reason": "All completed checks passed.", "scoring_version": "1.0" },
      "lst_amazon_bose": { "score": 88, "verdict": "trusted", "confidence": 1, "penalties": [], "fatal_flags": [], "top_reason": "All checks passed.", "scoring_version": "1.0" },
      "lst_bb_xm4": { "score": 64, "verdict": "caution", "confidence": 1, "penalties": [{ "check_id": "reddit_sentiment", "points": 6, "reason": "Shipping complaints" }], "fatal_flags": [], "top_reason": "A few shipping complaints. Not a scam pattern.", "scoring_version": "1.0" },
      "lst_nordstrom_at": { "score": 58, "verdict": "caution", "confidence": 1, "penalties": [], "fatal_flags": [], "top_reason": "Mixed reviews about this listing.", "scoring_version": "1.0" },
      "lst_target_bose": { "score": 61, "verdict": "caution", "confidence": 1, "penalties": [], "fatal_flags": [], "top_reason": "A few buyers could not match the seller name.", "scoring_version": "1.0" },
      "lst_amazon_budget": { "score": 48, "verdict": "caution", "confidence": 1, "penalties": [], "fatal_flags": [], "top_reason": "Countdown timer and stock warning.", "scoring_version": "1.0" },
      "lst_villain": { "score": 12, "verdict": "danger", "confidence": 1, "penalties": [{ "check_id": "domain_age", "points": 38, "reason": "Domain registered 12 days ago." }], "fatal_flags": ["domain_age"], "top_reason": "Domain registered 12 days ago.", "scoring_version": "1.0" }
    }
  }
}
```

Walmart is missing the Page flags check on purpose. That card shows a gray skeleton row, so you can see the “still loading” state. The other seven cards have all five checks.

Empty `image_url` is also on purpose. The card draws a colored block with the store’s initial instead of a broken image.

---

## Step 11 — The API client (`frontend/src/lib/api.ts`)

**Why:** This is the only file that knows how to talk to the server. Today every function returns the mock file. At 7:30 PM you flip `VITE_USE_MOCK` to `0` and the same function names call the real server. The screens do not change.

The functions you are creating, and the server route each one will use later:

| Function | Later it will call | Used on screen today? |
|---|---|---|
| `createSession` | `POST /api/sessions` | Yes, after the last question |
| `submitAnswers` | `POST /api/sessions/{id}/answers` | Yes, after the last question |
| `getSnapshot` | `GET /api/sessions/{id}` | Yes, this returns the eight products |
| `createCheckout` | `POST /api/checkout` | No. Throws if something calls it |
| `confirmCheckout` | `POST /api/checkout/{id}/confirm` | No |
| `getReceipt` | `GET /api/receipts/{id}` | No |

Create `frontend/src/lib/api.ts`. Paste and save.

```ts
import mockFile from "../data/mock-session.json"
import type {
  Answer,
  CreateSessionResponse,
  SearchSpec,
  SessionSnapshot,
  SubmitAnswersResponse,
} from "@/lib/types.ts"

type MockFile = {
  create_session: CreateSessionResponse
  snapshot: SessionSnapshot
}

const mock = mockFile as MockFile

const useMock = import.meta.env.VITE_USE_MOCK !== "0"

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const base = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
  const response = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  })
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as {
      error?: { code?: string; message?: string }
    } | null
    const message = body?.error?.message ?? response.statusText
    throw new Error(message)
  }
  return (await response.json()) as T
}

export async function createSession(input: {
  query: string
  client_id: string
}): Promise<CreateSessionResponse> {
  if (useMock) {
    await delay(300)
    return {
      ...mock.create_session,
      questions: mock.create_session.questions,
    }
  }
  return request<CreateSessionResponse>("/api/sessions", {
    method: "POST",
    body: JSON.stringify(input),
  })
}

export async function submitAnswers(
  sessionId: string,
  input: { answers: Answer[]; skip_remaining: boolean },
): Promise<SubmitAnswersResponse> {
  const budget = input.answers.find((answer) => answer.question_id === "q_budget")
  const budgetCents =
    budget?.option_id === "150"
      ? 15000
      : budget?.option_id === "300"
        ? 30000
        : budget?.option_id === "600"
          ? 60000
          : null
  const searchSpec: SearchSpec = {
    query: mock.snapshot.query,
    budget_max_cents: budgetCents,
    category: "audio",
    merchants_preferred: [],
  }
  if (useMock) {
    await delay(400)
    return {
      session_id: sessionId,
      stage: "searching",
      events_url: `/api/sessions/${sessionId}/events`,
      search_spec: searchSpec,
    }
  }
  return request<SubmitAnswersResponse>(`/api/sessions/${sessionId}/answers`, {
    method: "POST",
    body: JSON.stringify(input),
  })
}

export async function getSnapshot(sessionId: string): Promise<SessionSnapshot> {
  if (useMock) {
    await delay(300)
    return mock.snapshot
  }
  return request<SessionSnapshot>(`/api/sessions/${sessionId}`)
}

export async function createCheckout(): Promise<never> {
  throw new Error("Checkout UI starts at 6:00 PM.")
}

export async function confirmCheckout(): Promise<never> {
  throw new Error("Checkout UI starts at 6:00 PM.")
}

export async function getReceipt(): Promise<never> {
  throw new Error("Receipt UI starts at 6:00 PM.")
}
```

`useMock` is true unless the env var is the exact string `"0"`. If `.env.local` is missing, the app still uses the fake file. That is what you want today.

---

## Step 12 — The memory store (`frontend/src/store/sessionStore.ts`)

**Why:** React forgets values when you move between screens unless something holds them. Zustand is that holder. The discovery screen writes the snapshot into the store. The results screen reads it back.

Create the folder `frontend/src/store`. Create `sessionStore.ts`. Paste and save.

```ts
import { create } from "zustand"
import type {
  Listing,
  Question,
  Recommendation,
  ScoreResult,
  SessionSnapshot,
  SessionStage,
  TrustCheckResult,
} from "@/lib/types.ts"

type Stage = SessionStage | "discovery"

type SessionState = {
  sessionId: string | null
  stage: Stage
  query: string
  questions: Question[]
  listings: Listing[]
  checks: Record<string, TrustCheckResult[]>
  scores: Record<string, ScoreResult>
  recommendation: Recommendation | null
  setQuery: (query: string) => void
  showQuestions: (questions: Question[]) => void
  startSession: (snapshot: SessionSnapshot) => void
  reset: () => void
}

const empty = {
  sessionId: null as string | null,
  stage: "discovery" as Stage,
  query: "",
  questions: [] as Question[],
  listings: [] as Listing[],
  checks: {} as Record<string, TrustCheckResult[]>,
  scores: {} as Record<string, ScoreResult>,
  recommendation: null as Recommendation | null,
}

export const useSessionStore = create<SessionState>((set) => ({
  ...empty,
  setQuery: (query) => set({ query }),
  showQuestions: (questions) => set({ questions, stage: "clarifying" }),
  startSession: (snapshot) =>
    set({
      sessionId: snapshot.session_id,
      stage: "ready",
      query: snapshot.query,
      listings: snapshot.listings,
      checks: snapshot.checks,
      scores: snapshot.scores,
      recommendation: snapshot.recommendation,
    }),
  reset: () => set({ ...empty }),
}))
```

`stage` starts as `"discovery"`. After the questions it becomes `"ready"`, and the shell swaps in the product grid. `reset` sends you back to the first screen so you can practice the demo again.

---

## Step 13 — The shell (`frontend/src/App.tsx`)

**Why:** This is the page frame. It always shows the name Sniff and the sandbox badge. Inside the frame it shows either the questions or the cards, depending on the store.

The sandbox badge stays visible on every screen today and tonight. The words are: `Sandbox — simulated Visa flow`. Judges need to see that the payment is fake. You are not building payment yet. The badge is still required.

Open `frontend/src/App.tsx`. Select all, delete, paste this, save.

```tsx
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DiscoveryFlow } from "@/features/discovery/DiscoveryFlow.tsx"
import { ResultsGrid } from "@/features/results/ResultsGrid.tsx"
import { useSessionStore } from "@/store/sessionStore.ts"

export default function App() {
  const stage = useSessionStore((state) => state.stage)
  const query = useSessionStore((state) => state.query)
  const listings = useSessionStore((state) => state.listings)
  const checks = useSessionStore((state) => state.checks)
  const scores = useSessionStore((state) => state.scores)
  const recommendation = useSessionStore((state) => state.recommendation)
  const reset = useSessionStore((state) => state.reset)

  return (
    <div className="min-h-screen bg-white text-stone-900">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <h1 className="text-xl font-semibold tracking-tight">Sniff</h1>
        <Badge variant="outline">Sandbox — simulated Visa flow</Badge>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        {stage === "ready" ? (
          <div className="space-y-6">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-2xl font-semibold">Results for “{query}”</h2>
              <Button type="button" variant="outline" onClick={reset}>
                Start over
              </Button>
            </div>
            <ResultsGrid
              listings={listings}
              checks={checks}
              scores={scores}
              recommendation={recommendation}
            />
          </div>
        ) : (
          <DiscoveryFlow onStarted={() => undefined} />
        )}
      </main>
    </div>
  )
}
```

You will create `DiscoveryFlow` and `ResultsGrid` in the next steps. Until those files exist, the editor will underline the imports in red. That is expected. Do not “fix” it by deleting the imports.

Also open `frontend/index.html` and change the title from `frontend` to `Sniff`:

```html
<title>Sniff</title>
```

---

## Step 14 — The shell test, then your first commit

**Why:** The team rule is that every task ends with a passing test and a commit. This test only checks that the word Sniff is on the page. It will fail until Step 15 exists, because `App` imports `DiscoveryFlow`. So do Step 15, then come back and run the test. The commit covers Steps 8–15 together.

Create `frontend/src/App.test.tsx`. Paste and save.

```tsx
import { render, screen } from "@testing-library/react"
import App from "./App.tsx"

test("renders the app shell", () => {
  render(<App />)
  expect(screen.getByText(/sniff/i)).toBeInTheDocument()
})
```

`/sniff/i` means “the word sniff, any capitalization.” The heading `Sniff` matches.

---

## Step 15 — The discovery screen

**Why:** A blank chat box is the wrong product. The person types one sentence, then answers two or three tappable choices. The first question has to be **What’s your ceiling?** because the test looks for that sentence.

What the person does:

1. Types in the box. The placeholder text is exactly `What are you looking for?`
2. Presses **Find products**. The button stays disabled while the box is empty.
3. Sees one question at a time. Each choice is a button (a “pill”), not a dropdown.
4. The budget question also has a text box, because `allow_free_text` is true. They can pick a pill **or** type. They do not need both.
5. Presses **Next** until the last question, then **See results**.
6. Sees gray skeleton bars for about a second. That wait is the `delay()` in `api.ts`, so the loading state is visible.
7. Lands on the cards.

Create the folder `frontend/src/features`. Inside it, create `discovery`. Inside that, create `DiscoveryFlow.tsx`. Paste and save.

```tsx
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { createSession, getSnapshot, submitAnswers } from "@/lib/api.ts"
import type { Answer, Question } from "@/lib/types.ts"
import { useSessionStore } from "@/store/sessionStore.ts"

type Props = {
  onStarted: (sessionId: string) => void
}

export function DiscoveryFlow({ onStarted }: Props) {
  const setQuery = useSessionStore((state) => state.setQuery)
  const showQuestions = useSessionStore((state) => state.showQuestions)
  const startSession = useSessionStore((state) => state.startSession)
  const [query, setLocalQuery] = useState("")
  const [questions, setQuestions] = useState<Question[]>([])
  const [index, setIndex] = useState(0)
  const [phase, setPhase] = useState<"query" | "questions" | "submitting">("query")
  const [picked, setPicked] = useState<string | null>(null)
  const [freeText, setFreeText] = useState("")
  const [answers, setAnswers] = useState<Answer[]>([])
  const [error, setError] = useState<string | null>(null)

  const question = questions[index]

  async function onFindProducts() {
    const trimmed = query.trim()
    if (!trimmed) return
    setQuery(trimmed)
    setError(null)
    const created = await createSession({ query: trimmed, client_id: "demo" })
    setQuestions(created.questions)
    showQuestions(created.questions)
    setIndex(0)
    setPicked(null)
    setFreeText("")
    setPhase("questions")
  }

  function currentAnswer(): Answer | null {
    if (!question) return null
    if (picked) return { question_id: question.id, option_id: picked }
    if (freeText.trim()) return { question_id: question.id, text: freeText.trim() }
    return null
  }

  async function onNext() {
    const answer = currentAnswer()
    if (!question || !answer) return
    const nextAnswers = [...answers, answer]
    setAnswers(nextAnswers)
    setPicked(null)
    setFreeText("")
    if (index < questions.length - 1) {
      setIndex(index + 1)
      return
    }
    setPhase("submitting")
    setError(null)
    try {
      const submitted = await submitAnswers("ses_mock", {
        answers: nextAnswers,
        skip_remaining: false,
      })
      const snapshot = await getSnapshot(submitted.session_id)
      startSession(snapshot)
      onStarted(snapshot.session_id)
    } catch (caught) {
      setPhase("questions")
      setError(caught instanceof Error ? caught.message : "Something went wrong")
    }
  }

  if (phase === "submitting") {
    return (
      <div className="space-y-4" aria-busy="true">
        <p className="text-lg">Looking at retailers…</p>
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-28 w-full" />
      </div>
    )
  }

  if (phase === "query" || !question) {
    return (
      <form
        className="mx-auto max-w-xl space-y-4"
        onSubmit={(event) => {
          event.preventDefault()
          void onFindProducts()
        }}
      >
        <label className="block text-lg font-medium" htmlFor="query">
          What do you want to buy?
        </label>
        <Input
          id="query"
          value={query}
          placeholder="What are you looking for?"
          onChange={(event) => setLocalQuery(event.target.value)}
        />
        <Button type="submit" disabled={query.trim().length === 0}>
          Find products
        </Button>
      </form>
    )
  }

  const ready = picked !== null || freeText.trim().length > 0
  const last = index === questions.length - 1

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <p className="text-sm text-stone-500">
        Question {index + 1} of {questions.length}
      </p>
      <h2 className="text-2xl font-semibold">{question.prompt}</h2>
      <div className="flex flex-wrap gap-2">
        {question.options.map((option) => {
          const selected = picked === option.id
          return (
            <Button
              key={option.id}
              type="button"
              variant={selected ? "default" : "outline"}
              onClick={() => {
                setPicked(option.id)
                setFreeText("")
              }}
            >
              {option.label}
            </Button>
          )
        })}
      </div>
      {question.allow_free_text ? (
        <Input
          value={freeText}
          placeholder="Or type your own answer"
          onChange={(event) => {
            setFreeText(event.target.value)
            setPicked(null)
          }}
        />
      ) : null}
      {error ? <p className="text-sm text-red-800">{error}</p> : null}
      <Button type="button" disabled={!ready} onClick={() => void onNext()}>
        {last ? "See results" : "Next"}
      </Button>
    </div>
  )
}
```

Pressing Enter in the search box submits the form. That is the keyboard path. The pills are real `<button>` elements, so Tab and Enter work. Do not remove the focus ring. shadcn already draws one.

Create `frontend/src/features/discovery/DiscoveryFlow.test.tsx`. Paste and save.

```tsx
import { fireEvent, render, screen } from "@testing-library/react"
import { DiscoveryFlow } from "./DiscoveryFlow.tsx"

test("renders questions and submits", async () => {
  render(<DiscoveryFlow onStarted={() => undefined} />)
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "headphones" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))
  expect(await screen.findByText(/what's your ceiling/i)).toBeInTheDocument()
})
```

This test stops at the first question. It does not click through to the cards.

---

## Step 16 — Run the tests and make the first commit

**Why:** This checkpoint saves the shell, the types, the fake API, the store, and the question screen.

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks\frontend
npm.cmd test -- --run
```

**It worked if** you see 2 passed (`renders the app shell` and `renders questions and submits`).

If a test fails, read the red paragraph. It names the file. Fix that file and run the command again. Do not commit a red test.

When both pass:

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks
git add frontend/src frontend/package.json frontend/package-lock.json frontend/vite.config.ts frontend/tsconfig.app.json frontend/tsconfig.json frontend/.env.example frontend/index.html frontend/components.json
git commit -m "feat: add frontend shell, types, and api client"
```

`components.json` is a file shadcn creates. If git says it does not exist, leave it out of the `git add` line and run the add again without that name.

**It worked if** git prints `[c/web ...] feat: add frontend shell...`. If it says you are on `main`, stop and run `git checkout c/web` before committing again. Do not commit `node_modules` or `.env.local`. If those show up in `git status`, do not `git add` them.

The second half of discovery (the results grid) is the next commit. Keep going.

---

## Step 17 — The trust badge

**Why:** One label on the card tells the person the verdict. No score yet means the checks are still running, so the label says **Checking** in gray.

Create the folder `frontend/src/features/results`. Create `TrustBadge.tsx`. Paste and save.

```tsx
import { Badge } from "@/components/ui/badge"
import type { Verdict } from "@/lib/types.ts"

type Props = {
  score?: number
  verdict?: Verdict
}

const styleFor: Record<Verdict, { color: string; background: string; label: string }> = {
  trusted: {
    color: "var(--trust-trusted)",
    background: "var(--trust-trusted-bg)",
    label: "Trusted",
  },
  caution: {
    color: "var(--trust-caution)",
    background: "var(--trust-caution-bg)",
    label: "Caution",
  },
  danger: {
    color: "var(--trust-danger)",
    background: "var(--trust-danger-bg)",
    label: "Danger",
  },
}

export function TrustBadge({ score, verdict }: Props) {
  if (score === undefined || verdict === undefined) {
    return (
      <Badge
        variant="outline"
        style={{
          color: "var(--trust-pending)",
          background: "var(--trust-pending-bg)",
        }}
      >
        Checking
      </Badge>
    )
  }
  const tone = styleFor[verdict]
  return (
    <Badge
      variant="outline"
      style={{ color: tone.color, background: tone.background }}
    >
      {score} · {tone.label}
    </Badge>
  )
}
```

A trusted card reads `92 · Trusted`. A danger card reads `12 · Danger`.

---

## Step 18 — One check row

**Why:** Each investigation has five rows. This component draws one finished row. A check that has started but has no result yet is not this component. The card draws a skeleton instead.

Create `frontend/src/features/results/CheckRow.tsx`. Paste and save.

```tsx
import type { TrustCheckResult, TrustStatus } from "@/lib/types.ts"

type Props = {
  check: TrustCheckResult
}

const statusLabel: Record<TrustStatus, string> = {
  passed: "Passed",
  warning: "Warning",
  failed: "Failed",
  skipped: "Skipped",
}

export function CheckRow({ check }: Props) {
  return (
    <div className="flex items-start justify-between gap-3 border-t py-2 text-sm">
      <div>
        <p className="font-medium">{check.name}</p>
        <p className="text-stone-600">{check.summary}</p>
      </div>
      <p className="shrink-0 font-medium">{statusLabel[check.status]}</p>
    </div>
  )
}
```

“Skipped” is the word for a check that did not finish. Do not draw a checkmark for it.

---

## Step 19 — One product card

**Why:** This is the rectangle for a single store listing: picture, name, store, price, badge, and the five rows.

Create `frontend/src/features/results/ProductCard.tsx`. Paste and save.

```tsx
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { formatCents } from "@/lib/format.ts"
import type { CheckId, Listing, ScoreResult, TrustCheckResult } from "@/lib/types.ts"
import { CheckRow } from "@/features/results/CheckRow.tsx"
import { TrustBadge } from "@/features/results/TrustBadge.tsx"

const ALL_CHECKS: { id: CheckId; name: string }[] = [
  { id: "domain_age", name: "Domain age" },
  { id: "ssl_cert", name: "SSL certificate" },
  { id: "safe_browsing", name: "Safe Browsing" },
  { id: "reddit_sentiment", name: "Reddit" },
  { id: "page_flags", name: "Page flags" },
]

type Props = {
  listing: Listing
  checks: TrustCheckResult[]
  score?: ScoreResult
  isBest: boolean
}

export function ProductCard({ listing, checks, score, isBest }: Props) {
  const [imageFailed, setImageFailed] = useState(listing.image_url.length === 0)
  const initial = listing.merchant_name.slice(0, 1).toUpperCase()

  return (
    <Card className={isBest ? "ring-2 ring-stone-900" : undefined}>
      <CardHeader className="space-y-3">
        {imageFailed ? (
          <div
            className="flex h-36 items-center justify-center rounded-md bg-gradient-to-br from-stone-200 to-stone-400 text-3xl font-semibold text-stone-800"
            aria-hidden="true"
          >
            {initial}
          </div>
        ) : (
          <img
            src={listing.image_url}
            alt=""
            className="h-36 w-full rounded-md object-cover"
            onError={() => setImageFailed(true)}
          />
        )}
        {isBest ? (
          <p className="text-xs font-semibold uppercase tracking-wide text-stone-600">
            Best pick
          </p>
        ) : null}
        <CardTitle className="line-clamp-2 text-lg">{listing.title}</CardTitle>
        <p className="text-sm text-stone-600">
          {listing.merchant_name}
          <span className="text-stone-400"> · {listing.merchant_domain}</span>
        </p>
        <p className="text-xl font-semibold">{formatCents(listing.price_cents, listing.currency)}</p>
        <TrustBadge score={score?.score} verdict={score?.verdict} />
      </CardHeader>
      <CardContent>
        {ALL_CHECKS.map((meta) => {
          const found = checks.find((check) => check.id === meta.id)
          if (!found) {
            return <Skeleton key={meta.id} className="my-2 h-10 w-full" />
          }
          return <CheckRow key={meta.id} check={found} />
        })}
      </CardContent>
    </Card>
  )
}
```

The “Best pick” line and the dark ring only mark which card was sorted first. The sentence “You save $30” is the next time block. Do not add it now.

---

## Step 20 — The grid of cards

**Why:** This lays the cards out and moves the recommended product to the front.

Create `frontend/src/features/results/ResultsGrid.tsx`. Paste and save.

```tsx
import type { Listing, Recommendation, ScoreResult, TrustCheckResult } from "@/lib/types.ts"
import { ProductCard } from "@/features/results/ProductCard.tsx"

type Props = {
  listings: Listing[]
  checks: Record<string, TrustCheckResult[]>
  scores: Record<string, ScoreResult>
  recommendation?: Recommendation | null
}

export function ResultsGrid({ listings, checks, scores, recommendation = null }: Props) {
  const bestId = recommendation?.recommended_listing_id
  const ordered = [...listings].sort((a, b) => {
    if (a.id === bestId) return -1
    if (b.id === bestId) return 1
    return 0
  })

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      {ordered.map((listing) => (
        <ProductCard
          key={listing.id}
          listing={listing}
          checks={checks[listing.id] ?? []}
          score={scores[listing.id]}
          isBest={listing.id === bestId}
        />
      ))}
    </div>
  )
}
```

One column on a narrow window, two from a medium width, three on a wide window. The page itself should not scroll sideways.

Create `frontend/src/features/results/ResultsGrid.test.tsx`. Paste and save.

```tsx
import { render, screen } from "@testing-library/react"
import { ResultsGrid } from "./ResultsGrid.tsx"

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
  )
  expect(screen.getByText("Sony XM5")).toBeInTheDocument()
  expect(screen.getByText("Best Buy")).toBeInTheDocument()
  expect(screen.getByText(/\$249\.00/)).toBeInTheDocument()
})
```

This test uses its own tiny product. It does not read `mock-session.json`. The title in the test is `Sony XM5`. The mock file uses the longer name `Sony WH-1000XM5`. Both are correct. Do not change the test to match the mock.

---

## Step 21 — Tests, the second commit, then look at it

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks\frontend
npm.cmd test -- --run
```

**It worked if** you see 3 passed. The new one is `renders title, merchant, and formatted price`.

Then:

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks
git add frontend/src
git commit -m "feat: add results grid and trust ui"
```

Start the site:

```powershell
cd C:\Users\marcu\OneDrive\Code\Dubhacks\frontend
npm.cmd run dev
```

**It worked if** the terminal prints a local URL, usually `http://localhost:5173/`. Hold Ctrl and click that URL. Leave this terminal running. If you need to type more commands, open a second terminal with the **+** in the terminal panel.

The server from your teammates stays off. If the page only loads when their server is on, the mock switch is wrong. Check that `frontend/.env.local` contains `VITE_USE_MOCK=1`, then stop the dev server (Ctrl+C in that terminal) and run `npm.cmd run dev` again. Vite reads `.env.local` at startup.

---

## Step 22 — Click through this once

Do this in the browser. This is the 3:30 proof.

1. The top of the page says **Sniff**.
2. A badge says **Sandbox — simulated Visa flow**.
3. Type `noise cancelling headphones`. Press **Find products**.
4. The first question is **What’s your ceiling?** Click **$150–$300**.
5. Click **Next**. Answer the next two questions with any pill.
6. Click **See results**. Gray bars show up briefly.
7. Eight cards appear. The first one is **Sony WH-1000XM5** at Best Buy, price **$249.00**, with a small **Best pick** label.
8. You can see a green **Trusted** badge, an amber **Caution** badge, and a red **Danger** badge. Each badge also has the word, not only the color.
9. The **Premium Audio Deals** card says **Failed** on Domain age, Reddit, and Page flags.
10. The Walmart card has one gray skeleton row where Page flags would be.
11. Cards with no photo show a letter, not a broken-image icon.
12. **Start over** returns you to the search box.
13. Shrink the window. The cards stack. The page does not grow a horizontal scrollbar.

If step 7 fails, the bug is in your files, not in your teammate’s server. Do not start building the live-update hook to get past it.

---

## What to say at the 3:30 check-in

One sentence each:

- **Done:** discovery and the eight mock cards work with the server off.
- **Next:** connect the live event stream with A (that is the 3:30–6:00 block).
- **Blocked:** say the actual error if something in the list above failed. If you have been stuck for 15 minutes, do not wait for 3:30. Message the team when it happens.

---

## If a command fails

| What you see | What to do |
|---|---|
| `running scripts is disabled` | You typed `npm` or `npx`. Retype it as `npm.cmd` or `npx.cmd`. |
| `npm ERR!` | Copy the last 15 lines into the team channel. Do not delete `node_modules` unless someone tells you to. |
| Red squiggle on `@/something` | Step 3b or Step 5 did not finish. `@` only works after the tsconfig paths and shadcn exist. |
| Test cannot find “Sniff” or “What’s your ceiling?” | The visible text was changed. Put the original words back. The tests look for those exact phrases. |
| Browser shows the Vite starter page with a counter | `App.tsx` is still the starter file. Repeat Step 13. |
| `git commit` says “on main” | Run `git checkout c/web`, then commit again. |

You are not behind if the cards look plain. Plain and correct beats a decoration that hides a missing badge.
