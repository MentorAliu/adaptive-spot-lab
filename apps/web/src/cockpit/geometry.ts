// The Cockpit's drawings worked out as numbers (ExecPlan 0048 section 4.3), apart from React so the
// tests read them. Display only: prices and amounts stay the API's strings everywhere else; here
// they only place a dot on a line.

/** Where a fraction of a limit sits on the gauge: under half calm, then amber, from 80% red. */
export type Level = "calm" | "warning" | "danger"

export function limitLevel(fraction: number): Level {
  if (fraction >= 0.8) return "danger"
  if (fraction >= 0.5) return "warning"
  return "calm"
}

/** A number in [0, 1]; anything else (no limit, NaN) is null. */
export function share(used: number, limit: number): number | null {
  if (!Number.isFinite(used) || !Number.isFinite(limit) || limit <= 0)
    return null
  return Math.min(1, Math.max(0, used / limit))
}

/** How much of a span is left: 1 at its start, 0 at its end. */
export function leftOf(start: number, end: number, now: number): number {
  if (!(end > start)) return 0
  return Math.min(1, Math.max(0, (end - now) / (end - start)))
}
