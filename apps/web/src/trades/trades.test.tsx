import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import {
  cleanup,
  fireEvent,
  render,
  screen,
  within,
} from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"
import readingsSample from "@/spot/samples/readings.json"
import tradesSample from "@/spot/samples/trades.json"
import { readingsListQuery, tradesListQuery } from "@/spot/spot.query"
import { readingPageSchema, tradePageSchema } from "@/spot/schemas"
import type { ReadingPage, TradePage } from "@/spot/schemas"
import { TradesPage } from "./trades-page"
import type { TradesSearch } from "./trades-page"

// ExecPlan 0060 section 4.9: Trades and its daily readings on the engine's own answers on the browser
// chain's scratch database (src/spot/samples): run #1's buy, the owner's Stop and sell, run #2's buy,
// and the two readings that bought.

const navigate = vi.hoisted(() => vi.fn())
vi.mock(import("@tanstack/react-router"), async (original) => ({
  ...(await original()),
  useNavigate: (() => navigate) as never,
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

const trades = tradePageSchema.parse(tradesSample)
const readings = readingPageSchema.parse(readingsSample)

function page(
  search: TradesSearch,
  answers: { trades?: TradePage; readings?: ReadingPage } = {}
) {
  const client = new QueryClient({
    defaultOptions: { queries: { enabled: false, retry: false } },
  })
  client.setQueryData(tradesListQuery().queryKey, {
    pages: [answers.trades ?? trades],
    pageParams: [null],
  })
  client.setQueryData(readingsListQuery().queryKey, {
    pages: [answers.readings ?? readings],
    pageParams: [null],
  })
  render(
    <QueryClientProvider client={client}>
      <TradesPage search={search} />
    </QueryClientProvider>
  )
}

function rows(caption: string): string[][] {
  return within(screen.getByRole("table", { name: caption }))
    .getAllByRole("row")
    .slice(1)
    .map((row) =>
      within(row)
        .getAllByRole("cell")
        .map((cell) => cell.textContent)
    )
}

describe("Trades", () => {
  it("lists every buy and sell, newest first, with its price, fee and why", () => {
    page({})
    expect(
      rows("The account's buys and sells, newest first").map((row) =>
        row.slice(1)
      )
    ).toEqual([
      [
        "Buy",
        "0.00835 BTC",
        "61,037.41 USDT",
        "509.66 USDT",
        "0.51 USDT",
        "Daily ruleTrend up 2 of 3: target 5.1%, held 0.0%",
      ],
      [
        "Sell",
        "0.00835 BTC",
        "61,025.20 USDT",
        "509.56 USDT",
        "0.51 USDT",
        "Run stoppedSold everything when the run stopped, by you",
      ],
      [
        "Buy",
        "0.00835 BTC",
        "61,037.41 USDT",
        "509.66 USDT",
        "0.51 USDT",
        "Daily ruleTrend up 2 of 3: target 5.1%, held 0.0%",
      ],
    ])
    expect(screen.queryByRole("button", { name: "Earlier trades" })).toBeNull()
  })

  it("lists the daily readings on their tab, and switches tabs through the address", () => {
    page({ tab: "readings" })
    expect(
      rows("The rule's daily readings, newest first").map((row) =>
        row.slice(0, 6)
      )
    ).toEqual([
      [
        "12 Nov 2026",
        "60,726.19 USDT",
        "Trend up 2 of 3",
        "5.1%",
        "0.0%",
        "TradedBought 0.00835 BTC at 61,037.41 USDT",
      ],
      [
        "12 Nov 2026",
        "60,726.19 USDT",
        "Trend up 2 of 3",
        "5.1%",
        "0.0%",
        "TradedBought 0.00835 BTC at 61,037.41 USDT",
      ],
    ])
    fireEvent.click(screen.getByRole("tab", { name: "Trades" }))
    expect(navigate).toHaveBeenLastCalledWith({
      search: {},
      resetScroll: false,
    })
  })

  it("says why a day was not traded", () => {
    const [reading] = readings.items
    page(
      { tab: "readings" },
      {
        readings: {
          ...readings,
          items: [
            {
              ...reading,
              outcome: "REFUSED",
              codes: ["BOOK_STALE"],
              fill: null,
              spent: false,
            },
            {
              ...reading,
              outcome: "NOT_READABLE",
              result: "WARMUP",
              reason: "ANCHOR_MISSING_365",
              close: null,
              target: null,
              held: null,
              fill: null,
            },
            {
              ...reading,
              action: "NO_CHANGE",
              outcome: "NO_CHANGE",
              fill: null,
            },
          ],
        },
      }
    )
    expect(
      rows("The rule's daily readings, newest first").map((row) => [
        row[1],
        row[2],
        row[5],
      ])
    ).toEqual([
      [
        "60,726.19 USDT",
        "Trend up 2 of 3",
        "Refused, tries againthe order book is not fresh",
      ],
      ["—", "—", "Not readable yetthe close 365 days before is not stored"],
      [
        "60,726.19 USDT",
        "Trend up 2 of 3",
        "No trade neededClose enough to the target",
      ],
    ])
  })

  it("shows nothing yet, and offers the older ones when there are more", () => {
    page({}, { trades: { ...trades, items: [] } })
    expect(screen.getByText("No trades yet")).toBeTruthy()
    cleanup()
    page({}, { trades: { ...trades, next_cursor: "1" } })
    expect(screen.getByRole("button", { name: "Earlier trades" })).toBeTruthy()
    cleanup()
    page({}, { trades: { ...trades, state: "SCHEMA_PENDING", items: [] } })
    expect(screen.getByText("The database is being updated")).toBeTruthy()
  })
})
