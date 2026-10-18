import { type ReactNode, useEffect, useState } from "react"
import { BrandMark } from "@/components/BrandMark.tsx"
import { SANDBOX_LABEL } from "@/features/checkout/CheckoutSheet.tsx"
import { PAGE_SECTIONS, activeSectionPath, currentPath, go, scrollToId, withSearch } from "@/lib/path.ts"

type Props = {
  children: ReactNode
  bleed?: boolean
  spy?: boolean
}

function NavLink({
  to,
  label,
  section,
  onSection,
}: {
  to: string
  label: string
  section: string
  onSection?: (path: string) => void
}) {
  const current = section === to
  return (
    <a
      href={withSearch(to)}
      aria-current={current ? "page" : undefined}
      className={
        current
          ? "font-semibold text-foreground"
          : "text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
      }
      onClick={(event) => {
        event.preventDefault()
        if (onSection) {
          onSection(to)
          return
        }
        go(to)
      }}
    >
      {label}
    </a>
  )
}

export function AppShell({ children, bleed = false, spy = false }: Props) {
  const [section, setSection] = useState(currentPath)

  useEffect(() => {
    const onPop = () => setSection(currentPath())
    window.addEventListener("popstate", onPop)
    return () => window.removeEventListener("popstate", onPop)
  }, [])

  useEffect(() => {
    if (!spy) return
    const sync = () => {
      const next = activeSectionPath((id) => {
        const node = document.getElementById(id)
        if (!node) return null
        const rect = node.getBoundingClientRect()
        return { top: rect.top, bottom: rect.bottom }
      })
      setSection(next)
      if (next !== currentPath()) {
        window.history.replaceState({}, "", withSearch(next))
      }
    }
    sync()
    window.addEventListener("scroll", sync, { passive: true })
    window.addEventListener("resize", sync)
    return () => {
      window.removeEventListener("scroll", sync)
      window.removeEventListener("resize", sync)
    }
  }, [spy])

  function goSection(path: string) {
    go(path, { scroll: false })
    setSection(path)
    const id = PAGE_SECTIONS.find(([, href]) => href === path)?.[0] ?? "shop"
    scrollToId(id)
  }

  return (
    <div className="app-canvas min-h-screen text-left text-foreground">
      <header className="sticky top-0 z-30 border-b border-border bg-[color-mix(in_srgb,var(--paper)_92%,transparent)] backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <a
            href={withSearch("/")}
            className="min-w-0"
            onClick={(event) => {
              event.preventDefault()
              if (spy) {
                goSection("/")
                return
              }
              go("/")
            }}
          >
            <BrandMark />
          </a>
          <nav className="flex items-center gap-4 text-sm" aria-label="Sykes">
            <NavLink to="/" label="Shop" section={section} onSection={spy ? goSection : undefined} />
            <NavLink to="/how" label="How it works" section={section} onSection={spy ? goSection : undefined} />
            <NavLink to="/about" label="About" section={section} onSection={spy ? goSection : undefined} />
          </nav>
        </div>
        <p className="mx-auto max-w-6xl px-4 pb-2 text-xs text-muted-foreground sm:px-6">
          {SANDBOX_LABEL}
        </p>
      </header>
      <main
        className={
          bleed ? "min-w-0" : "mx-auto min-w-0 max-w-6xl space-y-8 px-4 py-8 sm:px-6 sm:py-12"
        }
      >
        {children}
      </main>
      <footer className="border-t border-border bg-[var(--paper)]">
        <div className="mx-auto max-w-6xl px-4 py-4 text-sm text-muted-foreground sm:px-6">
          <p>Sykes — a shopkeeper for the internet.</p>
        </div>
      </footer>
    </div>
  )
}
