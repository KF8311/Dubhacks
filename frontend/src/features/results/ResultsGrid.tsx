import { ProductCard } from "@/features/results/ProductCard.tsx"
import type { Listing, Recommendation, ScoreResult, TrustCheckResult } from "@/lib/types.ts"

type Props = {
  listings: Listing[]
  checks: Record<string, TrustCheckResult[]>
  scores: Record<string, ScoreResult>
  recommendation?: Recommendation | null
}

export function ResultsGrid({ listings, checks, scores, recommendation = null }: Props) {
  const bestId = recommendation?.recommended_listing_id
  const ordered = [...listings].sort((a, b) => {
    if (a.id === bestId) return -1
    if (b.id === bestId) return 1
    return 0
  })

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      {ordered.map((listing) => (
        <ProductCard
          key={listing.id}
          listing={listing}
          checks={checks[listing.id] ?? []}
          score={scores[listing.id]}
          isBest={listing.id === bestId}
        />
      ))}
    </div>
  )
}
