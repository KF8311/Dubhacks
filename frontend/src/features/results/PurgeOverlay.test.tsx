import { render, waitFor } from "@testing-library/react"
import { PurgeOverlay } from "./PurgeOverlay.tsx"

test("reduced motion finishes the purge without waiting", async () => {
  window.matchMedia = ((query: string) => ({
    matches: query.includes("reduce"),
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
  })) as typeof window.matchMedia
  const onComplete = vi.fn()
  render(<PurgeOverlay active onComplete={onComplete} />)
  await waitFor(() => expect(onComplete).toHaveBeenCalled())
})
