import { useCallback, useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { AppShell } from "@/components/AppShell.tsx"
import { EmptyState } from "@/components/EmptyState.tsx"
import { ErrorBanner } from "@/components/ErrorBanner.tsx"
import { Skeleton } from "@/components/ui/skeleton"
import { CheckoutSheet } from "@/features/checkout/CheckoutSheet.tsx"
import { PayPage } from "@/features/checkout/PayPage.tsx"
import { ReceiptPage, ReceiptView } from "@/features/receipt/ReceiptPage.tsx"
import type { Receipt } from "@/lib/types.ts"
import { DiscoveryFlow } from "@/features/discovery/DiscoveryFlow.tsx"
import { BestPick } from "@/features/results/BestPick.tsx"
import { PurgeOverlay } from "@/features/results/PurgeOverlay.tsx"
import { ResultsGrid } from "@/features/results/ResultsGrid.tsx"
import { useSessionStream } from "@/features/results/useSessionStream.ts"
import { useSessionStore } from "@/store/sessionStore.ts"
import { currentPath } from "@/lib/path.ts"
import { About } from "@/pages/About.tsx"
import { HowItWorks } from "@/pages/HowItWorks.tsx"

const RESULT_STAGES = new Set(["searching", "investigating", "ready", "no_trusted_option", "failed"])

function shareIdFromPath(): string | null {
  const match = window.location.pathname.match(/^\/r\/([^/]+)\/?$/)
  return match ? decodeURIComponent(match[1]) : null
}

function payIdFromPath(): string | null {
  const match = window.location.pathname.match(/^\/pay\/([^/]+)\/?$/)
  return match ? decodeURIComponent(match[1]) : null
}

function usePath(): string {
  const [path, setPath] = useState(currentPath)
  useEffect(() => {
    const onPop = () => setPath(currentPath())
    window.addEventListener("popstate", onPop)
    return () => window.removeEventListener("popstate", onPop)
  }, [])
  return path
}

export default function App() {
  const path = usePath()
  const shareId = shareIdFromPath()
  const payId = payIdFromPath()
  if (shareId) {
    return (
      <AppShell>
        <ReceiptPage shareId={shareId} />
      </AppShell>
    )
  }
  if (payId) {
    return (
      <AppShell>
        <PayPage checkoutId={payId} />
      </AppShell>
    )
  }
  if (path === "/how") {
    return (
      <AppShell>
        <HowItWorks />
      </AppShell>
    )
  }
  if (path === "/about") {
    return (
      <AppShell>
        <About />
      </AppShell>
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
  const budgetMaxCents = useSessionStore((state) => state.budgetMaxCents)
  const budgetMinCents = useSessionStore((state) => state.budgetMinCents)
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
  const searching = stage === "searching" && listings.length === 0
  const failed = stage === "failed"

  return (
    <AppShell>
      {RESULT_STAGES.has(stage) ? (
        <>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div className="min-w-0">
              <h2 className="min-w-0 font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
                What we found for “{query}”
              </h2>
            </div>
            <div className="flex flex-wrap gap-2">
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
          {error && !failed ? <ErrorBanner message={error} onDismiss={dismissError} /> : null}
          {failed ? (
            <EmptyState
              message={error ?? "Live search did not finish. Start over to try again."}
              onStartOver={reset}
            />
          ) : recommendation?.no_trusted_option ? (
            <EmptyState message={recommendation.reason} onStartOver={reset} />
          ) : (
            <>
              {recommendation && best ? (
                <BestPick
                  recommendation={recommendation}
                  listings={visible}
                  budgetMaxCents={budgetMaxCents}
                />
              ) : null}
              {searching ? (
                <div
                  role="status"
                  aria-busy="true"
                  className="surface-card rounded-2xl border p-6"
                >
                  <p className="text-lg font-medium">Searching live listings…</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Real merchants can take a few seconds. We would rather wait than show
                    products you did not ask for.
                  </p>
                  <div className="mt-4 space-y-3">
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                  </div>
                </div>
              ) : null}
                <ResultsGrid
                  listings={visible}
                  checks={checks}
                  scores={scores}
                  recommendation={recommendation}
                  budgetMaxCents={budgetMaxCents}
                  budgetMinCents={budgetMinCents}
                />
              {receipt ? (
                <ReceiptView receipt={receipt} />
              ) : best && scores[best.id] ? (
                <CheckoutSheet
                  listing={best}
                  verdict={scores[best.id].verdict}
                  score={scores[best.id].score}
                  confidence={scores[best.id].confidence}
                  allowlisted={scores[best.id].allowlisted === true}
                  sessionId={sessionId ?? undefined}
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
    </AppShell>
  )
}
