import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { CheckRow } from "@/features/results/CheckRow.tsx"
import { TrustBadge } from "@/features/results/TrustBadge.tsx"
import { formatCents } from "@/lib/format.ts"
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
  budgetMaxCents?: number | null
  budgetMinCents?: number | null
}

export function ProductCard({
  listing,
  checks,
  score,
  isBest,
  budgetMaxCents = null,
  budgetMinCents = null,
}: Props) {
  const [imageFailed, setImageFailed] = useState(listing.image_url.length === 0)
  const initial = listing.merchant_name.slice(0, 1).toUpperCase()

  return (
    <Card
      className={
        isBest
          ? "surface-card min-w-0 ring-2 ring-[#18D6C0]"
          : "min-w-0 bg-white shadow-sm ring-1 ring-border"
      }
    >
      <CardHeader className="space-y-3">
        {imageFailed ? (
          <div
            className="flex h-40 items-center justify-center rounded-xl bg-gradient-to-br from-[#101A2B] to-[#00A5B5] text-3xl font-semibold text-white"
            aria-hidden="true"
          >
            {initial}
          </div>
        ) : (
          <img
            src={listing.image_url}
            alt=""
            className="h-40 w-full rounded-xl bg-[#f4f7fa] object-cover"
            onError={() => setImageFailed(true)}
          />
        )}
        {isBest ? (
          <p className="text-xs font-semibold tracking-[0.16em] text-[#00A5B5] uppercase">Best pick</p>
        ) : null}
        <CardTitle className="line-clamp-2 text-lg">{listing.title}</CardTitle>
        <p className="text-sm text-muted-foreground">
          <span>{listing.merchant_name}</span>
          <span> · {listing.merchant_domain}</span>
        </p>
        <p className="text-xl font-semibold">{formatCents(listing.price_cents, listing.currency)}</p>
        {budgetMaxCents != null && listing.price_cents > budgetMaxCents ? (
          <p className="text-xs font-medium text-[#b45309]">Above your budget</p>
        ) : null}
        {budgetMinCents != null && listing.price_cents < budgetMinCents ? (
          <p className="text-xs font-medium text-[#b45309]">Below your budget</p>
        ) : null}
        <TrustBadge
          score={score?.score}
          verdict={score?.verdict}
          allowlisted={score?.allowlisted}
        />
      </CardHeader>
      <CardContent>
        {ALL_CHECKS.map((meta) => {
          const found = checks.find((check) => check.id === meta.id)
          if (!found) {
            return <Skeleton key={meta.id} className="my-2 h-10 w-full" />
          }
          return <CheckRow key={meta.id} check={found} listingId={listing.id} />
        })}
      </CardContent>
    </Card>
  )
}
