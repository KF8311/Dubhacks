import { formatCents } from "@/lib/format.ts"
import { productLink } from "@/lib/productLink.ts"
import type { Listing, Recommendation } from "@/lib/types.ts"

type Props = {
  recommendation: Recommendation
  listings: Listing[]
  budgetMaxCents?: number | null
}

export function BestPick({ recommendation, listings, budgetMaxCents = null }: Props) {
  const listing = listings.find((item) => item.id === recommendation.recommended_listing_id)
  if (!listing || recommendation.savings_cents === null) return null
  const overBudget = budgetMaxCents != null && listing.price_cents > budgetMaxCents
  const link = productLink(listing)

  return (
    <section className="ticket-best rounded-3xl p-6">
      <p className="inline-flex rounded-full bg-[var(--marigold)] px-3 py-1 text-xs font-semibold text-[var(--marigold-ink)]">
        Best pick
      </p>
      <h3 className="mt-1 break-words font-heading text-3xl font-semibold tracking-tight">{listing.title}</h3>
      <p className="mt-2 text-muted-foreground">
        {listing.merchant_name} · {formatCents(listing.price_cents, listing.currency)}
      </p>
      {link ? (
        <a
          href={link.href}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-1 inline-flex items-center gap-1 text-sm font-medium text-accent underline underline-offset-4"
        >
          {link.label}
          <span aria-hidden="true">↗</span>
        </a>
      ) : null}
      <p className="mt-4 font-heading text-2xl font-semibold">
        You save {formatCents(recommendation.savings_cents)} compared with the typical trusted price.
      </p>
      {overBudget ? (
        <p className="mt-2 text-sm text-muted-foreground">
          Your ceiling did not match a trusted listing, so this is the closest trusted match above that
          budget.
        </p>
      ) : null}
      {recommendation.narrative ? <p className="mt-2 text-muted-foreground">{recommendation.narrative}</p> : null}
    </section>
  )
}
