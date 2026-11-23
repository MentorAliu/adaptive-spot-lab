import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react"
import type { ReactNode } from "react"
import { afterEach, describe, expect, it, vi } from "vitest"
import type { Workspace } from "@/account/schemas"
import definitionsSample from "@/spot/samples/definitions.json"
import overviewSample from "@/spot/samples/overview.json"
import requestSample from "@/spot/samples/request-stop.json"
import statusSample from "@/spot/samples/status.json"
import { postSpotRequest, resolveSpotRequest } from "@/spot/spot.functions"
import type * as SpotFunctions from "@/spot/spot.functions"
import { definitionsQuery, spotOverviewQuery } from "@/spot/spot.query"
import { RuleSettings } from "@/spot/rule-words"
import { SpotRunSettings } from "@/spot/run-controls"
import {
  definitionsSchema,
  overviewSchema,
  requestSchema,
} from "@/spot/schemas"
import type { Overview, SpotRun } from "@/spot/schemas"
import { statusQueryOptions } from "@/system/status.query"
import { systemStatusSchema } from "@/system/status.schema"
import { SettingsPage } from "./settings-page"

// ExecPlan 0060 section 4.9: Settings' run controls, the rule in words, and the app's health and version,
// on the engine's own answers on the browser chain's scratch database (src/spot/samples). The account's
// top-ups are tested in src/account; here that section is a stand-in.

