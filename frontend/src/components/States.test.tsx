import { fireEvent, render, screen } from "@testing-library/react"
import { EmptyState } from "./EmptyState.tsx"
import { ErrorBanner } from "./ErrorBanner.tsx"

test("empty state shows the reason and start over", () => {
  const onStartOver = vi.fn()
  render(<EmptyState message="No trusted option at that budget." onStartOver={onStartOver} />)
  expect(screen.getByText(/no trusted option/i)).toBeInTheDocument()
  fireEvent.click(screen.getByRole("button", { name: /start over/i }))
  expect(onStartOver).toHaveBeenCalledOnce()
})

test("error banner can be dismissed", () => {
  const onDismiss = vi.fn()
  render(<ErrorBanner message="The live update stopped." onDismiss={onDismiss} />)
  expect(screen.getByRole("status")).toHaveTextContent(/live update stopped/i)
  fireEvent.click(screen.getByRole("button", { name: /dismiss/i }))
  expect(onDismiss).toHaveBeenCalledOnce()
})
