import { render, screen } from "@testing-library/react"
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
  expect(screen.getByText("Sony XM5")).toBeInTheDocument()
  expect(screen.getByText("Best Buy")).toBeInTheDocument()
  expect(screen.getByText(/\$249\.00/)).toBeInTheDocument()
})
