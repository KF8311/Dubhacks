import { fireEvent, render, screen } from "@testing-library/react"
import { ResultsGrid } from "./ResultsGrid.tsx"

test("renders title, merchant, and formatted price", () => {
  render(
    <ResultsGrid
      listings={[
        {
          id: "lst_1",
          title: "Sony XM5",
          price_cents: 24900,
          currency: "USD",
          merchant_name: "Best Buy",
          merchant_domain: "bestbuy.com",
          image_url: "",
          product_url: "",
          source: "catalog",
        },
      ]}
      checks={{}}
      scores={{}}
    />,
  )
  expect(screen.getAllByText("Sony XM5").length).toBeGreaterThan(0)
  expect(screen.getAllByText(/Best Buy/).length).toBeGreaterThan(0)
  expect(screen.getAllByText(/\$249\.00/).length).toBeGreaterThan(0)
})

test("picking an item slides its site stats over and back", () => {
  render(
    <ResultsGrid
      listings={[
        {
          id: "lst_1",
          title: "Sony XM5",
          price_cents: 24900,
          currency: "USD",
          merchant_name: "Best Buy",
          merchant_domain: "bestbuy.com",
          image_url: "",
          product_url: "",
          source: "catalog",
        },
        {
          id: "lst_2",
          title: "Bose QC",
          price_cents: 32900,
          currency: "USD",
          merchant_name: "Amazon",
          merchant_domain: "amazon.com",
          image_url: "",
          product_url: "",
          source: "catalog",
        },
      ]}
      checks={{}}
      scores={{}}
    />,
  )
  const track = document.querySelector("[data-view]")
  expect(track).toHaveAttribute("data-view", "items")
  expect(document.querySelectorAll("[data-slot='skeleton']")).toHaveLength(0)

  fireEvent.click(screen.getByRole("button", { name: /show checks for bose qc/i }))
  expect(track).toHaveAttribute("data-view", "stats")
  expect(track?.className).toContain("-translate-x-1/2")
  expect(screen.getAllByText("Bose QC").length).toBeGreaterThan(1)
  expect(document.querySelectorAll("[data-slot='skeleton']")).toHaveLength(5)

  fireEvent.click(screen.getByRole("button", { name: /back to items/i }))
  expect(track).toHaveAttribute("data-view", "items")
  expect(document.querySelectorAll("[data-slot='skeleton']")).toHaveLength(0)
})
