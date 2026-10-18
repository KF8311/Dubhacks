import { useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { go } from "@/lib/path.ts"

const CHAPTERS = [
  {
    title: "The shopkeeper",
    body: "Sykes is the friend who already walked the aisle for you. Named like a shopkeeper, built as a consumer shopping agent: find the deal, check the store, pay only if it holds up.",
  },
  {
    title: "Why it refuses",
    body: "Most shopping sites show you a price and a photo. Sykes shows you why a merchant is trusted, caution, or danger — five checks, a score you can read, and a checkout that refuses anything that did not pass. New shoppers get a storefront. Returning ones get the same shelves, faster.",
  },
  {
    title: "The sandbox",
    body: "This build is for the Visa Reimagine Shopping track at DubHacks. Payment is labeled on every screen: a simulated Visa Intelligent Commerce flow. Listings can be live, but the charge never is.",
  },
] as const

export function About({ embedded = false }: { embedded?: boolean }) {
  const [active, setActive] = useState(0)
  const chapter = CHAPTERS[active]

  return (
    <article className="about-stage">
      <header className="how-hero">
        <p className="shop-kicker">The shopkeeper</p>
        <h1 className="font-heading text-4xl font-semibold tracking-tight sm:text-6xl">About Sykes</h1>
      </header>
      <div className="shop-floor space-y-8">
        <div role="tablist" aria-label="About chapters" className="flex flex-wrap gap-2">
          {CHAPTERS.map((item, index) => (
            <button
              key={item.title}
              type="button"
              role="tab"
              aria-selected={index === active}
              className={index === active ? "check-tab check-tab-on" : "check-tab"}
              onClick={() => setActive(index)}
            >
              {item.title}
            </button>
          ))}
        </div>
        <div className="ticket-best min-h-52 rounded-lg p-6 sm:p-10" role="tabpanel">
          <AnimatePresence mode="wait">
            <motion.div
              key={chapter.title}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -16 }}
              transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
            >
              <h2 className="font-heading text-3xl font-semibold tracking-tight">{chapter.title}</h2>
              <p className="mt-4 max-w-prose text-lg leading-relaxed">{chapter.body}</p>
            </motion.div>
          </AnimatePresence>
        </div>
        {embedded ? null : (
          <button type="button" className="text-sm font-medium text-accent underline" onClick={() => go("/")}>
            Start a search
          </button>
        )}
      </div>
    </article>
  )
}
