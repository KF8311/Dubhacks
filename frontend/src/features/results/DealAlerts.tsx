import { useEffect, useState, type FormEvent } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  getPhoneOptIn,
  startPhoneOptIn,
  type PhoneOptInStatus,
} from "@/lib/phoneBridge.ts"

const FAILED_TO_REACH =
  "Could not reach the phone bridge. Start it with `bun start` in dub-spectrum."

export function DealAlerts() {
  const [phone, setPhone] = useState("")
  const [submitted, setSubmitted] = useState("")
  const [requestId, setRequestId] = useState<string | null>(null)
  const [status, setStatus] = useState<PhoneOptInStatus | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!requestId || status !== "pending") return
    const id = requestId
    let active = true

    async function check() {
      try {
        const next = await getPhoneOptIn(id)
        if (!active) return
        setStatus(next.status)
        setError(null)
      } catch (caught) {
        if (!active) return
        setError(caught instanceof Error ? caught.message : "Could not check the confirmation.")
      }
    }

    void check()
    const timer = setInterval(() => void check(), 3000)
    return () => {
      active = false
      clearInterval(timer)
    }
  }, [requestId, status])

  async function onStart(event: FormEvent) {
    event.preventDefault()
    const trimmed = phone.trim()
    if (!trimmed || busy) return
    setBusy(true)
    setError(null)
    try {
      const next = await startPhoneOptIn(trimmed)
      setSubmitted(trimmed)
      setRequestId(next.request_id)
      setStatus(next.status)
    } catch (caught) {
      setError(
        caught instanceof Error && caught.message === "Failed to fetch"
          ? FAILED_TO_REACH
          : caught instanceof Error
            ? caught.message
            : "Could not text that number.",
      )
    } finally {
      setBusy(false)
    }
  }

  function reset() {
    setPhone("")
    setSubmitted("")
    setRequestId(null)
    setStatus(null)
    setError(null)
  }

  const last4 = submitted.replace(/\D/g, "").slice(-4)
  const active = requestId !== null

  return (
    <section className="ticket mt-4 rounded-3xl p-3.5" aria-labelledby="deal-alerts-title">
      <h2 id="deal-alerts-title" className="font-heading text-sm font-semibold">
        Deal alerts
      </h2>

      {status === "confirmed" ? (
        <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
          On for ••••{last4}. The <span className="font-medium text-foreground">Send</span>{" "}
          buttons on every card now text this number.
        </p>
      ) : (
        <>
          <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
            Get the best trusted pick by text. We ask for a Y/N reply before sending anything
            else.
          </p>

          {active ? (
            <p className="mt-2 text-xs font-medium" role="status">
              {status === "pending"
                ? "Check your phone — reply Y to turn alerts on, or N to skip."
                : status === "declined"
                  ? "No alerts will be sent to that number."
                  : "That request expired. Send it again."}
            </p>
          ) : (
            <form className="mt-2 flex gap-2" onSubmit={(event) => void onStart(event)}>
              <Input
                id="deal-phone"
                type="tel"
                inputMode="tel"
                autoComplete="tel"
                aria-label="Your phone number"
                placeholder="+1 415 555 0123"
                value={phone}
                disabled={busy}
                className="h-8 flex-1 rounded-full bg-[var(--paper)] px-3 text-xs"
                onChange={(event) => setPhone(event.target.value)}
              />
              <Button
                type="submit"
                disabled={busy || phone.trim().length === 0}
                className="h-8 rounded-full px-3 text-xs font-semibold"
              >
                {busy ? "Sending…" : "Text me"}
              </Button>
            </form>
          )}

          <p className="mt-2 text-[0.7rem] leading-relaxed text-muted-foreground">
            Sent only to your local bridge; the number is not saved by the app.
          </p>
        </>
      )}

      {active ? (
        <button
          type="button"
          className="mt-2 text-xs font-medium text-accent underline underline-offset-4"
          onClick={reset}
        >
          Use a different number
        </button>
      ) : null}

      {error ? (
        <p className="mt-2 text-xs text-[color:var(--trust-danger)]" role="alert">
          {error}
        </p>
      ) : null}
    </section>
  )
}
