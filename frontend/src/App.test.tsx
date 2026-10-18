import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import App from "./App.tsx"
import { useSessionStore } from "@/store/sessionStore.ts"

beforeEach(() => {
  // Mock mode is opt-in now, so the tests ask for it explicitly.
  window.history.replaceState({}, "", "/?mock=1")
  useSessionStore.getState().reset()
})

afterEach(() => {
  useSessionStore.getState().reset()
})

test("live search shows a loading state instead of unrelated products", () => {
  useSessionStore.setState({ stage: "searching", query: "kayak", listings: [] })
  render(<App />)
  expect(screen.getByText(/searching live listings/i)).toBeInTheDocument()
  expect(screen.queryByText(/checking listings/i)).not.toBeInTheDocument()
})

test("a failed live search offers a retry instead of the catalog", () => {
  useSessionStore.setState({
    stage: "failed",
    query: "kayak",
    listings: [],
    error: "Live search is taking too long. We did not substitute unrelated products — start over to try again.",
  })
  render(<App />)
  expect(screen.getByText(/live search is taking too long/i)).toBeInTheDocument()
  expect(screen.getAllByRole("button", { name: /start over/i }).length).toBeGreaterThan(0)
})

test("renders the app shell", () => {
  render(<App />)
  expect(screen.getByRole("img", { name: /sykes/i })).toBeInTheDocument()
  expect(screen.getByText(/sandbox — simulated visa intelligent commerce flow/i)).toBeInTheDocument()
})

test("landing shows the branded search hero", () => {
  render(<App />)
  expect(screen.getByText(/secure your kart every second/i)).toBeInTheDocument()
  expect(screen.getByText(/what do you want to buy/i)).toBeInTheDocument()
  expect(screen.getByText(/five trust checks/i)).toBeInTheDocument()
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
  expect(await screen.findByText(/You save \$30\.00/, {}, { timeout: 8000 })).toBeInTheDocument()
  expect(screen.getByText("$249.00")).toBeInTheDocument()
  expect(screen.getAllByText("Sony WH-1000XM5").length).toBeGreaterThan(1)
  expect(screen.getAllByText(/92\s*·\s*Trusted/).length).toBeGreaterThan(0)
  expect(screen.getByText(/12\s*·\s*Danger/)).toBeInTheDocument()
  expect(screen.getAllByText("Best pick").length).toBeGreaterThan(0)
  expect(screen.getByRole("button", { name: /^pay$/i })).toBeEnabled()
  fireEvent.click(screen.getByRole("button", { name: /purge danger/i }))
  await waitFor(() => {
    expect(screen.queryByText(/XM5 Pro/)).not.toBeInTheDocument()
  })
}, 15000)
