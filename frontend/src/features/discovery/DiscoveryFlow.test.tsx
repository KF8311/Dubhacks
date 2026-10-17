import { fireEvent, render, screen } from "@testing-library/react"
import { DiscoveryFlow } from "./DiscoveryFlow.tsx"

test("renders questions and submits", async () => {
  render(<DiscoveryFlow onStarted={() => undefined} />)
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "headphones" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))
  expect(await screen.findByText(/what's your ceiling/i)).toBeInTheDocument()
})
