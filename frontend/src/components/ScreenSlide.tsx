import { type ReactNode } from "react"
import { cn } from "cn"

type Props = {
  /** Changing this remounts the panel, replaying the entrance. */
  step: string
  className?: string
  children: ReactNode
}

/**
 * One screen in the shop's sequence — search, questions, results. The panel
 * slides in from the right when the shopper advances, which makes the flow read
 * as moving along a counter instead of swapping pages.
 */
export function ScreenSlide({ step, className, children }: Props) {
  return (
    <div key={step} className={cn("screen-enter min-w-0", className)}>
      {children}
    </div>
  )
}
