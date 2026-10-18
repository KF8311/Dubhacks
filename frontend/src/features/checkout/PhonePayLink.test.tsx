import { fireEvent, render, screen } from "@testing-library/react"
import { PhonePayLink, payUrl } from "./PhonePayLink.tsx"

test("shows the absolute pay link for this device's origin", () => {
  render(<PhonePayLink checkoutId="chk_123" />)
  expect(screen.getByTestId("pay-url")).toHaveTextContent(payUrl("chk_123"))
  expect(screen.getByTestId("pay-url")).toHaveTextContent(/\/pay\/chk_123$/)
})

test("copying the link confirms it landed on the clipboard", async () => {
  const writeText = vi.fn().mockResolvedValue(undefined)
  Object.defineProperty(navigator, "clipboard", {
    value: { writeText },
    configurable: true,
  })
  render(<PhonePayLink checkoutId="chk_123" />)
  fireEvent.click(screen.getByRole("button", { name: /copy link/i }))
  expect(await screen.findByText("Copied.")).toBeInTheDocument()
  expect(writeText).toHaveBeenCalledWith(payUrl("chk_123"))
})
