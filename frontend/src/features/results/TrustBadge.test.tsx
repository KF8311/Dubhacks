import { render, screen } from "@testing-library/react"
import { expect, test } from "vitest"
import { TrustBadge } from "./TrustBadge.tsx"

test("shows the score for a scored merchant", () => {
  render(<TrustBadge score={92} verdict="trusted" />)
  expect(screen.getByText(/92\s*·\s*Trusted/)).toBeInTheDocument()
})

test("allowlisted merchants read as verified rather than a zero score", () => {
  render(<TrustBadge score={0} verdict="trusted" allowlisted />)
  expect(screen.getByText(/Verified\s*·\s*Trusted/)).toBeInTheDocument()
  expect(screen.queryByText(/^0/)).not.toBeInTheDocument()
})
