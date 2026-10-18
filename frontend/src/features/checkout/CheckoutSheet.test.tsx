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

test("disables pay when there is no session id", () => {
  render(
    <CheckoutSheet
      listing={listing}
      verdict="trusted"
      score={92}
      confidence={0.9}
      onComplete={() => undefined}
    />,
  )
  expect(screen.getByRole("button", { name: /pay/i })).toBeDisabled()
})

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

test("enables pay for an allowlisted trusted merchant with a zero score", () => {
  render(
    <CheckoutSheet
      listing={listing}
      verdict="trusted"
      score={0}
      confidence={1}
      allowlisted
      sessionId="ses_1"
      onComplete={() => undefined}
    />,
  )
  expect(screen.getByRole("button", { name: /pay/i })).toBeEnabled()
  expect(screen.getByText(/Verified · Trusted/)).toBeInTheDocument()
})

test("keeps pay disabled when a non-allowlisted score is below 70", () => {
  render(
    <CheckoutSheet
      listing={listing}
      verdict="trusted"
      score={0}
      confidence={1}
      sessionId="ses_1"
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
      sessionId="ses_1"
      onComplete={() => undefined}
    />,
  )
  expect(screen.getByRole("button", { name: /pay/i })).toBeEnabled()
  expect(screen.getByText(/Sandbox — simulated Visa Intelligent Commerce flow/)).toBeInTheDocument()
})

test("enables pay for an allowlisted trusted listing even at score 0", () => {
  render(
    <CheckoutSheet
      listing={listing}
      verdict="trusted"
      score={0}
      confidence={1}
      allowlisted
      sessionId="ses_1"
      onComplete={() => undefined}
    />,
  )
  expect(screen.getByRole("button", { name: /pay/i })).toBeEnabled()
})

test("keeps pay disabled for score 0 when not allowlisted", () => {
  render(
    <CheckoutSheet
      listing={listing}
      verdict="trusted"
      score={0}
      confidence={1}
      sessionId="ses_1"
      onComplete={() => undefined}
    />,
  )
  expect(screen.getByRole("button", { name: /pay/i })).toBeDisabled()
})

test("the mandate offers a link to finish payment on a phone", async () => {
  render(
    <CheckoutSheet
      listing={{ ...listing, id: "lst_bestbuy_xm5" }}
      verdict="trusted"
      score={92}
      confidence={1}
      sessionId="ses_mock"
      onComplete={() => undefined}
    />,
  )
  fireEvent.click(screen.getByRole("button", { name: /^pay$/i }))
  expect(await screen.findByText(/pay on your phone/i)).toBeInTheDocument()
  expect(screen.getByTestId("pay-url")).toHaveTextContent("/pay/chk_mock")
})

test("the review texts the pay link to the phone", async () => {
  const original = globalThis.fetch
  const calls: { url: string; body: string }[] = []
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), body: String(init?.body ?? "") })
    return { ok: true, status: 200, json: async () => ({ ok: true }) } as Response
  }) as typeof fetch

  try {
    render(
      <CheckoutSheet
        listing={{ ...listing, id: "lst_bestbuy_xm5" }}
        verdict="trusted"
        score={92}
        confidence={1}
        sessionId="ses_mock"
        onComplete={() => undefined}
      />,
    )
    fireEvent.click(screen.getByRole("button", { name: /send to phone/i }))
    expect(await screen.findByText(/sent to your phone/i)).toBeInTheDocument()
    expect(screen.queryByTestId("pay-url")).not.toBeInTheDocument()
    const sent = calls.find((call) => call.url.endsWith("/send"))
    expect(sent).toBeDefined()
    expect(sent?.body).toContain("/pay/chk_mock")
  } finally {
    globalThis.fetch = original
  }
})

test("keeps the copyable link when the phone bridge is down", async () => {
  const original = globalThis.fetch
  globalThis.fetch = (async () => {
    throw new Error("bridge offline")
  }) as typeof fetch

  try {
    render(
      <CheckoutSheet
        listing={{ ...listing, id: "lst_bestbuy_xm5" }}
        verdict="trusted"
        score={92}
        confidence={1}
        sessionId="ses_mock"
        onComplete={() => undefined}
      />,
    )
    fireEvent.click(screen.getByRole("button", { name: /send to phone/i }))
    expect(await screen.findByText(/could not text your phone/i)).toBeInTheDocument()
    expect(screen.getByTestId("pay-url")).toHaveTextContent("/pay/chk_mock")
  } finally {
    globalThis.fetch = original
  }
})

test("send to phone stays disabled when the listing cannot be paid", () => {
  render(
    <CheckoutSheet
      listing={listing}
      verdict="danger"
      score={10}
      confidence={1}
      sessionId="ses_1"
      onComplete={() => undefined}
    />,
  )
  expect(screen.getByRole("button", { name: /send to phone/i })).toBeDisabled()
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

test("a server refusal shows its PayabilityCode", async () => {
  window.history.replaceState({}, "", "/")
  globalThis.fetch = (async () =>
    ({
      ok: false,
      status: 409,
      statusText: "",
      json: async () => ({
        error: {
          code: "MERCHANT_NOT_TRUSTED",
          message: "This merchant did not pass the trust checks.",
          details: { verdict: "danger" },
        },
      }),
    }) as Response) as typeof fetch

  render(
    <CheckoutSheet
      listing={listing}
      verdict="trusted"
      score={92}
      confidence={1}
      sessionId="ses_1"
      onComplete={() => undefined}
    />,
  )
  fireEvent.click(screen.getByRole("button", { name: /^pay$/i }))

  const alert = await screen.findByRole("alert")
  expect(alert).toHaveTextContent(/MERCHANT_NOT_TRUSTED/)
  expect(alert).toHaveTextContent(/did not pass the trust checks/i)
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
