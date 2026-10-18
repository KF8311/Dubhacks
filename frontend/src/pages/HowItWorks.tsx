import { go } from "@/lib/path.ts"

const CHECKS = [
  {
    name: "Domain age",
    body: "A store that appeared last week is a different kind of risk from one that has been around for years.",
  },
  {
    name: "SSL certificate",
    body: "We look at whether the checkout is actually encrypted, and whether the certificate is brand new.",
  },
  {
    name: "Safe Browsing",
    body: "Google’s threat list is a coarse filter. A miss is not a green light; a hit is a stop.",
  },
  {
    name: "Reddit",
    body: "We scan for scam reports and shipping complaints, not star ratings copied onto the product page.",
  },
  {
    name: "Page flags",
    body: "Countdown timers, crypto-only checkout, and missing returns are pressure tactics, not merchandising.",
  },
]

export function HowItWorks() {
  return (
    <article className="mx-auto max-w-2xl space-y-8">
      <p className="text-sm font-medium text-accent">The process</p>
      <h1 className="font-heading text-4xl font-semibold tracking-tight">How Sykes checks a store</h1>
      <p className="text-lg leading-relaxed text-muted-foreground">
        You shop. Sykes investigates. Checkout stays closed until a merchant earns it. The agent cannot
        pay a merchant it cannot verify.
      </p>
      <ol className="space-y-5">
        {CHECKS.map((check, index) => (
          <li key={check.name} className="ticket rounded-lg p-5">
            <p className="text-sm text-muted-foreground">{index + 1} of 5</p>
            <h2 className="mt-1 font-heading text-xl font-semibold">{check.name}</h2>
            <p className="mt-2 leading-relaxed text-muted-foreground">{check.body}</p>
          </li>
        ))}
      </ol>
      <section className="ticket-best rounded-lg p-5">
        <h2 className="font-heading text-xl font-semibold">Then we pick a price</h2>
        <p className="mt-2 leading-relaxed text-muted-foreground">
          The recommendation is the cheapest listing that passed — not the cheapest thing on the page.
          Danger stays in view so you can see what got refused. Pay is a sandbox Visa flow: mandate,
          passkey, receipt. No real card is charged.
        </p>
      </section>
      <button
        type="button"
        className="text-sm font-medium text-accent underline"
        onClick={() => go("/")}
      >
        Back to the shop
      </button>
    </article>
  )
}
