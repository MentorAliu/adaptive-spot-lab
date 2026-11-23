import { useQuery, useQueryClient } from "@tanstack/react-query"
import { CirclePlay, LoaderCircle, Pause, Play, Square } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { useState } from "react"
import { IconTile } from "@/cockpit/visuals"
import { DateTime } from "@/components/date-time"
import {
  LoadingRows,
  ReadError,
  moneyText,
  percentText,
} from "@/components/page-parts"
import { OutcomeAlert, newIdempotencyKey } from "@/components/request-outcome"
import type { Outcome } from "@/components/request-outcome"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"
import { cn } from "@/lib/utils"
import { RUN, codeText, holdText, stopText } from "./parts"
import { postSpotRequest, resolveSpotRequest } from "./spot.functions"
import { SPOT_KEY, spotOverviewQuery } from "./spot.query"
import type { Overview, RequestKind, RunState, SpotRequest } from "./schemas"

// Settings' run controls for the spot account (ExecPlan 0060 section 4.9): Pause, Resume, Stop and sell,
// and Start. Each request is confirmed, bound to the run shown and idempotent; the engine applies it
// within a second and answers it once. The engine's Stop always sells the Bitcoin held, so the page
// offers one "Stop and sell". The limits never wait for any of them.

export type Control = "PAUSE" | "RESUME" | "STOP" | "START"

export const CONTROL: Record<
  Control,
  { label: string; consequence: string; kind: RequestKind }
> = {
  PAUSE: {
    label: "Pause",
    consequence:
      "No buy until you resume. The rule still reads every day and its sells still go through, and the limits keep working.",
    kind: "PAUSE",
  },
  RESUME: {
    label: "Resume",
    consequence:
      "Clears your pause. Buys start again at the next reading unless a limit still holds them.",
    kind: "RESUME",
  },
  STOP: {
    label: "Stop and sell",
    consequence:
      "Ends the run: the Bitcoin held is sold at once at the order book, then nothing trades. Only you can start a new run.",
    kind: "STOP",
  },
  START: {
    label: "Start trading",
    consequence:
      "Starts a new run under the rule in force, measured from the account's value now. Its first reading comes at once if today's is due, else just after midnight UTC.",
    kind: "START",
  },
}

/** The controls the run's state allows, in the engine's own terms (app/spot/engine.py). */
export function available(overview: Overview): Control[] {
  const run = overview.run
  if (overview.state !== "READY" || !overview.account?.initialized) return []
  if (run === null || run.state === "STOPPED") return ["START"]
  if (run.state === "STOPPING") return []
  const controls: Control[] = []
  if (run.causes.includes("OWNER")) controls.push("RESUME")
  else controls.push("PAUSE")
  controls.push("STOP")
  return controls
}

const RUN_ICON: Record<RunState, LucideIcon> = {
  RUNNING: Play,
  PAUSED: Pause,
  STOPPING: LoaderCircle,
  STOPPED: Square,
}

/** A recorded request in a line: "Pause was applied", "Start was refused: a run is already going". */
export function requestText(request: SpotRequest): string {
  const control = CONTROL[request.kind]
  return `${control.label} ${
    request.status === "PENDING"
      ? "is waiting for the engine"
      : request.status === "APPLIED"
        ? "was applied"
        : `was refused: ${request.reasons.map(codeText).join(", ")}`
  }.`
}

export function SpotRunSettings() {
  const overview = useQuery(spotOverviewQuery)
  if (overview.isPending) return <LoadingRows label="Loading the trading run" />
  if (overview.isError) return <ReadError what="Trading run" />
  return <RunCard overview={overview.data} />
}

