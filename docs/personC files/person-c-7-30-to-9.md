# Person C — 7:30–9:00 checklist

Done when a real session runs real checks, a real checkout, and a real receipt, with no mock data on screen. This block is stopped until `origin/main` is merged into `c/web` and Person A ships the checkout HTTP routes.

## Already done on main, not on this branch

- [ ] `POST /api/sessions` and `POST /api/sessions/{id}/answers` are the live path. Mock is opt-in with `?mock=1` or `VITE_USE_MOCK=1`.
- [ ] `EventSource` is the live path. The stream emits `listing.found`, `check.completed`, `listing.scored`, and `recommendation.ready`.
- [ ] Discovery must submit the real session id. Main fixed a bug where the client always sent `ses_mock`.
- [ ] An allowlisted merchant shows `Verified · Trusted` instead of `0 · Trusted`.
- [ ] Happy-path answers are `$150–$300`, then the priority, then the use. `Under $150` leaves only the villain and ends in `no_trusted_option`.

## Task 23 is missing, so checkout cannot go live

- [ ] `POST /api/checkout` does not exist yet. Payability is tested, but there is no HTTP route.
- [ ] `POST /api/checkout/{id}/confirm` does not exist yet.
- [ ] `GET /api/public/receipts/{share_id}` does not exist yet.
- [ ] The frozen request is `{ session_id, listing_id, mandate: { max_amount_cents, currency, expires_in_seconds } }`. This branch still sends a flat cap.
- [ ] The frozen 201 body uses `checkout_id`, `merchant`, `trust_snapshot`, and `passkey_challenge`. This branch still expects `id` and a smaller mandate.
- [ ] Confirm sends `{ passkey_assertion: { credential_id, client_data }, idempotency_key }`. `client_data: "fail"` must show the decline inline.
- [ ] A 200 confirm returns `receipt_url` like `/r/shr_abc`. The receipt page then loads that share id.

## Layout, after the live payload is on screen

- [ ] Long titles stay inside the card.
- [ ] A missing image keeps the letter placeholder.
- [ ] Nine cards, not eight, still fit without horizontal scroll.
- [ ] The best pick from the live run is `lst_tgt_bsp` at $179.99, not the mock Best Buy $249.00.
- [ ] The villain `lst_vln_xm5` renders danger with the local-denylist reason.

## Not started

No frontend files were changed for this block. Coding it on this branch would overwrite the live client already on main.
