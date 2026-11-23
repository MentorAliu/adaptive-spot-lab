import { render, screen, within } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { parseSystemStatus } from "./status.schema"
import type { SystemStatus } from "./status.schema"
import { StatusTable, StatusTiles, statusRows, toneOf } from "./status-table"
import { createRequestQueryClient } from "./query-client"

// Settings' health (ExecPlan 0060): the account, the Bitcoin price feed, the trading run, the trading
// engine and the backtest, read from the API's status and nothing else.
const status: SystemStatus = {
  mode: "PAPER",
  denomination: "USDT (virtual)",
  account: "funded",
  market_data: "ready",
  trading: "running",
  execution_worker: "running",
  backtest: "not_computed",
}

describe("the status boundary", () => {
  it("takes the API's status as it is and refuses anything else", () => {
    expect(parseSystemStatus(status)).toEqual(status)
    expect(() => parseSystemStatus({ ...status, trading: "enabled" })).toThrow()
    expect(() => parseSystemStatus({ ...status, balance: "100" })).toThrow()
    // The futures era's fields are gone from the API and refused here (ExecPlan 0060).
    expect(() => parseSystemStatus({ ...status, model: "enabled" })).toThrow()
    expect(() =>
      parseSystemStatus({ ...status, decisions: "running" })
    ).toThrow()
    const { backtest: _backtest, ...withoutBacktest } = status
    expect(() => parseSystemStatus(withoutBacktest)).toThrow()
  })

  it("accepts every state the engine names", () => {
    for (const trading of [
      "inactive",
      "running",
      "paused",
      "stopping",
      "stopped",
      "unavailable",
    ])
      expect(parseSystemStatus({ ...status, trading }).trading).toBe(trading)
    for (const backtest of ["not_computed", "computed", "unavailable"])
      expect(parseSystemStatus({ ...status, backtest }).backtest).toBe(backtest)
    for (const market_data of ["disabled", "unavailable", "degraded", "ready"])
      expect(parseSystemStatus({ ...status, market_data }).market_data).toBe(
        market_data
      )
  })

  it("uses a separate Query cache for each server router request", () => {
    const first = createRequestQueryClient()
    const second = createRequestQueryClient()
    first.setQueryData(["system", "status", "M0"], status)
    expect(second.getQueryData(["system", "status", "M0"])).toBeUndefined()
  })
})

describe("the health rows", () => {
  it("lists the five parts in order, in plain words", () => {
    expect(statusRows(status)).toEqual([
      { id: "account", capability: "Account", state: "funded" },
      { id: "market", capability: "Bitcoin price feed", state: "ready" },
      { id: "trading", capability: "Trading run", state: "running" },
      { id: "execution", capability: "Trading engine", state: "running" },
      { id: "backtest", capability: "Backtest", state: "not computed" },
    ])
  })

  it("renders the rows through TanStack Table and shadcn Table", () => {
    const view = render(
      <StatusTable status={{ ...status, execution_worker: "not_running" }} />
    )
    expect(
      within(view.container).getByRole("row", {
        name: /^Trading engine not running/,
      })
    ).toBeTruthy()
    const feed = within(view.container).getByRole("row", {
      name: /Bitcoin price feed ready/,
    })
    expect(within(feed).getByText("ready")).toBeTruthy()
    view.unmount()
  })

  it("draws a tile per part with what its state means", () => {
    const view = render(
      <StatusTiles
        status={{ ...status, market_data: "degraded", trading: "paused" }}
      />
    )
    expect(within(view.container).getByText("Bitcoin price feed")).toBeTruthy()
    expect(within(view.container).getByText("degraded")).toBeTruthy()
    expect(within(view.container).getByText("paused")).toBeTruthy()
    expect(within(view.container).getByText("not computed")).toBeTruthy()
    expect(screen.queryByText("Model runtime")).toBeNull()
    view.unmount()
  })
})

describe("the health table's states (ExecPlan 0036)", () => {
  it("sorts each API state by what it means and keeps an unknown one in view", () => {
    expect(toneOf("ready")).toBe("good")
    expect(toneOf("running")).toBe("good")
    expect(toneOf("computed")).toBe("good")
    expect(toneOf("paused")).toBe("paused")
    expect(toneOf("stopping")).toBe("paused")
    expect(toneOf("unavailable")).toBe("bad")
    expect(toneOf("not running")).toBe("off")
    expect(toneOf("stopped")).toBe("off")
    expect(toneOf("inactive")).toBe("off")
    expect(toneOf("not computed")).toBe("pending")
    expect(toneOf("degraded")).toBe("attention")
    expect(toneOf("unfunded")).toBe("attention")
    expect(toneOf("a state this web does not know")).toBe("attention")
  })
})
