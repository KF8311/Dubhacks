import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { TrustBadge } from "@/features/results/TrustBadge.tsx"
import { ApiError, confirmCheckout, getCheckout } from "@/lib/api.ts"
import { formatCents } from "@/lib/format.ts"
import { go } from "@/lib/path.ts"
import type { CheckoutSummary } from "@/lib/types.ts"

const SANDBOX = "Sandbox — simulated Visa Intelligent Commerce flow."

const FINISHED_STAGES = new Set(["captured", "declined", "expired", "cancelled"])

function describe(caught: unknown): string {
  if (caught instanceof ApiError) return caught.message
  return caught instanceof Error ? caught.message : "Something went wrong."
}

/**
 * The phone side of "send this to my phone": the checkout was created on a
 * computer, and this page reads it by id so payment can happen where the
 * passkey lives. No card details ever touch the computer.
 */
export function PayPage({ checkoutId }: { checkoutId: string }) {
  const [summary, setSummary] = useState<CheckoutSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let alive = true
    getCheckout(checkoutId)
      .then((next) => {
        if (alive) setSummary(next)
      })
      .catch((caught) => {
        if (alive) setError(describe(caught))
      })
    return () => {
      alive = false
    }
  }, [checkoutId])

  async function onPay() {
    setBusy(true)
    setError(null)
    try {
      const receipt = await confirmCheckout(checkoutId, { client_data: "phone-passkey" })
      go(`/r/${receipt.share_id}`)
    } catch (caught) {
      setError(describe(caught))
    } finally {
      setBusy(false)
    }
  }

  if (!summary) {
    return (
      <section className="mx-auto max-w-xl space-y-3">
        <p className="text-sm text-muted-foreground">{SANDBOX}</p>
        <h2 className="font-heading text-2xl font-semibold tracking-tight">Pay on this phone</h2>
        {error ? (
          <p className="text-sm text-red-800" role="alert">
            This pay link is not available. {error}
          </p>
        ) : (
          <p className="text-sm text-muted-foreground" role="status">
            Opening the payment…
          </p>
        )}
      </section>
    )
  }

  const finished = FINISHED_STAGES.has(summary.stage)
  const paid = summary.stage === "captured"

  return (
    <section className="mx-auto max-w-xl space-y-4">
      <p className="text-sm text-muted-foreground">{summary.sandbox_label || SANDBOX}</p>
      <h2 className="font-heading text-2xl font-semibold tracking-tight">Pay on this phone</h2>

      <div className="ticket space-y-3 rounded-lg p-6">
        {summary.listing ? (
          <p className="font-heading text-lg font-semibold leading-snug">{summary.listing.title}</p>
        ) : null}
        <p className="text-foreground">
          {summary.merchant?.name ?? "Merchant"} ·{" "}
          {formatCents(summary.amount_cents, summary.currency)}
        </p>
        {summary.merchant?.domain ? (
          <p className="text-sm text-muted-foreground">{summary.merchant.domain}</p>
        ) : null}
        {summary.trust_snapshot ? (
          <TrustBadge
            score={summary.trust_snapshot.score}
            verdict={summary.trust_snapshot.verdict}
            allowlisted={summary.trust_snapshot.allowlisted}
          />
        ) : null}

        {paid && summary.receipt_url ? (
          <a
            href={summary.receipt_url}
            className="inline-flex items-center gap-1 text-sm font-medium text-accent underline underline-offset-4"
          >
            View the receipt
            <span aria-hidden="true">↗</span>
          </a>
        ) : finished ? (
          <p className="text-sm text-muted-foreground">
            This checkout is {summary.stage}. Start a new one on the computer to try again.
          </p>
        ) : (
          <div className="space-y-2">
            <Button type="button" className="h-11 px-5" disabled={busy} onClick={() => void onPay()}>
              Approve with passkey
            </Button>
            <p className="text-xs text-muted-foreground">
              Simulated biometric — no fingerprint or device credential is collected.
            </p>
          </div>
        )}

        {error ? (
          <p className="text-sm text-red-800" role="alert">
            {error}
          </p>
        ) : null}
      </div>
    </section>
  )
}
