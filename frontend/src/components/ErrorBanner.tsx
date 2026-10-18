import { Button } from "@/components/ui/button"

type Props = {
  message: string
  onDismiss: () => void
}

export function ErrorBanner({ message, onDismiss }: Props) {
  return (
    <div
      role="status"
      className="flex items-center justify-between gap-4 rounded-md border border-[color:var(--trust-caution)] bg-[color:var(--trust-caution-bg)] px-4 py-3 text-[color:var(--trust-caution)]"
    >
      <p>{message}</p>
      <Button type="button" variant="outline" onClick={onDismiss}>
        Dismiss
      </Button>
    </div>
  )
}
