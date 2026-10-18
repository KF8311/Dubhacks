/** Browser API origin. Empty means same-origin `/api` (Vercel services rewrite). */
export function apiBase(pageHost = typeof window === "undefined" ? "" : window.location.hostname): string {
  const raw = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "")
  const deployed = Boolean(pageHost) && pageHost !== "localhost" && pageHost !== "127.0.0.1"
  if (deployed) return ""
  return raw
}
