import { create } from "zustand"
import type {
  Listing,
  Question,
  Recommendation,
  ScoreResult,
  SessionSnapshot,
  SessionStage,
  TrustCheckResult,
} from "@/lib/types.ts"

type Stage = SessionStage | "discovery"

type SessionState = {
  sessionId: string | null
  stage: Stage
  query: string
  questions: Question[]
  listings: Listing[]
  checks: Record<string, TrustCheckResult[]>
  scores: Record<string, ScoreResult>
  recommendation: Recommendation | null
  setQuery: (query: string) => void
  showQuestions: (questions: Question[]) => void
  startSession: (snapshot: SessionSnapshot) => void
  reset: () => void
}

const empty = {
  sessionId: null as string | null,
  stage: "discovery" as Stage,
  query: "",
  questions: [] as Question[],
  listings: [] as Listing[],
  checks: {} as Record<string, TrustCheckResult[]>,
  scores: {} as Record<string, ScoreResult>,
  recommendation: null as Recommendation | null,
}

export const useSessionStore = create<SessionState>((set) => ({
  ...empty,
  setQuery: (query) => set({ query }),
  showQuestions: (questions) => set({ questions, stage: "clarifying" }),
  startSession: (snapshot) =>
    set({
      sessionId: snapshot.session_id,
      stage: "ready",
      query: snapshot.query,
      listings: snapshot.listings,
      checks: snapshot.checks,
      scores: snapshot.scores,
      recommendation: snapshot.recommendation,
    }),
  reset: () => set({ ...empty }),
}))
