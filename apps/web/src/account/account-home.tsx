import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect, useState } from "react"
import { Controller, useForm } from "react-hook-form"
import { z } from "zod"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
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
import { Separator } from "@/components/ui/separator"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { HandCoins, History } from "lucide-react"
import type { ReactNode } from "react"
import { DateTime } from "@/components/date-time"
import { CardHeading, NothingYet } from "@/cockpit/states"
import { navText, quantityText } from "@/components/page-parts"
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from "@/components/ui/empty"
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Spinner } from "@/components/ui/spinner"
import { formatExact, formatMoney } from "@/lib/display"
import {
  cancelPending,
  confirmTopup,
  getTopupDraft,
  resolveFundingKey,
  retryPending,
} from "./account.functions"
import { FundingTable } from "./funding-table"
import {
  clearFundingIntent,
  loadFundingIntent,
  observeFundingIntent,
  saveFundingIntent,
} from "./funding-intent"
import type { FundingIntent } from "./funding-intent"
import { amountInput } from "./schemas"
import type { Account, FundingDraft, Workspace } from "./schemas"
import { useRefreshWorkspace } from "./use-refresh"

const topupInput = z.object({ amount: amountInput })
const unknownStorageKey = "asl_m1_uncertain_request"

function newIdempotencyKey(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16))
  bytes[6] = (bytes[6] & 0x0f) | 0x40
  bytes[8] = (bytes[8] & 0x3f) | 0x80
  const hex = Array.from(bytes, (byte) =>
    byte.toString(16).padStart(2, "0")
  ).join("")
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`
}

export function AccountHome({
  workspace,
  workspaceVerified = true,
  workspaceError = false,
}: {
  workspace: Workspace
  workspaceVerified?: boolean
  workspaceError?: boolean
}) {
  const refresh = useRefreshWorkspace()
  const [draft, setDraft] = useState<FundingDraft | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [activeIntent, setActiveIntent] = useState<FundingIntent | null>(null)
  const [legacyKey, setLegacyKey] = useState<string | null>(null)
  const [intentReady, setIntentReady] = useState(false)
  const [intentError, setIntentError] = useState(false)
  const [busy, setBusy] = useState(false)
  const form = useForm({
    resolver: zodResolver(topupInput),
    defaultValues: { amount: "" },
  })
  const { isSubmitting, errors } = form.formState
  const interactionBusy = busy || isSubmitting
  const account = workspace.account
  const unknownKey = activeIntent?.payload.idempotency_key ?? legacyKey
  const fundingBlocked =
    !workspaceVerified || !intentReady || intentError || !!unknownKey

  useEffect(() => {
    let mounted = true
    async function reloadIntent() {
      try {
        let value = await loadFundingIntent()
        if (value?.kind === "INITIALIZE") {
          // Saved before ExecPlan 0042: the app funds the account itself now, so the owner's
          // initialization is never sent again; the server keeps any that arrived.
          await clearFundingIntent(value.payload.idempotency_key)
          value = null
        }
        if (mounted) {
          setActiveIntent(value)
          setIntentError(false)
          setIntentReady(true)
        }
      } catch {
        if (mounted) {
          setIntentError(true)
          setIntentReady(false)
        }
      }
    }
    const timer = window.setTimeout(() => {
      try {
        setLegacyKey(sessionStorage.getItem(unknownStorageKey))
      } catch {
        // A missing legacy key does not affect current IndexedDB persistence.
      }
      void reloadIntent()
    }, 0)
    const stopObserving = observeFundingIntent(() => void reloadIntent())
    return () => {
      mounted = false
      window.clearTimeout(timer)
      stopObserving()
    }
  }, [])

  async function prepareTopup(values: { amount: string }) {
    setMessage(null)
    try {
      setDraft(await getTopupDraft({ data: values }))
    } catch {
      form.setError("root.server", {
        type: "server",
        message:
          "Unable to prepare this amount. Refresh the account and try again.",
      })
    }
  }

  async function confirmDraft() {
    if (!draft || fundingBlocked || interactionBusy) return
    setBusy(true)
    setMessage(null)
    const payload = {
      amount: draft.amount,
      expected_version: draft.version,
      draft_hash: draft.draft_hash,
      idempotency_key: newIdempotencyKey(),
    }
    try {
      const saved = await saveFundingIntent(draft.kind, payload)
      setActiveIntent(saved)
      setDraft(null)
      await sendIntent(saved)
    } catch {
      setMessage(
        "The funding request was not sent because its recovery record could not be confirmed. Check local storage and existing requests before trying again."
      )
      try {
        setActiveIntent(await loadFundingIntent())
      } catch {
        setIntentError(true)
      }
    } finally {
      setBusy(false)
    }
  }

  async function finishKnownIntent(
    key: string,
    status: "POSTED" | "PENDING_VALUATION" | "CANCELED"
  ) {
    try {
      await clearFundingIntent(key)
      setActiveIntent(null)
      if (legacyKey === key) {
        sessionStorage.removeItem(unknownStorageKey)
        setLegacyKey(null)
      }
    } catch {
      setMessage(
        "The result is known, but the local recovery record could not be cleared. Funding stays blocked; check this request again."
      )
      return
    }
    if (status === "POSTED") form.reset()
    setMessage(
      status === "POSTED"
        ? "Funding posted."
        : status === "PENDING_VALUATION"
          ? "Funding is pending a valid valuation; no cash is spendable yet."
          : "Funding request canceled."
    )
    try {
      await refresh()
    } catch {
      setMessage(
        `Request is ${status.toLowerCase().replaceAll("_", " ")}, but the account view could not be refreshed. Reload before another action.`
      )
    }
  }

  async function sendIntent(intent: FundingIntent) {
    try {
      const result = await confirmTopup({ data: intent.payload })
      if (result.kind === "RESULT") {
        await finishKnownIntent(
          intent.payload.idempotency_key,
          result.funding.status
        )
      } else if (result.kind === "REJECTED") {
        await clearFundingIntent(intent.payload.idempotency_key)
        setActiveIntent(null)
        setMessage(result.code.replaceAll("_", " ").toLowerCase())
        try {
          await refresh()
        } catch {
          // The rejection is definitive; the view separately reports refresh loss.
        }
      } else {
        setMessage(
          "The outcome is unknown. Check this request before considering another funding action."
        )
      }
    } catch {
      setMessage(
        "The outcome is unknown. Check this request before considering another funding action."
      )
    }
  }

  async function checkUnknown() {
    if (!unknownKey) return
    setBusy(true)
    try {
      const result = await resolveFundingKey({ data: { key: unknownKey } })
      if (result.kind === "RESULT") {
        await finishKnownIntent(unknownKey, result.funding.status)
      } else if (result.kind === "NOT_FOUND") {
        setMessage(
          activeIntent
            ? "No request is recorded yet. You can retry the exact saved request with the same key; do not create a new contribution."
            : "No request is recorded yet. This older recovery key has no saved payload, so only lookup is safe."
        )
      } else {
        setMessage(
          "Result lookup is unavailable. Keep this request and check again."
        )
      }
    } catch {
      setMessage(
        "Result lookup is unavailable. Keep the request key and check again."
      )
    } finally {
      setBusy(false)
    }
  }

  async function retrySameIntent() {
    if (!activeIntent || !workspaceVerified || interactionBusy) return
    setBusy(true)
    setMessage(null)
    try {
      await sendIntent(activeIntent)
    } finally {
      setBusy(false)
    }
  }

  async function actOnPending(id: string, action: "retry" | "cancel") {
    setBusy(true)
    setMessage(null)
    try {
      const result =
        action === "retry"
          ? await retryPending({ data: { id } })
          : await cancelPending({ data: { id } })
      setMessage(
        result.kind === "RESULT"
          ? `Request is ${result.funding.status.toLowerCase().replaceAll("_", " ")}.`
          : result.kind === "REJECTED"
            ? result.code.replaceAll("_", " ").toLowerCase()
            : "The pending action outcome is unknown. Check this request in funding history before another action."
      )
      await refresh()
    } catch {
      setMessage(
        "Outcome unavailable. Refresh funding history before another action."
      )
    } finally {
      setBusy(false)
    }
  }

  async function retryAccountCheck() {
    setBusy(true)
    try {
      await refresh()
    } catch {
      // The cached-error alert remains visible until a verified result arrives.
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      {message && (
        <Alert role="status">
          <AlertTitle>Funding status</AlertTitle>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}
      {!workspaceVerified && (
        <Alert variant={workspaceError ? "destructive" : "default"}>
          <AlertTitle>
            {workspaceError ? "Account refresh failed" : "Checking the account"}
          </AlertTitle>
          <AlertDescription>
            {workspaceError
              ? "The displayed account is a previous snapshot. Funding is disabled until the private service responds again."
              : "Funding waits while the account is read again."}
          </AlertDescription>
          {workspaceError && (
            <Button
              variant="outline"
              onClick={retryAccountCheck}
              disabled={interactionBusy}
              className="mt-3"
            >
              Retry account check
            </Button>
          )}
        </Alert>
      )}
      {intentError && (
        <Alert variant="destructive">
          <AlertTitle>Funding recovery storage unavailable</AlertTitle>
          <AlertDescription>
            Funding is blocked because this browser cannot safely read its
            unresolved request record. Restore local storage before continuing.
          </AlertDescription>
        </Alert>
      )}
      {unknownKey && (
        <Card>
          <CardHeader>
            <CardTitle>Check uncertain request</CardTitle>
            <CardDescription>
              Request key: <code>{unknownKey}</code>
            </CardDescription>
          </CardHeader>
          <CardFooter>
            <Button
              variant="outline"
              onClick={checkUnknown}
              disabled={interactionBusy}
            >
              Check authoritative result
            </Button>
            {activeIntent && (
              <Button
                variant="outline"
                onClick={retrySameIntent}
                disabled={interactionBusy || !workspaceVerified}
              >
                Retry the same saved request
              </Button>
            )}
          </CardFooter>
        </Card>
      )}
      {account.reconciliation_failed && (
        <Alert variant="destructive">
          <AlertTitle>Reconciliation required</AlertTitle>
          <AlertDescription>
            The account projection differs from the ledger. New funding is
            blocked until reviewed.
          </AlertDescription>
        </Alert>
      )}
      {account.paused && !account.reconciliation_failed && (
        <Alert variant="destructive">
          <AlertTitle>Funding paused</AlertTitle>
          <AlertDescription>
            New funding is blocked by the account pause.
          </AlertDescription>
        </Alert>
      )}
      {account.valuation_status !== "VALID" && (
        <Alert>
          <AlertTitle>Valuation unavailable</AlertTitle>
          <AlertDescription>
            New contributions remain pending and do not become spendable until
            an owner retries after valuation recovers.
          </AlertDescription>
        </Alert>
      )}
      {!account.initialized ? (
        <Card>
          <CardHeader>
            <CardTitle role="heading" aria-level={3}>
              Starting contribution
            </CardTitle>
            <CardDescription>
              The app adds 10,000.00 USDT by itself when it starts, and tries
              again every minute while something holds it; there is nothing to
              confirm. It has not been posted yet.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Empty>
              <EmptyHeader>
                <EmptyTitle>No account funding yet</EmptyTitle>
                <EmptyDescription>
                  There is no balance, holding, return or market price to
                  display. A note above says what holds it, if anything does.
                </EmptyDescription>
              </EmptyHeader>
            </Empty>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="flex flex-col gap-4">
            <AccountBalances account={account} />
            <Separator />
            {errors.root?.server.message && (
              <Alert variant="destructive">
                <AlertTitle>Top-up review failed</AlertTitle>
                <AlertDescription>
                  {errors.root.server.message}
                </AlertDescription>
              </Alert>
            )}
            <form
              id="topup-form"
              method="post"
              onSubmit={form.handleSubmit(prepareTopup)}
              className="flex flex-col gap-2"
            >
              <h3 className="flex items-center gap-2 font-heading text-sm font-medium">
                <HandCoins
                  className="size-4 text-muted-foreground"
                  aria-hidden="true"
                />
                Top-up
              </h3>
              <FieldGroup>
                <Controller
                  name="amount"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="topup-amount" className="sr-only">
                        Amount in USDT
                      </FieldLabel>
                      <div className="flex gap-2">
                        <Input
                          {...field}
                          onChange={(event) => {
                            field.onChange(event)
                            form.clearErrors("root.server")
                          }}
                          id="topup-amount"
                          inputMode="decimal"
                          autoComplete="off"
                          aria-invalid={fieldState.invalid}
                          placeholder="Amount in USDT"
                          maxLength={32}
                          className="max-w-xs"
                        />
                        <Button
                          type="submit"
                          disabled={
                            interactionBusy ||
                            fundingBlocked ||
                            account.paused ||
                            account.reconciliation_failed
                          }
                        >
                          {isSubmitting && <Spinner data-icon="inline-start" />}
                          Review top-up
                        </Button>
                      </div>
                      <FieldDescription>
                        A top-up is not a gain: the NAV stays where it is.
                      </FieldDescription>
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
              </FieldGroup>
            </form>
          </CardContent>
        </Card>
      )}
      {workspace.funding.some(
        (entry) => entry.status === "PENDING_VALUATION"
      ) && (
        <Card>
          <CardHeader>
            <CardTitle>Pending valuation</CardTitle>
            <CardDescription>
              These requests have no spendable cash. Retry only after a valid
              valuation, or cancel a top-up before posting. The starting
              contribution cannot be canceled; the app posts it by itself within
              a minute once the valuation is valid.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            {workspace.funding
              .filter((entry) => entry.status === "PENDING_VALUATION")
              .map((entry) => (
                <div
                  key={entry.id}
                  className="flex flex-wrap items-center justify-between gap-3"
                >
                  <span>
                    {formatExact(entry.amount, 2)} USDT · {entry.id}
                  </span>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      disabled={
                        interactionBusy ||
                        !workspaceVerified ||
                        !!unknownKey ||
                        account.paused ||
                        account.reconciliation_failed ||
                        account.valuation_status !== "VALID"
                      }
                      onClick={() => actOnPending(entry.id, "retry")}
                    >
                      Retry
                    </Button>
                    {/* ExecPlan 0042: the starting contribution, while it is
                    the only way the account is funded, is not canceled. */}
                    {(entry.kind === "TOPUP" || account.initialized) && (
                      <Button
                        variant="destructive"
                        disabled={
                          interactionBusy || !workspaceVerified || !!unknownKey
                        }
                        onClick={() => actOnPending(entry.id, "cancel")}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </div>
              ))}
          </CardContent>
        </Card>
      )}
      <Card>
        <CardHeader>
          <CardHeading icon={History} level={3}>
            Funding history
          </CardHeading>
        </CardHeader>
        <CardContent>
          {workspace.funding.length ? (
            <FundingTable funding={workspace.funding} />
          ) : (
            <NothingYet
              icon={History}
              title="No funding requests"
              detail="Confirmed contributions will appear here."
            />
          )}
        </CardContent>
      </Card>
      <AlertDialog
        open={draft !== null}
        onOpenChange={(open) => {
          if (!open && !interactionBusy) setDraft(null)
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm top-up</AlertDialogTitle>
            <AlertDialogDescription>
              Account 1 · {draft ? formatExact(draft.amount, 2) : ""} USDT ·
              version {draft?.version}.{" "}
              {draft?.valuation_status === "UNAVAILABLE"
                ? "It will stay pending until valuation recovers and you retry it."
                : "It will post immediately if account state is still valid."}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={interactionBusy}>
              Back
            </AlertDialogCancel>
            <AlertDialogAction
              disabled={interactionBusy || fundingBlocked}
              onClick={confirmDraft}
            >
              {busy && <Spinner data-icon="inline-start" />}Confirm funding
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}

/** How the account's value was read, in a line under the balances. */
function valuationText(account: Account): ReactNode {
  return account.valuation_source === "CASH_ONLY" ? (
    "No Bitcoin is held; the value is the USDT."
  ) : account.valuation_source === "PERSISTED_VALUATION" ? (
    <>
      The USDT plus the Bitcoin at the best bid, valued{" "}
      <DateTime value={account.valued_at} fallback="Unknown" />.
    </>
  ) : (
    "The value is unavailable until the Bitcoin held is valued at a fresh bid."
  )
}

/** The coins held: Bitcoin, and any other coin's dust kept from before the switch, not valued. */
function holdingsText(account: Account): string | null {
  const coins = account.holdings.filter(
    (holding) => holding.valued || !/^0(?:\.0+)?$/.test(holding.quantity)
  )
  if (coins.length === 0) return null
  return coins
    .map(
      (holding) =>
        `${quantityText(holding.quantity, holding.asset)}${holding.valued ? "" : " (kept from before, not valued)"}`
    )
    .join(" · ")
}

function Balance({
  label,
  value,
  unit = "USDT",
}: {
  label: string
  value: string | null
  unit?: string
}) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="font-heading text-lg leading-tight font-semibold tabular-nums">
        {value === null ? (
          "—"
        ) : (
          <span title={unit ? `${value} ${unit}` : value}>
            {unit ? formatMoney(value) : navText(value)}
            {unit && (
              <>
                {" "}
                <span className="font-sans text-xs font-normal text-muted-foreground">
                  {unit}
                </span>
              </>
            )}
          </span>
        )}
      </dd>
    </div>
  )
}

/**
 * The account's balances in one row (ExecPlan 0048 part 3; spot since ExecPlan 0060): the value, the
 * USDT, what is available, what is reserved, what was contributed and the NAV per unit, each the
 * ledger's exact value on hover; then the coins held and how the value was read.
 */
function AccountBalances({ account }: { account: Account }) {
  const coins = holdingsText(account)
  return (
    <section aria-label="Account balances" className="flex flex-col gap-2">
      <dl className="grid grid-cols-2 gap-x-6 gap-y-3 @xl/main:grid-cols-3 @4xl/main:grid-cols-6">
        <Balance label="Value" value={account.equity} />
        <Balance label="USDT" value={account.cash} />
        <Balance label="Available" value={account.available} />
        <Balance label="Reserved" value={account.reserved} />
        <Balance label="Contributions" value={account.contributions} />
        <Balance label="NAV" value={account.nav} unit="" />
      </dl>
      {coins && (
        <p className="text-sm">
          <span className="text-muted-foreground">Coins held: </span>
          <span className="tabular-nums">{coins}</span>
        </p>
      )}
      <p className="text-xs text-muted-foreground">{valuationText(account)}</p>
    </section>
  )
}
