import type { Listing } from "@/lib/types.ts"

export type ProductLink = { href: string; label: string }

const GOOGLE_HOSTS = new Set(["google.com", "googleusercontent.com"])

function isGoogleHost(host: string): boolean {
  if (GOOGLE_HOSTS.has(host)) return true
  return host.endsWith(".google.com") || host.endsWith(".googleusercontent.com")
}

/**
 * Where the "view" link should go, and what it should say.
 *
 * Google Shopping results carry a real product link on google.com while the
 * retailer is named separately, so the label has to match the destination:
 * calling that link "View at target.com" would be a lie.
 */
export function productLink(
  listing: Pick<Listing, "product_url" | "merchant_domain">,
): ProductLink | null {
  const href = listing.product_url.trim()
  if (!href.startsWith("http")) return null
  let host: string
  try {
    host = new URL(href).hostname.toLowerCase()
  } catch {
    return null
  }
  if (isGoogleHost(host)) return { href, label: "View on Google Shopping" }
  const domain = listing.merchant_domain || host.replace(/^www\./, "")
  return domain ? { href, label: `View at ${domain}` } : null
}
