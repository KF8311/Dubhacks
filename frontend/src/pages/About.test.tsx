import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { About } from "./About.tsx"

test("clicking a chapter swaps the story without leaving the page", async () => {
  render(<About />)
  expect(screen.getByText(/already walked the aisle/i)).toBeInTheDocument()
  fireEvent.click(screen.getByRole("tab", { name: /why it refuses/i }))
  expect(await screen.findByText(/five checks, a score you can read/i)).toBeInTheDocument()
  await waitFor(() => {
    expect(screen.queryByText(/already walked the aisle/i)).not.toBeInTheDocument()
  })
})

test("chapters are the tabs; there is no previous or next chapter control", () => {
  render(<About />)
  expect(screen.queryByRole("button", { name: /previous/i })).not.toBeInTheDocument()
  expect(screen.queryByRole("button", { name: /next chapter/i })).not.toBeInTheDocument()
})
