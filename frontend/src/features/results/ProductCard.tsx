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
      className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-[var(--ink)] text-sm font-semibold text-[var(--paper)]"
      aria-hidden="true"
    >
      {initial}
    </div>
  ) : (
    <img
      src={listing.image_url}
      alt=""
      className="size-10 shrink-0 rounded-lg bg-muted object-cover"
      onError={() => setImageFailed(true)}
    />
  )

  const body = (
    <>
      {thumb}
      <div className="min-w-0 flex-1 space-y-0.5 text-left">
        {isBest ? <p className="text-xs font-semibold text-accent">Best pick</p> : null}
        <h3 className="font-heading line-clamp-2 text-sm font-semibold leading-snug">{listing.title}</h3>
        <p className="truncate text-xs text-muted-foreground">
          <span>{listing.merchant_name}</span>
          <span> · {listing.merchant_domain}</span>
        </p>
        <p className="font-heading text-base font-semibold">
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

  /** The link sits on both faces: the front for touch and keyboard, the back
      so it is still clickable while the card is turned over on hover. The
      mirrored copy is removed from the tab order and the accessibility tree;
      the front link is the one assistive tech hears. */
  function renderLink(mirror: boolean) {
    if (!link) return null
    return (
      <a
        href={link.href}
        target="_blank"
        rel="noopener noreferrer"
        tabIndex={mirror ? -1 : undefined}
        className="inline-flex items-center gap-1 text-xs font-medium text-accent underline underline-offset-4"
      >
        {link.label}
        <span aria-hidden="true">↗</span>
      </a>
    )
  }

  const passed = checks.filter((check) => check.status === "passed").length
  const warnings = checks.filter((check) => check.status === "warning").length
  const failed = checks.filter((check) => check.status === "failed").length
  const waiting = checks.length === 0

  // The flip covers the whole ticket, merchant link included. It turns on
  // hover only: the link and the select button stay reachable by keyboard
  // without the face they are on rotating away.
  const front = (
    <div className="flip-face flip-front flex flex-col rounded-2xl p-2.5">
      {onSelect ? (
        <button
          type="button"
          className="flex w-full items-start gap-2.5 text-left"
          aria-pressed={selected}
          onClick={onSelect}
        >
          {body}
        </button>
      ) : (
        <div className="flex items-start gap-2.5">{body}</div>
      )}
      {link ? <div className="mt-2 flex">{renderLink(false)}</div> : null}
    </div>
  )

  const stats = (
    <div className="space-y-1">
      <p className="font-heading text-sm font-semibold">Site stats</p>
      <p className="text-xs text-muted-foreground">
        {listing.merchant_name} · {listing.merchant_domain}
      </p>
      <TrustBadge
        score={score?.score}
        verdict={score?.verdict}
        allowlisted={score?.allowlisted}
      />
      {waiting ? (
        <p className="text-xs text-muted-foreground">Checks are still running.</p>
      ) : (
        <p className="text-xs">
          {passed} passed · {warnings} warning{warnings === 1 ? "" : "s"} · {failed} failed
        </p>
      )}
      {score?.top_reason ? (
        <p className="line-clamp-2 text-xs text-muted-foreground">{score.top_reason}</p>
      ) : null}
    </div>
  )

  const back = (
    <div
      className="flip-face flip-back flex flex-col justify-center rounded-2xl p-2.5"
      data-testid="site-stats"
    >
      {onSelect ? (
        <button
          type="button"
          className="text-left"
          aria-pressed={selected}
          onClick={onSelect}
        >
          {stats}
        </button>
      ) : (
        stats
      )}
      {link ? (
        <div className="mt-2 flex" aria-hidden="true">
          {renderLink(true)}
        </div>
      ) : null}
    </div>
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
          {link ? <div className="mt-2 flex px-3">{renderLink(false)}</div> : null}
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
        <div className="flip-card min-w-0">
          <div className="flip-inner">
            {front}
            {back}
          </div>
        </div>
      )}
    </Card>
  )
}
