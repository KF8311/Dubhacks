import { useState } from "react"
import { explainCheck, type ExplainSource } from "@/lib/api.ts"
import { useSessionStore } from "@/store/sessionStore.ts"
import type { TrustCheckResult, TrustStatus } from "@/lib/types.ts"

type Props = {
  check: TrustCheckResult
  listingId: string
}

const statusLabel: Record<TrustStatus, string> = {
  passed: "Passed",
  warning: "Warning",
  failed: "Failed",
  skipped: "Could not verify",
}

const statusColor: Record<TrustStatus, string> = {
  passed: "text-[color:var(--trust-trusted)]",
  warning: "text-[color:var(--trust-caution)]",
  failed: "text-[color:var(--trust-danger)]",
  skipped: "text-stone-600",
}

export function CheckRow({ check, listingId }: Props) {
  const sessionId = useSessionStore((state) => state.sessionId)
  const [explanation, setExplanation] = useState<{ text: string; source: ExplainSource } | null>(null)
  const [busy, setBusy] = useState(false)

  async function onExplain() {
    if (!sessionId || busy) return
    setBusy(true)
    try {
      setExplanation(await explainCheck({ sessionId, listingId, checkId: check.id }))
    } catch {
      setExplanation({ text: check.summary, source: "template" })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex items-start justify-between gap-3 border-t py-2 text-sm">
      <div>
        <p className="font-medium">{check.name}</p>
        <p className="text-muted-foreground">{check.summary}</p>
        {explanation ? (
          <p className="mt-1 text-foreground">
            {explanation.text}{" "}
            <span className="ml-1 rounded-full border px-2 py-0.5 align-middle text-xs text-muted-foreground">
              {explanation.source === "gemini" ? "AI-generated" : "From evidence"}
            </span>
          </p>
        ) : null}
        <button
          type="button"
          className="mt-1 text-xs font-medium text-accent underline"
          onClick={onExplain}
          disabled={busy || !sessionId}
        >
          {busy ? "Explaining…" : "Explain"}
        </button>
      </div>
      <p className={`shrink-0 font-medium ${statusColor[check.status]}`}>{statusLabel[check.status]}</p>
    </div>
  )
}
