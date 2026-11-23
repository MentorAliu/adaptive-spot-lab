import { Link } from "@tanstack/react-router"
import { FlaskConical } from "lucide-react"
import { AlertsMenu, LiveBadge } from "@/components/live-status"
import { ModeToggle } from "@/components/mode-toggle"
import { Separator } from "@/components/ui/separator"
import { SidebarTrigger } from "@/components/ui/sidebar"

/**
 * The bar above every page (ExecPlan 0036 section 4.1): the sidebar's toggle from 768 px, the app's
 * name on a phone, and on every width whether the trades are live with the trade alerts' bell
 * (ExecPlan 0047) and the theme switch. Since ExecPlan 0060 every page is a section's own, so there is
 * no detail page to lead back from.
 */
export function SiteHeader() {
  return (
    <header className="flex h-(--header-height) shrink-0 items-center border-b">
      <div className="flex w-full min-w-0 items-center gap-2 px-4 lg:px-6">
        <SidebarTrigger className="-ml-1 hidden md:inline-flex" />
        <Separator
          orientation="vertical"
          className="mr-1 hidden md:block data-vertical:h-4 data-vertical:self-center"
        />
        <Link
          to="/"
          className="flex min-w-0 items-center gap-2 font-heading font-semibold md:hidden"
        >
          <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-chart-3 text-sidebar-primary-foreground">
            <FlaskConical className="size-4" />
          </span>
          <span className="truncate">Adaptive Spot Lab</span>
        </Link>
        <div className="ml-auto flex shrink-0 items-center gap-2">
          <LiveBadge />
          <AlertsMenu />
          <ModeToggle />
        </div>
      </div>
    </header>
  )
}
