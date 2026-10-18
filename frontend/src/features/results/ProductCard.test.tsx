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
  expect(photo).toHaveClass("size-16")
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
