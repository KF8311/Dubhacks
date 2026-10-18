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

test("a skipped check says it could not be verified", () => {
  render(
    <CheckRow
      check={{ ...check, status: "skipped", summary: "Allowlisted merchant; checks skipped." }}
      listingId="lst_1"
    />,
  )
  expect(screen.getByText("Could not verify")).toBeInTheDocument()
  expect(screen.queryByText("Skipped")).not.toBeInTheDocument()
})

test("explain button asks the API and shows the sentence", async () => {
  useSessionStore.setState({ sessionId: "ses_1" })
  globalThis.fetch = (async () =>
    ({
      ok: true,
      status: 200,
      json: async () => ({
        explanation: "The cert is valid and issued to the merchant.",
        source: "gemini",
      }),
    }) as Response) as typeof fetch

  render(<CheckRow check={check} listingId="lst_1" />)
  await userEvent.click(screen.getByRole("button", { name: "Explain" }))
  expect(await screen.findByText(/issued to the merchant/)).toBeInTheDocument()
  expect(screen.getByText("AI-generated")).toBeInTheDocument()
  useSessionStore.getState().reset()
})

test("a template explanation is labelled as evidence, never as AI", async () => {
  useSessionStore.setState({ sessionId: "ses_1" })
  globalThis.fetch = (async () =>
    ({
      ok: true,
      status: 200,
      json: async () => ({ explanation: "Valid certificate.", source: "template" }),
    }) as Response) as typeof fetch

  render(<CheckRow check={check} listingId="lst_1" />)
  await userEvent.click(screen.getByRole("button", { name: "Explain" }))
  expect(await screen.findByText("From evidence")).toBeInTheDocument()
  expect(screen.queryByText("AI-generated")).not.toBeInTheDocument()
  useSessionStore.getState().reset()
})