vi.mock("@/spot/spot.functions", async (original) => ({
  ...(await original<typeof SpotFunctions>()),
  postSpotRequest: vi.fn(),
  resolveSpotRequest: vi.fn(),
}))
vi.mock("@/account/account-home", () => ({
  AccountHome: () => <p>The account&apos;s top-ups</p>,
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

const overview = overviewSchema.parse(overviewSample)
const run = overview.run as SpotRun
const definitions = definitionsSchema.parse(definitionsSample)

function withRun(fields: Partial<SpotRun>): Overview {
  return { ...overview, run: { ...run, ...fields } }
}

function withData(node: ReactNode, fill: (client: QueryClient) => void) {
  const client = new QueryClient({
    defaultOptions: { queries: { enabled: false, retry: false } },
  })
  fill(client)
  render(<QueryClientProvider client={client}>{node}</QueryClientProvider>)
  return client
}

function runSettings(answer: Overview = overview) {
  return withData(<SpotRunSettings />, (client) =>
    client.setQueryData(spotOverviewQuery.queryKey, answer)
  )
}

function factOf(label: string): string {
  const term = screen.getByText(label, { selector: "dt" })
  return term.nextElementSibling?.textContent ?? ""
}

function buttons(): string[] {
  return screen.getAllByRole("button").map((button) => button.textContent)
}

describe("Settings' trading run", () => {
  it("shows the run's state with the controls it allows", () => {
    runSettings()
    expect(screen.getByRole("heading", { name: "Run #2" })).toBeTruthy()
    expect(screen.getByText("Trading")).toBeTruthy()
    expect(buttons()).toEqual(["Pause", "Stop and sell"])
    expect(factOf("Started")).toMatch(/ by you$/)
    expect(factOf("From")).toBe("9,998.88 USDT")
    expect(factOf("Below the run's high")).toBe("0.01%")
  })

  it("asks before Stop and sell, then sends it bound to the run shown", async () => {
    vi.mocked(postSpotRequest).mockResolvedValue({
      kind: "RESULT",
      value: requestSchema.parse(requestSample),
    })
    const client = runSettings()
    const refresh = vi.spyOn(client, "invalidateQueries")
    fireEvent.click(screen.getByRole("button", { name: "Stop and sell" }))
    const dialog = within(await screen.findByRole("alertdialog"))
    expect(dialog.getByText("Stop and sell: run #2?")).toBeTruthy()
    expect(
      dialog.getByText(
        "Ends the run: the Bitcoin held is sold at once at the order book, then nothing trades. Only you can start a new run."
      )
    ).toBeTruthy()
    const confirm = dialog.getByRole("button", { name: "Stop and sell" })
    expect(confirm.className).toMatch(/destructive/)
    expect(postSpotRequest).not.toHaveBeenCalled()
    fireEvent.click(confirm)
    await waitFor(() => expect(postSpotRequest).toHaveBeenCalledTimes(1))
    const sent = vi.mocked(postSpotRequest).mock.calls[0][0] as {
      data: { kind: string; run_id: string | null; idempotency_key: string }
    }
    expect(sent.data).toMatchObject({ kind: "STOP", run_id: run.id })
    expect(sent.data.idempotency_key).toMatch(/^[A-Za-z0-9_-]{8,64}$/)
    expect(
      await screen.findByText(
        "Stop and sell accepted. The engine applies it within a second; this page shows the run's new state."
      )
    ).toBeTruthy()
    expect(refresh).toHaveBeenCalledWith({ queryKey: ["spot"] })
  })

  it("says a refusal in words, and finds out what became of a request it lost", async () => {
    vi.mocked(postSpotRequest).mockResolvedValueOnce({
      kind: "REJECTED",
      code: "RUN_CHANGED",
    })
    runSettings()
    fireEvent.click(screen.getByRole("button", { name: "Pause" }))
    fireEvent.click(
      within(await screen.findByRole("alertdialog")).getByRole("button", {
        name: "Pause",
      })
    )
    expect(
      await screen.findByText(/the run changed since the page showed it/)
    ).toBeTruthy()
    // The answer is lost on the way back: the page asks the engine by the request's key.
    vi.mocked(postSpotRequest).mockRejectedValueOnce(new Error("network"))
    vi.mocked(resolveSpotRequest).mockResolvedValueOnce({
      kind: "RESULT",
      value: { ...requestSchema.parse(requestSample), kind: "PAUSE" },
    })
    fireEvent.click(screen.getByRole("button", { name: "Pause" }))
    fireEvent.click(
      within(await screen.findByRole("alertdialog")).getByRole("button", {
        name: "Pause",
      })
    )
    const check = await screen.findByRole("button", { name: /Check/ })
    fireEvent.click(check)
    expect(await screen.findByText("Pause was applied.")).toBeTruthy()
    const key = (
      vi.mocked(postSpotRequest).mock.calls[1][0] as {
        data: { idempotency_key: string }
      }
    ).data.idempotency_key
    expect(resolveSpotRequest).toHaveBeenCalledWith({ data: { key } })
  })

  it("offers Resume for the owner's pause, Start once stopped and nothing while the run sells", () => {
    runSettings(withRun({ state: "PAUSED", causes: ["OWNER"] }))
    expect(buttons()).toEqual(["Resume", "Stop and sell"])
    expect(screen.getByText("Held by your Pause")).toBeTruthy()
    cleanup()

    runSettings(
      withRun({
        state: "STOPPED",
        stop_reason: "DRAWDOWN",
        stopped_at: "2026-11-12T14:00:00Z",
      })
    )
    expect(buttons()).toEqual(["Start trading"])
    expect(factOf("Stopped")).toMatch(/ by the drawdown stop$/)
    expect(screen.queryByText("Below the run's high")).toBeNull()
    cleanup()

    runSettings(withRun({ state: "STOPPING", stop_reason: "OWNER" }))
    expect(screen.queryAllByRole("button")).toEqual([])
    expect(
      screen.getByText(
        "No control while the run sells its Bitcoin; it stops by itself once only USDT is held."
      )
    ).toBeTruthy()
  })

  it("starts a new run with no run named", async () => {
    vi.mocked(postSpotRequest).mockResolvedValue({
      kind: "RESULT",
      value: { ...requestSchema.parse(requestSample), kind: "START" },
    })
    runSettings(withRun({ state: "STOPPED", stop_reason: "OWNER" }))
    fireEvent.click(screen.getByRole("button", { name: "Start trading" }))
    const dialog = within(await screen.findByRole("alertdialog"))
    expect(dialog.getByText("Start a new trading run?")).toBeTruthy()
    fireEvent.click(dialog.getByRole("button", { name: "Start trading" }))
    await waitFor(() => expect(postSpotRequest).toHaveBeenCalledTimes(1))
    expect(
      (vi.mocked(postSpotRequest).mock.calls[0][0] as { data: object }).data
    ).toMatchObject({ kind: "START", run_id: null })
  })
})

describe("Settings' rule and limits", () => {
  it("writes the rule in force in words, with its ids and hashes", () => {
    withData(<RuleSettings />, (client) =>
      client.setQueryData(definitionsQuery.queryKey, definitions)
    )
    expect(
      screen.getByText(
        "The rule, in code: no person and no AI decides a trade."
      )
    ).toBeTruthy()
    expect(
      screen.getByText(
        "When the account falls 8% below the run's high, the run sells everything at once and stops. Only you can start a new one."
      )
    ).toBeTruthy()
    expect(
      screen.getByText(
        "SPOT_RULE_V1 ac8b5e989985… · SPOT_POLICY_V1 f424c2a04373… · SPOT_COST_V1 ae7f8a3610dc…"
      )
    ).toBeTruthy()
  })
})

describe("the Settings page", () => {
  it("has a section each for the run, the rule, the account and the health, with the version", () => {
    withData(
      <SettingsPage
        workspace={{} as Workspace}
        workspaceVerified
        workspaceError={false}
      />,
      (client) => {
        client.setQueryData(spotOverviewQuery.queryKey, overview)
        client.setQueryData(definitionsQuery.queryKey, definitions)
        client.setQueryData(
          statusQueryOptions.queryKey,
          systemStatusSchema.parse(statusSample)
        )
      }
    )
    expect(
      within(screen.getByRole("navigation", { name: "Settings sections" }))
        .getAllByRole("link")
        .map((link) => [link.textContent, link.getAttribute("href")])
    ).toEqual([
      ["Trading run", "#run"],
      ["Rule and limits", "#rule"],
      ["Account", "#account"],
      ["Health", "#health"],
    ])
    expect(
      screen.getAllByRole("heading", { level: 2 }).map((h) => h.textContent)
    ).toEqual(["Trading run", "Rule and limits", "Account", "Health"])
    expect(screen.getByText("The account's top-ups")).toBeTruthy()
    expect(screen.getByText("App version")).toBeTruthy()
    expect(screen.getByText(definitions.code_identity)).toBeTruthy()
  })
})
