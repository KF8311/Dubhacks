import { useCallback, useState } from "react"
import { Button } from "@/components/ui/button"
import { MandateCard } from "@/features/checkout/MandateCard.tsx"
import { PasskeyDialog } from "@/features/checkout/PasskeyDialog.tsx"
import { ProcessingState } from "@/features/checkout/ProcessingState.tsx"
import { confirmCheckout, createCheckout } from "@/lib/api.ts"
import { formatCents } from "@/lib/format.ts"
import type { Checkout, Listing, Receipt, Verdict } from "@/lib/types.ts"

export const SANDBOX_LABEL = "Sandbox — simulated Visa Intelligent Commerce flow"

type Props = {
  listing: Listing
  verdict: Verdict
  score: number
  confidence: number
  sessionId?: string
  onComplete: (receipt: Receipt) => void
}

export function CheckoutSheet({
  listing,
  verdict,
  score,
  confidence,
  sessionId = "ses_mock",
  onComplete,
}: Props) {
  const payable = verdict === "trusted" && score >= 70 && confidence >= 0.6
  const [phase, setPhase] = useState<"review" | "mandate" | "passkey" | "processing">("review")
  const [checkout, setCheckout] = useState<Checkout | null>(null)
  const [receipt, setReceipt] = useState<Receipt | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const finish = useCallback(() => {
    if (receipt) onComplete(receipt)
  }, [onComplete, receipt])

  async function onPay() {
    setError(null)
    setBusy(true)
    try {
      const created = await createCheckout({
        session_id: sessionId,
        listing_id: listing.id,
        max_amount_cents: listing.price_cents,
      })
      setCheckout(created)
      setPhase("mandate")
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Checkout failed.")
    } finally {
      setBusy(false)
    }
  }

  async function onConfirm(clientData: string) {
    if (!checkout) return
    setError(null)
    setBusy(true)
    try {
      const next = await confirmCheckout(checkout.id, { client_data: clientData })
      setReceipt(next)
      setPhase("processing")
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Payment failed.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <aside className="rounded-xl border bg-white p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-stone-500">{SANDBOX_LABEL}</p>
      <h3 className="mt-2 text-lg font-semibold">Checkout</h3>
      {phase === "review" ? (
        <div className="mt-3 space-y-3">
          <p className="text-stone-700">
            {listing.merchant_name} · {formatCents(listing.price_cents, listing.currency)}
          </p>
          <p className="text-sm text-stone-600">
            {score} · {verdict} · confidence {confidence}
          </p>
          <Button type="button" disabled={!payable || busy} onClick={() => void onPay()}>
            Pay
          </Button>
        </div>
      ) : null}
      {phase === "mandate" && checkout ? (
        <div className="mt-3">
          <MandateCard mandate={checkout.mandate} onContinue={() => setPhase("passkey")} />
        </div>
      ) : null}
      {phase === "passkey" ? (
        <div className="mt-3">
          <PasskeyDialog busy={busy} onConfirm={(clientData) => void onConfirm(clientData)} />
        </div>
      ) : null}
      {phase === "processing" ? (
        <div className="mt-3">
          <ProcessingState onDone={finish} />
        </div>
      ) : null}
      {error ? (
        <p className="mt-3 text-sm text-red-800" role="alert">
          {error}
        </p>
      ) : null}
    </aside>
  )
}
