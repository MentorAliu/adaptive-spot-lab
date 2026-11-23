import { describe, expect, it } from "vitest"
import type { z } from "zod"
import { systemStatusSchema as statusSchema } from "@/system/status.schema"
import activitySample from "./samples/activity.json"
import backtestSample from "./samples/backtest.json"
import dayCandlesSample from "./samples/candles-1d.json"
import hourCandlesSample from "./samples/candles-1h.json"
import definitionsSample from "./samples/definitions.json"
import marketSample from "./samples/market.json"
import markersSample from "./samples/markers.json"
import overviewSample from "./samples/overview.json"
import readingsSample from "./samples/readings.json"
import requestSample from "./samples/request-stop.json"
import statusSample from "./samples/status.json"
import tradesSample from "./samples/trades.json"
import valuationsSample from "./samples/valuations.json"
import {
  codeText,
  codesText,
  holdText,
  readingText,
  shareText,
  stopText,
  toastFor,
  todayText,
  whyText,
} from "./parts"
import { ruleWords, valueAt } from "./rule-words"
import { available, requestText } from "./run-controls"
import {
  activitySchema,
  backtestSchema,
  candlesSchema,
  definitionsSchema,
  marketSchema,
  markersSchema,
  overviewSchema,
  readingPageSchema,
  requestInput,
  requestSchema,
  tradePageSchema,
  valuationsSchema,
} from "./schemas"
import type { Market, Overview, Reading, SpotRun, Today } from "./schemas"
import { spotStatus } from "./status"

// ExecPlan 0060 section 4.9: the spot pages' words and status, on the engine's own answers. The
// samples are what the API sent on the browser chain's scratch database (services/engine/tests/
// spot_browser_fixture.py): SYNTHETIC prices, the real engine, rule and ledger. Run #1 bought on the
// day's reading, the owner's Stop and sell sold it, and run #2, started by the owner, bought again.

const overview = overviewSchema.parse(overviewSample)
const market = marketSchema.parse(marketSample)
const status = statusSchema.parse(statusSample)
const trades = tradePageSchema.parse(tradesSample).items
const reading = overview.last_reading as Reading
const run = overview.run as SpotRun

describe("the engine's answers", () => {
  const SAMPLES: [string, z.ZodType, unknown][] = [
    ["overview", overviewSchema, overviewSample],
    ["trades", tradePageSchema, tradesSample],
    ["readings", readingPageSchema, readingsSample],
    ["activity", activitySchema, activitySample],
    ["markers", markersSchema, markersSample],
    ["valuations", valuationsSchema, valuationsSample],
    ["backtest", backtestSchema, backtestSample],
    ["definitions", definitionsSchema, definitionsSample],
    ["market", marketSchema, marketSample],
    ["daily candles", candlesSchema, dayCandlesSample],
    ["hourly candles", candlesSchema, hourCandlesSample],
    ["request", requestSchema, requestSample],
    ["status", statusSchema, statusSample],
  ]
  for (const [name, schema, sample] of SAMPLES)
    it(`reads the ${name} as the engine sent it`, () => {
      expect(schema.safeParse(sample).success).toBe(true)
    })

  it("refuses a field it does not know, a number for an amount and a futures leftover", () => {
    expect(
      overviewSchema.safeParse({ ...overviewSample, position: null }).success
    ).toBe(false)
    expect(
      overviewSchema.safeParse({
        ...overviewSample,
        account: { ...overviewSample.account, cash: 9488.7 },
      }).success
    ).toBe(false)
    const trade = tradesSample.items[0]
    for (const changed of [
      { ...trade, leverage: "2" },
      { ...trade, side: "LONG" },
      { ...trade, quantity: "-0.00835" },
      { ...trade, reason: "AGENT_ENTRY" },
    ])
      expect(
        tradePageSchema.safeParse({ ...tradesSample, items: [changed] }).success
      ).toBe(false)
    expect(
      marketSchema.safeParse({ ...marketSample, symbol: "SOLUSDT" }).success
    ).toBe(false)
    const computed = backtestSample.computed
    expect(
      backtestSchema.safeParse({
        ...backtestSample,
        computed: { ...computed, label: "FILLED" },
      }).success
    ).toBe(false)
  })

  it("asks for a request bound to the run shown, with a key the engine accepts", () => {
    const input = {
      kind: "STOP",
      run_id: run.id,
      idempotency_key: "spot-stop-0001",
    }
    expect(requestInput.safeParse(input).success).toBe(true)
    expect(requestInput.safeParse({ ...input, run_id: null }).success).toBe(
      true
    )
    expect(
      requestInput.safeParse({ ...input, idempotency_key: "short" }).success
    ).toBe(false)
    expect(
      requestInput.safeParse({ ...input, kind: "CLOSE_POSITION" }).success
    ).toBe(false)
    const { run_id: _, ...unbound } = input
    expect(requestInput.safeParse(unbound).success).toBe(false)
  })
})

