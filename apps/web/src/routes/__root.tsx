import type { QueryClient } from "@tanstack/react-query"
import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRouteWithContext,
} from "@tanstack/react-router"
import { FileQuestionMark } from "lucide-react"
import type { CSSProperties } from "react"
import { TabBarNav } from "@/components/app-nav"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { ThemeProvider } from "@/components/theme-provider"
import { TimeZoneProvider, ZoneNote } from "@/components/time-zone-provider"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { Toaster } from "@/components/ui/toast"
import { TooltipProvider } from "@/components/ui/tooltip"
import { EmptyState, PageShell } from "@/components/page-parts"
import { LiveTrades } from "@/live/live-trades"
import { displayTimeZone } from "@/lib/time-zone.functions"

import appCss from "../styles.css?url"

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()(
  {
    loader: () => ({ timeZone: displayTimeZone() }),
    head: () => ({
      meta: [
        {
          charSet: "utf-8",
        },
        {
          name: "viewport",
          content: "width=device-width, initial-scale=1",
        },
        {
          title: "Adaptive Spot Lab",
        },
      ],
      links: [
        {
          rel: "stylesheet",
          href: appCss,
        },
      ],
    }),
    component: RootOutlet,
    notFoundComponent: () => (
      <PageShell>
        <EmptyState
          icon={FileQuestionMark}
          title="Page not found."
          description="This address is not one of the app's pages. The menu lists them all."
        />
      </PageShell>
    ),
    shellComponent: RootDocument,
  }
)

function RootOutlet() {
  return (
    <>
      <Outlet />
      <LiveTrades />
    </>
  )
}

// shadcn's dashboard-01 sizes: a 16rem sidebar and a 3rem bar above the page.
const SHELL = {
  "--sidebar-width": "calc(var(--spacing) * 64)",
  "--header-height": "calc(var(--spacing) * 12)",
} as CSSProperties

function RootDocument({ children }: { children: React.ReactNode }) {
  const { timeZone } = Route.useLoaderData()
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <HeadContent />
      </head>
      <body>
        <ThemeProvider>
          <TimeZoneProvider serverZone={timeZone}>
            <TooltipProvider>
              <Toaster>
                <SidebarProvider style={SHELL}>
                  <AppSidebar />
                  <SidebarInset>
                    <SiteHeader />
                    <div className="@container/main flex flex-1 flex-col pb-20 md:pb-0">
                      {children}
                      <footer className="mt-auto flex flex-col gap-1 px-4 py-6 text-xs text-muted-foreground md:hidden">
                        <ZoneNote />
                      </footer>
                    </div>
                  </SidebarInset>
                  <TabBarNav />
                </SidebarProvider>
              </Toaster>
            </TooltipProvider>
          </TimeZoneProvider>
        </ThemeProvider>
        <Scripts />
      </body>
    </html>
  )
}
