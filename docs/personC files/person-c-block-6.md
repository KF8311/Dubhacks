# Person C — Block 6 checklist

Block 6 is 10:30 PM–2:00 AM. Person C's piece is phone-width reflow, loading and error states, and the `?mock=1` fallback. Mongo and the feature freeze are not this checklist.

Done when a 390px-wide screen shows the search, results, checkout, and receipt without sideways scrolling, a failed search or a missing receipt says what went wrong, and `?mock=1` finishes the demo with the API ignored.

## Loading and error states

- [x] "Looking at retailers…" uses skeleton rows while answers are submitting.
- [x] Results say "Checking listings…" until the first card arrives.
- [x] A missing check on a card is a skeleton row.
- [x] Find products shows an alert and stays on the search screen when the API is unreachable.
- [x] A session error shows the dismissible banner.
- [x] An unknown `/r/:shareId` says "Receipt not found."
- [x] A failed passkey shows the decline and does not open the receipt.

## `?mock=1` fallback

- [x] `?mock=1` runs discovery, the animated checks, the best pick, purge, and checkout without calling the API.
- [x] The sandbox sentence is on the header, checkout, and receipt.

## Phone width (390px)

- [x] Search, results, checkout, and receipt do not scroll sideways. Measured overflow 0.
- [x] The results grid is one column (342px).
- [x] The sandbox label wraps instead of clipping.
- [x] The receipt title sits beside the score without pushing the page wider. Titles use `break-words`.
