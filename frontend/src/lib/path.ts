export const PAGE_SECTIONS = [
  ["shop", "/"],
  ["how", "/how"],
  ["about", "/about"],
] as const

/** Pixel line under the sticky header used to decide which nav item is current. */
const SECTION_LINE = 120

export function currentPath(): string {
  const raw = window.location.pathname.replace(/\/+$/, "")
  return raw === "" ? "/" : raw
}

export function activeSectionPath(
  rectFor: (id: string) => { top: number; bottom: number } | null,
  line = SECTION_LINE,
): string {
  let current = "/"
  for (const [id, path] of PAGE_SECTIONS) {
    const rect = rectFor(id)
    if (!rect || rect.bottom <= line) continue
    if (rect.top <= line) current = path
  }
  return current
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
