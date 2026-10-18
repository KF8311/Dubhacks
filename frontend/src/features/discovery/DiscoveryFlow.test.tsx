import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, expect, test, vi } from "vitest"
import { DiscoveryFlow } from "./DiscoveryFlow.tsx"

const questions = [
  {
    id: "q_budget",
    prompt: "What's your ceiling?",
    kind: "single_select",
    options: [{ id: "300", label: "$150–$300" }],
    allow_free_text: false,
  },
]

const snapshot = {
  session_id: "ses_real",
  stage: "searching",
  query: "headphones",
  listings: [],
  checks: {},
  scores: {},
  recommendation: null,
  last_seq: 0,
  stats: { listings: 0, trusted: 0, caution: 0, danger: 0, duration_ms: 0 },
}

function jsonResponse(body: unknown, status = 200): Response {
  return { ok: status < 400, status, statusText: "", json: async () => body } as Response
}

beforeEach(() => {
  window.history.replaceState({}, "", "/")
})

afterEach(() => {
  vi.restoreAllMocks()
})

test("says it is asking questions while the session is created", async () => {
  let finish: ((value: Response) => void) | undefined
  vi.spyOn(globalThis, "fetch").mockImplementation(
    () =>
      new Promise<Response>((resolve) => {
        finish = resolve
      }),
  )

  render(<DiscoveryFlow onStarted={() => undefined} />)
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "running shoes" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))
  expect(await screen.findByText(/asking a few questions/i)).toBeInTheDocument()
  finish?.(
    jsonResponse({
      session_id: "ses_real",
      stage: "clarifying",
      questions,
      expires_at: "2026-10-17T22:00:00Z",
    }),
  )
})

test("question screens show progress through the set", async () => {
  window.history.replaceState({}, "", "/?mock=1")

  render(<DiscoveryFlow onStarted={() => undefined} />)
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "headphones" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))
  expect(await screen.findByText(/question 1 of 3/i)).toBeInTheDocument()
  expect(screen.getByRole("progressbar", { name: /question progress/i })).toHaveAttribute(
    "aria-valuenow",
    "1",
  )
})

test("shows an alert and stays on the search when the API is unreachable", async () => {
  vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"))

  render(<DiscoveryFlow onStarted={() => undefined} />)
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "headphones" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))

  expect(await screen.findByRole("alert")).toHaveTextContent(/could not reach the server/i)
  expect(screen.getByText(/what do you want to buy/i)).toBeInTheDocument()
})

test("lets you type a price even when the question is chips only", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const url = String(input)
    if (url.endsWith("/api/sessions")) {
      return jsonResponse({
        session_id: "ses_real",
        stage: "clarifying",
        questions: [
          {
            id: "q_budget",
            prompt: "What's your ceiling?",
            kind: "single_select",
            options: [{ id: "100", label: "Under $100" }],
            allow_free_text: false,
          },
        ],
        expires_at: "2026-10-17T22:00:00Z",
      })
    }
    return jsonResponse(snapshot)
  })

  render(<DiscoveryFlow onStarted={() => undefined} />)
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "water bottles" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))
  expect(await screen.findByPlaceholderText(/or type your own answer/i)).toBeInTheDocument()
})

test("renders questions from the mock session", async () => {
  window.history.replaceState({}, "", "/?mock=1")

  render(<DiscoveryFlow onStarted={() => undefined} />)
  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "headphones" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))
  expect(await screen.findByText(/what's your ceiling/i)).toBeInTheDocument()
})

test("submits answers against the session id the server returned", async () => {
  const calls: string[] = []
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const url = String(input)
    calls.push(url)
    if (url.endsWith("/api/sessions")) {
      return jsonResponse({
        session_id: "ses_real",
        stage: "clarifying",
        questions,
        expires_at: "2026-10-17T22:00:00Z",
      })
    }
    if (url.endsWith("/api/sessions/ses_real/answers")) {
      return jsonResponse(
        { session_id: "ses_real", stage: "searching", events_url: "/x", search_spec: {} },
        202,
      )
    }
    return jsonResponse(snapshot)
  })

  render(<DiscoveryFlow onStarted={() => undefined} />)

  fireEvent.change(screen.getByPlaceholderText(/what are you looking for/i), {
    target: { value: "headphones" },
  })
  fireEvent.click(screen.getByRole("button", { name: /find products/i }))
  fireEvent.click(await screen.findByRole("button", { name: /\$150–\$300/i }))
  fireEvent.click(screen.getByRole("button", { name: /see results/i }))

  await waitFor(() => {
    expect(calls.some((url) => url.endsWith("/api/sessions/ses_real/answers"))).toBe(true)
  })
  expect(calls.some((url) => url.includes("ses_mock"))).toBe(false)
})
