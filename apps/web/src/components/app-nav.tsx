import { Link, linkOptions, useLocation } from "@tanstack/react-router"
import { ArrowLeftRight, FlaskConical, Gauge, Settings } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { buttonVariants } from "@/components/ui/button"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { cn } from "@/lib/utils"

// The menu's four sections (ExecPlan 0060 section 4.9): the Cockpit, the trades with the daily
// readings, the backtest, and Settings.
export type Section = "home" | "trades" | "backtest" | "settings"

const SECTIONS: Record<string, Section> = {
  "/": "home",
  "/trades": "trades",
  "/backtest": "backtest",
  "/settings": "settings",
}

/** The section a path belongs to, or null for an address the app does not have. Each section is one
 * page since ExecPlan 0060, so a removed detail page below one marks none. */
export function sectionOf(pathname: string): Section | null {
  const path = pathname.length > 1 ? pathname.replace(/\/+$/, "") : pathname
  return Object.hasOwn(SECTIONS, path) ? SECTIONS[path] : null
}

// Each section's word, icon and first page (ExecPlan 0036 section 4.1): the sidebar, the tab bar and the
// page titles show the same icon for a section.
export const MENU = [
  {
    section: "home",
    // ExecPlan 0048: Home is the Cockpit, a gauge in the menu.
    label: "Cockpit",
    icon: Gauge,
    link: linkOptions({ to: "/" }),
  },
  {
    section: "trades",
    label: "Trades",
    icon: ArrowLeftRight,
    link: linkOptions({ to: "/trades", search: {} }),
  },
  {
    section: "backtest",
    label: "Backtest",
    icon: FlaskConical,
    link: linkOptions({ to: "/backtest", search: {} }),
  },
  {
    section: "settings",
    label: "Settings",
    icon: Settings,
    link: linkOptions({ to: "/settings" }),
  },
] as const satisfies readonly {
  section: Section
  label: string
  icon: LucideIcon
  link: object
}[]

export function menuItem(section: Section) {
  return MENU.find((item) => item.section === section)!
}

function usePath() {
  return useLocation({ select: (location) => location.pathname })
}

export function useSection(): Section | null {
  return sectionOf(usePath())
}

/**
 * The router marks a link current only on its own address; the section marks every page of it. The
 * links keep their link role: they take a button's look from `buttonVariants`, because Base UI's
 * Button names any element it renders a button.
 */
function current(active: boolean) {
  return active ? ("page" as const) : undefined
}

/** The menu in the sidebar, from 768 px: an icon and a word each, the icon alone when collapsed. */
export function SidebarNav() {
  const section = useSection()
  return (
    <nav aria-label="Primary">
      <SidebarMenu>
        {MENU.map((item) => (
          <SidebarMenuItem key={item.section}>
            <SidebarMenuButton
              isActive={section === item.section}
              tooltip={item.label}
              render={
                <Link
                  {...item.link}
                  aria-current={current(section === item.section)}
                />
              }
            >
              <item.icon />
              <span>{item.label}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </nav>
  )
}

/** The menu as a tab bar at the bottom of a phone's screen, below 768 px, where the sidebar is hidden. */
export function TabBarNav() {
  const section = useSection()
  return (
    <nav
      aria-label="Primary"
      className="fixed inset-x-0 bottom-0 z-20 grid grid-cols-4 gap-1 border-t bg-background p-1 pb-[max(--spacing(1),env(safe-area-inset-bottom))] md:hidden"
    >
      {MENU.map((item) => (
        <Link
          key={item.section}
          {...item.link}
          aria-current={current(section === item.section)}
          className={cn(
            buttonVariants({
              variant: section === item.section ? "secondary" : "ghost",
            }),
            "h-auto min-w-0 flex-col gap-0.5 px-1 py-1.5 text-xs"
          )}
        >
          <item.icon />
          {item.label}
        </Link>
      ))}
    </nav>
  )
}
