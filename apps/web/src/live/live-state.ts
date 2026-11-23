import { useSyncExternalStore } from "react"

// The live connection's state in this tab (ExecPlan 0047 section 4.4): the header shows it, and the
// spot reads poll slower while it is live. The server renders "connecting", as does each tab
// until its connection, or the tab holding it, says otherwise.
export type LiveState = "connecting" | "live" | "offline"

let current: LiveState = "connecting"
const listeners = new Set<() => void>()

export function liveState(): LiveState {
  return current
}

export function setLiveState(next: LiveState) {
  if (next === current) return
  current = next
  for (const listener of listeners) listener()
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

export function useLiveState(): LiveState {
  return useSyncExternalStore(subscribe, liveState, () => "connecting")
}
