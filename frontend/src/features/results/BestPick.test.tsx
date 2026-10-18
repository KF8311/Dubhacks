import { render, screen } from "@testing-library/react"
import { BestPick } from "./BestPick.tsx"

test("shows the best pick and savings", () => {
  render(
    <BestPick
      recommendation={{
        recommended_listing_id: "lst_1",
        median_trusted_cents: 26000,
        savings_cents: 1100,
        eligible_ids: ["lst_1"],
        reason: "cheapest trusted",
        no_trusted_option: false,
        narrative: "Target is the cheapest trusted XM5.",
      }}
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
    />,
  )
  expect(screen.getByText(/Sony XM5/)).toHaveClass("break-words")
  expect(screen.getByText(/\$11\.00/)).toBeInTheDocument()
  expect(screen.getByText(/Target is the cheapest trusted XM5/)).toBeInTheDocument()
})
