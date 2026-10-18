import { useEffect } from "react"
import { motion, useReducedMotion } from "framer-motion"

type Props = {
  active: boolean
  onComplete: () => void
}

export function PurgeOverlay({ active, onComplete }: Props) {
  useEffect(() => {
    if (!active) return
    const reduced = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false
    const timer = window.setTimeout(onComplete, reduced ? 0 : 700)
    return () => window.clearTimeout(timer)
  }, [active, onComplete])

  const reduced = useReducedMotion()
  if (!active) return null

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center px-6 text-center text-3xl font-bold tracking-wide text-white sm:text-4xl bg-red-950/80"
      initial={reduced ? false : { opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: reduced ? 0 : 0.25 }}
      role="status"
    >
      PURGE CURSED
    </motion.div>
  )
}
