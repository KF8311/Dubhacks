import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { PayPage } from "./PayPage.tsx"

beforeEach(() => {
  window.history.replaceState({}, "", "/?mock=1")
})

test("reads the checkout and shows what the phone is about to pay", async () => {
  render(<PayPage checkoutId="chk_mock" />)
  expect(await screen.findByRole("heading", { name: /pay on this phone/i })).toBeInTheDocument()
  expect(await screen.findByText(/Sandbox — simulated Visa Intelligent Commerce flow/)).toBeInTheDocument()
  expect(await screen.findByText(/Best Buy ·/)).toBeInTheDocument()
})

test("approving the passkey opens the shared receipt", async () => {
  render(<PayPage checkoutId="chk_mock" />)
  const pay = await screen.findByRole("button", { name: /approve with passkey/i })
  fireEvent.click(pay)
  await waitFor(() => expect(window.location.pathname).toBe("/r/shr_mock"))
})

test("an unknown checkout id explains that the link is not available", async () => {
  window.history.replaceState({}, "", "/")
  globalThis.fetch = (async () =>
    ({
      ok: false,
      status: 404,
      statusText: "",
      json: async () => ({
        error: { code: "CHECKOUT_NOT_FOUND", message: "Checkout not found.", details: {} },
      }),
    }) as Response) as typeof fetch

  render(<PayPage checkoutId="chk_missing" />)
  const alert = await screen.findByRole("alert")
  expect(alert).toHaveTextContent(/not available/i)
  expect(alert).toHaveTextContent(/Checkout not found/i)
})
