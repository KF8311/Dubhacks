export function currentPath(): string {
  const raw = window.location.pathname.replace(/\/+$/, "")
  return raw === "" ? "/" : raw
}

export function withSearch(path: string): string {
  return `${path}${window.location.search}`
}

export function go(path: string, opts?: { scroll?: boolean }): void {
  const next = withSearch(path)
  const here = `${window.location.pathname}${window.location.search}`
  if (here !== next) {
    window.history.pushState({}, "", next)
    window.dispatchEvent(new PopStateEvent("popstate"))
  }
  if (opts?.scroll !== false) window.scrollTo(0, 0)
}

export function scrollToId(id: string): void {
  const node = document.getElementById(id)
  if (!node?.scrollIntoView) return
  const reduced = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches
  node.scrollIntoView({
    behavior: reduced ? "auto" : "smooth",
    block: "start",
  })
}
