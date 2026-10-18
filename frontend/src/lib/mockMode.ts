/**
 * Mock mode is opt-in so the real backend is what the browser talks to by default.
 *
 * Fallback for the demo if the API dies: add `?mock=1` to the URL, or set
 * `VITE_USE_MOCK=1` at build time.
 */
export function isMockMode(): boolean {
  if (typeof window === "undefined") return false
  const params = new URLSearchParams(window.location.search)
  return params.get("mock") === "1" || import.meta.env.VITE_USE_MOCK === "1"
}
