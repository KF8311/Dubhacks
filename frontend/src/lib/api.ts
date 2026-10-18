import mockFile from "../data/mock-session.json"
import { isMockMode } from "@/lib/mockMode.ts"
import type {
  Answer,
  CreateSessionResponse,
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

export async function createCheckout(): Promise<never> {
  throw new Error("Checkout UI starts at 6:00 PM.")
}

export async function confirmCheckout(): Promise<never> {
  throw new Error("Checkout UI starts at 6:00 PM.")
}

export async function getReceipt(): Promise<never> {
  throw new Error("Receipt UI starts at 6:00 PM.")
}
