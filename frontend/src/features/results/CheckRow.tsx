import type { TrustCheckResult, TrustStatus } from "@/lib/types.ts"

type Props = {
  check: TrustCheckResult
}

const statusLabel: Record<TrustStatus, string> = {
  passed: "Passed",
  warning: "Warning",
  failed: "Failed",
  skipped: "Skipped",
}

export function CheckRow({ check }: Props) {
  return (
    <div className="flex items-start justify-between gap-3 border-t py-2 text-sm">
      <div>
        <p className="font-medium">{check.name}</p>
        <p className="text-stone-600">{check.summary}</p>
      </div>
      <p className="shrink-0 font-medium">{statusLabel[check.status]}</p>
    </div>
  )
}
