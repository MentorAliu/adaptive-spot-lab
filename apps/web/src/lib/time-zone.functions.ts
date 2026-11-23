import { createIsomorphicFn } from "@tanstack/react-start"
import { browserTimeZone } from "./time-zone"
import { cookieTimeZone } from "./time-zone.server"

/** The zone a page's times are written in: the cookie's on the server, the browser's own after it. */
export const displayTimeZone = createIsomorphicFn()
  .server(() => cookieTimeZone())
  .client(() => browserTimeZone() ?? "UTC")
