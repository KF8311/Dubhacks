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

async function bridgeRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${phoneBridgeBase()}${path}`, {
    method: init?.method ?? "GET",
    headers: { "content-type": "application/json" },
    body: init?.body,
    signal: AbortSignal.timeout(8000),
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
  })
}

/** Ask the bridge to text `phone` for permission. The number is not stored. */
export async function startPhoneOptIn(phone: string): Promise<PhoneOptIn> {
  return bridgeRequest<PhoneOptIn>("/opt-in", {
    method: "POST",
    body: JSON.stringify({ phone }),
  })
}

export async function getPhoneOptIn(requestId: string): Promise<PhoneOptIn> {
  return bridgeRequest<PhoneOptIn>(`/opt-in/${encodeURIComponent(requestId)}`)
}

/** Send only to a number that already replied Y. */
export async function sendPhoneNotification(requestId: string, text: string): Promise<void> {
  await bridgeRequest<{ ok: true }>(`/notify/${encodeURIComponent(requestId)}`, {
    method: "POST",
    body: JSON.stringify({ text }),
  })
}