describe("a reading in words", () => {
  it("says the trend, the target and the trade", () => {
    expect(readingText(reading)).toBe(
      "Trend up 2 of 3: hold 5.1% in Bitcoin; bought 0.00835 BTC"
    )
  })

  it("says why a day cannot be read or traded, and when nothing needs to change", () => {
    const waiting = (reason: string): Reading => ({
      ...reading,
      outcome: "NOT_READABLE",
      result: "WARMUP",
      reason,
      fill: null,
    })
    expect(readingText(waiting("ANCHOR_MISSING_365"))).toBe(
      "Not readable yet: the close 365 days before is not stored"
    )
    expect(readingText(waiting("TOO_FEW_DAYS_120"))).toBe(
      "Not readable yet: too few days stored (120) to measure how much Bitcoin moves"
    )
    expect(readingText(waiting("CLOSE_MISSING"))).toBe(
      "Not readable yet: the day's close is not stored yet"
    )
    expect(
      readingText({
        ...reading,
        outcome: "REFUSED",
        codes: ["BOOK_STALE", "DEPTH_SHORT"],
        fill: null,
      })
    ).toBe(
      "Trend up 2 of 3: hold 5.1% in Bitcoin; no trade: the order book is not fresh; the order book is too thin for the trade"
    )
    expect(
      readingText({
        ...reading,
        up: 0,
        target: "0",
        held: "0.051",
        action: "SELL_ALL",
        fill: reading.fill && { ...reading.fill, side: "SELL" },
      })
    ).toBe("Trend up 0 of 3: hold no Bitcoin; sold 0.00835 BTC")
    expect(
      readingText({
        ...reading,
        action: "NO_CHANGE",
        outcome: "NO_CHANGE",
        fill: null,
      })
    ).toBe("Trend up 2 of 3: hold 5.1% in Bitcoin; no trade needed")
  })

  it("shows a code it does not know as the engine wrote it", () => {
    expect(codeText("SOMETHING_NEW")).toBe("something new")
    expect(codesText([])).toBe("no reason recorded")
    expect(codesText(["CASH_SHORT", "RUN_NOT_RUNNING"])).toBe(
      "not enough USDT for the buy and its fee; the run is paused, so it buys nothing"
    )
  })

  it("writes shares, holds and stops in words", () => {
    expect(shareText(overview.account?.share ?? null)).toBe("5.1%")
    expect(shareText("1")).toBe("100.0%")
    expect(shareText(null)).toBe("unknown")
    expect(holdText([])).toBe("Nothing holds it")
    expect(holdText(["OWNER"])).toBe("Held by your Pause")
    expect(holdText(["OWNER", "DAILY_LOSS", "INTEGRITY"])).toBe(
      "Held by your Pause, the daily loss limit and a failed reconciliation check"
    )
    expect([stopText("OWNER"), stopText("DRAWDOWN"), stopText(null)]).toEqual([
      "you",
      "the drawdown stop",
      "the app",
    ])
  })

  it("says when today's reading comes", () => {
    const at = (iso: string) => iso.slice(11, 16)
    const today = overview.today as Today
    const day = (fields: Partial<Today>): Today => ({ ...today, ...fields })
    expect(todayText(null, at)).toBe(
      "No reading: the account is not set up yet."
    )
    expect(todayText(today, at)).toBe("Done for today. Next reading at 00:05.")
    expect(todayText(day({ status: "WAITING" }), at)).toBe(
      "Today's reading at 00:05."
    )
    expect(
      todayText(day({ status: "WAITING", next_reading_at: null }), at)
    ).toBe("Today's reading comes just after midnight UTC.")
    expect(todayText(day({ status: "DUE" }), at)).toBe(
      "Today's reading is due now."
    )
    expect(todayText(day({ status: "RETRYING" }), at)).toBe(
      "Today's reading tries again every 15 minutes."
    )
    expect(todayText(day({ status: "NONE" }), at)).toBe(
      "No reading while the run is stopping or stopped."
    )
  })
})

