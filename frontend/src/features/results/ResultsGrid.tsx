import { useEffect, useRef, useState } from "react"
import { cn } from "cn"
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

/**
 * Two panels on one track: the items the search found, and the site stats for
 * the item the shopper picked. Choosing an item slides the stats over; choosing
 * it again (or Back to items) slides the grid back.
 */
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
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const selected = selectedId ? ordered.find((listing) => listing.id === selectedId) ?? null : null
  const backRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (selectedId && !listings.some((listing) => listing.id === selectedId)) {
      setSelectedId(null)
    }
  }, [listings, selectedId])

  // The card that opened the panel becomes inert, so hand focus to the way back.
  useEffect(() => {
    if (selectedId) backRef.current?.focus({ preventScroll: true })
  }, [selectedId])

  function choose(listingId: string) {
    setSelectedId((current) => (current === listingId ? null : listingId))
  }

  return (
    <div className="overflow-x-clip">
      <div
        data-view={selected ? "stats" : "items"}
        className={cn(
          "flex w-[200%] items-start transition-transform duration-500 ease-[cubic-bezier(0.2,0.75,0.25,1)]",
          selected ? "-translate-x-1/2" : "translate-x-0",
        )}
      >
        <section
          className="w-1/2 min-w-0 shrink-0 pr-0 lg:pr-6"
          aria-label="Listings found"
          inert={selected ? true : undefined}
        >
          <ul className="grid min-w-0 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {ordered.map((listing) => (
              <li key={listing.id} className="min-w-0">
                <ProductCard
                  listing={listing}
                  checks={checks[listing.id] ?? []}
                  score={scores[listing.id]}
                  isBest={listing.id === bestId}
                  selected={listing.id === selectedId}
                  onSelect={() => choose(listing.id)}
                  budgetMaxCents={budgetMaxCents}
                  budgetMinCents={budgetMinCents}
                />
              </li>
            ))}
          </ul>
        </section>

        <aside
          className="w-1/2 min-w-0 shrink-0"
          aria-label="Site stats"
          aria-hidden={selected ? undefined : true}
          inert={selected ? undefined : true}
        >
          {selected ? (
            <div className="mx-auto w-full max-w-xl">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <p className="inline-flex rounded-full bg-[var(--sky-wash)] px-3 py-1 text-xs font-semibold text-foreground ring-1 ring-[color-mix(in_srgb,var(--sky)_35%,transparent)]">
                  On the counter
                </p>
                <button
                  ref={backRef}
                  type="button"
                  className="text-sm font-medium text-muted-foreground underline underline-offset-4 transition-colors hover:text-foreground"
                  onClick={() => setSelectedId(null)}
                >
                  Back to items
                </button>
              </div>
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
              {ordered.length > 1 ? (
                <div className="mt-4">
                  <p className="text-xs font-semibold text-muted-foreground">Compare another</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {ordered
                      .filter((listing) => listing.id !== selected.id)
                      .map((listing) => (
                        <button
                          key={listing.id}
                          type="button"
                          className="max-w-full truncate rounded-full border border-border bg-[var(--paper)] px-3 py-1.5 text-xs font-medium transition-colors hover:border-[color-mix(in_srgb,var(--sky)_45%,var(--border))] hover:bg-[var(--sky-wash)]"
                          onClick={() => choose(listing.id)}
                        >
                          {listing.title}
                        </button>
                      ))}
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}
        </aside>
      </div>
    </div>
  )
}
