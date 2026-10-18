import { useState } from "react"
import { Button, buttonVariants } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { CheckRow } from "@/features/results/CheckRow.tsx"
import { TrustBadge } from "@/features/results/TrustBadge.tsx"
import { formatCents } from "@/lib/format.ts"
import { sendPhoneText } from "@/lib/phoneBridge.ts"
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

const SCORE_COLOR: Record<string, string> = {
  trusted: "var(--trust-trusted)",
  caution: "var(--trust-caution)",
  danger: "var(--trust-danger)",
}

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

function Photo({
  listing,
  failed,
  onFail,
  hero,
}: {
  listing: Listing
  failed: boolean
  onFail: () => void
  hero?: boolean
}) {
  const initial = listing.merchant_name.slice(0, 1).toUpperCase()
  if (failed) {
    return (
      <div
        className={
          hero
            ? "flex aspect-[4/3] w-full items-center justify-center bg-[var(--ink)] text-4xl font-semibold text-[var(--paper)]"
            : "flex size-20 shrink-0 items-center justify-center rounded-md bg-[var(--ink)] text-lg font-semibold text-[var(--paper)]"
        }
        aria-hidden="true"
      >
        {initial}
      </div>
    )
  }
  return (
    <img
      src={listing.image_url}
      alt=""
      className={
        hero
          ? "listing-photo-hero aspect-[4/3] w-full bg-[var(--paper)] object-contain"
          : "listing-photo size-20 shrink-0 rounded-md bg-[var(--paper)] object-contain"
      }
      onError={onFail}
    />
  )
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
  const [sendState, setSendState] = useState<"idle" | "sending" | "sent" | "failed">("idle")
  const [sendError, setSendError] = useState<string | null>(null)
  const initial = listing.merchant_name.slice(0, 1).toUpperCase()
  const link = productLink(listing)

  const thumb = imageFailed ? (
    <div
      className="flex h-28 w-full items-center justify-center bg-[var(--ink)] text-3xl font-semibold text-[var(--paper)]"
      aria-hidden="true"
    >
      {initial}
    </div>
  ) : (
    <img
      src={listing.image_url}
      alt=""
      className="h-28 w-full bg-muted object-cover"
      onError={() => setImageFailed(true)}
    />
  )

  const passed = checks.filter((check) => check.status === "passed").length
  const warnings = checks.filter((check) => check.status === "warning").length
  const failed = checks.filter((check) => check.status === "failed").length
  const waiting = checks.length === 0
  const tally = waiting
    ? "Checks running…"
    : `${passed} passed · ${warnings} warning${warnings === 1 ? "" : "s"} · ${failed} failed`
  const scoreColor = SCORE_COLOR[score?.verdict ?? "pending"] ?? "var(--trust-pending)"
  const price = formatCents(listing.price_cents, listing.currency)

  async function onSend() {
    if (sendState === "sending") return
    setSendState("sending")
    setSendError(null)
    const href = link?.href ?? (listing.merchant_domain ? `https://${listing.merchant_domain}` : "")
    try {
      await sendPhoneText(
        `Sykes found: ${listing.title} — ${price} at ${listing.merchant_name}.${href ? ` ${href}` : ""}`,
      )
      setSendState("sent")
    } catch (caught) {
      setSendError(caught instanceof Error ? caught.message : "The phone bridge did not accept the message.")
      setSendState("failed")
    }
  }

  const actions = (
    <div className="flex gap-2 px-2.5 pb-2.5">
      {link ? (
        <a
          href={link.href}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={link.label.replace(/^View/, "Visit")}
          className={cn(
            buttonVariants({ size: "lg" }),
            "h-9 flex-1 font-semibold transition-all hover:-translate-y-px hover:shadow-sm",
          )}
        >
          Visit site
        </a>
      ) : null}
      <Button
        type="button"
        variant="outline"
        className="h-9 flex-1 font-semibold transition-all hover:-translate-y-px hover:border-[color-mix(in_srgb,var(--sky)_45%,var(--border))] hover:bg-[var(--sky-wash)] hover:shadow-sm"
        aria-label={`Send ${listing.title} to your phone`}
        disabled={sendState === "sending"}
        onClick={() => void onSend()}
      >
        {sendState === "sending"
          ? "Sending…"
          : sendState === "sent"
            ? "Sent"
            : sendState === "failed"
              ? "Retry"
              : "Send"}
      </Button>
    </div>
  )

  const front = (
    <span className="flip-face flip-front block">
      {thumb}
      <span className="block space-y-1 p-3 text-left">
        {isBest ? (
          <span className="inline-flex rounded-full bg-[var(--marigold)] px-2 py-0.5 text-[0.7rem] font-semibold text-[var(--marigold-ink)]">
            Best pick
          </span>
        ) : null}
        <span className="line-clamp-2 font-heading text-sm font-semibold leading-snug">
          {listing.title}
        </span>
        <span className="block truncate text-xs text-muted-foreground">
          {listing.merchant_name} · {listing.merchant_domain}
        </span>
        <span className="flex items-center justify-between gap-2 pt-1">
          <span className="font-heading text-lg font-semibold">{price}</span>
          <TrustBadge score={score?.score} verdict={score?.verdict} allowlisted={score?.allowlisted} />
        </span>
        <span className="block truncate text-xs text-muted-foreground">{tally}</span>
        {budgetMaxCents != null && listing.price_cents > budgetMaxCents ? (
          <span className="block text-xs font-medium text-[color:var(--trust-caution)]">Above your budget</span>
        ) : null}
        {budgetMinCents != null && listing.price_cents < budgetMinCents ? (
          <span className="block text-xs font-medium text-[color:var(--trust-caution)]">Below your budget</span>
        ) : null}
      </span>
    </span>
  )

  const back = (
    <span className="flip-face flip-back block" aria-hidden="true">
      <span className="flex h-full min-h-[12rem] flex-col items-center justify-center gap-1 bg-[var(--paper)] p-4 text-center">
        <span className="text-xs font-semibold text-muted-foreground">Site safety</span>
        <span
          className={cn(
            "font-heading font-semibold leading-none",
            score?.allowlisted ? "text-3xl" : "text-5xl",
          )}
          style={{ color: scoreColor }}
        >
          {score?.allowlisted ? "Verified" : (score?.score ?? "—")}
        </span>
        <TrustBadge score={score?.score} verdict={score?.verdict} allowlisted={score?.allowlisted} />
        <span className="text-xs">{tally}</span>
        {score?.top_reason ? (
          <span className="line-clamp-3 text-xs text-muted-foreground">{score.top_reason}</span>
        ) : null}
        <span className="mt-1 text-[0.7rem] text-muted-foreground">{listing.merchant_domain}</span>
      </span>
    </span>
  )

  return (
    <Card
      data-verdict={score?.verdict ?? "pending"}
      className={cn(
        "product-card h-full min-w-0 gap-0 rounded-3xl",
        !expanded ? "product-flip" : null,
        isBest && !expanded ? "ticket-best" : "ticket",
        !isBest && selected && !expanded ? "ticket-selected" : null,
      )}
    >
      {expanded ? (
        <>
          <div className="flex items-start gap-2.5 px-3 pt-3">
            {imageFailed ? (
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[var(--ink)] text-sm font-semibold text-[var(--paper)]" aria-hidden="true">
                {initial}
              </div>
            ) : (
              <img
                src={listing.image_url}
                alt=""
                className="size-10 shrink-0 rounded-xl bg-muted object-cover"
                onError={() => setImageFailed(true)}
              />
            )}
            <div className="min-w-0 flex-1 space-y-0.5 text-left">
              <h3 className="truncate font-heading text-sm font-semibold leading-tight">{listing.title}</h3>
              <p className="truncate text-xs text-muted-foreground">
                {listing.merchant_name} · {listing.merchant_domain}
              </p>
              <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                <TrustBadge score={score?.score} verdict={score?.verdict} allowlisted={score?.allowlisted} />
                <span className="truncate text-xs text-muted-foreground">{tally}</span>
              </div>
            </div>
            <p className="shrink-0 font-heading text-sm font-semibold">{price}</p>
          </div>
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
        <>
          <button
            type="button"
            className="flip-card block w-full cursor-pointer text-left"
            aria-label={`Show checks for ${listing.title}`}
            aria-pressed={selected}
            onClick={onSelect}
          >
            <span className="flip-inner">
              {front}
              {back}
            </span>
          </button>
          {actions}
          {sendState === "failed" ? (
            <p className="px-3 pb-2 text-xs text-[color:var(--trust-danger)]" role="alert">
              Could not send. {sendError ?? "Open the site with Visit instead."}
            </p>
          ) : null}
        </>
      )}
    </Card>
  )
}
