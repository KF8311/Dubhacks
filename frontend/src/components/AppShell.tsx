import { type ReactNode, useEffect, useState } from "react"
import { BrandMark } from "@/components/BrandMark.tsx"
import { DealAlerts } from "@/features/results/DealAlerts.tsx"
import { currentPath, go, withSearch } from "@/lib/path.ts"

type Props = {
  children: ReactNode
}

function NavLink({ to, label }: { to: string; label: string }) {
  const [path, setPath] = useState(currentPath)
  useEffect(() => {
    const onPop = () => setPath(currentPath())
    window.addEventListener("popstate", onPop)
    return () => window.removeEventListener("popstate", onPop)
  }, [])
  const current = path === to
  return (
    <a
      href={withSearch(to)}
      aria-current={current ? "page" : undefined}
      className={
        current
          ? "rounded-full bg-[var(--paper)] px-3 py-1.5 font-semibold text-foreground shadow-[0_6px_16px_-14px_rgb(23_37_30/70%)]"
          : "rounded-full px-3 py-1.5 text-muted-foreground hover:bg-[var(--marigold-wash)] hover:text-foreground"
      }
      onClick={(event) => {
        event.preventDefault()
        go(to)
      }}
    >
      {label}
    </a>
  )
}

export function AppShell({ children }: Props) {
  // The phone-facing pages keep a single job: approving or showing a receipt.
  const showDealAlerts = !/^\/(pay|r)\//.test(currentPath())
  return (
    <div className="app-canvas min-h-screen text-left text-foreground">
      <header className="sticky top-0 z-20 border-b border-border bg-[color-mix(in_srgb,var(--paper)_92%,transparent)] backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 sm:px-6">
          <a
            href={withSearch("/")}
            className="inline-flex min-w-0 items-center rounded-full bg-[var(--paper)] px-3 py-1.5 shadow-[0_10px_24px_-20px_rgb(23_37_30/60%)] ring-1 ring-[color-mix(in_srgb,var(--ink)_10%,transparent)]"
            onClick={(event) => {
              event.preventDefault()
              go("/")
            }}
          >
            <BrandMark />
          </a>
          <div className="ml-auto flex min-w-0 flex-wrap items-center justify-end gap-x-4 gap-y-2">
            <nav className="flex items-center gap-4 text-sm" aria-label="Sykes">
              <NavLink to="/" label="Shop" />
              <NavLink to="/how" label="How it works" />
              <NavLink to="/about" label="About" />
            </nav>
            {showDealAlerts ? (
              <div className="flex items-center gap-3">
                <span className="hidden h-6 w-px bg-border sm:block" aria-hidden="true" />
                <DealAlerts />
              </div>
            ) : null}
          </div>
        </div>
      </header>
      <main className="mx-auto min-w-0 max-w-6xl space-y-8 px-4 py-8 sm:px-6 sm:py-12">{children}</main>
      <footer className="border-t border-border bg-[var(--paper)]">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4 text-sm text-muted-foreground sm:px-6">
          <p>Sykes — a shopkeeper for the internet.</p>
          <a
            href={withSearch("/how")}
            className="font-medium text-accent underline"
            onClick={(event) => {
              event.preventDefault()
              go("/how")
            }}
          >
            The five checks
          </a>
        </div>
      </footer>
    </div>
  )
}
