import { CheckWalkthrough } from "@/components/CheckWalkthrough.tsx"
import { go } from "@/lib/path.ts"

export function HowItWorks({ embedded = false }: { embedded?: boolean }) {
  return (
    <article className="how-stage">
      <header className="how-hero">
        <p className="shop-kicker">The process</p>
        <h1 className="font-heading text-4xl font-semibold tracking-tight sm:text-6xl">
          How Sykes checks a store
        </h1>
        <p className="mt-4 max-w-2xl text-lg leading-relaxed text-[color-mix(in_srgb,var(--paper)_82%,transparent)]">
          You shop. Sykes investigates. Checkout stays closed until a merchant earns it. The agent cannot
          pay a merchant it cannot verify.
        </p>
      </header>
      <div className="shop-floor space-y-10">
        <CheckWalkthrough />
        <section className="ticket-best rounded-lg p-6 sm:p-8">
          <h2 className="font-heading text-2xl font-semibold">Then we pick a price</h2>
          <p className="mt-3 max-w-prose leading-relaxed text-muted-foreground">
            The recommendation is the cheapest listing that passed — not the cheapest thing on the page.
            Danger stays in view so you can see what got refused. Pay is a sandbox Visa flow: mandate,
            passkey, receipt. No real card is charged.
          </p>
        </section>
        {embedded ? null : (
          <button type="button" className="text-sm font-medium text-accent underline" onClick={() => go("/")}>
            Back to the shop
          </button>
        )}
      </div>
    </article>
  )
}
