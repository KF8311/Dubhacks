import { Button } from "@/components/ui/button"

type Props = {
  message: string
  onStartOver: () => void
}

export function EmptyState({ message, onStartOver }: Props) {
  return (
    <div className="ticket rounded-lg px-6 py-10">
      <p className="font-heading text-xl font-semibold">{message}</p>
      <Button type="button" className="mt-4 rounded-md font-semibold" variant="outline" onClick={onStartOver}>
        Start over
      </Button>
    </div>
  )
}
