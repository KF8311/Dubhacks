---
title: VEYZL audit
type: audit
updated: 2026-10-17
owner: B
status: awaiting tool access
---

# VEYZL audit

Task 29 requires a real audit that finds a missing control, the fix, and evidence. This file records the scope, the method, and the result. **Nothing here is a finding until it is reproduced and written up in §Results.**

## Status

**Blocked on access.** The repository contains no reference to VEYZL beyond the task name: no URL, no CLI, no credential, no config. Web search returns nothing for the name. Needed from the team before this can proceed:

- [ ] What VEYZL is and where it came from (mentor, sponsor table, Discord, event page)
- [ ] How to run it: CLI command, install instructions, or dashboard URL
- [ ] Access: an account, an API key, or a GitHub App install
- [ ] Scope: does it scan the GitHub repo, the local tree, or the deployed URL?
- [ ] Output: a dashboard, a JSON report, or a PR comment

## Scope

The payment path and its controls, because that is where the product's claim lives:

| Surface | Why it is in scope |
|---|---|
| `POST /api/checkout` | Creates a spending mandate |
| `POST /api/checkout/{checkout_id}/confirm` | Captures money; trusts the passkey assertion |
| `POST /api/demo/reset` | Destructive, unauthenticated in demo mode |
| `app/payments/receipts.py` | Signs and verifies the public receipt |
| `app/payments/payability.py` | The gate itself |
| `app/checks/page_flags.py` | Fetches a remote URL server-side |
| `app/core/config.py` | Defaults that ship to production |

## Candidate controls to test

These are **hypotheses from a read of the code**, not findings. Each is cheap to confirm or clear.

| # | Hypothesis | Where | Why it matters |
|---|---|---|---|
| 1 | The receipt signing secret defaults to a known constant (`dev-only-change-me`), so a receipt can be forged when the env var is unset | `app/core/config.py`, `app/payments/receipts.py` | A "public trust signal" that anyone can mint is not a signal |
| 2 | `POST /api/demo/reset` is reachable without authentication whenever `demo_mode` is on — and `demo_mode` defaults to `on` | `app/api/routes_health.py:40` | One unauthenticated request destroys every session and receipt |
| 3 | The mandate cap is chosen by the client; the server validates the amount against it but has no independent ceiling | `app/api/routes_checkout.py`, `MandateDraft` | A caller can authorize an arbitrarily large spend |
| 4 | The passkey is asserted by the same client that requests the charge, with only `client_data == "fail"` distinguishing a decline | `routes_checkout.py` confirm | There is no second factor; the "human" is the client |
| 5 | Server-side page fetch | `app/checks/page_flags.py` uses `validate_public_url` | Confirm the guard covers redirects and DNS rebinding, not just the first hop |
| 6 | No rate limit on session creation or checkout | `app/api/` | Resource exhaustion and scripted enumeration |

If VEYZL reports something outside this list, the tool's finding wins — this table is a starting point, not a filter.

## Method

1. Run the audit against the scope above and capture the raw report.
2. Reproduce the top finding by hand (a request, a test, or a script). **An unreproduced finding is not a finding.**
3. Write a failing test that demonstrates the gap.
4. Fix it.
5. Re-run the audit and the test; record before/after.
6. Note what was deliberately **not** fixed and why (prototype scope).

## Results

_Empty until the audit runs._

### Finding 1

- **What:**
- **Where:**
- **Reproduction:**
- **Impact:**
- **Fix:**
- **Before / after evidence:**
- **Test that now pins it:**

## Not fixed, on purpose

Record every accepted risk here so the omission is a decision, not an oversight.

- The passkey is simulated. The production control is Visa Payment Passkey; the prototype shows the consent moment, not the cryptography.
- Payment is mock VIC. No Visa network call exists.
- The store is in memory; restarting loses receipts.

## Sign-off

- [ ] One finding reproduced and fixed
- [ ] A test pins the fix
- [ ] The audit doc names the finding, the fix, and the evidence
- [ ] `docs/status.md` updated
