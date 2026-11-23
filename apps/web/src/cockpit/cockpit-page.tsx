import { useQuery } from "@tanstack/react-query"
import { DatabaseZap, TriangleAlert, Wallet } from "lucide-react"
import type { Workspace } from "@/account/schemas"
import { Alert, AlertTitle } from "@/components/ui/alert"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { spotOverviewQuery } from "@/spot/spot.query"
import { ChartCard } from "./chart-card"
import { ReadingCard } from "./reading-card"
import { RecentTrades } from "./recent-trades"
import { NothingYet, ReadFailed } from "./states"
import { StatusPill } from "./status-pill"
import { ValueCard } from "./value-card"

// The Cockpit (ExecPlan 0060 section 4.9, ExecPlan 0048's bento): the account's value with the USDT and
// Bitcoin held, the rule's reading of the day, Bitcoin's chart with the buys and sells, and the latest
// trades. One column on a phone; two from 672 px of content; from 896 px the value takes the left with
// the reading beside it, the chart under the value and the trades under the reading.

const AREA = {
  value:
    "@2xl/main:col-span-2 @4xl/main:col-span-1 @4xl/main:col-start-1 @4xl/main:row-span-2 @4xl/main:row-start-1",
  reading: "@4xl/main:col-start-2 @4xl/main:row-start-1",
  trades: "@4xl/main:col-start-2 @4xl/main:row-start-2 @4xl/main:row-span-2",
  chart:
    "@2xl/main:col-span-2 @4xl/main:col-span-1 @4xl/main:col-start-1 @4xl/main:row-start-3",
}

const GRID =
  "grid grid-cols-1 gap-4 @2xl/main:grid-cols-2 @4xl/main:grid-cols-[minmax(0,7fr)_minmax(0,5fr)]"

export function CockpitPage({
  workspace,
  stale,
}: {
  workspace: Workspace
  stale: boolean
}) {
  const account = workspace.account
  const overview = useQuery(spotOverviewQuery)
  return (
    <>
      <header className="flex min-h-8 flex-wrap items-center gap-x-3 gap-y-2">
        <h1 className="font-heading text-xl font-semibold tracking-tight">
          Cockpit
        </h1>
        <StatusPill />
      </header>
      {stale && (
        <Alert variant="destructive">
          <TriangleAlert />
          <AlertTitle>
            Account refresh failed: showing the last snapshot
          </AlertTitle>
        </Alert>
      )}
      {!account.initialized ? (
        <Card>
          <CardContent>
            <NothingYet
              icon={Wallet}
              title="No account yet"
              detail="The app adds the starting 10,000 USDT by itself."
            />
          </CardContent>
        </Card>
      ) : overview.isPending ? (
        <div className={GRID} aria-hidden="true">
          <Skeleton className={`h-96 ${AREA.value}`} />
          <Skeleton className={`h-48 ${AREA.reading}`} />
          <Skeleton className={`h-44 ${AREA.trades}`} />
        </div>
      ) : overview.isError ? (
        <ReadFailed
          what="the account"
          onRetry={() => void overview.refetch()}
        />
      ) : overview.data.state !== "READY" ? (
        <Card>
          <CardContent>
            <NothingYet
              icon={DatabaseZap}
              title="The database is being updated"
              detail="The account shows once the update has finished."
            />
          </CardContent>
        </Card>
      ) : (
        <div className={GRID}>
          <ValueCard overview={overview.data} className={AREA.value} />
          <ReadingCard overview={overview.data} className={AREA.reading} />
          <RecentTrades className={AREA.trades} />
          <ChartCard className={AREA.chart} />
        </div>
      )}
    </>
  )
}
