import { cleanup, render, screen, within } from "@testing-library/react"
import type { ReactNode } from "react"
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest"
import { SidebarProvider } from "@/components/ui/sidebar"
import { SidebarNav, TabBarNav, sectionOf } from "./app-nav"

// The menu of four (ExecPlan 0060 section 4.9), in the sidebar from 768 px and in the tab bar below
// (ExecPlan 0036). Links here are plain anchors that keep the props the menu sets; the path the menu
// reads is the one each test names.
let pathname = "/"
vi.mock(import("@tanstack/react-router"), async (original) => {
  const actual = await original()
  const link = ({
    children,
    to,
    className,
    "aria-current": currentPage,
  }: {
    children: ReactNode
    to: string
    className?: string
    "aria-current"?: "page"
  }) => (
    <a href={to} className={className} aria-current={currentPage}>
      {children}
    </a>
  )
  const useLocation = ({
    select,
  }: {
    select: (location: { pathname: string }) => unknown
  }) => select({ pathname })
  return {
    ...actual,
    Link: link as unknown as typeof actual.Link,
    useLocation: useLocation as unknown as typeof actual.useLocation,
  }
})
afterEach(cleanup)

// The sidebar reads the viewport's width with shadcn's useIsMobile; jsdom has no matchMedia.
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

const MENUS: [string, () => ReactNode][] = [
  [
    "sidebar",
    () => (
      <SidebarProvider>
        <SidebarNav />
      </SidebarProvider>
    ),
  ],
  ["tab bar", () => <TabBarNav />],
]

function current(scope: HTMLElement): string[] {
  return within(scope)
    .getAllByRole("link")
    .filter((link) => link.getAttribute("aria-current") === "page")
    .map((link) => link.textContent)
}

describe("the menu's sections", () => {
  it("puts every page in its section, and a removed address in none", () => {
    const cases: [string, ReturnType<typeof sectionOf>][] = [
      ["/", "home"],
      ["/trades", "trades"],
      ["/trades/", "trades"],
      ["/backtest", "backtest"],
      ["/settings", "settings"],
      ["/settings/", "settings"],
      // ExecPlan 0060 removed the futures, AI and old spot pages: they answer "Page not found".
      ["/trades/00000000-0000-4000-8000-000000000001", null],
      ["/decisions", null],
      ["/decisions/00000000-0000-4000-8000-000000000001", null],
      ["/agents/00000000-0000-4000-8000-000000000001", null],
      ["/markets", null],
      ["/coins", null],
      ["/positions", null],
      ["/orders", null],
      ["/experiments/00000000-0000-4000-8000-000000000001", null],
      ["/research", null],
      ["/backtests", null],
      ["/tradesx", null],
    ]
    for (const [path, section] of cases)
      expect(sectionOf(path), path).toBe(section)
  })

  it.each(MENUS)(
    "lists exactly Cockpit, Trades, Backtest and Settings in the %s, and marks the section shown",
    (_, menu) => {
      pathname = "/trades"
      render(menu())
      const nav = screen.getByRole("navigation", { name: "Primary" })
      expect(
        within(nav)
          .getAllByRole("link")
          .map((link) => link.textContent)
      ).toEqual(["Cockpit", "Trades", "Backtest", "Settings"])
      expect(current(nav)).toEqual(["Trades"])
      cleanup()
      pathname = "/backtest"
      render(menu())
      expect(
        current(screen.getByRole("navigation", { name: "Primary" }))
      ).toEqual(["Backtest"])
      cleanup()
      // An address the app does not have marks no section.
      pathname = "/decisions"
      render(menu())
      expect(
        current(screen.getByRole("navigation", { name: "Primary" }))
      ).toEqual([])
    }
  )

  it.each(MENUS)("opens one page per section from the %s", (_, menu) => {
    pathname = "/"
    render(menu())
    const nav = screen.getByRole("navigation", { name: "Primary" })
    expect(
      within(nav)
        .getAllByRole("link")
        .map((link) => link.getAttribute("href"))
    ).toEqual(["/", "/trades", "/backtest", "/settings"])
  })
})

// S4: every route a kept file links to, or navigates to, is one of the routes the app has.
const ROUTES = ["/", "/trades", "/backtest", "/settings"]
const sources = import.meta.glob<string>(
  ["../**/*.tsx", "../**/*.ts", "!../**/*.test.*", "!../routeTree.gen.ts"],
  { query: "?raw", import: "default", eager: true }
)

describe("links to pages", () => {
  it("name only routes the app has", () => {
    const targets = new Map<string, string>()
    for (const [file, text] of Object.entries(sources))
      for (const match of text.matchAll(/\bto(?:=|:\s*)"(\/[^"]*)"/g))
        targets.set(`${file}: ${match[1]}`, match[1])
    expect(targets.size).toBeGreaterThan(5)
    for (const [where, to] of targets) expect(ROUTES, where).toContain(to)
  })
})
