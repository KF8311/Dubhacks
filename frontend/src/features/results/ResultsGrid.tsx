import { useEffect, useState } from "react"
import { DealAlerts } from "@/features/results/DealAlerts.tsx"
import { ProductCard } from "@/features/results/ProductCard.tsx"
import type { Listing, Recommendation, ScoreResult, TrustCheckResult } from "@/lib/types.ts"

type Props = {
  listings: Listing[]
  checks: Record<string, TrustCheckResult[]>
  scores: Record<string, ScoreResult>
  recommendation?: Recommendation | null
  budgetMaxCents?: number | null
  budgetMinCents?: number | null
}

export function ResultsGrid({
  listings,
  checks,
  scores,
  recommendation = null,
  budgetMaxCents = null,
  budgetMinCents = null,
}: Props) {
  const bestId = recommendation?.recommended_listing_id
  const ordered = [...listings].sort((a, b) => {
    if (a.id === bestId) return -1
    if (b.id === bestId) return 1
    return 0
  })
  const [selectedId, setSelectedId] = useState(ordered[0]?.id)
  const selected = ordered.find((listing) => listing.id === selectedId) ?? ordered[0]

  useEffect(() => {
    if (selectedId && listings.some((listing) => listing.id === selectedId)) return
    setSelectedId(bestId ?? listings[0]?.id)
  }, [bestId, listings, selectedId])

  if (!selected) return null

  return (
    <div className="grid min-w-0 gap-5 lg:grid-cols-[21rem_minmax(0,1fr)]">
      <aside className="order-2 min-w-0 lg:order-none lg:sticky lg:top-24 lg:self-start">
        <p className="mb-2 inline-flex rounded-full bg-[var(--sky-wash)] px-3 py-1 text-xs font-semibold text-foreground ring-1 ring-[color-mix(in_srgb,var(--sky)_35%,transparent)]">
          On the counter
        </p>
        <ProductCard
          listing={selected}
          checks={checks[selected.id] ?? []}
          score={scores[selected.id]}
          isBest={selected.id === bestId}
          expanded
          selected
          budgetMaxCents={budgetMaxCents}
          budgetMinCents={budgetMinCents}
        />
        <DealAlerts />
      </aside>
      <section className="order-1 min-w-0 lg:order-none" aria-label="Listings found">
        <ul className="grid min-w-0 gap-4 sm:grid-cols-2">
          {ordered.map((listing) => (
            <li key={listing.id} className="min-w-0">
              <ProductCard
                listing={listing}
                checks={checks[listing.id] ?? []}
                score={scores[listing.id]}
                isBest={listing.id === bestId}
                selected={listing.id === selected.id}
                onSelect={() => setSelectedId(listing.id)}
                budgetMaxCents={budgetMaxCents}
                budgetMinCents={budgetMinCents}
              />
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
