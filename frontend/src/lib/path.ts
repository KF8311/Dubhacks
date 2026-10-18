export function currentPath(): string {
  const raw = window.location.pathname.replace(/\/+$/, "")
  return raw === "" ? "/" : raw
}

export function withSearch(path: string): string {
  return `${path}${window.location.search}`
}

export function go(path: string): void {
  const next = withSearch(path)
  const here = `${window.location.pathname}${window.location.search}`
  if (here === next) return
  window.history.pushState({}, "", next)
  window.dispatchEvent(new PopStateEvent("popstate"))
}
