import { apiBase } from "@/lib/apiBase.ts"
import type { StreamEvent } from "@/lib/types.ts"

const EVENT_TYPES = [
  "session.stage",
  "search.started",
  "search.completed",
  "listing.found",
  "check.started",
  "check.completed",
  "listing.scored",
  "recommendation.ready",
  "investigation.complete",
  "session.error",
] as const

export function openSessionEvents(
  sessionId: string,
  handlers: { onEvent: (event: StreamEvent) => void; onError: () => void },
): () => void {
  const base = apiBase()
  const source = new EventSource(`${base}/api/sessions/${sessionId}/events`)
  let closed = false

  const close = () => {
    if (closed) return
    closed = true
    source.close()
  }

  for (const type of EVENT_TYPES) {
    source.addEventListener(type, (message) => {
      const data = JSON.parse((message as MessageEvent<string>).data) as StreamEvent & {
        recoverable?: boolean
      }
      handlers.onEvent({ ...data, type: data.type ?? type, seq: Number(data.seq) })
      if (type === "investigation.complete") close()
      if (type === "session.error" && data.recoverable === false) close()
    })
  }

  source.onerror = () => {
    close()
    handlers.onError()
  }

  return close
}
