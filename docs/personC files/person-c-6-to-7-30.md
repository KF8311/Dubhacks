# Person C — 6:00–7:30 checklist

Done when a mocked checkout on the trusted Best Buy listing ends on a receipt in the browser. Pay stays disabled for caution and danger. This block does not call the real checkout API.

## Task 25 — checkout

- [x] Pay is enabled only when the verdict is `trusted`, the score is at least 70, and confidence is at least 0.6.
- [x] The sheet shows the merchant, the amount in dollars, the trust snapshot, and the full sandbox line: “Sandbox — simulated Visa Intelligent Commerce flow.”
- [x] Pay calls the mock `createCheckout` with the session id, listing id, and cap in cents.
- [x] `MandateCard` shows the merchant, the cap, and the expiry, then continues.
- [x] `PasskeyDialog` is a simulated biometric. Confirm sends a passing assertion. A second action sends `client_data: "fail"`.
- [x] A failed confirm shows the server message inline and does not open the receipt.
- [x] `ProcessingState` shows three steps: tokenizing, authorizing, capturing. Then the receipt opens.

## Task 26 — receipt

- [x] `ReceiptView` shows a score ring, the merchant, the amount, and token last4.
- [x] Verified and unverified check names are listed separately.
- [x] The issued time and “What this receipt proves” are visible.
- [x] Copy link copies `/r/{share_id}`.
- [x] The same sandbox line is on the receipt.
- [x] `/r/:shareId` loads a mock receipt. An unknown id shows a not-found state.
- [x] No new package. Routing is a path check, not React Router.

## Not this block

The real `POST /api/checkout` and `/confirm` stay at 7:30. Contrast, focus, and the 1024px layout stay at 9:00.
