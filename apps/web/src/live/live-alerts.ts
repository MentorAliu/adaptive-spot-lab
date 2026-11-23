import { useSyncExternalStore } from "react"
import type { Activity, Trade } from "@/spot/schemas"

// What the owner is told of each trade (ExecPlan 0047 sections 4.6 and 4.7, the spot fills' since
// ExecPlan 0060): toasts in each visible tab, after the cursor this browser shares between its tabs, and
// desktop pop-ups for fills when they are turned on and no tab of the app has focus.
export const SHOWN_MAX = 3
export const CURSOR_KEY = "asl.spot.toast-cursor"
// The key the futures app stored this browser's choice under: kept, so the choice carries over.
export const DESKTOP_KEY = "asl.futures.desktop-alerts"
// How long the tab holding the stream waits for a tab with focus to say it showed the toasts.
export const SEEN_WAIT_MS = 400

/** The toasts one read of the feed gives: the newest three, then a summary of the rest. */
export function plan(activity: Pick<Activity, "count" | "items">) {
  const shown = activity.items.slice(-SHOWN_MAX)
  const more = activity.count - shown.length
  return { shown, more }
}

/** The desktop pop-ups for the same entries: every entry is a fill, so the same three and summary. */
export function popups(activity: Pick<Activity, "count" | "items">) {
  return plan(activity)
}

export function moreText(more: number, where: string) {
  return `${more} more ${more === 1 ? "entry" : "entries"} ${where}`
}

// Without storage a tab keeps its own cursor: a fresh tab starts at the newest entry.
let memoryCursor: string | null = null

export function storedCursor(): string | null {
  try {
    const value = window.localStorage.getItem(CURSOR_KEY)
    return value !== null && /^[0-9]{1,20}$/.test(value) ? value : null
  } catch {
    // Storage blocked: this tab's own cursor.
    return memoryCursor
  }
}

export function storeCursor(cursor: string) {
  memoryCursor = cursor
  try {
    window.localStorage.setItem(CURSOR_KEY, cursor)
  } catch {
    // Storage blocked: the next tab starts at the newest entry again.
  }
}

export function after(cursor: string, than: string): boolean {
  return BigInt(cursor) > BigInt(than)
}

// ---- desktop pop-ups -------------------------------------------------------------------------------

export type DesktopAlerts =
  | "unsupported"
  | "off"
  | "on"
  // Wanted, but the browser's permission was refused (the site's settings in the browser allow it again).
  | "blocked"

const desktopListeners = new Set<() => void>()

function notificationsSupported() {
  return typeof window !== "undefined" && "Notification" in window
}

function desktopWanted(): boolean {
  try {
    return window.localStorage.getItem(DESKTOP_KEY) === "on"
  } catch {
    return false
  }
}

export function desktopAlerts(): DesktopAlerts {
  if (!notificationsSupported()) return "unsupported"
  if (!desktopWanted()) return "off"
  if (Notification.permission === "granted") return "on"
  return Notification.permission === "denied" ? "blocked" : "off"
}

function changed() {
  for (const listener of desktopListeners) listener()
}

function subscribeDesktop(listener: () => void) {
  desktopListeners.add(listener)
  // Another tab may turn them on or off.
  const storage = (event: StorageEvent) => {
    if (event.key === DESKTOP_KEY) listener()
  }
  window.addEventListener("storage", storage)
  return () => {
    desktopListeners.delete(listener)
    window.removeEventListener("storage", storage)
  }
}

export function useDesktopAlerts(): DesktopAlerts {
  return useSyncExternalStore(subscribeDesktop, desktopAlerts, () => "off")
}

/**
 * Turns the pop-ups on or off for this browser. Turning them on asks for the browser's permission,
 * which only a click may do (MDN, "Using the Notifications API").
 */
export async function setDesktopAlerts(on: boolean): Promise<DesktopAlerts> {
  try {
    if (on) window.localStorage.setItem(DESKTOP_KEY, "on")
    else window.localStorage.removeItem(DESKTOP_KEY)
  } catch {
    // Storage blocked: the choice cannot be kept.
  }
  if (on && notificationsSupported() && Notification.permission === "default")
    await Notification.requestPermission()
  changed()
  return desktopAlerts()
}

export type PopupContent = {
  title: string
  body: string
  tag: string
}

/** Shows one desktop pop-up; a click brings this tab forward and runs `open`. */
export function showPopup(content: PopupContent, open: () => void) {
  try {
    const notification = new Notification(content.title, {
      body: content.body,
      tag: content.tag,
    })
    notification.onclick = () => {
      window.focus()
      open()
      notification.close()
    }
  } catch {
    // The browser refused it (permission withdrawn meanwhile): the toasts still show.
  }
}

export function popupFor(
  item: Trade,
  content: { title: string; description?: string }
): PopupContent {
  return {
    title: content.title,
    body: content.description ?? "",
    tag: `asl-fill-${item.seq}`,
  }
}
