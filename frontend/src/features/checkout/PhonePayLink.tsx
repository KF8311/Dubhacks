import { useState } from "react"
import { Button } from "@/components/ui/button"

export function payUrl(checkoutId: string): string {
  return `${window.location.origin}/pay/${checkoutId}`
}

/**
 * The checkout exists on this device; the passkey lives on the phone. Hand the
 * payer a link (copy or share sheet) so the card is never entered here.
 */
export function PhonePayLink({
  checkoutId,
  prominent = false,
}: {
  checkoutId: string
  prominent?: boolean
}) {
  const url = payUrl(checkoutId)
  const [copied, setCopied] = useState(false)
  const canShare = typeof navigator !== "undefined" && typeof navigator.share === "function"

  async function copy() {
    try {
      await navigator.clipboard.writeText(url)
      setCopied(true)
    } catch {
      // Clipboard access can be blocked; the link is visible and selectable.
      setCopied(false)
    }
  }

  async function share() {
    try {
      await navigator.share({ title: "Pay on your phone", url })
    } catch {
      // The share sheet was dismissed or is unavailable; nothing to recover.
    }
  }

  return (
    <div
      className={
        prominent
          ? "rounded-2xl border border-[var(--marigold)] bg-[var(--marigold-wash)] p-4 shadow-[0_14px_30px_-26px_rgb(30_42_36/45%)]"
          : "rounded-2xl border border-[var(--border)] p-3"
      }
    >
      <p className="font-heading text-sm font-semibold">Pay on your phone</p>
      <p className="mt-1 text-xs text-muted-foreground">
        Open this link on your phone and approve with your passkey. No card is
        entered on this computer.
      </p>
      <p className="mt-2 break-all font-mono text-xs" data-testid="pay-url">
        {url}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        <Button type="button" size="sm" variant="outline" onClick={() => void copy()}>
          Copy link
        </Button>
        {canShare ? (
          <Button type="button" size="sm" variant="outline" onClick={() => void share()}>
            Share link
          </Button>
        ) : null}
        {copied ? <span className="text-xs text-accent">Copied.</span> : null}
      </div>
      <p className="mt-2 text-xs text-muted-foreground">The link expires with the mandate.</p>
    </div>
  )
}
