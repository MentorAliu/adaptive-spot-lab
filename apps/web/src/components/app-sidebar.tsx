import { Link } from "@tanstack/react-router"
import { Clock, FlaskConical } from "lucide-react"
import type { ComponentProps } from "react"
import { SidebarNav } from "@/components/app-nav"
import { ZoneNote } from "@/components/time-zone-provider"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"

/**
 * The app's sidebar (ExecPlan 0036 section 4.1), after shadcn's dashboard-01 block: the app's mark and
 * name, the menu, and the time zone of the pages' times. From 768 px; phones get the tab bar.
 */
export function AppSidebar(props: ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              size="lg"
              tooltip="Adaptive Spot Lab"
              render={<Link to="/" />}
            >
              <span className="flex aspect-square size-8 items-center justify-center rounded-lg bg-chart-3 text-sidebar-primary-foreground">
                <FlaskConical />
              </span>
              <span className="grid flex-1 text-left leading-tight">
                <span className="truncate font-heading font-semibold">
                  Adaptive Spot Lab
                </span>
                <span className="truncate text-xs text-sidebar-foreground/70">
                  BTCUSDT · spot
                </span>
              </span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Menu</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarNav />
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <div className="flex items-start gap-2 rounded-lg border border-sidebar-border p-2 text-xs text-sidebar-foreground/70 group-data-[collapsible=icon]:hidden">
          <Clock className="mt-0.5 size-4 shrink-0" />
          <ZoneNote />
        </div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
