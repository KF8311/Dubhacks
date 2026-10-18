import { render, screen } from "@testing-library/react"
import { ReceiptPage, ReceiptView } from "./ReceiptPage.tsx"

beforeEach(() => {
  window.history.replaceState({}, "", "/?mock=1")
})

const receipt = {
  id: "rcp_1",
  share_id: "shr_1",
  checkout_id: "chk_1",
  transaction_id: "txn_1",
  listing: {
    id: "lst_1",
    title: "Sony XM5",
    price_cents: 24900,
    currency: "USD",
    merchant_name: "Best Buy",
    merchant_domain: "bestbuy.com",
    image_url: "",
    product_url: "",
    source: "catalog" as const,
  },
  investigation_snapshot: {
    id: "inv_1",
    listing_id: "lst_1",
    session_id: "ses_1",
    checks: [],
    score: {
      score: 92,
      verdict: "trusted" as const,
      confidence: 0.9,
      penalties: [],
      fatal_flags: [],
      top_reason: "ok",
      scoring_version: "1.0",
    },
    allowlisted: false,
    duration_ms: 1,
    created_at: "",
  },
  amount_cents: 24900,
  currency: "USD",
  token_last4: "4242",
  verified: ["Domain age", "SSL", "Safe Browsing"],
  unverified: ["Reddit"],
  issued_at: "2026-10-17T18:00:00.000Z",
  signature: "",
}

test("renders score and amount", () => {
  render(<ReceiptView receipt={receipt} />)
  expect(screen.getByText(/92/)).toBeInTheDocument()
  expect(screen.getByText(/\$249\.00/)).toBeInTheDocument()
  expect(screen.getByText(/4242/)).toBeInTheDocument()
  expect(screen.getByText("Domain age")).toBeInTheDocument()
  expect(screen.getByText("Reddit")).toBeInTheDocument()
})

test("an allowlisted receipt says verified instead of score zero", () => {
  render(
    <ReceiptView
      receipt={{
        ...receipt,
        investigation_snapshot: {
          ...receipt.investigation_snapshot,
          allowlisted: true,
          score: { ...receipt.investigation_snapshot.score, score: 0, allowlisted: true },
        },
      }}
    />,
  )
  expect(screen.getByRole("img", { name: "Verified" })).toBeInTheDocument()
  expect(screen.queryByLabelText("Score 0")).not.toBeInTheDocument()
})

test("unknown share id shows not found", async () => {
  render(<ReceiptPage shareId="missing" />)
  expect(await screen.findByText(/not found/i)).toBeInTheDocument()
})
