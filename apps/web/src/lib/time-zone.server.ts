import "@tanstack/react-start/server-only"
import { getCookie } from "@tanstack/react-start/server"
import { TIME_ZONE_COOKIE, isTimeZone } from "./time-zone"

/** The zone the browser named in its cookie, or UTC until it has (ExecPlan 0037). */
export function cookieTimeZone(): string {
  const zone = getCookie(TIME_ZONE_COOKIE)
  return isTimeZone(zone) ? zone : "UTC"
}
