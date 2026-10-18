import { render, screen } from "@testing-library/react"
import { ProductCard } from "./ProductCard.tsx"
import type { TrustCheckResult } from "@/lib/types.ts"

const listing = {
  id: "lst_1",
  title: "Sony WH-1000XM5",
  price_cents: 24900,
  currency: "USD",
  merchant_name: "Best Buy",
  merchant_domain: "bestbuy.com",
  image_url: "",
  product_url: "",
  source: "catalog" as const,
}

test("a listing above the stated budget is labelled", () => {
  render(
    <ProductCard listing={listing} checks={[]} score={undefined} isBest={false} budgetMaxCents={15000} />,
  )
  expect(screen.getByText("Above your budget")).toBeInTheDocument()
})

test("a listing below a typed range is labelled", () => {
  render(
    <ProductCard
      listing={listing}
      checks={[]}
      score={undefined}
      isBest={false}
      budgetMinCents={100000}
      budgetMaxCents={120000}
    />,
  )
  expect(screen.getByText("Below your budget")).toBeInTheDocument()
})

test("links the listing to the merchant page", () => {
  render(
    <ProductCard
      listing={{ ...listing, product_url: "https://www.bestbuy.com/site/sony-xm5" }}
      checks={[]}
      isBest={false}
    />,
  )
  const link = screen.getByRole("link", { name: /view at bestbuy\.com/i })
  expect(link).toHaveAttribute("href", "https://www.bestbuy.com/site/sony-xm5")
  expect(link).toHaveAttribute("target", "_blank")
  expect(link).toHaveAttribute("rel", "noopener noreferrer")
})

test("omits the link when the listing has no product url", () => {
  render(<ProductCard listing={listing} checks={[]} isBest={false} />)
  expect(screen.queryByRole("link")).not.toBeInTheDocument()
})

test("leads with a compact ticket, not a hero photo", () => {
  render(
    <ProductCard
      listing={{ ...listing, image_url: "https://example.com/xm5.jpg" }}
      checks={[]}
      isBest={false}
    />,
  )
  const photo = document.querySelector("img")
  expect(photo).toHaveClass("size-10")
  const title = screen.getByText("Sony WH-1000XM5")
  expect(photo && title.compareDocumentPosition(photo) & Node.DOCUMENT_POSITION_PRECEDING).toBeTruthy()
})

test("a collapsed ticket hides the check list", () => {
  render(<ProductCard listing={listing} checks={[]} isBest={false} />)
  expect(document.querySelectorAll("[data-slot='skeleton']")).toHaveLength(0)
})

test("a missing check stays a skeleton row", () => {
  render(<ProductCard listing={listing} checks={[]} isBest={false} expanded />)
  expect(screen.getAllByRole("generic").length).toBeGreaterThan(0)
  expect(document.querySelectorAll("[data-slot='skeleton']")).toHaveLength(5)
  expect(screen.queryByText("Domain age")).not.toBeInTheDocument()
})

const checks: TrustCheckResult[] = [
  {
    id: "domain_age",
    name: "Domain age",
    status: "passed",
    severity: 0,
    summary: "Registered in 1998.",
    evidence: [],
    source: "live",
    duration_ms: 12,
  },
  {
    id: "ssl_cert",
    name: "SSL certificate",
    status: "warning",
    severity: 0.5,
    summary: "Certificate expires soon.",
    evidence: [],
    source: "live",
    duration_ms: 9,
  },
  {
    id: "safe_browsing",
    name: "Safe Browsing",
    status: "failed",
    severity: 1,
    summary: "Flagged.",
    evidence: [],
    source: "live",
    duration_ms: 8,
  },
]

test("only the best pick wears the marigold edge", () => {
  const { container, rerender } = render(
    <ProductCard listing={listing} checks={[]} isBest={false} selected onSelect={() => undefined} />,
  )
  const card = container.querySelector("[data-slot='card']")
  expect(card).not.toHaveClass("ticket-best")
  expect(card).toHaveClass("ticket-selected")

  rerender(<ProductCard listing={listing} checks={[]} isBest selected onSelect={() => undefined} />)
  expect(card).toHaveClass("ticket-best")
  expect(card).not.toHaveClass("ticket-selected")
})

test("the row never flips and keeps the merchant link beside it", () => {
  const { container } = render(
    <ProductCard
      listing={{ ...listing, product_url: "https://www.bestbuy.com/site/sony-xm5" }}
      checks={[]}
      isBest={false}
      onSelect={() => undefined}
    />,
  )
  expect(container.querySelector(".flip-card")).toBeNull()
  expect(container.querySelector(".flip-inner")).toBeNull()
  expect(screen.getByRole("link", { name: /view at bestbuy\.com/i })).toHaveAttribute(
    "href",
    "https://www.bestbuy.com/site/sony-xm5",
  )
})

test("the tally sits on the row, no flip required", () => {
  render(
    <ProductCard
      listing={listing}
      checks={checks}
      score={{
        score: 45,
        verdict: "caution",
        confidence: 0.8,
        penalties: [],
        fatal_flags: [],
        top_reason: "One check failed.",
        scoring_version: "1.0",
      }}
      isBest={false}
    />,
  )
  expect(screen.getByText("1 passed · 1 warning · 1 failed")).toBeInTheDocument()
})

test("a pending row says checks are still running", () => {
  render(<ProductCard listing={listing} checks={[]} isBest={false} />)
  expect(screen.getByText("Checks running…")).toBeInTheDocument()
})
