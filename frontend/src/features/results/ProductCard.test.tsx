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

test("the shelf ticket shows a product photo", () => {
  render(
    <ProductCard
      listing={{ ...listing, image_url: "https://example.com/xm5.jpg" }}
      checks={[]}
      isBest={false}
    />,
  )
  const photo = document.querySelector("img.listing-photo")
  expect(photo).toHaveAttribute("src", "https://example.com/xm5.jpg")
})

test("the counter card shows a large product photo", () => {
  render(
    <ProductCard
      listing={{ ...listing, image_url: "https://example.com/xm5.jpg" }}
      checks={[]}
      isBest={false}
      expanded
    />,
  )
  expect(document.querySelector("img.listing-photo-hero")).toHaveAttribute(
    "src",
    "https://example.com/xm5.jpg",
  )
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
