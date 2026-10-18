import { useEffect, useState } from "react"

const STEPS = ["Tokenizing", "Authorizing", "Capturing"]

type Props = {
  onDone: () => void
}

export function ProcessingState({ onDone }: Props) {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const timers = [1, 2].map((index) => window.setTimeout(() => setStep(index), index * 300))
    const done = window.setTimeout(onDone, 1000)
    return () => {
      timers.forEach((timer) => window.clearTimeout(timer))
      window.clearTimeout(done)
    }
  }, [onDone])

  return (
    <div className="space-y-2" aria-busy="true">
      <h3 className="text-lg font-semibold">Processing</h3>
      <ol className="space-y-1">
        {STEPS.map((label, index) => (
          <li key={label} className={index <= step ? "font-semibold text-stone-900" : "text-stone-600"}>
            {label}
          </li>
        ))}
      </ol>
    </div>
  )
}
