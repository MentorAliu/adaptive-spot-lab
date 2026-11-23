import { useCallback, useSyncExternalStore } from "react"

// A per-browser choice, such as the equity curve's range (ExecPlan 0048): kept in localStorage when
// the browser allows it, and the default when it does not (a private window, blocked storage). The
// server renders the default; the stored choice shows once the page hydrates.

const listeners = new Set<() => void>()
// What this tab chose, for a browser that refuses storage.
const memory = new Map<string, string>()

function subscribe(listener: () => void) {
  listeners.add(listener)
  window.addEventListener("storage", listener)
  return () => {
    listeners.delete(listener)
    window.removeEventListener("storage", listener)
  }
}

function read(key: string): string | null {
  try {
    return window.localStorage.getItem(key) ?? memory.get(key) ?? null
  } catch {
    return memory.get(key) ?? null
  }
}

export function useStoredChoice<T extends string>(
  key: string,
  choices: readonly T[],
  fallback: T
): [T, (next: T) => void] {
  const stored = useSyncExternalStore(
    subscribe,
    () => read(key),
    () => null
  )
  const value = choices.find((choice) => choice === stored) ?? fallback
  const choose = useCallback(
    (next: T) => {
      memory.set(key, next)
      try {
        window.localStorage.setItem(key, next)
      } catch {
        // Storage refused: the choice lasts while the tab is open.
      }
      for (const listener of listeners) listener()
    },
    [key]
  )
  return [value, choose]
}
