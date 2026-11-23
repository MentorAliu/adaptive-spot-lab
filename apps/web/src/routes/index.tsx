import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { ServerCrash } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { workspaceQueryOptions } from "@/account/workspace.query"
import { CockpitPage } from "@/cockpit/cockpit-page"
import { PageShell } from "@/components/page-parts"

export const Route = createFileRoute("/")({
  loader: ({ context }) =>
    context.queryClient.ensureQueryData(workspaceQueryOptions),
  headers: () => ({ "Cache-Control": "private, no-store", Vary: "Cookie" }),
  component: Cockpit,
  errorComponent: () => (
    <PageShell>
      <Alert variant="destructive">
        <ServerCrash />
        <AlertTitle>Account unavailable</AlertTitle>
        <AlertDescription>
          The private engine or database is not ready. No account state is being
          shown.
        </AlertDescription>
      </Alert>
    </PageShell>
  ),
  pendingComponent: () => (
    <PageShell>
      <Skeleton className="h-8 w-56" />
      <Skeleton className="h-96 w-full" />
    </PageShell>
  ),
})

function Cockpit() {
  const { data: workspace, isError } = useSuspenseQuery(workspaceQueryOptions)
  return (
    <PageShell>
      <CockpitPage workspace={workspace} stale={isError} />
    </PageShell>
  )
}