describe("a trade in words", () => {
  const [buy, stopSell] = trades

  it("says why it was made", () => {
    expect(whyText(buy)).toBe("Trend up 2 of 3: target 5.1%, held 0.0%")
    expect(whyText(stopSell)).toBe(
      "Sold everything when the run stopped, by you"
    )
    expect(whyText({ ...buy, reading: null })).toBe("The rule's daily reading")
  })

  it("makes its toast: a buy as news, the run's stop as a warning", () => {
    expect(toastFor(buy)).toEqual({
      title: "Bought 0.00835 BTC at 61,037.41 USDT",
      description: "Trend up 2 of 3: target 5.1%, held 0.0%. Fee 0.51 USDT.",
      type: "info",
    })
    expect(toastFor(stopSell)).toEqual({
      title: "Sold 0.00835 BTC at 61,025.20 USDT",
      description: "The run stopped, by you. Fee 0.51 USDT.",
      type: "warning",
    })
    expect(toastFor({ ...stopSell, stop_reason: "DRAWDOWN" }).description).toBe(
      "The run stopped, by the drawdown stop. Fee 0.51 USDT."
    )
  })
})

describe("the trading status", () => {
  const reads = { overview, market, status }
  const withRun = (fields: Partial<SpotRun>): Overview => ({
    ...overview,
    run: { ...run, ...fields },
  })

  it("is all good while the run trades and every read answered", () => {
    expect(spotStatus(reads)).toEqual({
      state: "trading",
      title: "Trading by itself",
      notes: [],
    })
  })

  it("is unknown while a read failed, and says which, without guessing", () => {
    const unread = spotStatus({ ...reads, market: null, status: null })
    expect(unread.state).toBe("unknown")
    expect(unread.notes[0].text).toBe(
      "The app could not read the Bitcoin price feed and the app's health. Nothing is guessed; the page reads again by itself."
    )
    const noAccount = spotStatus({ ...reads, overview: null })
    expect(noAccount.title).toBe("Status unknown")
    expect(noAccount.notes.map((note) => note.text)).toEqual([
      "The app could not read the account. Nothing is guessed; the page reads again by itself.",
    ])
    // A read that failed beside a stopped run: unknown, and the stop is still told.
    const stopped = spotStatus({
      ...reads,
      status: null,
      overview: withRun({ state: "STOPPED", stop_reason: "DRAWDOWN" }),
    })
    expect(stopped.state).toBe("unknown")
    expect(stopped.notes.map((note) => note.kind)).toEqual([
      "problem",
      "action",
    ])
    expect(
      spotStatus({
        ...reads,
        overview: { ...overview, state: "SCHEMA_PENDING" },
      }).state
    ).toBe("unknown")
  })

  it("holds the buys while the engine or the feed is down", () => {
    const worker = spotStatus({
      ...reads,
      status: { ...status, execution_worker: "not_running" },
    })
    expect(worker.state).toBe("held")
    expect(worker.notes[0]).toMatchObject({ kind: "problem", place: "health" })
    const feed: Market = { ...market, status: "DEGRADED" }
    expect(spotStatus({ ...reads, market: feed }).notes[0].text).toBe(
      "The Bitcoin price feed is behind, so trades wait for a fresh order book."
    )
  })

  it("asks the owner only for what only the owner can do", () => {
    const stopped = spotStatus({
      ...reads,
      overview: withRun({ state: "STOPPED", stop_reason: "DRAWDOWN" }),
    })
    expect(stopped).toMatchObject({ state: "stopped", title: "Not trading" })
    expect(stopped.notes).toEqual([
      {
        kind: "action",
        text: "Run #2 was stopped by the drawdown stop. Nothing trades until you start a new run.",
        place: "run",
      },
    ])
    const paused = spotStatus({
      ...reads,
      overview: withRun({ state: "PAUSED", causes: ["DAILY_LOSS", "OWNER"] }),
    })
    expect(paused.state).toBe("held")
    // What needs the owner comes first; the daily loss limit clears by itself.
    expect(paused.notes.map((note) => [note.kind, note.place])).toEqual([
      ["action", "run"],
      ["info", "rule"],
    ])
    expect(paused.notes[1].text).toBe(
      "The account fell 2% today, so it buys nothing until the next UTC day."
    )
    const stopping = spotStatus({
      ...reads,
      overview: withRun({ state: "STOPPING", stop_reason: "OWNER" }),
    })
    expect(stopping.state).toBe("held")
    expect(stopping.notes[0].text).toBe(
      "Run #2 is stopping, by you: it sells the Bitcoin at the order book, then stops."
    )
  })

  it("says what a fresh account waits for", () => {
    const fresh = spotStatus({
      ...reads,
      overview: {
        ...overview,
        account: overview.account && {
          ...overview.account,
          initialized: false,
        },
        run: null,
      },
    })
    expect(fresh.state).toBe("stopped")
    expect(fresh.notes[0].kind).toBe("info")
    expect(spotStatus({ ...reads, overview: withNoRun() }).notes[0].text).toBe(
      "The first run starts by itself within a few seconds."
    )
  })

  it("says why today's reading tries again", () => {
    const retrying = (fields: Partial<Reading>): Overview => ({
      ...overview,
      today: { ...(overview.today as Today), status: "RETRYING" },
      last_reading: { ...reading, spent: false, ...fields },
    })
    expect(
      spotStatus({
        ...reads,
        overview: retrying({
          outcome: "REFUSED",
          codes: ["BOOK_STALE"],
          fill: null,
        }),
      }).notes
    ).toEqual([
      {
        kind: "info",
        text: "Today's trade was refused: the order book is not fresh. It tries again every 15 minutes.",
      },
    ])
    expect(
      spotStatus({
        ...reads,
        overview: retrying({
          outcome: "NOT_READABLE",
          reason: "CLOSE_MISSING",
          fill: null,
        }),
      }).notes[0].text
    ).toBe(
      "Today's reading waits: the day's close is not stored yet. It tries again every 15 minutes."
    )
  })

  function withNoRun(): Overview {
    return { ...overview, run: null }
  }
})

