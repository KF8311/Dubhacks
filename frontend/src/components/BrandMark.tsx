import { cn } from "cn"

type Props = {
  className?: string
  size?: "header" | "hero"
}

export function BrandMark({ className, size = "header" }: Props) {
  return (
    <img
      src="/sykes-logo.svg"
      alt="Sykes"
      className={cn(
        "w-auto max-w-full object-contain object-left",
        size === "hero" ? "h-16 sm:h-20" : "h-10 sm:h-12",
        className,
      )}
    />
  )
}
