export const CHECKS = [
  {
    name: "Domain age",
    body: "A store that appeared last week is a different kind of risk from one that has been around for years.",
    detail:
      "Most throwaway shops register a domain days before a fake sale. We treat anything under a few months as a warning, and a brand-new store as a stop unless it is on the allowlist.",
  },
  {
    name: "SSL certificate",
    body: "We look at whether the checkout is actually encrypted, and whether the certificate is brand new.",
    detail:
      "HTTPS is table stakes, not a gold star. A certificate issued yesterday on a store you have never heard of is a common scam pattern, not a sign they just launched.",
  },
  {
    name: "Safe Browsing",
    body: "Google’s threat list is a coarse filter. A miss is not a green light; a hit is a stop.",
    detail:
      "If the domain is on a known phishing or malware list, checkout stays closed. If it is not listed, we still run the other four checks — absence from a list is not proof the merchant is real.",
  },
  {
    name: "Reddit",
    body: "We scan for scam reports and shipping complaints, not star ratings copied onto the product page.",
    detail:
      "Merchant sites host their own reviews. We look for threads where people say the package never arrived, the card was charged twice, or the store vanished after payday.",
  },
  {
    name: "Page flags",
    body: "Countdown timers, crypto-only checkout, and missing returns are pressure tactics, not merchandising.",
    detail:
      "A legitimate shop can have a sale. A page that forces crypto, hides a street address, and tells you the deal expires in seven minutes is trying to skip the part where you think.",
  },
] as const
