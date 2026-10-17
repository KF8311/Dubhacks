import { Button } from "@/components/ui/button"
import { formatCents } from "@/lib/format.ts"
import type { Listing } from "@/lib/types.ts"

type Props = {
  listing: Listing
}

export function CheckoutSheet({ listing }: Props) {
  return (
    <aside className="rounded-xl border bg-white p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-stone-500">
        Sandbox — simulated Visa flow
      </p>
      <h3 className="mt-2 text-lg font-semibold">Checkout</h3>
      <p className="mt-2 text-stone-700">
        {listing.merchant_name} · {formatCents(listing.price_cents, listing.currency)}
      </p>
      <Button type="button" className="mt-4" disabled>
        Pay
      </Button>
    </aside>
  )
}
