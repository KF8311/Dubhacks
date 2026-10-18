import { useEffect, useState, type FormEvent } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  getPhoneOptIn,
  looksLikePhone,
  startPhoneOptIn,
  type PhoneOptInStatus,
} from "@/lib/phoneBridge.ts"

const FAILED_TO_REACH =
  "Could not reach the phone bridge. Start it with `bun start` in dub-spectrum."

const PRIVACY_NOTE = "Sent only to your local bridge; the number is not saved by the app."

/**
 * Deal alerts sit in the site header so the phone option is visible from the
 * first screen. The number goes to the local bridge only; the bridge keeps the
 * consent request and never the number.
 */
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
    if (!looksLikePhone(trimmed)) {
      setError("Use the full number with its country code, e.g. +1 415 555 0123.")
      return
    }
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
  const retryable = status === "declined" || status === "expired"

  return (
    <div
      className="flex min-w-0 flex-wrap items-center justify-end gap-x-2 gap-y-1.5"
      aria-labelledby="deal-alerts-title"
    >
      <span id="deal-alerts-title" className="text-xs font-semibold text-muted-foreground">
        Deal alerts
      </span>

      {status === "confirmed" ? (
        <>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-[var(--trust-trusted-bg)] px-2.5 py-1 text-xs font-semibold text-[color:var(--trust-trusted)] ring-1 ring-[color-mix(in_srgb,var(--trust-trusted)_35%,transparent)]">
            <span className="size-1.5 rounded-full bg-current" aria-hidden="true" />
            On for ••••{last4}
          </span>
          <span className="hidden text-xs text-muted-foreground sm:inline">
            Send buttons text this number.
          </span>
          <button
            type="button"
            className="text-xs font-medium text-accent underline underline-offset-4"
            onClick={reset}
          >
            Change
          </button>
        </>
      ) : active ? (
        <>
          <span className="text-xs font-medium" role="status">
            {status === "pending"
              ? "Reply Y to turn alerts on, or N to skip."
              : status === "declined"
                ? "No alerts will be sent to that number."
                : "That request expired. Send it again."}
          </span>
          <button
            type="button"
            className="text-xs font-medium text-accent underline underline-offset-4"
            onClick={reset}
          >
            {retryable ? "Try another number" : "Cancel"}
          </button>
        </>
      ) : (
        <form
          className="flex items-center gap-2"
          title={PRIVACY_NOTE}
          onSubmit={(event) => void onStart(event)}
        >
          <Input
            id="deal-phone"
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            aria-label="Your phone number"
            aria-describedby="deal-phone-note"
            placeholder="+1 415 555 0123"
            value={phone}
            disabled={busy}
            className="h-9 w-40 rounded-full bg-[var(--paper)] px-3 text-xs sm:w-44"
            onChange={(event) => setPhone(event.target.value)}
          />
          <Button
            type="submit"
            disabled={busy || phone.trim().length === 0}
            className="h-9 rounded-full px-3.5 text-xs font-semibold"
          >
            {busy ? "Sending…" : "Text me"}
          </Button>
        </form>
      )}

      <span id="deal-phone-note" className="sr-only">
        {PRIVACY_NOTE}
      </span>

      {error ? (
        <p
          role="alert"
          className="basis-full text-right text-xs leading-relaxed text-[color:var(--trust-danger)]"
        >
          {error}
        </p>
      ) : null}
    </div>
  )
}
