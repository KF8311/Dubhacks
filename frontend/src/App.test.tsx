import { fireEvent, render, screen } from "@testing-library/react"
import App from "./App.tsx"

test("renders the app shell", () => {
  render(<App />)
  expect(screen.getByText(/sniff/i)).toBeInTheDocument()
  expect(screen.getByText(/sandbox — simulated visa flow/i)).toBeInTheDocument()
})

test("walks discovery into the mock results", async () => {
  render(<App />)
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "headphones" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))
  expect(await screen.findByText(/what's your ceiling/i)).toBeInTheDocument()
  fireEvent.click(screen.getByRole("button", { name: /\$150–\$300/i }))
  fireEvent.click(screen.getByRole("button", { name: /^next$/i }))
  fireEvent.click(screen.getByRole("button", { name: /lowest trusted price/i }))
  fireEvent.click(screen.getByRole("button", { name: /^next$/i }))
  fireEvent.click(screen.getByRole("button", { name: /^travel$/i }))
  fireEvent.click(screen.getByRole("button", { name: /see results/i }))
  expect(await screen.findByText("$249.00", {}, { timeout: 3000 })).toBeInTheDocument()
  expect(screen.getAllByText("Sony WH-1000XM5").length).toBeGreaterThan(1)
  expect(screen.getByText(/92\s*·\s*Trusted/)).toBeInTheDocument()
  expect(screen.getByText(/12\s*·\s*Danger/)).toBeInTheDocument()
  expect(screen.getByText("Best pick")).toBeInTheDocument()
})
