import { useQuery } from "@tanstack/react-query"
import { BookOpenText, HeartPulse, Play, Tag, Wallet } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import type { ReactNode } from "react"
import { AccountHome } from "@/account/account-home"
import type { Workspace } from "@/account/schemas"
import { LoadingRows, ReadError } from "@/components/page-parts"
import { buttonVariants } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { SettingRow, SettingsList } from "@/settings/parts"
import { RuleSettings } from "@/spot/rule-words"
import { SpotRunSettings } from "@/spot/run-controls"
import { definitionsQuery } from "@/spot/spot.query"
import type { Place } from "@/spot/status"
import { StatusTiles } from "@/system/status-table"
import { statusQueryOptions } from "@/system/status.query"

// Settings (ExecPlan 0060 section 4.9): the run's controls, the rule and its limits in words, the
// account's top-ups, and the app's health and version, one section each. The Cockpit's notes link here
// by these ids.
const SECTIONS: { id: Place; title: string; icon: LucideIcon }[] = [
  { id: "run", title: "Trading run", icon: Play },
  { id: "rule", title: "Rule and limits", icon: BookOpenText },
  { id: "account", title: "Account", icon: Wallet },
  { id: "health", title: "Health", icon: HeartPulse },
]

export function SettingsPage({
  workspace,
  workspaceVerified,
  workspaceError,
}: {
  workspace: Workspace
  workspaceVerified: boolean
  workspaceError: boolean
}) {
  const body: Record<Place, ReactNode> = {
    run: <SpotRunSettings />,
    rule: <RuleSettings />,
    account: (
      <AccountHome
        workspace={workspace}
        workspaceVerified={workspaceVerified}
        workspaceError={workspaceError}
      />
    ),
    health: <HealthSection />,
  }
  // The section links are a row of buttons; on a phone the row scrolls sideways, not the page.
  return (
    <div className="flex flex-col gap-8">
      <nav
        aria-label="Settings sections"
        className="-mx-4 flex gap-1.5 overflow-x-auto px-4 pb-1 @3xl/main:mx-0 @3xl/main:flex-wrap @3xl/main:overflow-visible @3xl/main:px-0"
      >
        {SECTIONS.map((section) => (
          <a
            key={section.id}
            href={`#${section.id}`}
            className={cn(
              buttonVariants({ variant: "outline", size: "sm" }),
              "shrink-0"
            )}
          >
            <section.icon data-icon="inline-start" />
            {section.title}
          </a>
        ))}
      </nav>
      {SECTIONS.map((section) => (
        <section
          key={section.id}
          id={section.id}
          aria-labelledby={`${section.id}-heading`}
          className="flex min-w-0 scroll-mt-6 flex-col gap-3"
        >
          <h2
            id={`${section.id}-heading`}
            className="flex items-center gap-2 font-heading text-base font-semibold"
          >
            <section.icon
              className="size-4 text-muted-foreground"
              aria-hidden="true"
            />
            {section.title}
          </h2>
          {body[section.id]}
        </section>
      ))}
    </div>
  )
}

// The Cockpit's status pill reads the status at this cadence too.
const STATUS_MS = 30_000

function HealthSection() {
  const status = useQuery({
    ...statusQueryOptions,
    refetchInterval: STATUS_MS,
    retry: false,
  })
  return status.isPending ? (
    <LoadingRows label="Loading the app's health" />
  ) : status.isError ? (
    <ReadError what="System status" />
  ) : (
    <>
      <StatusTiles status={status.data} />
      <VersionRow />
    </>
  )
}

/** The app's version: the installed code's identity, as each run records it. */
export function VersionRow() {
  const definitions = useQuery(definitionsQuery)
  return (
    <Card size="sm">
      <CardContent>
        <SettingsList label="Version">
          <SettingRow
            icon={Tag}
            title="App version"
            description={
              definitions.isPending
                ? "Loading"
                : definitions.isError
                  ? "Couldn't read the installed version"
                  : definitions.data.code_identity
            }
          />
        </SettingsList>
      </CardContent>
    </Card>
  )
}
