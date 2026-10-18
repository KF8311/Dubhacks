import { Button } from "@/components/ui/button"

type Props = {
  busy: boolean
  onConfirm: (clientData: string) => void
}

export function PasskeyDialog({ busy, onConfirm }: Props) {
  return (
    <div className="space-y-3" role="dialog" aria-label="Simulated passkey">
      <h3 className="text-lg font-semibold">Passkey</h3>
      <p className="text-sm text-muted-foreground">
        This is a simulated biometric. No fingerprint or device credential is collected.
      </p>
      <div className="flex flex-wrap gap-2">
        <Button type="button" disabled={busy} onClick={() => onConfirm("ok")}>
          Confirm with passkey
        </Button>
        <Button type="button" variant="outline" disabled={busy} onClick={() => onConfirm("fail")}>
          Simulate a failed passkey
        </Button>
      </div>
    </div>
  )
}
