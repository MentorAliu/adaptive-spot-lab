import { z } from "zod"

// Settings' health tiles (ExecPlan 0060): the account, the Bitcoin spot feed, the spot run, the
// execution worker and the backtest, from recorded facts only.
export const systemStatusSchema = z.strictObject({
  mode: z.literal("PAPER"),
  denomination: z.literal("USDT (virtual)"),
  account: z.enum(["unconfigured", "unfunded", "funded"]),
  market_data: z.enum(["disabled", "unavailable", "degraded", "ready"]),
  trading: z.enum([
    "inactive",
    "running",
    "paused",
    "stopping",
    "stopped",
    "unavailable",
  ]),
  execution_worker: z.enum(["not_running", "running"]),
  backtest: z.enum(["not_computed", "computed", "unavailable"]),
})

export type SystemStatus = z.infer<typeof systemStatusSchema>

export function parseSystemStatus(value: unknown): SystemStatus {
  return systemStatusSchema.parse(value)
}
