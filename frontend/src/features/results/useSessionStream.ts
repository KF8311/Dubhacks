import { useCallback, useEffect, useState } from "react"
import { getSnapshot } from "@/lib/api.ts"
import { openSessionEvents } from "@/lib/sse.ts"
import type { StreamEvent } from "@/lib/types.ts"
import { useSessionStore } from "@/store/sessionStore.ts"
import { MOCK_EVENT_MS, buildMockEvents } from "@/features/results/mockEvents.ts"

const useMock = import.meta.env.VITE_USE_MOCK !== "0"

export function useSessionStream(sessionId: string | null) {
  const lastSeq = useSessionStore((state) => state.lastSeq)
  const [applied, setApplied] = useState(0)

  const onEvent = useCallback((event: StreamEvent) => {
    const accepted = useSessionStore.getState().applyEvent(event)
    if (accepted) setApplied((count) => count + 1)
  }, [])

  useEffect(() => {
    if (!sessionId) return

    if (useMock) {
      const timers = buildMockEvents().map((event, index) =>
        window.setTimeout(() => onEvent(event), index * MOCK_EVENT_MS),
      )
      return () => timers.forEach((timer) => window.clearTimeout(timer))
    }

    return openSessionEvents(sessionId, {
      onEvent,
      onError: () => {
        void getSnapshot(sessionId)
          .then((snapshot) => useSessionStore.getState().applySnapshot(snapshot))
          .catch(() => {
            useSessionStore.getState().applyEvent({
              type: "session.error",
              seq: useSessionStore.getState().lastSeq + 1,
              payload: { message: "The live update stopped. Showing the last saved results.", recoverable: true },
            })
          })
      },
    })
  }, [sessionId, onEvent])

  return { lastSeq, onEvent, applied }
}
