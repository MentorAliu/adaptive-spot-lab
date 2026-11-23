import { useSyncExternalStore } from "react"

// One clock for the countdowns and "7 min ago" texts (ExecPlan 0048), ticking each second while
// anything reads it. The server and hydration read null, so text that depends on the time is
// written in the browser after hydration and never differs between the two.
let current = 0
let timer: ReturnType<typeof setInterval> | null = null
const listeners = new Set<() => void>()

function tick() {
  current = Date.now()
  for (const listener of listeners) listener()
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  if (timer === null) {
    current = Date.now()
    timer = setInterval(tick, 1_000)
  }
  return () => {
    listeners.delete(listener)
    if (listeners.size === 0 && timer !== null) {
      clearInterval(timer)
      timer = null
    }
  }
}

function snapshot() {
  if (current === 0) current = Date.now()
  return current
}

/** The time now in milliseconds, or null while the server renders and during hydration. */
export function useNow(): number | null {
  return useSyncExternalStore(subscribe, snapshot, () => null)
}
