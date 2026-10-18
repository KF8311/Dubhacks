/**
 * The Spectrum bridge runs beside the dev server and can text the shopper.
 * It is local-only (127.0.0.1) and can only message a number that replied Y
 * to the bridge's opt-in text, the configured number, or the chat that last
 * texted it, so these calls carry a message but never choose a recipient.
 * A deployed website has no bridge; the caller falls back to the copyable
 * link.
 */
export function phoneBridgeBase(): string {
  const host = typeof window === "undefined" ? "localhost" : window.location.hostname || "localhost"
  return `http://${host}:8787`
}

export type PhoneOptInStatus = "pending" | "confirmed" | "declined" | "expired"

export type PhoneOptIn = {
  request_id: string
  status: PhoneOptInStatus
}

/** The forms the bridge accepts: E.164, or a US 10/11-digit number. */
export function looksLikePhone(raw: string): boolean {
  const cleaned = raw.trim().replace(/[\s().-]/g, "")
  return /^\+\d{8,15}$/.test(cleaned) || /^\d{10}$/.test(cleaned) || /^1\d{10}$/.test(cleaned)
}

async function bridgeRequest<T>(
  path: string,
  init?: RequestInit,
  timeoutMs = 8000,
): Promise<T> {
  const response = await fetch(`${phoneBridgeBase()}${path}`, {
    method: init?.method ?? "GET",
    headers: { "content-type": "application/json" },
    body: init?.body,
    signal: AbortSignal.timeout(timeoutMs),
  })
  if (!response.ok) {
    let message = "The phone bridge did not accept the request."
    try {
      const body = (await response.json()) as { error?: string }
      if (body.error) message = body.error
    } catch {
      // Keep the generic message when the bridge answers with plain text.
    }
    throw new Error(message)
  }
  return (await response.json()) as T
}

export async function sendPhoneText(text: string): Promise<void> {
  await bridgeRequest<{ ok: true }>("/send", {
    method: "POST",
    body: JSON.stringify({ text }),
  }, 15000)
}

/**
 * Ask the bridge to text `phone` for permission. The number is not stored by
 * the site. Opening the iMessage chat can take a few seconds on a cold start,
 * so this request waits longer than the other bridge calls.
 */
export async function startPhoneOptIn(phone: string): Promise<PhoneOptIn> {
  return bridgeRequest<PhoneOptIn>("/opt-in", {
    method: "POST",
    body: JSON.stringify({ phone }),
  }, 25000)
}

export async function getPhoneOptIn(requestId: string): Promise<PhoneOptIn> {
  return bridgeRequest<PhoneOptIn>(`/opt-in/${encodeURIComponent(requestId)}`)
}

/** Send only to a number that already replied Y. */
export async function sendPhoneNotification(requestId: string, text: string): Promise<void> {
  await bridgeRequest<{ ok: true }>(`/notify/${encodeURIComponent(requestId)}`, {
    method: "POST",
    body: JSON.stringify({ text }),
  }, 15000)
}
