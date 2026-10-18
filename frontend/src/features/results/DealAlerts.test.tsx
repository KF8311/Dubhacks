import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, test, vi } from "vitest"

import { DealAlerts } from "@/features/results/DealAlerts.tsx"
import { getPhoneOptIn, startPhoneOptIn } from "@/lib/phoneBridge.ts"

vi.mock("@/lib/phoneBridge.ts", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/phoneBridge.ts")>()
  return {
    ...actual,
    startPhoneOptIn: vi.fn(),
    getPhoneOptIn: vi.fn(),
  }
})

const start = vi.mocked(startPhoneOptIn)
const check = vi.mocked(getPhoneOptIn)

async function askToOptIn(number = "+14155550123") {
  fireEvent.change(screen.getByLabelText(/your phone number/i), {
    target: { value: number },
  })
  fireEvent.click(screen.getByRole("button", { name: /text me/i }))
  await waitFor(() => expect(start).toHaveBeenCalledWith(number))
}

beforeEach(() => {
  vi.clearAllMocks()
  start.mockResolvedValue({ request_id: "req_1", status: "pending" })
  check.mockResolvedValue({ request_id: "req_1", status: "pending" })
})

describe("DealAlerts", () => {
  test("asks the bridge to text the number the shopper typed", async () => {
    render(<DealAlerts />)

    await askToOptIn()

    expect(await screen.findByText(/reply y to turn alerts on/i)).toBeInTheDocument()
  })

  test("shows the masked number once the reply confirms consent", async () => {
    check.mockResolvedValue({ request_id: "req_1", status: "confirmed" })
    render(<DealAlerts />)

    await askToOptIn()

    await waitFor(() => expect(screen.getByText(/on for ••••0123/i)).toBeInTheDocument())
    expect(screen.getByText(/send/i)).toBeInTheDocument()
  })

  test("does not claim consent when the shopper replies no", async () => {
    check.mockResolvedValue({ request_id: "req_1", status: "declined" })
    render(<DealAlerts />)

    await askToOptIn()

    expect(await screen.findByText(/no alerts will be sent/i)).toBeInTheDocument()
  })

  test("asks for the country code before calling the bridge", async () => {
    render(<DealAlerts />)

    fireEvent.change(screen.getByLabelText(/your phone number/i), {
      target: { value: "555-0123" },
    })
    fireEvent.click(screen.getByRole("button", { name: /text me/i }))

    expect(await screen.findByRole("alert")).toHaveTextContent(/country code/i)
    expect(start).not.toHaveBeenCalled()
  })

  test("surfaces a bridge failure instead of pretending the text went out", async () => {
    start.mockRejectedValue(new Error("Could not reach the phone bridge."))
    render(<DealAlerts />)

    await askToOptIn()

    expect(await screen.findByRole("alert")).toHaveTextContent(/could not reach/i)
  })
})
