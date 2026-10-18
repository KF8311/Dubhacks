import { Button } from "@/components/ui/button"

type Props = {
  message: string
  onStartOver: () => void
}

export function EmptyState({ message, onStartOver }: Props) {
  return (
    <div className="rounded-xl border border-dashed px-6 py-10 text-center">
      <p className="text-lg">{message}</p>
      <Button type="button" className="mt-4" variant="outline" onClick={onStartOver}>
        Start over
      </Button>
    </div>
  )
}
