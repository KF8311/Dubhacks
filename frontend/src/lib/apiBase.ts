/** Browser API origin. Empty means same-origin `/api` (Vercel services rewrite). */
type ApiEnv = { VITE_API_BASE_URL?: string; DEV?: boolean }

export function apiBase(
  env: ApiEnv = import.meta.env,
  hostname: string = window.location.hostname,
): string {
  const raw = env.VITE_API_BASE_URL
  if (raw) return raw.replace(/\/$/, "")
  // A Vite dev server has no /api proxy: talk to Uvicorn directly so local
  // dev still works with no `.env`. A production build is served beside /api
  // by the Vercel service rewrite, so same-origin is correct there.
  //
  // Use the page's hostname, not `localhost`: a phone that opens the dev server
  // at http://192.168.1.20:5173 must reach the API at that same machine. With
  // `localhost` it would call itself and the pay link would look broken.
  if (env.DEV) return `http://${hostname || "localhost"}:8000`
  return ""
}
