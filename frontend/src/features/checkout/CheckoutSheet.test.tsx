import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { CheckoutSheet } from "./CheckoutSheet.tsx"

beforeEach(() => {
  window.history.replaceState({}, "", "/?mock=1")
})

const listing = {
  id: "lst_1",
  title: "Sony XM5",
  price_cents: 24900,
  currency: "USD",
  merchant_name: "Best Buy",
  merchant_domain: "bestbuy.com",
  image_url: "",
  product_url: "",
  source: "catalog" as const,
}

test("disables pay for caution", () => {
  render(
    <CheckoutSheet
      listing={listing}
      verdict="caution"
      score={50}
      confidence={0.9}
      onComplete={() => undefined}
    />,
  )
  expect(screen.getByRole("button", { name: /pay/i })).toBeDisabled()
})

test("enables pay for trusted", () => {
  render(
    <CheckoutSheet
      listing={listing}
      verdict="trusted"
      score={92}
      confidence={0.9}
      onComplete={() => undefined}
    />,
  )
  expect(screen.getByRole("button", { name: /pay/i })).toBeEnabled()
  expect(screen.getByText(/Sandbox — simulated Visa Intelligent Commerce flow/)).toBeInTheDocument()
})

test("trusted checkout reaches the receipt", async () => {
  const onComplete = vi.fn()
  render(
    <CheckoutSheet
      listing={{ ...listing, id: "lst_bestbuy_xm5" }}
      verdict="trusted"
      score={92}
      confidence={1}
      sessionId="ses_mock"
      onComplete={onComplete}
    />,
  )
  fireEvent.click(screen.getByRole("button", { name: /^pay$/i }))
  expect(await screen.findByRole("heading", { name: /mandate/i })).toBeInTheDocument()
  fireEvent.click(screen.getByRole("button", { name: /continue/i }))
  fireEvent.click(await screen.findByRole("button", { name: /confirm with passkey/i }))
  expect(await screen.findByText(/capturing/i)).toBeInTheDocument()
  await waitFor(() => expect(onComplete).toHaveBeenCalled(), { timeout: 3000 })
})

test("a failed passkey stays on the error", async () => {
  const onComplete = vi.fn()
  render(
    <CheckoutSheet
      listing={{ ...listing, id: "lst_bestbuy_xm5" }}
      verdict="trusted"
      score={92}
      confidence={1}
      sessionId="ses_mock"
      onComplete={onComplete}
    />,
  )
  fireEvent.click(screen.getByRole("button", { name: /^pay$/i }))
  fireEvent.click(await screen.findByRole("button", { name: /continue/i }))
  fireEvent.click(await screen.findByRole("button", { name: /simulate a failed passkey/i }))
  expect(await screen.findByRole("alert")).toHaveTextContent(/payment declined/i)
  expect(onComplete).not.toHaveBeenCalled()
})
