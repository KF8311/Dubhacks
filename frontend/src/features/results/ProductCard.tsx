import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { CheckRow } from "@/features/results/CheckRow.tsx"
import { TrustBadge } from "@/features/results/TrustBadge.tsx"
import { formatCents } from "@/lib/format.ts"
import { productLink } from "@/lib/productLink.ts"
import { cn } from "cn"
import type { CheckId, Listing, ScoreResult, TrustCheckResult } from "@/lib/types.ts"

const ALL_CHECKS: { id: CheckId; name: string }[] = [
  { id: "domain_age", name: "Domain age" },
  { id: "ssl_cert", name: "SSL certificate" },
  { id: "safe_browsing", name: "Safe Browsing" },
  { id: "reddit_sentiment", name: "Reddit" },
  { id: "page_flags", name: "Page flags" },
]

type Props = {
  listing: Listing
  checks: TrustCheckResult[]
  score?: ScoreResult
  isBest: boolean
  expanded?: boolean
  selected?: boolean
  onSelect?: () => void
  budgetMaxCents?: number | null
  budgetMinCents?: number | null
}

export function ProductCard({
  listing,
  checks,
  score,
  isBest,
  expanded = false,
  selected = false,
  onSelect,
  budgetMaxCents = null,
  budgetMinCents = null,
}: Props) {
  const [imageFailed, setImageFailed] = useState(listing.image_url.length === 0)
  const initial = listing.merchant_name.slice(0, 1).toUpperCase()
  const link = productLink(listing)

  const thumb = imageFailed ? (
    <div
      className="flex size-16 shrink-0 items-center justify-center rounded-md bg-[var(--ink)] text-lg font-semibold text-[var(--paper)]"
      aria-hidden="true"
    >
      {initial}
    </div>
  ) : (
    <img
      src={listing.image_url}
      alt=""
      className="size-16 shrink-0 rounded-md bg-muted object-cover"
      onError={() => setImageFailed(true)}
    />
  )

  const body = (
    <>
      {thumb}
      <div className="min-w-0 flex-1 space-y-1 text-left">
        {isBest ? <p className="text-sm font-semibold text-accent">Best pick</p> : null}
        <h3 className="font-heading line-clamp-2 text-base font-semibold leading-snug">{listing.title}</h3>
        <p className="text-sm text-muted-foreground">
          <span>{listing.merchant_name}</span>
          <span> · {listing.merchant_domain}</span>
        </p>
        <p className="font-heading text-xl font-semibold">
          {formatCents(listing.price_cents, listing.currency)}
        </p>
        {budgetMaxCents != null && listing.price_cents > budgetMaxCents ? (
          <p className="text-xs font-medium text-[color:var(--trust-caution)]">Above your budget</p>
        ) : null}
        {budgetMinCents != null && listing.price_cents < budgetMinCents ? (
          <p className="text-xs font-medium text-[color:var(--trust-caution)]">Below your budget</p>
        ) : null}
        <TrustBadge
          score={score?.score}
          verdict={score?.verdict}
          allowlisted={score?.allowlisted}
        />
      </div>
    </>
  )

  return (
    <Card
      className={cn(
        "min-w-0 rounded-lg py-3",
        isBest || selected ? "ticket-best" : "ticket shadow-none",
        onSelect && !expanded ? "shelf-row" : null,
      )}
    >
      {onSelect ? (
        <button
          type="button"
          className="flex w-full items-start gap-3 px-4"
          aria-pressed={selected}
          onClick={onSelect}
        >
          {body}
        </button>
      ) : (
        <div className="flex items-start gap-3 px-4">{body}</div>
      )}
      {link ? (
        <a
          href={link.href}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 inline-flex items-center gap-1 px-4 text-sm font-medium text-accent underline underline-offset-4"
        >
          {link.label}
          <span aria-hidden="true">↗</span>
        </a>
      ) : null}
      {expanded ? (
        <CardContent className="mt-3">
          {ALL_CHECKS.map((meta) => {
            const found = checks.find((check) => check.id === meta.id)
            if (!found) {
              return <Skeleton key={meta.id} className="my-2 h-10 w-full" />
            }
            return <CheckRow key={meta.id} check={found} listingId={listing.id} />
          })}
        </CardContent>
      ) : null}
    </Card>
  )
}
