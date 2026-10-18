import { useCallback, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/EmptyState.tsx"
import { ErrorBanner } from "@/components/ErrorBanner.tsx"
import { CheckoutSheet, SANDBOX_LABEL } from "@/features/checkout/CheckoutSheet.tsx"
import { ReceiptPage, ReceiptView } from "@/features/receipt/ReceiptPage.tsx"
import type { Receipt } from "@/lib/types.ts"
import { DiscoveryFlow } from "@/features/discovery/DiscoveryFlow.tsx"
import { BestPick } from "@/features/results/BestPick.tsx"
import { PurgeOverlay } from "@/features/results/PurgeOverlay.tsx"
import { ResultsGrid } from "@/features/results/ResultsGrid.tsx"
import { useSessionStream } from "@/features/results/useSessionStream.ts"
import { useSessionStore } from "@/store/sessionStore.ts"

const RESULT_STAGES = new Set(["searching", "investigating", "ready", "no_trusted_option", "failed"])

function shareIdFromPath(): string | null {
  const match = window.location.pathname.match(/^\/r\/([^/]+)\/?$/)
  return match ? decodeURIComponent(match[1]) : null
}

export default function App() {
  const shareId = shareIdFromPath()
  if (shareId) {
    return (
      <div className="min-h-screen bg-white text-left text-stone-900">
        <header className="flex items-center justify-between border-b px-6 py-4">
          <h1 className="text-xl font-semibold tracking-tight">Sniff</h1>
          <Badge variant="outline">{SANDBOX_LABEL}</Badge>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">
          <ReceiptPage shareId={shareId} />
        </main>
      </div>
    )
  }
  return <Shop />
}

function Shop() {
  const stage = useSessionStore((state) => state.stage)
  const sessionId = useSessionStore((state) => state.sessionId)
  const query = useSessionStore((state) => state.query)
  const listings = useSessionStore((state) => state.listings)
  const checks = useSessionStore((state) => state.checks)
  const scores = useSessionStore((state) => state.scores)
  const recommendation = useSessionStore((state) => state.recommendation)
  const error = useSessionStore((state) => state.error)
  const purgedIds = useSessionStore((state) => state.purgedIds)
  const dismissError = useSessionStore((state) => state.dismissError)
  const reset = useSessionStore((state) => state.reset)
  const [purging, setPurging] = useState(false)
  const [receipt, setReceipt] = useState<Receipt | null>(null)
  useSessionStream(sessionId)

  const finishPurge = useCallback(() => {
    useSessionStore.getState().purgeDanger()
    setPurging(false)
  }, [])

  const visible = listings.filter((listing) => !purgedIds.includes(listing.id))
  const best = listings.find((listing) => listing.id === recommendation?.recommended_listing_id)
  const hasDanger = visible.some((listing) => scores[listing.id]?.verdict === "danger")

  return (
    <div className="min-h-screen bg-white text-left text-stone-900">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <h1 className="text-xl font-semibold tracking-tight">Sniff</h1>
        <Badge variant="outline">{SANDBOX_LABEL}</Badge>
      </header>
      <main className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        {RESULT_STAGES.has(stage) ? (
          <>
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-2xl font-semibold">Results for “{query}”</h2>
              <div className="flex gap-2">
                {hasDanger ? (
                  <Button type="button" variant="destructive" onClick={() => setPurging(true)}>
                    Purge danger
                  </Button>
                ) : null}
                <Button type="button" variant="outline" onClick={reset}>
                  Start over
                </Button>
              </div>
            </div>
            {error ? <ErrorBanner message={error} onDismiss={dismissError} /> : null}
            {recommendation?.no_trusted_option ? (
              <EmptyState message={recommendation.reason} onStartOver={reset} />
            ) : (
              <>
                {recommendation && best ? <BestPick recommendation={recommendation} listings={visible} /> : null}
                {listings.length === 0 ? <p>Checking listings…</p> : null}
                <ResultsGrid
                  listings={visible}
                  checks={checks}
                  scores={scores}
                  recommendation={recommendation}
                />
                {receipt ? (
                  <ReceiptView receipt={receipt} />
                ) : best && scores[best.id] ? (
                  <CheckoutSheet
                    listing={best}
                    verdict={scores[best.id].verdict}
                    score={scores[best.id].score}
                    confidence={scores[best.id].confidence}
                    sessionId={sessionId ?? "ses_mock"}
                    onComplete={setReceipt}
                  />
                ) : null}
              </>
            )}
            <PurgeOverlay active={purging} onComplete={finishPurge} />
          </>
        ) : (
          <DiscoveryFlow onStarted={() => undefined} />
        )}
      </main>
    </div>
  )
}
