import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { CheckRow } from "./CheckRow.tsx"
import { useSessionStore } from "@/store/sessionStore.ts"

const check = {
  id: "ssl_cert" as const,
  name: "SSL certificate",
  status: "passed" as const,
  severity: 0,
  summary: "Valid certificate.",
  evidence: [],
  source: "live" as const,
  duration_ms: 1,
}

test("explain button asks the API and shows the sentence", async () => {
  useSessionStore.setState({ sessionId: "ses_1" })
  globalThis.fetch = (async () =>
    ({
      ok: true,
      status: 200,
      json: async () => ({ explanation: "The cert is valid and issued to the merchant." }),
    }) as Response) as typeof fetch

  render(<CheckRow check={check} listingId="lst_1" />)
  await userEvent.click(screen.getByRole("button", { name: "Explain" }))
  expect(await screen.findByText(/issued to the merchant/)).toBeInTheDocument()
  useSessionStore.getState().reset()
})
