import { createServerFn } from "@tanstack/react-start"
import { setResponseHeader } from "@tanstack/react-start/server"
import { readSystemStatus } from "./status.server"

export const getSystemStatus = createServerFn({ method: "GET" }).handler(
  async () => {
    setResponseHeader("Cache-Control", "private, no-store")
    return readSystemStatus()
  }
)
