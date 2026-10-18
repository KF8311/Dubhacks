/** Browser API origin. Empty means same-origin `/api` (Vercel services rewrite). */
type ApiEnv = { VITE_API_BASE_URL?: string; DEV?: boolean }

export function apiBase(env: ApiEnv = import.meta.env): string {
  const raw = env.VITE_API_BASE_URL
  if (raw) return raw.replace(/\/$/, "")
  // A Vite dev server has no /api proxy: talk to Uvicorn directly so local
  // dev still works with no `.env`. A production build is served beside /api
  // by the Vercel service rewrite, so same-origin is correct there.
  return env.DEV ? "http://localhost:8000" : ""
}
