import { tableFeatures, useTable } from "@tanstack/react-table"
import type { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { DateTime } from "@/components/date-time"
import { navText } from "@/components/page-parts"
import { formatExact } from "@/lib/display"
import { cn } from "@/lib/utils"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { Funding } from "./schemas"

const features = tableFeatures({})
// The amounts line up on the right.
const NUMERIC = new Set(["amount", "preflow_nav"])

const columns: Array<ColumnDef<typeof features, Funding>> = [
  {
    accessorKey: "created_at",
    header: "Date",
    cell: ({ row }) => (
      <DateTime value={row.original.created_at} seconds={false} />
    ),
  },
  {
    accessorKey: "kind",
    header: "Flow",
    cell: ({ row }) =>
      row.original.kind === "INITIALIZE" ? "Initial contribution" : "Top-up",
  },
  {
    accessorKey: "amount",
    header: "USDT",
    cell: ({ row }) => formatExact(row.original.amount, 2),
  },
  {
    accessorKey: "preflow_nav",
    header: "NAV",
    cell: ({ row }) =>
      row.original.preflow_nav === null
        ? "—"
        : navText(row.original.preflow_nav),
  },
  {
    accessorKey: "status",
    header: "State",
    cell: ({ row }) => (
      <Badge
        variant={row.original.status === "POSTED" ? "secondary" : "outline"}
      >
        {row.original.status.replace("_", " ")}
      </Badge>
    ),
  },
]

export function FundingTable({ funding }: { funding: Funding[] }) {
  const table = useTable({ features, columns, data: funding })
  return (
    <Table>
      <TableCaption>The starting contribution and your top-ups.</TableCaption>
      <TableHeader>
        {table.getHeaderGroups().map((group) => (
          <TableRow key={group.id}>
            {group.headers.map((header) => (
              <TableHead
                key={header.id}
                className={cn(NUMERIC.has(header.column.id) && "text-right")}
              >
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
              <TableCell
                key={cell.id}
                className={cn(
                  NUMERIC.has(cell.column.id) && "text-right tabular-nums"
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
