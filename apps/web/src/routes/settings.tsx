import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, useHydrated } from "@tanstack/react-router"
import { workspaceQueryOptions } from "@/account/workspace.query"
import { PageShell, ReadError } from "@/components/page-parts"
import { SettingsPage } from "@/settings/settings-page"
import { definitionsQuery, spotOverviewQuery } from "@/spot/spot.query"
import { statusQueryOptions } from "@/system/status.query"

export const Route = createFileRoute("/settings")({
  loader: async ({ context }) => {
    await context.queryClient.ensureQueryData(workspaceQueryOptions)
    if (typeof window !== "undefined") return
    await Promise.allSettled([
      // The run, the rule in force and the health, so the page is written with them.
      context.queryClient.ensureQueryData(spotOverviewQuery),
      context.queryClient.ensureQueryData(definitionsQuery),
      context.queryClient.ensureQueryData(statusQueryOptions),
    ])
  },
  headers: () => ({ "Cache-Control": "private, no-store", Vary: "Cookie" }),
  component: Settings,
  errorComponent: () => (
    <PageShell>
      <ReadError what="Settings page" />
    </PageShell>
  ),
})

function Settings() {
  const {
    data: workspace,
    isError,
    isFetching,
  } = useSuspenseQuery(workspaceQueryOptions)
  // The page is written with the account just read; a read the browser starts while it takes the
  // page over shows only once it has, so both render the same first.
  const hydrated = useHydrated()
  return (
    <PageShell>
      <h1 className="font-heading text-xl font-semibold tracking-tight">
        Settings
      </h1>
      <SettingsPage
        workspace={workspace}
        workspaceVerified={!isError && !(hydrated && isFetching)}
        workspaceError={isError}
      />
    </PageShell>
  )
}
