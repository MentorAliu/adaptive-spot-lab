import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"

// The owner's requests (the run's controls since ExecPlan 0039, kept by ExecPlan 0060): each carries a
// fresh idempotency key, so a request whose answer was lost can be looked up instead of repeated.

/** A fresh owner idempotency key (UUID v4 text; the API accepts [A-Za-z0-9_-]{8,64}). */
export function newIdempotencyKey(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16))
  bytes[6] = (bytes[6] & 0x0f) | 0x40
  bytes[8] = (bytes[8] & 0x3f) | 0x80
  const hex = Array.from(bytes, (byte) =>
    byte.toString(16).padStart(2, "0")
  ).join("")
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`
}

export function shortHash(value: string | null): string {
  return value ? `${value.slice(0, 12)}…` : "Unset"
}

export type Outcome =
  | { kind: "RESULT"; message: string }
  | { kind: "REJECTED"; code: string }
  | { kind: "UNKNOWN"; key: string }
  | { kind: "NOT_FOUND"; key: string }

export function OutcomeAlert({
  outcome,
  resolving,
  onResolve,
  describe = (code) => code.replaceAll("_", " "),
}: {
  outcome: Outcome | null
  resolving: boolean
  onResolve: (key: string) => void
  /** The refusal's code in words. */
  describe?: (code: string) => string
}) {
  if (outcome === null) return null
  if (outcome.kind === "RESULT")
    return (
      <Alert role="status">
        <AlertTitle>Recorded</AlertTitle>
        <AlertDescription>{outcome.message}</AlertDescription>
      </Alert>
    )
  if (outcome.kind === "REJECTED")
    return (
      <Alert variant="destructive" role="alert">
        <AlertTitle>Refused: {describe(outcome.code)}</AlertTitle>
        <AlertDescription>
          Nothing was recorded. Review the current state, then try again.
        </AlertDescription>
      </Alert>
    )
  if (outcome.kind === "NOT_FOUND")
    return (
      <Alert role="status">
        <AlertTitle>Not recorded</AlertTitle>
        <AlertDescription>
          The API has no record for request {outcome.key}. It is safe to submit
          again.
        </AlertDescription>
      </Alert>
    )
  return (
    <Alert variant="destructive" role="alert">
      <AlertTitle>Outcome unknown</AlertTitle>
      <AlertDescription className="flex flex-col items-start gap-2">
        <p>
          The request may or may not have been recorded. Do not repeat it; check
          its outcome by its key ({outcome.key}).
        </p>
        <Button
          variant="outline"
          size="sm"
          disabled={resolving}
          onClick={() => onResolve(outcome.key)}
        >
          {resolving && <Spinner data-icon="inline-start" />}Check outcome
        </Button>
      </AlertDescription>
    </Alert>
  )
}