describe("the run's controls", () => {
  const withRun = (fields: Partial<SpotRun>): Overview => ({
    ...overview,
    run: { ...run, ...fields },
  })

  it("offers what the engine accepts in each state", () => {
    expect(available(overview)).toEqual(["PAUSE", "STOP"])
    expect(
      available(withRun({ state: "PAUSED", causes: ["OWNER", "DAILY_LOSS"] }))
    ).toEqual(["RESUME", "STOP"])
    // A pause by a limit is not the owner's to resume.
    expect(
      available(withRun({ state: "PAUSED", causes: ["DAILY_LOSS"] }))
    ).toEqual(["PAUSE", "STOP"])
    expect(available(withRun({ state: "STOPPING" }))).toEqual([])
    expect(available(withRun({ state: "STOPPED" }))).toEqual(["START"])
    expect(available({ ...overview, run: null })).toEqual(["START"])
    expect(available({ ...overview, state: "SCHEMA_PENDING" })).toEqual([])
    expect(
      available({
        ...overview,
        account: overview.account && {
          ...overview.account,
          initialized: false,
        },
      })
    ).toEqual([])
  })

  it("tells a recorded request in a line", () => {
    const request = requestSchema.parse(requestSample)
    expect(requestText(request)).toBe("Stop and sell was applied.")
    expect(requestText({ ...request, status: "PENDING" })).toBe(
      "Stop and sell is waiting for the engine."
    )
    expect(
      requestText({
        ...request,
        kind: "START",
        status: "REJECTED",
        reasons: ["RUN_LIVE"],
      })
    ).toBe("Start trading was refused: a run is already going.")
  })
})

describe("the rule and its limits in words", () => {
  const definitions = definitionsSchema.parse(definitionsSample)

  it("writes each sentence from the documents in force", () => {
    expect(ruleWords(definitions)).toEqual({
      when: "Once a UTC day, just after 00:05 UTC, it reads the last complete day's close; a day it cannot trade yet is tried again every 15 minutes.",
      trend:
        "It compares that close with the closes 30, 91 and 365 days before. It holds Bitcoin only while the close is above more of them than below, and never borrows or sells short.",
      size: "The share it holds aims for the account to swing about 5% a year: the more of those closes it is above and the calmer Bitcoin has been, the larger the share, up to all of the account.",
      trade:
        "It buys or sells the difference only when its target is more than 3% of the account away from what is held; a target of nothing sells everything.",
      dailyLoss:
        "When the account falls 2% below the UTC day's reference value, it buys nothing more that day; sells still go through, and the limit clears at the next day's reference.",
      drawdown:
        "When the account falls 8% below the run's high, the run sells everything at once and stops. Only you can start a new one.",
      costs:
        "Market orders priced from the top 10 levels of the order book, 1 basis point of slippage against each, and a 0.1% fee, paid in USDT.",
    })
  })

  it("leaves out a value a later document no longer has, rather than guessing it", () => {
    const words = ruleWords({
      ...definitions,
      rule_document: {},
      policy_document: {},
      cost_document: {},
    })
    expect(words.when).toBe(
      "Once a UTC day, just after midnight UTC, it reads the last complete day's close."
    )
    expect(words.trend).toMatch(/^It compares that close with earlier closes\./)
    expect(words.drawdown).toMatch(/^When the account falls its limit below/)
    expect(words.costs).toBe(
      "Market orders priced from the order book, paid in USDT."
    )
    expect(valueAt({ a: { b: "1" } }, "a", "b")).toBe("1")
    expect(valueAt({ a: { b: 2 } }, "a", "b")).toBe("2")
    expect(valueAt({ a: ["x"] }, "a", "0")).toBeNull()
    expect(valueAt({ a: "" }, "a")).toBeNull()
  })
})
