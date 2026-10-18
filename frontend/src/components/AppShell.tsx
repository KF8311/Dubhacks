import type { ReactNode } from "react"
import { Badge } from "@/components/ui/badge"
import { BrandMark } from "@/components/BrandMark.tsx"
import { SANDBOX_LABEL } from "@/features/checkout/CheckoutSheet.tsx"

type Props = {
  children: ReactNode
}

export function AppShell({ children }: Props) {
  return (
    <div className="app-canvas min-h-screen text-left text-foreground">
      <header className="sticky top-0 z-20 border-b border-border/80 bg-[color-mix(in_srgb,var(--background)_82%,white)] backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-2.5 sm:px-6">
          <BrandMark />
          <Badge
            variant="outline"
            className="h-auto max-w-[min(100%,20rem)] shrink whitespace-normal border-[#00A5B5]/40 bg-white/80 py-1.5 text-left text-[#101A2B] sm:max-w-full"
          >
            {SANDBOX_LABEL}
          </Badge>
        </div>
      </header>
      <main className="mx-auto min-w-0 max-w-6xl space-y-6 px-4 py-8 sm:px-6 sm:py-10">{children}</main>
    </div>
  )
}
