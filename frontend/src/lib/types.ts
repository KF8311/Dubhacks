export type CheckId =
  | "domain_age"
  | "ssl_cert"
  | "safe_browsing"
  | "reddit_sentiment"
  | "page_flags"

export type TrustStatus = "passed" | "warning" | "failed" | "skipped"

export type Verdict = "trusted" | "caution" | "danger"

export type SessionStage =
  | "clarifying"
  | "searching"
  | "investigating"
  | "ready"
  | "no_trusted_option"
  | "failed"

export type CheckoutStage =
  | "awaiting_passkey"
  | "authorized"
  | "captured"
  | "declined"
  | "expired"
  | "cancelled"

export type CheckSource =
  | "live"
  | "cache"
  | "allowlist"
  | "fixture"
  | "timeout"
  | "unavailable"

export interface Evidence {
  label: string
  value: string
  url?: string | null
}

export interface TrustCheckResult {
  id: CheckId
  name: string
  status: TrustStatus
  severity: number
  summary: string
  evidence: Evidence[]
  source: CheckSource
  duration_ms: number
}

export interface Listing {
  id: string
  title: string
  price_cents: number
  currency: string
  merchant_name: string
  merchant_domain: string
  image_url: string
  product_url: string
  category?: string | null
  source: "serpapi" | "catalog" | "fixture"
}

export interface Penalty {
  check_id: CheckId
  points: number
  reason: string
}

export interface ScoreResult {
  score: number
  verdict: Verdict
  confidence: number
  penalties: Penalty[]
  fatal_flags: string[]
  top_reason: string
  scoring_version: string
}

export interface QuestionOption {
  id: string
  label: string
}

export interface Question {
  id: string
  prompt: string
  kind: "single_select"
  options: QuestionOption[]
  allow_free_text: boolean
}

export interface Answer {
  question_id: string
  option_id?: string | null
  text?: string | null
}

export interface SearchSpec {
  query: string
  budget_max_cents?: number | null
  category?: string | null
  merchants_preferred: string[]
}

export interface Recommendation {
  recommended_listing_id: string | null
  median_trusted_cents: number | null
  savings_cents: number | null
  eligible_ids: string[]
  reason: string
  no_trusted_option: boolean
}

export interface SessionStats {
  listings: number
  trusted: number
  caution: number
  danger: number
  duration_ms: number
}

export interface SessionSnapshot {
  session_id: string
  stage: SessionStage
  query: string
  listings: Listing[]
  checks: Record<string, TrustCheckResult[]>
  scores: Record<string, ScoreResult>
  recommendation: Recommendation | null
  last_seq: number
  stats: SessionStats
}

export interface CreateSessionResponse {
  session_id: string
  stage: SessionStage
  questions: Question[]
  expires_at: string
}

export interface SubmitAnswersResponse {
  session_id: string
  stage: SessionStage
  events_url: string
  search_spec: SearchSpec
}
