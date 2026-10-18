/**
 * The Spectrum bridge runs beside the dev server and can text the shopper.
 * It is local-only (127.0.0.1) and only sends to the configured number or the
 * chat that last texted it, so this call can carry a message but not a
 * recipient. A deployed website has no bridge; the caller falls back to the
 * copyable link.
 */
export function phoneBridgeBase(): string {
  const host = typeof window === "undefined" ? "localhost" : window.location.hostname || "localhost"
  return `http://${host}:8787`
}

export async function sendPhoneText(text: string): Promise<void> {
  const response = await fetch(`${phoneBridgeBase()}/send`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ text }),
    signal: AbortSignal.timeout(8000),
  })
  if (!response.ok) {
    let message = "The phone bridge did not accept the message."
    try {
      const body = (await response.json()) as { error?: string }
      if (body.error) message = body.error
    } catch {
      // Keep the generic message when the bridge answers with plain text.
    }
    throw new Error(message)
  }
}
