import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest"
import { ModeToggle } from "./mode-toggle"
import { ThemeProvider } from "./theme-provider"

// The script that sets the class before hydration needs a router; the browser suites cover it.
vi.mock(import("@tanstack/react-router"), async (original) => ({
  ...(await original()),
  ScriptOnce: () => null,
}))

// shadcn's dark mode (ExecPlan 0036 section 4.2): the switch stores the choice and sets the class on
// <html>; System follows the device. jsdom has no matchMedia: here the device prefers light.
beforeAll(() => {
  Object.defineProperty(window, "matchMedia", {
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      addEventListener: () => {},
      removeEventListener: () => {},
    }),
  })
})

afterEach(() => {
  cleanup()
  localStorage.clear()
  document.documentElement.className = ""
  document.documentElement.style.colorScheme = ""
})

// Base UI opens a menu on the trigger's mousedown, as a pointer does; a radio item keeps it open.
async function pick(name: string) {
  if (screen.queryByRole("menu") === null)
    fireEvent.mouseDown(screen.getByRole("button", { name: "Theme" }))
  const item = await screen.findByRole("menuitemradio", { name })
  fireEvent.click(item)
  expect(item.getAttribute("aria-checked")).toBe("true")
}

describe("the theme switch", () => {
  it("offers Light, Dark and System, and keeps the choice", async () => {
    render(
      <ThemeProvider>
        <ModeToggle />
      </ThemeProvider>
    )
    await pick("Dark")
    expect(document.documentElement.classList.contains("dark")).toBe(true)
    expect(document.documentElement.style.colorScheme).toBe("dark")
    expect(localStorage.getItem("theme")).toBe("dark")

    await pick("Light")
    expect(document.documentElement.classList.contains("dark")).toBe(false)
    expect(document.documentElement.classList.contains("light")).toBe(true)
    expect(localStorage.getItem("theme")).toBe("light")

    await pick("System")
    expect(document.documentElement.classList.contains("light")).toBe(true)
    expect(localStorage.getItem("theme")).toBe("system")
  })

  it("applies a stored choice after hydration", async () => {
    localStorage.setItem("theme", "dark")
    render(
      <ThemeProvider>
        <ModeToggle />
      </ThemeProvider>
    )
    await screen.findByRole("button", { name: "Theme" })
    expect(document.documentElement.classList.contains("dark")).toBe(true)
  })
})
