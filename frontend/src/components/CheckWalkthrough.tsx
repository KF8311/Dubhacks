import { useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { CHECKS } from "@/lib/checks.ts"

export function CheckWalkthrough() {
  const [active, setActive] = useState(0)
  const check = CHECKS[active]

  return (
    <section className="check-walk">
      <h2 className="font-heading text-2xl font-semibold tracking-tight sm:text-3xl">Five trust checks</h2>
      <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground">
        Click a check. Sykes runs all five on every merchant before anyone can pay.
      </p>
      <div className="mt-6 grid gap-4 lg:grid-cols-[14rem_minmax(0,1fr)]">
        <div role="tablist" aria-label="The five checks" className="flex flex-row gap-2 overflow-x-auto lg:flex-col">
          {CHECKS.map((item, index) => {
            const selected = index === active
            return (
              <button
                key={item.name}
                type="button"
                role="tab"
                aria-selected={selected}
                className={selected ? "check-tab check-tab-on" : "check-tab"}
                onClick={() => setActive(index)}
              >
                <span className="check-tab-index">{index + 1}</span>
                {item.name}
              </button>
            )
          })}
        </div>
        <div className="check-panel ticket-best rounded-lg p-6 sm:p-8" role="tabpanel">
          <p className="text-sm text-muted-foreground">
            {active + 1} of {CHECKS.length}
          </p>
          <AnimatePresence mode="wait">
            <motion.div
              key={check.name}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
            >
              <h3 className="mt-2 font-heading text-3xl font-semibold tracking-tight">{check.name}</h3>
              <p className="mt-4 max-w-prose text-lg leading-relaxed">{check.body}</p>
              <p className="mt-3 max-w-prose leading-relaxed text-muted-foreground">{check.detail}</p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  )
}
