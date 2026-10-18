import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { SANDBOX_LABEL } from "@/features/checkout/CheckoutSheet.tsx"
import { getReceipt } from "@/lib/api.ts"
import { formatCents } from "@/lib/format.ts"
import type { Receipt } from "@/lib/types.ts"

type ViewProps = {
  receipt: Receipt
}

function ScoreRing({ score, allowlisted = false }: { score: number; allowlisted?: boolean }) {
  const radius = 36
  const circumference = 2 * Math.PI * radius
  const shown = allowlisted ? 100 : score
  const filled = (Math.max(0, Math.min(100, shown)) / 100) * circumference

  return (
    <svg
      viewBox="0 0 100 100"
      className="h-28 w-28"
      role="img"
      aria-label={allowlisted ? "Verified" : `Score ${score}`}
    >
      <circle cx="50" cy="50" r={radius} fill="none" stroke="#cfe0d4" strokeWidth="8" />
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        stroke="#1f6b4a"
        strokeWidth="8"
        strokeDasharray={`${filled} ${circumference - filled}`}
        strokeLinecap="round"
        transform="rotate(-90 50 50)"
      />
      <text
        x="50"
        y={allowlisted ? 54 : 56}
        textAnchor="middle"
        fontSize={allowlisted ? 13 : 22}
        fontWeight="700"
      >
        {allowlisted ? "Verified" : score}
      </text>
    </svg>
  )
}

export function ReceiptView({ receipt }: ViewProps) {
  const [copied, setCopied] = useState(false)
  const issued = receipt.issued_at
    ? new Date(receipt.issued_at).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })
    : "Not issued"

  const shareUrl = `${window.location.origin}/r/${receipt.share_id}`

  async function copyLink() {
    try {
      await navigator.clipboard?.writeText(shareUrl)
      setCopied(true)
    } catch {
      setCopied(false)
    }
  }

  return (
    <article className="ticket space-y-4 rounded-lg p-6">
      <p className="text-sm text-muted-foreground">{SANDBOX_LABEL}</p>
      <div className="flex min-w-0 flex-wrap items-center gap-4">
        <ScoreRing
          score={receipt.investigation_snapshot.score.score}
          allowlisted={
            receipt.investigation_snapshot.allowlisted ||
            receipt.investigation_snapshot.score.allowlisted === true
          }
        />
        <div className="min-w-0 flex-1">
          <h2 className="break-words text-xl font-semibold tracking-tight">{receipt.listing.title}</h2>
          <p className="text-muted-foreground">{receipt.listing.merchant_name}</p>
          <p className="text-lg font-semibold">{formatCents(receipt.amount_cents, receipt.currency)}</p>
          <p className="text-sm text-muted-foreground">Token ····{receipt.token_last4}</p>
        </div>
      </div>
      <div>
        <h3 className="font-semibold">Verified</h3>
        <ul className="list-disc pl-5 text-sm">
          {receipt.verified.map((name) => (
            <li key={name}>{name}</li>
          ))}
        </ul>
      </div>
      <div>
        <h3 className="font-semibold">Unverified</h3>
        {receipt.unverified.length === 0 ? (
          <p className="text-sm text-muted-foreground">None</p>
        ) : (
          <ul className="list-disc pl-5 text-sm">
            {receipt.unverified.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        )}
      </div>
      <p className="text-sm text-muted-foreground">Issued {issued}</p>
      <div>
        <h3 className="font-semibold">What this receipt proves</h3>
        <p className="text-sm text-muted-foreground">
          This sandbox receipt records the trust checks and a simulated Visa payment. It is not a charge on a real card.
        </p>
      </div>
      <p className="text-sm break-all text-muted-foreground">{shareUrl}</p>
      <Button type="button" variant="outline" onClick={() => void copyLink()}>
        {copied ? "Link copied" : "Copy link"}
      </Button>
    </article>
  )
}

export function ReceiptPage({ shareId }: { shareId: string }) {
  const [receipt, setReceipt] = useState<Receipt | null>(null)
  const [missing, setMissing] = useState(false)

  useEffect(() => {
    let active = true
    void getReceipt(shareId)
      .then((next) => {
        if (active) setReceipt(next)
      })
      .catch(() => {
        if (active) setMissing(true)
      })
    return () => {
      active = false
    }
  }, [shareId])

  if (missing) return <p className="text-lg">Receipt not found.</p>
  if (!receipt) return <p className="text-stone-500">Loading receipt…</p>
  return <ReceiptView receipt={receipt} />
}
