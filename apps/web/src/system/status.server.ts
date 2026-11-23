import "@tanstack/react-start/server-only"
import { readFile } from "node:fs/promises"
import { parseSystemStatus } from "./status.schema"
import type { SystemStatus } from "./status.schema"

export async function readSystemStatus(): Promise<SystemStatus> {
  const baseUrl = process.env.ASL_API_BASE_URL
  if (!baseUrl) throw new Error("Private engine address is not configured")

  const keyPath =
    process.env.ASL_INTERNAL_KEY_FILE ?? "/run/secrets/api_internal_key"
  let key: string
  try {
    key = (await readFile(keyPath, "utf8")).trim()
  } catch {
    throw new Error("Private engine identity is unavailable")
  }
  if (!key) throw new Error("Private engine identity is unavailable")

  let response: Response
  try {
    response = await fetch(new URL("/v1/system/status", baseUrl), {
      headers: { "X-Internal-Key": key },
      cache: "no-store",
      signal: AbortSignal.timeout(3_000),
    })
  } catch {
    throw new Error("Private engine is unavailable")
  }
  if (!response.ok) throw new Error("Private engine is not ready")
  return parseSystemStatus(await response.json())
}
