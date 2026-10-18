import { act, renderHook } from "@testing-library/react"
import { useSessionStream } from "./useSessionStream.ts"

test("applies events and dedupes by seq", () => {
  const { result } = renderHook(() => useSessionStream(null))
  act(() => result.current.onEvent({ type: "check.completed", seq: 1, payload: {} }))
  act(() => result.current.onEvent({ type: "check.completed", seq: 1, payload: {} }))
  expect(result.current.applied).toBe(1)
})
