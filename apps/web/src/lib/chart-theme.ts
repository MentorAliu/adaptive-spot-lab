// The charts follow the app's light and dark theme with Lightweight Charts' own colours.

import { useSyncExternalStore } from "react"

/**
 * The chart's backdrop for the theme. Light is the library's defaults, written out because
 * `applyOptions` merges and has no reset; dark is the colours its customization tutorial, "Chart
 * colors", gives "to better suit a dark theme". Candles, lines and markers keep their colours in both.
 */
export function chartColors(dark: boolean) {
  return dark
    ? {
        layout: { background: { color: "#222" }, textColor: "#DDD" },
        grid: { vertLines: { color: "#444" }, horzLines: { color: "#444" } },
      }
    : {
        layout: { background: { color: "#FFFFFF" }, textColor: "#191919" },
        grid: {
          vertLines: { color: "#D6DCDE" },
          horzLines: { color: "#D6DCDE" },
        },
      }
}

function subscribe(onChange: () => void) {
  const observer = new MutationObserver(onChange)
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  })
  return () => observer.disconnect()
}

/**
 * Whether the page shows the dark theme, from the `dark` class the theme provider sets on `<html>`,
 * so a System choice follows the device too. The server renders light; the charts draw in the browser.
 */
export function useDarkTheme(): boolean {
  return useSyncExternalStore(
    subscribe,
    () => document.documentElement.classList.contains("dark"),
    () => false
  )
}
