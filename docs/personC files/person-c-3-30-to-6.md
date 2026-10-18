# Person C — 3:30–6:00 checklist

Done when mock events fill the cards one check at a time, a danger card can be purged, and the best pick is highlighted. Pay stays disabled. This block does not build the real checkout.

## Task 20 — session stream

- [x] `frontend/src/lib/sse.ts` opens one `EventSource` per session and closes it on cleanup.
- [x] Listen for the named events in `docs/contracts.md` (`listing.found`, `check.completed`, `listing.scored`, `recommendation.ready`, `investigation.complete`, `session.error`).
- [x] `useSessionStream` drops any event whose `seq` was already applied.
- [x] The store upserts checks by listing id + check id.
- [x] On a connection error, load `GET /api/sessions/{id}` and render that snapshot.
- [x] Close the stream on `investigation.complete` and on a non-recoverable `session.error`.
- [x] StrictMode cleanup closes the first connection and cancels mock timers.
- [x] While `VITE_USE_MOCK` is not `0`, play the fake session as timed events so the grid animates with no server.

## Task 21 — best pick, purge, empty, error

- [x] `BestPick` shows the recommended title and the savings in dollars.
- [x] The recommended card stays first and visibly marked.
- [x] `no_trusted_option` shows an empty state with the reason and Start over. It is not an error.
- [x] `ErrorBanner` can be dismissed and does not block the page.
- [x] `PurgeOverlay` wipes danger cards. Reduced motion skips the animation.
- [x] A danger card stays on screen until Purge is clicked.

## Checkout shell

- [x] A sheet shows the best-pick merchant and amount.
- [x] The Pay button is disabled.
- [x] The sandbox badge stays visible.

## Not this block

Live checkout, passkey, receipt, and replacing the mock with the real server. Those start at 6:00 and 7:30.