function RunCard({ overview }: { overview: Overview }) {
  const queryClient = useQueryClient()
  const [pending, setPending] = useState<Control | null>(null)
  const [busy, setBusy] = useState(false)
  const [resolving, setResolving] = useState(false)
  const [outcome, setOutcome] = useState<Outcome | null>(null)
  const run = overview.run
  const controls = available(overview)

  async function confirm() {
    if (!pending) return
    const control = CONTROL[pending]
    setBusy(true)
    const key = newIdempotencyKey()
    try {
      const result = await postSpotRequest({
        data: {
          kind: control.kind,
          // The run this page showed; a request for another run is refused.
          run_id: control.kind === "START" ? null : (run?.id ?? null),
          idempotency_key: key,
        },
      })
      setOutcome(
        result.kind === "RESULT"
          ? {
              kind: "RESULT",
              message: `${control.label} accepted. The engine applies it within a second; this page shows the run's new state.`,
            }
          : result
      )
    } catch {
      setOutcome({ kind: "UNKNOWN", key })
    } finally {
      setBusy(false)
      setPending(null)
      await queryClient.invalidateQueries({ queryKey: [SPOT_KEY] })
    }
  }

  async function resolve(key: string) {
    setResolving(true)
    try {
      const found = await resolveSpotRequest({ data: { key } })
      setOutcome(
        found.kind === "RESULT"
          ? { kind: "RESULT", message: requestText(found.value) }
          : found.kind === "NOT_FOUND"
            ? { kind: "NOT_FOUND", key }
            : { kind: "UNKNOWN", key }
      )
      await queryClient.invalidateQueries({ queryKey: [SPOT_KEY] })
    } finally {
      setResolving(false)
    }
  }

  const Icon = run === null ? CirclePlay : RUN_ICON[run.state]
  const fall = overview.limits?.fall_from_high ?? null
  return (
    <Card>
      <CardContent className="flex flex-col gap-4">
        <div className="flex flex-col gap-4 @3xl/main:flex-row @3xl/main:items-center">
          <div className="flex min-w-0 flex-1 items-center gap-3">
            <IconTile size="lg" accent={run?.state === "RUNNING"}>
              <Icon
                className={cn(
                  "size-5",
                  run?.state === "STOPPING" && "motion-safe:animate-spin"
                )}
              />
            </IconTile>
            <div className="flex min-w-0 flex-col gap-0.5">
              <CardTitle
                role="heading"
                aria-level={3}
                className="text-xs font-medium text-muted-foreground"
              >
                {run === null ? "No run yet" : `Run #${run.seq}`}
              </CardTitle>
              <p className="font-heading text-xl leading-tight font-semibold">
                {run === null ? "Not started" : RUN[run.state].text}
              </p>
              <p className="text-sm text-muted-foreground">
                {run === null
                  ? "The first run starts by itself once the starting money is added."
                  : run.state === "PAUSED"
                    ? holdText(run.causes)
                    : RUN[run.state].detail}
              </p>
            </div>
          </div>
          {controls.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {controls.map((control) => (
                <Button
                  key={control}
                  variant={
                    control === "START" || control === "RESUME"
                      ? "default"
                      : control === "STOP"
                        ? "destructive"
                        : "outline"
                  }
                  disabled={busy}
                  onClick={() => {
                    setOutcome(null)
                    setPending(control)
                  }}
                >
                  {CONTROL[control].label}
                </Button>
              ))}
            </div>
          )}
        </div>
        {run !== null && (
          <dl className="flex flex-wrap gap-x-8 gap-y-2 border-t pt-3 text-sm">
            <div className="flex flex-col gap-0.5">
              <dt className="text-xs text-muted-foreground">Started</dt>
              <dd>
                <DateTime value={run.started_at} seconds={false} /> by{" "}
                {run.started_by === "OWNER" ? "you" : "the app"}
              </dd>
            </div>
            <div className="flex flex-col gap-0.5">
              <dt className="text-xs text-muted-foreground">From</dt>
              <dd className="tabular-nums">{moneyText(run.start_equity)}</dd>
            </div>
            {run.state !== "STOPPED" && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-xs text-muted-foreground">
                  Below the run&apos;s high
                </dt>
                <dd className="tabular-nums">
                  {fall === null ? "Not measured" : percentText(fall)}
                </dd>
              </div>
            )}
            {run.stopped_at && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-xs text-muted-foreground">Stopped</dt>
                <dd>
                  <DateTime value={run.stopped_at} seconds={false} /> by{" "}
                  {stopText(run.stop_reason)}
                </dd>
              </div>
            )}
          </dl>
        )}
        <OutcomeAlert
          outcome={outcome}
          resolving={resolving}
          onResolve={(key) => void resolve(key)}
          describe={codeText}
        />
        {controls.length === 0 && (
          <p className="text-sm text-muted-foreground">
            {run?.state === "STOPPING"
              ? "No control while the run sells its Bitcoin; it stops by itself once only USDT is held."
              : `No control is offered now${overview.account?.initialized ? "" : ": the starting money is added first"}.`}
          </p>
        )}
      </CardContent>
      <AlertDialog
        open={pending !== null}
        onOpenChange={(open) => {
          if (!open && !busy) setPending(null)
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {pending
                ? pending === "START"
                  ? "Start a new trading run?"
                  : `${CONTROL[pending].label}: run #${run?.seq ?? ""}?`
                : ""}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {pending ? CONTROL[pending].consequence : ""}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={busy}>Back</AlertDialogCancel>
            <AlertDialogAction
              variant={pending === "STOP" ? "destructive" : "default"}
              disabled={busy}
              onClick={() => void confirm()}
            >
              {busy && <Spinner data-icon="inline-start" />}
              {pending ? CONTROL[pending].label : "Confirm"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  )
}
