/** Browser API origin. Empty means same-origin `/api` (Vercel services rewrite). */
export function apiBase(): string {
  const raw = import.meta.env.VITE_API_BASE_URL
  if (!raw) return ""
  return raw.replace(/\/$/, "")
}
