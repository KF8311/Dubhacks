# Person C — 1:15–3:30 checklist

Done when discovery → results works offline with fake checks. This block does not open a live `EventSource` or a real checkout.

Verified against `frontend/src` on `2dce62c`. Tests: `App.test.tsx`, `DiscoveryFlow.test.tsx`, `ProductCard.test.tsx`, `TrustBadge.test.tsx`, `CheckRow.test.tsx`.

## Task 17 — shell, types, client, store

- [x] Vite + React + TypeScript + Tailwind + shadcn/ui (`frontend/package.json`).
- [x] `frontend/src/lib/types.ts` mirrors the session, listing, check, score, and receipt shapes.
- [x] `frontend/src/lib/api.ts` talks to `/api/sessions`. Mock is opt-in (`?mock=1` / `VITE_USE_MOCK=1`).
- [x] `frontend/src/store/sessionStore.ts` holds the query, questions, listings, checks, scores, and recommendation.
- [x] `AppShell` shows the Sykes mark and the full sandbox line: “Sandbox — simulated Visa Intelligent Commerce flow.”

## Task 18 — discovery

- [x] Search box + Find products.
- [x] Two to three clarifying questions, one at a time, with a progress mark (`Question 1 of 3`).
- [x] Chips plus a free-text field (“Or type your own answer”).
- [x] Submit starts a session and leaves the landing screen.

## Task 19 — results grid

- [x] `ResultsGrid` + `ProductCard` + `TrustBadge` + `CheckRow`.
- [x] Tokens: trusted teal, caution amber, danger red, pending gray (`--trust-*` in `index.css`).
- [x] `frontend/src/data/mock-session.json` has listings and fake checks so the UI renders with the API ignored.

## Not this block

Live SSE, best-pick highlight, purge, and a working Pay button. Those start at 3:30.
