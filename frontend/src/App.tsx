import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DiscoveryFlow } from "@/features/discovery/DiscoveryFlow.tsx"
import { ResultsGrid } from "@/features/results/ResultsGrid.tsx"
import { useSessionStore } from "@/store/sessionStore.ts"

export default function App() {
  const stage = useSessionStore((state) => state.stage)
  const query = useSessionStore((state) => state.query)
  const listings = useSessionStore((state) => state.listings)
  const checks = useSessionStore((state) => state.checks)
  const scores = useSessionStore((state) => state.scores)
  const recommendation = useSessionStore((state) => state.recommendation)
  const reset = useSessionStore((state) => state.reset)

  return (
    <div className="min-h-screen bg-white text-left text-stone-900">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <h1 className="text-xl font-semibold tracking-tight">Sniff</h1>
        <Badge variant="outline">Sandbox — simulated Visa flow</Badge>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        {stage === "ready" ? (
          <div className="space-y-6">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-2xl font-semibold">Results for “{query}”</h2>
              <Button type="button" variant="outline" onClick={reset}>
                Start over
              </Button>
            </div>
            <ResultsGrid
              listings={listings}
              checks={checks}
              scores={scores}
              recommendation={recommendation}
            />
          </div>
        ) : (
          <DiscoveryFlow onStarted={() => undefined} />
        )}
      </main>
    </div>
  )
}
