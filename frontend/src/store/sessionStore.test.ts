import { useSessionStore } from "./sessionStore.ts"
import type { SessionSnapshot } from "@/lib/types.ts"

const listing = {
  id: "lst_1",
  title: "Purple cotton tee",
  price_cents: 1200,
  currency: "USD",
  merchant_name: "Old Navy",
  merchant_domain: "oldnavy.gap.com",
  image_url: "",
  product_url: "https://oldnavy.gap.com/item/1",
  source: "serpapi" as const,
}

const snapshot: SessionSnapshot = {
  session_id: "ses_1",
  stage: "ready",
  query: "purple t shirt",
  listings: [listing],
  checks: {},
  scores: {},
  recommendation: null,
  last_seq: 9,
  stats: { listings: 1, trusted: 0, caution: 0, danger: 0, duration_ms: 0 },
}

beforeEach(() => {
  useSessionStore.getState().reset()
})

test("startSession keeps snapshot listings when the investigation already finished", () => {
  useSessionStore.getState().startSession(snapshot)
  const state = useSessionStore.getState()
  expect(state.sessionId).toBe("ses_1")
  expect(state.stage).toBe("ready")
  expect(state.listings).toEqual([listing])
})
