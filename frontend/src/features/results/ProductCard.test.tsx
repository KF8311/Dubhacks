import { render, screen } from "@testing-library/react"
import { ProductCard } from "./ProductCard.tsx"

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

test("a missing check stays a skeleton row", () => {
  render(<ProductCard listing={listing} checks={[]} isBest={false} />)
  expect(screen.getAllByRole("generic").length).toBeGreaterThan(0)
  expect(document.querySelectorAll("[data-slot='skeleton']")).toHaveLength(5)
  expect(screen.queryByText("Domain age")).not.toBeInTheDocument()
})
