import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useSyncExternalStore,
} from "react"
import { formatDateTime, zonePlace } from "@/lib/display"
import type { TimeOptions } from "@/lib/display"
import { TIME_ZONE_COOKIE, browserTimeZone } from "@/lib/time-zone"

const TimeZoneContext = createContext("UTC")

const subscribe = () => () => {}

/**
 * Every time on the pages is written in the viewer's zone (ExecPlan 0037). The server writes the
 * zone its cookie names, and hydration keeps that text; then the browser's own zone takes over,
 * and the cookie remembers it, so the next page load is written in it from the start. This is
 * TanStack Start's guidance for time zones in server rendering (cookie first, UTC until then).
 */
export function TimeZoneProvider({
  serverZone,
  children,
}: {
  serverZone: string
  children: React.ReactNode
}) {
  const zone = useSyncExternalStore(
    subscribe,
    () => browserTimeZone() ?? serverZone,
    () => serverZone
  )
  useEffect(() => {
    document.cookie = `${TIME_ZONE_COOKIE}=${encodeURIComponent(zone)}; Path=/; Max-Age=31536000; SameSite=Lax`
  }, [zone])
  return <TimeZoneContext value={zone}>{children}</TimeZoneContext>
}

export function useTimeZone(): string {
  return useContext(TimeZoneContext)
}

/** Which zone the pages' times are in; each time's hover text gives its offset and UTC. */
export function ZoneNote() {
  return <p>{`Times in ${zonePlace(useTimeZone())}`}</p>
}

/** Times in the viewer's zone for text that is not a `DateTime`, such as a sentence's middle. */
export function useTimeText() {
  const zone = useTimeZone()
  return useCallback(
    (value: string | number | null, options?: TimeOptions) =>
      value === null ? "Not recorded" : formatDateTime(value, zone, options),
    [zone]
  )
}
