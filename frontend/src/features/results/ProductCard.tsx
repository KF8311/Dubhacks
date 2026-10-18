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
}

export function ProductCard({ listing, checks, score, isBest }: Props) {
  const [imageFailed, setImageFailed] = useState(listing.image_url.length === 0)
  const initial = listing.merchant_name.slice(0, 1).toUpperCase()

  return (
    <Card className={isBest ? "ring-2 ring-stone-900" : undefined}>
      <CardHeader className="space-y-3">
        {imageFailed ? (
          <div
            className="flex h-36 items-center justify-center rounded-md bg-gradient-to-br from-stone-200 to-stone-400 text-3xl font-semibold text-stone-800"
            aria-hidden="true"
          >
            {initial}
          </div>
        ) : (
          <img
            src={listing.image_url}
            alt=""
            className="h-36 w-full rounded-md object-cover"
            onError={() => setImageFailed(true)}
          />
        )}
        {isBest ? (
          <p className="text-xs font-semibold uppercase tracking-wide text-stone-600">Best pick</p>
        ) : null}
        <CardTitle className="line-clamp-2 text-lg">{listing.title}</CardTitle>
        <p className="text-sm text-stone-600">
          <span>{listing.merchant_name}</span>
          <span className="text-stone-400"> · {listing.merchant_domain}</span>
        </p>
        <p className="text-xl font-semibold">{formatCents(listing.price_cents, listing.currency)}</p>
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
