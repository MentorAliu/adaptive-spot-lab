import { createFileRoute } from "@tanstack/react-router"
import { PageShell, ReadError } from "@/components/page-parts"
import { readingsListQuery, tradesListQuery } from "@/spot/spot.query"
import { TradesPage } from "@/trades/trades-page"
import type { TradesSearch } from "@/trades/trades-page"

export const Route = createFileRoute("/trades")({
  // Each key is named, undefined when the page refuses its value: the router keeps the address's own value
  // for a key left out. Load more reads the older entries, so the address carries no page.
  validateSearch: (search: Record<string, unknown>): TradesSearch => ({
    tab: search.tab === "readings" ? "readings" : undefined,
  }),
  loaderDeps: ({ search }) => search,
  loader: async ({ context, deps }) => {
    if (typeof window !== "undefined") return
    await Promise.allSettled([
      deps.tab === "readings"
        ? context.queryClient.ensureInfiniteQueryData(readingsListQuery())
        : context.queryClient.ensureInfiniteQueryData(tradesListQuery()),
    ])
  },
  headers: () => ({ "Cache-Control": "private, no-store", Vary: "Cookie" }),
  component: TradesRoute,
  errorComponent: () => (
    <PageShell>
      <ReadError what="Trades page" />
    </PageShell>
  ),
})

function TradesRoute() {
  const search = Route.useSearch()
  return (
    <PageShell>
      <TradesPage search={search} />
    </PageShell>
  )
}
