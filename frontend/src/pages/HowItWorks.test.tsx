import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { HowItWorks } from "./HowItWorks.tsx"

test("clicking a check opens that drawer and hides the previous body", async () => {
  render(<HowItWorks />)
  expect(screen.getByText(/a store that appeared last week/i)).toBeInTheDocument()
  fireEvent.click(screen.getByRole("tab", { name: /ssl certificate/i }))
  expect(await screen.findByText(/checkout is actually encrypted/i)).toBeInTheDocument()
  await waitFor(() => {
    expect(screen.queryByText(/a store that appeared last week/i)).not.toBeInTheDocument()
  })
})

test("the five check names stay on screen as a click-through", () => {
  render(<HowItWorks />)
  expect(screen.getByRole("tab", { name: /domain age/i })).toBeInTheDocument()
  expect(screen.getByRole("tab", { name: /safe browsing/i })).toBeInTheDocument()
  expect(screen.getByRole("tab", { name: /page flags/i })).toBeInTheDocument()
})

test("a check explains what it looks for, not just a slogan", () => {
  render(<HowItWorks />)
  expect(screen.getByText(/a store that appeared last week/i)).toBeInTheDocument()
  expect(screen.getByText(/under a few months/i)).toBeInTheDocument()
})
