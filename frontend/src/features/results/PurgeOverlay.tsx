import { useEffect } from "react"
import { motion } from "framer-motion"

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

  if (!active) return null

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-red-950/80 text-4xl font-bold tracking-wide text-white"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      role="status"
    >
      PURGE CURSED
    </motion.div>
  )
}
