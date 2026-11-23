import { afterEach, describe, expect, it } from "vitest"
import { act, renderHook } from "@testing-library/react"
import { chartColors, useDarkTheme } from "./chart-theme"

afterEach(() => {
  document.documentElement.className = ""
})

describe("the charts' colours for the theme", () => {
  it("are Lightweight Charts' defaults in the light theme", () => {
    expect(chartColors(false)).toEqual({
      layout: { background: { color: "#FFFFFF" }, textColor: "#191919" },
      grid: {
        vertLines: { color: "#D6DCDE" },
        horzLines: { color: "#D6DCDE" },
      },
    })
  })

  it("are the dark colours of its customization tutorial in the dark theme", () => {
    expect(chartColors(true)).toEqual({
      layout: { background: { color: "#222" }, textColor: "#DDD" },
      grid: { vertLines: { color: "#444" }, horzLines: { color: "#444" } },
    })
  })
})

describe("useDarkTheme", () => {
  it("follows the dark class on <html> as the theme switches", async () => {
    const { result } = renderHook(() => useDarkTheme())
    expect(result.current).toBe(false)
    await act(async () => {
      document.documentElement.classList.add("dark")
    })
    expect(result.current).toBe(true)
    await act(async () => {
      document.documentElement.classList.replace("dark", "light")
    })
    expect(result.current).toBe(false)
  })
})
