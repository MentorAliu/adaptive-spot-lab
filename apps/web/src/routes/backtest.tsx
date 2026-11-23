import { createFileRoute } from "@tanstack/react-router"
import { BacktestPage } from "@/backtest/backtest-page"
import type { BacktestSearch } from "@/backtest/backtest-page"
import { PageShell, ReadError } from "@/components/page-parts"
import { backtestQuery } from "@/spot/spot.query"

export const Route = createFileRoute("/backtest")({
  // The first window is the address without a search; another is named, and anything else is dropped:
  // the key is undefined then, as the router keeps the address's own value for a key left out.
  validateSearch: (search: Record<string, unknown>): BacktestSearch => ({
    window:
      search.window === "SINCE_2023" || search.window === "LAST_12_MONTHS"
        ? search.window
        : undefined,
  }),
  loaderDeps: ({ search }) => search,
  loader: async ({ context, deps }) => {
    if (typeof window !== "undefined") return
    await Promise.allSettled([
      context.queryClient.ensureQueryData(
        backtestQuery(deps.window ?? "SINCE_2019")
      ),
    ])
  },
  headers: () => ({ "Cache-Control": "private, no-store", Vary: "Cookie" }),
  component: BacktestRoute,
  errorComponent: () => (
    <PageShell>
      <ReadError what="Backtest page" />
    </PageShell>
  ),
})

function BacktestRoute() {
  const search = Route.useSearch()
  return (
    <PageShell>
      <BacktestPage search={search} />
    </PageShell>
  )
}
