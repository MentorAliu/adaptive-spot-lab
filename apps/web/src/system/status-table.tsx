import { useMemo } from "react"
import {
  createColumnHelper,
  tableFeatures,
  useTable,
} from "@tanstack/react-table"
import { Activity, ChartCandlestick, Cog, History, Wallet } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { Hint } from "@/cockpit/states"
import { IconTile, StatusDot } from "@/cockpit/visuals"
import type { DotTone } from "@/cockpit/visuals"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ToneBadge } from "@/components/page-parts"
import type { Tone } from "@/components/page-parts"
import type { SystemStatus } from "./status.schema"

type CapabilityRow = {
  id: string
  capability: string
  state: string
}

// What each state means for the owner (ExecPlan 0036 section 4.4): working, on hold, needs a look,
// failing or off. The word stays the API's; the icon and the colour only sort it.
const GOOD = ["funded", "ready", "running", "computed"]
const PAUSED = ["paused", "stopping"]
const BAD = ["unavailable"]
const OFF = ["unconfigured", "disabled", "inactive", "not running", "stopped"]
// The backtest is worked out within minutes of a start: waiting, not a fault.
const PENDING = ["not computed"]

export function toneOf(state: string): Tone {
  if (GOOD.includes(state)) return "good"
  if (PAUSED.includes(state)) return "paused"
  if (BAD.includes(state)) return "bad"
  if (OFF.includes(state)) return "off"
  if (PENDING.includes(state)) return "pending"
  return "attention"
}

/** The app's parts and their state, in the order the health section shows them (ExecPlan 0060). */
export function statusRows(status: SystemStatus): CapabilityRow[] {
  return [
    { id: "account", capability: "Account", state: status.account },
    {
      id: "market",
      capability: "Bitcoin price feed",
      state: status.market_data,
    },
    { id: "trading", capability: "Trading run", state: status.trading },
    {
      id: "execution",
      capability: "Trading engine",
      state: status.execution_worker.replace("_", " "),
    },
    {
      id: "backtest",
      capability: "Backtest",
      state: status.backtest.replace("_", " "),
    },
  ]
}

const features = tableFeatures({})
const columnHelper = createColumnHelper<typeof features, CapabilityRow>()
const columns = columnHelper.columns([
  columnHelper.accessor("capability", { header: "Capability" }),
  columnHelper.accessor("state", {
    header: "State",
    cell: (info) => (
      <ToneBadge tone={toneOf(info.getValue())}>{info.getValue()}</ToneBadge>
    ),
  }),
])

export function StatusTable({ status }: { status: SystemStatus }) {
  const data = useMemo(() => statusRows(status), [status])
  const table = useTable({ features, data, columns, getRowId: (row) => row.id })

  return (
    <Table>
      <TableCaption>The app&apos;s parts and their state</TableCaption>
      <TableHeader>
        {table.getHeaderGroups().map((group) => (
          <TableRow key={group.id}>
            {group.headers.map((header) => (
              <TableHead key={header.id}>
                {header.isPlaceholder ? null : (
                  <table.FlexRender header={header} />
                )}
              </TableHead>
            ))}
          </TableRow>
        ))}
      </TableHeader>
      <TableBody>
        {table.getRowModel().rows.map((row) => (
          <TableRow key={row.id}>
            {row.getAllCells().map((cell) => (
              <TableCell key={cell.id}>
                <table.FlexRender cell={cell} />
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

const ICON: Record<string, LucideIcon> = {
  account: Wallet,
  market: Activity,
  trading: ChartCandlestick,
  execution: Cog,
  backtest: History,
}

const DOT: Record<Tone, DotTone> = {
  good: "ok",
  active: "ok",
  paused: "warning",
  attention: "warning",
  bad: "danger",
  off: "off",
  pending: "off",
}

const MEANING: Record<Tone, string> = {
  good: "working",
  active: "working",
  paused: "on hold",
  attention: "needs a look",
  bad: "failing",
  off: "off",
  pending: "waiting",
}

/**
 * The health section's tiles (ExecPlan 0048 part 3): one per part of the app, its icon, its name and a
 * dot with the engine's word; what the word means is on hover and focus.
 */
export function StatusTiles({ status }: { status: SystemStatus }) {
  const rows = statusRows(status)
  return (
    <ul
      aria-label="The app's parts and their state"
      className="grid grid-cols-1 gap-3 @md/main:grid-cols-2 @3xl/main:grid-cols-3 @6xl/main:grid-cols-5"
    >
      {rows.map((row) => {
        const tone = toneOf(row.state)
        const Icon = ICON[row.id] ?? Activity
        return (
          <li
            key={row.id}
            aria-label={`${row.capability}: ${row.state}`}
            className="flex items-center gap-3 rounded-xl bg-card p-3 text-sm ring-1 ring-foreground/10"
          >
            <IconTile>
              <Icon className="size-3.5" />
            </IconTile>
            <span className="flex min-w-0 flex-col gap-0.5">
              <span className="truncate font-medium">{row.capability}</span>
              <Hint
                label={`${row.capability}: ${row.state} (${MEANING[tone]})`}
                className="gap-1.5 text-xs text-muted-foreground"
              >
                <StatusDot tone={DOT[tone]} />
                <span className="truncate">{row.state}</span>
              </Hint>
            </span>
          </li>
        )
      })}
    </ul>
  )
}
