import { go } from "@/lib/path.ts"

export function About() {
  return (
    <article className="mx-auto max-w-2xl space-y-8">
      <p className="text-sm font-medium text-accent">The shopkeeper</p>
      <h1 className="font-heading text-4xl font-semibold tracking-tight">About Sykes</h1>
      <p className="text-lg leading-relaxed">
        Sykes is the friend who already walked the aisle for you. Named like a shopkeeper, built as a
        consumer shopping agent: find the deal, check the store, pay only if it holds up.
      </p>
      <p className="leading-relaxed text-muted-foreground">
        Most shopping sites show you a price and a photo. Sykes shows you why a merchant is trusted,
        caution, or danger — five checks, a score you can read, and a checkout that refuses anything
        that did not pass. New shoppers get a storefront. Returning ones get the same shelves, faster.
      </p>
      <p className="leading-relaxed text-muted-foreground">
        This build is for the Visa Reimagine Shopping track at DubHacks. Payment is labeled on every
        screen: a simulated Visa Intelligent Commerce flow. Listings can be live, but the charge never
        is.
      </p>
      <button
        type="button"
        className="text-sm font-medium text-accent underline"
        onClick={() => go("/")}
      >
        Start a search
      </button>
    </article>
  )
}
