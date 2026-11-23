import { metaHelper, tableFeatures, useTable } from "@tanstack/react-table"
import type { ColumnDef, RowData } from "@tanstack/react-table"
import {
  Activity,
  CircleCheck,
  CircleDashed,
  CircleMinus,
  CirclePause,
  CircleX,
  Inbox,
  ServerCrash,
  TriangleAlert,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import type { ReactNode } from "react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  formatMoney,
  formatNumber,
  formatPercent,
  formatPrice,
  formatQuantity,
} from "@/lib/display"
import { cn } from "@/lib/utils"

// The pages' shared parts (ExecPlan 0036 section 4.4, kept by ExecPlan 0060 when the order and position
// pages went): the page's column and title, the empty, loading and error states, a plain table, and
// each kind of value in its own format with its unit.

/**
 * What a state means for the owner: done, working now, on hold, needs a look, failed, off, or not yet
 * under way. The word stays the API's; the icon and colour only sort it.
 */
export type Tone =
  "good" | "active" | "paused" | "attention" | "bad" | "off" | "pending"

const TONE: Record<
  Tone,
  {
    variant: "default" | "secondary" | "outline" | "destructive"
    icon: LucideIcon
  }
> = {
  good: { variant: "secondary", icon: CircleCheck },
  active: { variant: "default", icon: Activity },
  paused: { variant: "secondary", icon: CirclePause },
  attention: { variant: "outline", icon: TriangleAlert },
  bad: { variant: "destructive", icon: CircleX },
  off: { variant: "outline", icon: CircleMinus },
  pending: { variant: "outline", icon: CircleDashed },
}

export function ToneBadge({
  tone,
  children,
}: {
  tone: Tone
  children: ReactNode
}) {
  const { variant, icon: Icon } = TONE[tone]
  return (
    <Badge variant={variant}>
      <Icon data-icon="inline-start" />
      {children}
    </Badge>
  )
}

// Display only (ExecPlan 0037): a missing value reads "Unavailable"; the API's strings stay exact
// everywhere else.
function withUnit(text: string, unit?: string): string {
  return unit ? `${text} ${unit}` : text
}

/** A USDT amount: 1,234.56 USDT; `signed` for a gain or loss (+12.30, -4.05). */
export function moneyText(
  value: string | null,
  unit = "USDT",
  { signed = false }: { signed?: boolean } = {}
): string {
  return value === null
    ? "Unavailable"
    : withUnit(formatMoney(value, { signed }), unit)
}

/** A price: 64,123.46 USDT. */
export function priceText(value: string | null, unit = "USDT"): string {
  return value === null ? "Unavailable" : withUnit(formatPrice(value), unit)
}

/** A coin amount, exact, with its coin: 0.00093 BTC. */
export function quantityText(value: string | null, asset?: string): string {
  return value === null ? "Unavailable" : withUnit(formatQuantity(value), asset)
}

/** An amount in the asset it is held or charged in: USDT as money, a coin exactly. */
export function amountText(value: string | null, asset: string): string {
  return asset === "USDT" ? moneyText(value) : quantityText(value, asset)
}

/** NAV per unit, to four decimals (1.0234). */
export function navText(value: string | null): string {
  return value === null
    ? "Unavailable"
    : formatNumber(value, { min: 4, max: 4 })
}

/** A fraction as a percentage (1.25%); see `formatPercent` for the options. */
export function percentText(
  fraction: string | null,
  options?: Parameters<typeof formatPercent>[1]
): string {
  return fraction === null ? "Unavailable" : formatPercent(fraction, options)
}

/** Labelled figures. */
export function Facts({
  items,
}: {
  items: [label: string, value: ReactNode][]
}) {
  return (
    <dl className="grid gap-x-6 gap-y-3 text-sm sm:grid-cols-2">
      {items.map(([label, value]) => (
        <div key={label} className="flex min-w-0 flex-col gap-1">
          <dt className="text-muted-foreground">{label}</dt>
          <dd className="break-words">{value}</dd>
        </div>
      ))}
    </dl>
  )
}

/** A column marked `numeric` aligns right, so place values line up (ExecPlan 0036 section 4.4). */
export type ColumnLayout = { numeric?: boolean }
export const plainFeatures = tableFeatures({
  columnMeta: metaHelper<ColumnLayout>(),
})
export type PlainFeatures = typeof plainFeatures

export function DataTable<TData extends RowData>({
  columns,
  data,
  getRowId,
  caption,
  className,
}: {
  // The column helper returns this exact type (TanStack Table v9).
  columns: ColumnDef<PlainFeatures, TData, any>[]
  data: TData[]
  getRowId: (row: TData, index: number) => string
  caption: string
  className?: string
}) {
  const table = useTable({ features: plainFeatures, data, columns, getRowId })
  return (
    <Table className={className}>
      <caption className="sr-only">{caption}</caption>
      <TableHeader>
        {table.getHeaderGroups().map((group) => (
          <TableRow key={group.id}>
            {group.headers.map((header) => (
              <TableHead
                key={header.id}
                scope="col"
                className={cn(
                  header.column.columnDef.meta?.numeric && "text-right"
                )}
              >
                {header.isPlaceholder ? null : (
                  <table.FlexRender header={header} />
                )}
              </TableHead>
            ))}
          </TableRow>
        ))}
      </TableHeader>
      <TableBody className="tabular-nums">
        {table.getRowModel().rows.map((row) => (
          <TableRow key={row.id}>
            {row.getAllCells().map((cell) => (
              <TableCell
                key={cell.id}
                className={cn(
                  cell.column.columnDef.meta?.numeric && "text-right"
                )}
              >
                <table.FlexRender cell={cell} />
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export function EmptyState({
  title,
  description,
  icon: Icon = Inbox,
}: {
  title: string
  description: string
  icon?: LucideIcon
}) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Icon />
        </EmptyMedia>
        <EmptyTitle>{title}</EmptyTitle>
        <EmptyDescription>{description}</EmptyDescription>
      </EmptyHeader>
    </Empty>
  )
}

export function LoadingRows({ label }: { label: string }) {
  return (
    <div role="status" aria-label={label} className="flex flex-col gap-2">
      <Skeleton className="h-8 w-full" />
      <Skeleton className="h-8 w-full" />
      <Skeleton className="h-8 w-2/3" />
    </div>
  )
}

export function ReadError({ what }: { what: string }) {
  return (
    <Alert variant="destructive">
      <ServerCrash />
      <AlertTitle>{what} unavailable</AlertTitle>
      <AlertDescription>
        The private API did not return a valid response. Values are not guessed;
        check that the app is running, then reload.
      </AlertDescription>
    </Alert>
  )
}

/** A page's column. The shell's inset is the page's one `main` (ExecPlan 0036 section 4.1). */
export function PageShell({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 lg:px-6">
      {children}
    </div>
  )
}

/** A page's title: its section's icon, the title and what the page shows; `children` below it. */
export function PageHeader({
  icon: Icon,
  title,
  description,
  children,
}: {
  icon: LucideIcon
  title: ReactNode
  description?: ReactNode
  children?: ReactNode
}) {
  return (
    <header className="flex items-start gap-3">
      <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
        <Icon />
      </span>
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <h1 className="font-heading text-2xl font-semibold tracking-tight">
          {title}
        </h1>
        {description && (
          <p className="max-w-3xl text-sm text-muted-foreground">
            {description}
          </p>
        )}
        {children}
      </div>
    </header>
  )
}
