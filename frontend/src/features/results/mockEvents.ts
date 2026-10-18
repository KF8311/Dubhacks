import mockFile from "../../data/mock-session.json"
import type { Listing, ScoreResult, SessionSnapshot, StreamEvent, TrustCheckResult } from "@/lib/types.ts"

const snapshot = (mockFile as { snapshot: SessionSnapshot }).snapshot

export const MOCK_EVENT_MS = 12

export function buildMockEvents(): StreamEvent[] {
  const events: StreamEvent[] = []
  let seq = 0
  const push = (type: string, payload: Record<string, unknown>) => {
    seq += 1
    events.push({ type, seq, ...payload, payload })
  }

  snapshot.listings.forEach((listing: Listing, index) => {
    push("listing.found", { listing, rank: index + 1 })
    const checks = snapshot.checks[listing.id] ?? []
    checks.forEach((check: TrustCheckResult, checkIndex) => {
      push("check.started", { listing_id: listing.id, check_id: check.id, name: check.name, index: checkIndex })
      push("check.completed", { listing_id: listing.id, check })
    })
    const score: ScoreResult | undefined = snapshot.scores[listing.id]
    if (score) {
      push("listing.scored", {
        listing_id: listing.id,
        score: score.score,
        verdict: score.verdict,
        confidence: score.confidence,
        top_reason: score.top_reason,
        penalties: score.penalties,
        fatal_flags: score.fatal_flags,
        scoring_version: score.scoring_version,
      })
    }
  })

  if (snapshot.recommendation) {
    push("recommendation.ready", { ...snapshot.recommendation })
  }
  push("investigation.complete", { stats: snapshot.stats, duration_ms: snapshot.stats.duration_ms })
  return events
}
