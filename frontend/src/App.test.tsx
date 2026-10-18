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

test("search results stay visible when the URL is /how", () => {
  window.history.replaceState({}, "", "/how?mock=1")
  useSessionStore.setState({ stage: "searching", query: "kayak", listings: [] })
  render(<App />)
  expect(screen.getByText(/searching live listings/i)).toBeInTheDocument()
  expect(screen.getByRole("heading", { name: /what we found for/i })).toBeInTheDocument()
})

test("listings stay visible when the URL is /about", () => {
  window.history.replaceState({}, "", "/about?mock=1")
  useSessionStore.setState({
    stage: "ready",
    query: "headphones",
    listings: [
      {
        id: "lst_sony",
        title: "Sony WH-1000XM5",
        price_cents: 24900,
        currency: "USD",
        merchant_name: "Sony",
        merchant_domain: "sony.com",
        image_url: "",
        product_url: "https://sony.com/x",
        source: "serpapi",
      },
    ],
    scores: {
      lst_sony: {
        score: 92,
        verdict: "trusted",
        confidence: 1,
        penalties: [],
        fatal_flags: [],
        top_reason: "ok",
        scoring_version: "1.0",
        allowlisted: true,
      },
    },
  })
  render(<App />)
  expect(screen.getByRole("heading", { name: /what we found for/i })).toBeInTheDocument()
  expect(screen.getAllByText("Sony WH-1000XM5").length).toBeGreaterThan(0)
})

test("clarifying questions stay on the shop after opening how it works", async () => {
  render(<App />)
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "headphones" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))
  expect(await screen.findByText(/what's your ceiling/i)).toBeInTheDocument()
  fireEvent.click(screen.getByRole("link", { name: /how it works/i }))
  expect(screen.getByText(/what's your ceiling/i)).toBeInTheDocument()
  fireEvent.click(screen.getByRole("button", { name: /\$150–\$300/i }))
  fireEvent.click(screen.getByRole("button", { name: /^next$/i }))
  expect(await screen.findByText(/question 2 of 3/i)).toBeInTheDocument()
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
  expect(screen.getByRole("link", { name: /how it works/i })).toBeInTheDocument()
  expect(screen.getByRole("link", { name: /^about$/i })).toBeInTheDocument()
  expect(screen.queryByRole("link", { name: /the five checks/i })).not.toBeInTheDocument()
})

test("how it works explains the five checks and the pay rule", () => {
  window.history.replaceState({}, "", "/how")
  render(<App />)
  expect(screen.getByRole("heading", { name: /how sykes checks a store/i })).toBeInTheDocument()
  expect(screen.getAllByText(/domain age/i).length).toBeGreaterThan(0)
  expect(screen.getAllByText(/safe browsing/i).length).toBeGreaterThan(0)
  expect(screen.getByText(/cannot pay a merchant it cannot verify/i)).toBeInTheDocument()
})

test("about page tells the brand story", () => {
  window.history.replaceState({}, "", "/about")
  render(<App />)
  expect(screen.getByRole("heading", { name: /about sykes/i })).toBeInTheDocument()
  expect(screen.getAllByText(/shopkeeper/i).length).toBeGreaterThan(0)
})

test("landing shows the branded search hero", () => {
  render(<App />)
  expect(screen.queryByText(/secure your kart every second/i)).not.toBeInTheDocument()
  expect(screen.getByRole("heading", { name: /find a deal you can actually pay for/i })).toBeInTheDocument()
  expect(screen.getByText(/what do you want to buy/i)).toBeInTheDocument()
  expect(screen.getByText(/five trust checks/i)).toBeInTheDocument()
  expect(screen.getByRole("button", { name: /^headphones$/i })).toBeInTheDocument()
})

test("landing has a shop window you can scroll into", () => {
  render(<App />)
  expect(screen.getByTestId("shop-window")).toBeInTheDocument()
  expect(screen.getByText(/drag to turn/i)).toBeInTheDocument()
})

test("the shop globe can be turned with the pointer", () => {
  render(<App />)
  expect(screen.getByTestId("shop-orb").getAttribute("aria-label")).toMatch(/drag to turn/i)
})

test("how it works and about live on the shop page", () => {
  render(<App />)
  fireEvent.click(screen.getByRole("link", { name: /how it works/i }))
  expect(screen.getByRole("heading", { name: /find a deal you can actually pay for/i })).toBeInTheDocument()
  expect(screen.getByRole("heading", { name: /how sykes checks a store/i })).toBeInTheDocument()
  expect(screen.getByRole("link", { name: /how it works/i })).toHaveAttribute("aria-current", "page")
  fireEvent.click(screen.getByRole("link", { name: /^about$/i }))
  expect(screen.getByRole("heading", { name: /about sykes/i })).toBeInTheDocument()
  expect(screen.getByRole("heading", { name: /find a deal you can actually pay for/i })).toBeInTheDocument()
  expect(screen.getByRole("link", { name: /^about$/i })).toHaveAttribute("aria-current", "page")
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
  expect(screen.getAllByText("$249.00").length).toBeGreaterThan(0)
  expect(screen.getAllByText("Sony WH-1000XM5").length).toBeGreaterThan(1)
  expect(screen.getAllByText(/92\s*·\s*Trusted/).length).toBeGreaterThan(0)
  expect(screen.getByText(/12\s*·\s*Danger/)).toBeInTheDocument()
  expect(screen.getAllByText("Best pick").length).toBeGreaterThan(0)
  expect(screen.queryByText(/^Investigation$/)).not.toBeInTheDocument()
  expect(screen.getByRole("heading", { name: /what we found for/i })).toBeInTheDocument()
  expect(screen.getByRole("button", { name: /^pay$/i })).toBeEnabled()
  fireEvent.click(screen.getByRole("button", { name: /purge danger/i }))
  await waitFor(() => {
    expect(screen.queryByText(/XM5 Pro/)).not.toBeInTheDocument()
  })
}, 15000)
