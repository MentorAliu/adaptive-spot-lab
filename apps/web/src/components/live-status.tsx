import { Bell, BellOff, BellRing, Radio, WifiOff } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Spinner } from "@/components/ui/spinner"
import { setDesktopAlerts, useDesktopAlerts } from "@/live/live-alerts"
import type { DesktopAlerts } from "@/live/live-alerts"
import { useLiveState } from "@/live/live-state"
import type { LiveState } from "@/live/live-state"

const STATES: Record<LiveState, { label: string; detail: string }> = {
  live: {
    label: "Live",
    detail: ": trades show the moment the engine saves them",
  },
  connecting: { label: "Connecting", detail: " to the live trades" },
  offline: {
    label: "Offline",
    detail:
      ": the pages refresh every few seconds until the live connection is back",
  },
}

/**
 * Whether the trades are live (ExecPlan 0047 section 4.8). On a phone only the icon shows; the
 * words stay for screen readers.
 */
export function LiveBadge() {
  const state = useLiveState()
  const { label, detail } = STATES[state]
  return (
    <Badge
      variant={state === "offline" ? "secondary" : "outline"}
      role="status"
      data-state={state}
    >
      {state === "live" ? (
        <Radio data-icon="inline-start" />
      ) : state === "connecting" ? (
        <Spinner data-icon="inline-start" aria-hidden />
      ) : (
        <WifiOff data-icon="inline-start" />
      )}
      <span className="sr-only sm:not-sr-only">{label}</span>
      <span className="sr-only">{detail}</span>
    </Badge>
  )
}

const DESKTOP: Record<DesktopAlerts, string> = {
  on: "A pop-up for each buy and sell while the app is in the background.",
  off: "Turn on for a pop-up for each buy and sell while the app is in the background.",
  blocked:
    "Blocked by this browser: allow notifications for this site in the browser's site settings, then turn them on here.",
  unsupported: "This browser cannot show desktop pop-ups.",
}

/** The bell: desktop pop-ups for this browser, asked of the browser on the click that turns them on. */
export function AlertsMenu() {
  const desktop = useDesktopAlerts()
  const Icon =
    desktop === "on" ? BellRing : desktop === "blocked" ? BellOff : Bell
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={<Button variant="outline" size="icon-sm" />}
        aria-label="Trade alerts"
      >
        <Icon />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-72">
        <DropdownMenuGroup>
          <DropdownMenuLabel>Trade alerts</DropdownMenuLabel>
          <DropdownMenuCheckboxItem
            checked={desktop === "on"}
            disabled={desktop === "unsupported"}
            onCheckedChange={(checked) => void setDesktopAlerts(checked)}
          >
            <span className="flex flex-col gap-0.5">
              <span>Desktop pop-ups</span>
              <span className="text-xs text-muted-foreground">
                {DESKTOP[desktop]}
              </span>
            </span>
          </DropdownMenuCheckboxItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
