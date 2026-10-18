import { formatCents } from "@/lib/format.ts"
import type { Listing, Recommendation } from "@/lib/types.ts"

type Props = {
  recommendation: Recommendation
  listings: Listing[]
}

export function BestPick({ recommendation, listings }: Props) {
  const listing = listings.find((item) => item.id === recommendation.recommended_listing_id)
  if (!listing || recommendation.savings_cents === null) return null

  return (
    <section className="rounded-xl border-2 border-stone-900 bg-stone-50 p-5">
      <p className="text-xs font-semibold uppercase tracking-wide text-stone-600">Best pick</p>
      <h3 className="mt-1 break-words text-2xl font-semibold">{listing.title}</h3>
      <p className="mt-1 text-stone-700">
        {listing.merchant_name} · {formatCents(listing.price_cents, listing.currency)}
      </p>
      <p className="mt-3 text-lg">
        You save {formatCents(recommendation.savings_cents)} compared with the typical trusted price.
      </p>
      {recommendation.narrative ? <p className="mt-2 text-stone-700">{recommendation.narrative}</p> : null}
    </section>
  )
}
