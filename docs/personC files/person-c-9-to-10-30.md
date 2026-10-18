# Person C — 9:00–10:30 checklist

Done when the four demo screens are captured, text meets WCAG AA on white, keyboard focus is visible, the layout holds at 1024px, and reduced motion skips the purge fade.

The 7:30 live checkout stays blocked. `POST /api/checkout` is still not on the server.

## Screenshots for the Devpost draft

- [x] Results grid, with the best pick visible.
- [x] One trust card, showing the verdict and the check rows.
- [x] Checkout, with the sandbox line and Pay.
- [x] Receipt, with the score, amount, and verified list.

## Contrast, focus, and 1024px

- [x] Trust badge colors stay at least 4.5:1. They already measure about 8:1.
- [x] Merchant domains and unfinished processing steps move off `stone-400` (2.5:1) onto `stone-600`.
- [x] Buttons, links, and inputs show a solid green focus outline.
- [x] The header and the results title wrap instead of overflowing at 1024px.
- [x] Cards can shrink, so a long title does not force a horizontal scrollbar.

## Reduced motion

- [x] `prefers-reduced-motion: reduce` skips the purge fade and finishes immediately.
