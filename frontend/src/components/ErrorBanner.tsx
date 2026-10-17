import { Button } from "@/components/ui/button"

type Props = {
  message: string
  onDismiss: () => void
}

export function ErrorBanner({ message, onDismiss }: Props) {
  return (
    <div
      role="status"
      className="flex items-center justify-between gap-4 rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-amber-950"
    >
      <p>{message}</p>
      <Button type="button" variant="outline" onClick={onDismiss}>
        Dismiss
      </Button>
    </div>
  )
}
