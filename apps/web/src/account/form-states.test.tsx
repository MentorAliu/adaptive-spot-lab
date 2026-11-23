import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { AccountHome } from "./account-home"
import { getTopupDraft } from "./account.functions"
import { clearFundingIntent, loadFundingIntent } from "./funding-intent"
import { accountSchema, fundingSchema } from "./schemas"

vi.mock("./account.functions", () => ({
  getTopupDraft: vi.fn(),
}))
vi.mock("./use-refresh", () => ({
  useRefreshWorkspace: () => async () => {},
}))
vi.mock("./funding-intent", () => ({
  loadFundingIntent: vi.fn(async () => null),
  observeFundingIntent: vi.fn(() => () => {}),
  saveFundingIntent: vi.fn(),
  clearFundingIntent: vi.fn(),
}))

const account = accountSchema.parse({
  id: 1,
  denomination: "USDT (virtual)",
  initialized: true,
  version: 1,
  cash: "10000.00000000",
  reserved: "0.00000000",
  available: "10000.00000000",
  contributions: "10000.00000000",
  equity: "10000.00000000",
  valuation_status: "VALID",
  units: "100.00000000",
  nav: "100.00000000",
  high_water_nav: "100.00000000",
  pnl: "0.00000000",
  paused: false,
  reconciliation_failed: false,
  valuation_source: "CASH_ONLY",
  valued_at: null,
  // The engine lists Bitcoin always and another coin only while some is held (ExecPlan 0060).
  holdings: [
    {
      asset: "BTC",
      quantity: "0",
      reserved: "0",
      available: "0",
      valued: true,
    },
  ],
})

beforeEach(() => {
  vi.clearAllMocks()
  sessionStorage.clear()
})

afterEach(cleanup)

describe("React Hook Form submission states", () => {
  it("keeps a top-up draft distinct from posting and reports draft failures in the form", async () => {
    vi.mocked(getTopupDraft).mockRejectedValueOnce(new Error("offline"))
    render(<AccountHome workspace={{ account, funding: [] }} />)
    const input = screen.getByLabelText("Amount in USDT")
    const submit = screen.getByRole("button", { name: "Review top-up" })
    await waitFor(() => expect(submit.hasAttribute("disabled")).toBe(false))
    fireEvent.change(input, { target: { value: "25" } })
    fireEvent.click(submit)
    expect(
      await screen.findByText(/Unable to prepare this amount/)
    ).toBeTruthy()
    expect(screen.queryByRole("alertdialog")).toBeNull()
    fireEvent.change(input, { target: { value: "26" } })
    await waitFor(() =>
      expect(screen.queryByText(/Unable to prepare this amount/)).toBeNull()
    )
    expect((input as HTMLInputElement).value).toBe("26")
  })

  it("blocks repeat top-up review while the draft request is pending", async () => {
    let finish!: (draft: Awaited<ReturnType<typeof getTopupDraft>>) => void
    vi.mocked(getTopupDraft).mockReturnValue(
      new Promise((resolve) => {
        finish = resolve
      })
    )
    render(<AccountHome workspace={{ account, funding: [] }} />)
    fireEvent.change(screen.getByLabelText("Amount in USDT"), {
      target: { value: "25" },
    })
    const submit = screen.getByRole("button", { name: "Review top-up" })
    await waitFor(() => expect(submit.hasAttribute("disabled")).toBe(false))
    fireEvent.click(submit)
    await waitFor(() => expect(submit.hasAttribute("disabled")).toBe(true))
    fireEvent.click(submit)
    expect(getTopupDraft).toHaveBeenCalledTimes(1)
    finish({
      account_id: 1,
      amount: "25.00000000",
      denomination: "USDT (virtual)",
      kind: "TOPUP",
      version: 1,
      draft_hash: "a".repeat(64),
      valuation_status: "VALID",
    })
    expect(await screen.findByRole("alertdialog")).toBeTruthy()
    expect(
      screen.getByLabelText<HTMLInputElement>("Amount in USDT").value
    ).toBe("25")
  })

  it("shows the app's starting contribution with nothing to confirm and no way to cancel it", async () => {
    const pending = fundingSchema.parse({
      id: "6f93caf1-821d-4d85-b5b4-fd79344c46f1",
      kind: "INITIALIZE",
      amount: "10000.00000000",
      status: "PENDING_VALUATION",
      idempotency_key: "SYSTEM:INITIALIZE",
      expected_version: 0,
      preflow_nav: null,
      issued_units: null,
      unit_residual: null,
      journal_tx_id: null,
      created_at: "2026-10-25T08:00:00+00:00",
      completed_at: null,
    })
    render(
      <AccountHome
        workspace={{
          account: { ...account, initialized: false, version: 0 },
          funding: [pending],
        }}
      />
    )
    expect(await screen.findByText("Starting contribution")).toBeTruthy()
    expect(screen.getByText(/adds 10,000.00 USDT by itself/)).toBeTruthy()
    expect(
      screen.queryByRole("button", { name: /initial contribution/i })
    ).toBeNull()
    expect(screen.queryByLabelText("Amount in USDT")).toBeNull()
    expect(screen.getByRole("button", { name: "Retry" })).toBeTruthy()
    expect(screen.queryByRole("button", { name: "Cancel" })).toBeNull()
    expect(screen.queryByRole("button", { name: /sign out/i })).toBeNull()
  })

  it("offers Cancel on an initialization an older app left pending beside the funded account", async () => {
    const leftover = fundingSchema.parse({
      id: "0b4f2b8e-6a0c-4f5e-9d61-2c7a3e9f1b20",
      kind: "INITIALIZE",
      amount: "10000.00000000",
      status: "PENDING_VALUATION",
      idempotency_key: "owner-old-confirmation",
      expected_version: 0,
      preflow_nav: null,
      issued_units: null,
      unit_residual: null,
      journal_tx_id: null,
      created_at: "2026-10-24T08:00:00+00:00",
      completed_at: null,
    })
    render(<AccountHome workspace={{ account, funding: [leftover] }} />)
    expect(await screen.findByRole("button", { name: "Cancel" })).toBeTruthy()
    expect(screen.getByRole("button", { name: "Retry" })).toBeTruthy()
  })

  it("clears an initialization saved before the app funded itself, so top-ups stay open", async () => {
    const key = "0d7b5c1e-2f4a-4b8c-9d6e-1a2b3c4d5e6f"
    vi.mocked(loadFundingIntent).mockResolvedValueOnce({
      scope: "owner:1",
      format: 1,
      account_id: 1,
      kind: "INITIALIZE",
      payload: {
        amount: "10000.00000000",
        expected_version: 0,
        draft_hash: "a".repeat(64),
        idempotency_key: key,
      },
      created_at: "2026-10-24T08:00:00.000Z",
    })
    render(<AccountHome workspace={{ account, funding: [] }} />)
    await waitFor(() => expect(clearFundingIntent).toHaveBeenCalledWith(key))
    const submit = screen.getByRole("button", { name: "Review top-up" })
    await waitFor(() => expect(submit.hasAttribute("disabled")).toBe(false))
    expect(screen.queryByText("Check uncertain request")).toBeNull()
  })
})
