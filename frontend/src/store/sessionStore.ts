import { create } from "zustand"
import type {
  Listing,
  Penalty,
  Question,
  Recommendation,
  ScoreResult,
  SessionSnapshot,
  SessionStage,
  StreamEvent,
  TrustCheckResult,
  Verdict,
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
  lastSeq: number
  error: string | null
  purgedIds: string[]
  setQuery: (query: string) => void
  showQuestions: (questions: Question[]) => void
  startSession: (snapshot: SessionSnapshot) => void
  applyEvent: (event: StreamEvent) => boolean
  applySnapshot: (snapshot: SessionSnapshot) => void
  dismissError: () => void
  purgeDanger: () => void
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
  lastSeq: 0,
  error: null as string | null,
  purgedIds: [] as string[],
}

function eventFields(event: StreamEvent): Record<string, unknown> {
  const { type: _type, seq: _seq, payload, ...rest } = event
  return { ...rest, ...(payload ?? {}) }
}

function asScore(fields: Record<string, unknown>): ScoreResult {
  return {
    score: Number(fields.score ?? 0),
    verdict: (fields.verdict as Verdict) ?? "caution",
    confidence: Number(fields.confidence ?? 1),
    penalties: (fields.penalties as Penalty[]) ?? [],
    fatal_flags: (fields.fatal_flags as string[]) ?? [],
    top_reason: String(fields.top_reason ?? ""),
    scoring_version: String(fields.scoring_version ?? "1.0"),
    allowlisted: fields.allowlisted === true,
  }
}

export const useSessionStore = create<SessionState>((set, get) => ({
  ...empty,
  setQuery: (query) => set({ query }),
  showQuestions: (questions) => set({ questions, stage: "clarifying" }),
  startSession: (snapshot) =>
    set({
      ...empty,
      sessionId: snapshot.session_id,
      stage: "searching",
      query: snapshot.query,
    }),
  applyEvent: (event) => {
    if (event.seq <= get().lastSeq) return false
    const fields = eventFields(event)
    set((state) => {
      const next = { ...state, lastSeq: event.seq }
      if (event.type === "session.stage" && typeof fields.stage === "string") {
        next.stage = fields.stage as Stage
      }
      if (event.type === "listing.found" && fields.listing) {
        const listing = fields.listing as Listing
        const without = state.listings.filter((item) => item.id !== listing.id)
        next.listings = [...without, listing]
      }
      if (event.type === "check.completed" && typeof fields.listing_id === "string" && fields.check) {
        const listingId = fields.listing_id
        const check = fields.check as TrustCheckResult
        const current = state.checks[listingId] ?? []
        const without = current.filter((item) => item.id !== check.id)
        next.checks = { ...state.checks, [listingId]: [...without, check] }
      }
      if (event.type === "listing.scored" && typeof fields.listing_id === "string") {
        next.scores = { ...state.scores, [fields.listing_id]: asScore(fields) }
      }
      if (event.type === "recommendation.ready") {
        const recommended = (fields.recommended_listing_id as string | null) ?? null
        next.recommendation = {
          recommended_listing_id: recommended,
          median_trusted_cents: (fields.median_trusted_cents as number | null) ?? null,
          savings_cents: (fields.savings_cents as number | null) ?? null,
          eligible_ids: (fields.eligible_ids as string[]) ?? [],
          reason: String(fields.reason ?? (recommended ? "cheapest trusted" : "no trusted option")),
          no_trusted_option: fields.no_trusted_option === true || recommended === null,
        }
        if (next.recommendation.no_trusted_option) next.stage = "no_trusted_option"
      }
      if (event.type === "investigation.complete") next.stage = state.stage === "no_trusted_option" ? state.stage : "ready"
      if (event.type === "session.error" && typeof fields.message === "string") {
        next.error = fields.message
        if (fields.recoverable === false) next.stage = "failed"
      }
      return next
    })
    return true
  },
  applySnapshot: (snapshot) =>
    set({
      sessionId: snapshot.session_id,
      stage: snapshot.stage,
      query: snapshot.query,
      listings: snapshot.listings,
      checks: snapshot.checks,
      scores: snapshot.scores,
      recommendation: snapshot.recommendation,
      lastSeq: snapshot.last_seq,
      error: null,
    }),
  dismissError: () => set({ error: null }),
  purgeDanger: () =>
    set((state) => ({
      purgedIds: state.listings
        .filter((listing) => state.scores[listing.id]?.verdict === "danger")
        .map((listing) => listing.id),
    })),
  reset: () => set({ ...empty }),
}))
