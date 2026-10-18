import { Button } from "@/components/ui/button"
import { formatCents } from "@/lib/format.ts"
import type { Mandate } from "@/lib/types.ts"

type Props = {
  mandate: Mandate
  onContinue: () => void
}

export function MandateCard({ mandate, onContinue }: Props) {
  const expires = new Date(mandate.expires_at).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  })

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">Mandate</h3>
      <p className="text-foreground">
        {mandate.merchant_name} · {mandate.merchant_domain}
      </p>
      <p className="text-foreground">
        Cap {formatCents(mandate.max_amount_cents, mandate.currency)}
      </p>
      <p className="text-sm text-muted-foreground">Expires at {expires}</p>
      <Button type="button" onClick={onContinue}>
        Continue
      </Button>
    </div>
  )
}
