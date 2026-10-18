import mockFile from "../data/mock-session.json"
import { isMockMode } from "@/lib/mockMode.ts"
import type {
  Answer,
  Checkout,
  CreateSessionResponse,
  Listing,
  Receipt,
  SearchSpec,
  SessionSnapshot,
  SubmitAnswersResponse,
} from "@/lib/types.ts"

type MockFile = {
  create_session: CreateSessionResponse
  snapshot: SessionSnapshot
}

const mock = mockFile as MockFile

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const base = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
  const response = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  })
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as {
      error?: { code?: string; message?: string }
    } | null
    const message = body?.error?.message ?? response.statusText
    throw new Error(message)
  }
  return (await response.json()) as T
}

export async function createSession(input: {
  query: string
  client_id: string
}): Promise<CreateSessionResponse> {
  if (isMockMode()) {
    await delay(300)
    return { ...mock.create_session }
  }
  return request<CreateSessionResponse>("/api/sessions", {
    method: "POST",
    body: JSON.stringify(input),
  })
}

export async function submitAnswers(
  sessionId: string,
  input: { answers: Answer[]; skip_remaining: boolean },
): Promise<SubmitAnswersResponse> {
  if (isMockMode()) {
    const budget = input.answers.find((answer) => answer.question_id === "q_budget")
    const budgetCents =
      budget?.option_id === "150"
        ? 15000
        : budget?.option_id === "300"
          ? 30000
          : budget?.option_id === "600"
            ? 60000
            : null
    const searchSpec: SearchSpec = {
      query: mock.snapshot.query,
      budget_max_cents: budgetCents,
      category: "audio",
      merchants_preferred: [],
    }
    await delay(400)
    return {
      session_id: sessionId,
      stage: "searching",
      events_url: `/api/sessions/${sessionId}/events`,
      search_spec: searchSpec,
    }
  }
  return request<SubmitAnswersResponse>(`/api/sessions/${sessionId}/answers`, {
    method: "POST",
    body: JSON.stringify(input),
  })
}

export async function getSnapshot(sessionId: string): Promise<SessionSnapshot> {
  if (isMockMode()) {
    await delay(300)
    return mock.snapshot
  }
  return request<SessionSnapshot>(`/api/sessions/${sessionId}`)
}

const receipts = new Map<string, Receipt>()
let pendingListingId: string | null = null

function buildReceipt(listing: Listing, checkoutId: string): Receipt {
  const checks = mock.snapshot.checks[listing.id] ?? []
  const score = mock.snapshot.scores[listing.id]
  const receipt: Receipt = {
    id: "rcp_mock",
    share_id: "shr_mock",
    checkout_id: checkoutId,
    transaction_id: "txn_mock",
    listing,
    investigation_snapshot: {
      id: "inv_mock",
      listing_id: listing.id,
      session_id: mock.snapshot.session_id,
      checks,
      score,
      allowlisted: false,
      duration_ms: 1,
      created_at: new Date().toISOString(),
    },
    amount_cents: listing.price_cents,
    currency: listing.currency,
    token_last4: "4242",
    verified: checks.filter((check) => check.status === "passed").map((check) => check.name),
    unverified: checks.filter((check) => check.status !== "passed").map((check) => check.name),
    issued_at: new Date().toISOString(),
    signature: "sandbox",
  }
  receipts.set(receipt.share_id, receipt)
  return receipt
}

const hero = mock.snapshot.listings.find((listing) => listing.id === "lst_bestbuy_xm5")
if (hero) buildReceipt(hero, "chk_mock")

export async function createCheckout(input: {
  session_id: string
  listing_id: string
  max_amount_cents: number
}): Promise<Checkout> {
  if (isMockMode()) {
    await delay(200)
    const listing = mock.snapshot.listings.find((item) => item.id === input.listing_id)
    const score = listing ? mock.snapshot.scores[listing.id] : undefined
    if (
      !listing ||
      !score ||
      score.verdict !== "trusted" ||
      score.score < 70 ||
      score.confidence < 0.6
    ) {
      throw new Error("This merchant is not trusted enough to pay.")
    }
    if (input.max_amount_cents < listing.price_cents) {
      throw new Error("Amount exceeds the cap.")
    }
    pendingListingId = listing.id
    return {
      id: "chk_mock",
      stage: "awaiting_passkey",
      listing_id: listing.id,
      mandate: {
        merchant_name: listing.merchant_name,
        merchant_domain: listing.merchant_domain,
        max_amount_cents: input.max_amount_cents,
        currency: listing.currency,
        expires_at: new Date(Date.now() + 600_000).toISOString(),
      },
    }
  }
  return request<Checkout>("/api/checkout", {
    method: "POST",
    body: JSON.stringify(input),
  })
}

export async function confirmCheckout(
  checkoutId: string,
  input: { client_data: string },
): Promise<Receipt> {
  if (isMockMode()) {
    await delay(200)
    if (input.client_data === "fail") throw new Error("Payment declined.")
    const listing = mock.snapshot.listings.find((item) => item.id === pendingListingId)
    if (!listing) throw new Error("Checkout expired.")
    return buildReceipt(listing, checkoutId)
  }
  return request<Receipt>(`/api/checkout/${checkoutId}/confirm`, {
    method: "POST",
    body: JSON.stringify({ passkey_assertion: input }),
  })
}

export async function getReceipt(shareId: string): Promise<Receipt> {
  if (isMockMode()) {
    await delay(150)
    const found = receipts.get(shareId)
    if (!found) throw new Error("Receipt not found.")
    return found
  }
  return request<Receipt>(`/api/public/receipts/${shareId}`)
}
