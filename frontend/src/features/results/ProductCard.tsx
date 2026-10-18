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
      className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[var(--ink)] text-sm font-semibold text-[var(--paper)]"
      aria-hidden="true"
    >
      {initial}
    </div>
  ) : (
    <img
      src={listing.image_url}
      alt=""
      className="size-10 shrink-0 rounded-xl bg-muted object-cover"
      onError={() => setImageFailed(true)}
    />
  )

  const passed = checks.filter((check) => check.status === "passed").length
  const warnings = checks.filter((check) => check.status === "warning").length
  const failed = checks.filter((check) => check.status === "failed").length
  const waiting = checks.length === 0
  // The tally lives on the row itself; there is no hidden face to turn over.
  const tally = waiting
    ? "Checks running…"
    : `${passed} passed · ${warnings} warning${warnings === 1 ? "" : "s"} · ${failed} failed`

  const body = (
    <>
      {thumb}
      <div className="min-w-0 flex-1 space-y-0.5 text-left">
        {isBest ? <p className="text-xs font-semibold text-accent">Best pick</p> : null}
        <h3 className="truncate font-heading text-sm font-semibold leading-tight">{listing.title}</h3>
        <p className="truncate text-xs text-muted-foreground">
          <span>{listing.merchant_name}</span>
          <span> · {listing.merchant_domain}</span>
        </p>
        <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
          <TrustBadge
            score={score?.score}
            verdict={score?.verdict}
            allowlisted={score?.allowlisted}
          />
          <span className="truncate text-xs text-muted-foreground">{tally}</span>
        </div>
        {budgetMaxCents != null && listing.price_cents > budgetMaxCents ? (
          <p className="text-xs font-medium text-[color:var(--trust-caution)]">Above your budget</p>
        ) : null}
        {budgetMinCents != null && listing.price_cents < budgetMinCents ? (
          <p className="text-xs font-medium text-[color:var(--trust-caution)]">Below your budget</p>
        ) : null}
      </div>
      <p className="shrink-0 font-heading text-sm font-semibold">
        {formatCents(listing.price_cents, listing.currency)}
      </p>
    </>
  )

  return (
    <Card
      data-verdict={score?.verdict ?? "pending"}
      className={cn(
        "product-card min-w-0 rounded-3xl",
        /** Only the actual pick wears the marigold edge. A merely selected
            row gets a neutral ring so several cards never compete for it. */
        isBest && !expanded ? "ticket-best" : "ticket",
        !isBest && selected && !expanded ? "ticket-selected" : null,
        onSelect && !expanded ? "shelf-row" : null,
      )}
    >
      {expanded ? (
        <>
          <div className="flex items-start gap-2.5 px-3 pt-3">{body}</div>
          {link ? (
            <div className="mt-2 flex px-3">
              <a
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs font-medium text-accent underline underline-offset-4"
              >
                {link.label}
                <span aria-hidden="true">↗</span>
              </a>
            </div>
          ) : null}
          <CardContent className="mt-3">
            {ALL_CHECKS.map((meta) => {
              const found = checks.find((check) => check.id === meta.id)
              if (!found) {
                return <Skeleton key={meta.id} className="my-2 h-10 w-full" />
              }
              return <CheckRow key={meta.id} check={found} listingId={listing.id} />
            })}
          </CardContent>
        </>
      ) : (
        <div className="flex items-center gap-1 py-2 pl-2.5 pr-1.5">
          {onSelect ? (
            <button
              type="button"
              className="flex min-w-0 flex-1 items-start gap-2.5 rounded-2xl text-left"
              aria-pressed={selected}
              onClick={onSelect}
            >
              {body}
            </button>
          ) : (
            <div className="flex min-w-0 flex-1 items-start gap-2.5">{body}</div>
          )}
          {link ? (
            <a
              href={link.href}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={link.label}
              title={link.label}
              className="flex size-8 shrink-0 items-center justify-center rounded-full bg-[var(--paper)] text-sm font-semibold text-accent ring-1 ring-[color-mix(in_srgb,var(--accent)_25%,transparent)] transition-colors hover:bg-[var(--marigold-wash)]"
            >
              <span aria-hidden="true">↗</span>
            </a>
          ) : null}
        </div>
      )}
    </Card>
  )
}
