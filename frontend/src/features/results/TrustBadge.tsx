import { Badge } from "@/components/ui/badge"
import type { Verdict } from "@/lib/types.ts"

type Props = {
  score?: number
  verdict?: Verdict
}

const styleFor: Record<Verdict, { color: string; background: string; label: string }> = {
  trusted: {
    color: "var(--trust-trusted)",
    background: "var(--trust-trusted-bg)",
    label: "Trusted",
  },
  caution: {
    color: "var(--trust-caution)",
    background: "var(--trust-caution-bg)",
    label: "Caution",
  },
  danger: {
    color: "var(--trust-danger)",
    background: "var(--trust-danger-bg)",
    label: "Danger",
  },
}

export function TrustBadge({ score, verdict }: Props) {
  if (score === undefined || verdict === undefined) {
    return (
      <Badge
        variant="outline"
        style={{
          color: "var(--trust-pending)",
          background: "var(--trust-pending-bg)",
        }}
      >
        Checking
      </Badge>
    )
  }
  const tone = styleFor[verdict]
  return (
    <Badge variant="outline" style={{ color: tone.color, background: tone.background }}>
      {score} · {tone.label}
    </Badge>
  )
}
