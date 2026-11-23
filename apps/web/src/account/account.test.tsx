import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { FundingTable } from "./funding-table"
import { amountInput, fundingSchema } from "./schemas"

describe("M1 financial presentation", () => {
  it("rejects ambiguous amounts before sending a draft while retaining server authority", () => {
    for (const value of [
      "0",
      "0.00000000",
      "-1",
      "1e3",
      "1,000",
      "NaN",
      "1.000000001",
      "01",
    ]) {
      expect(amountInput.safeParse(value).success).toBe(false)
    }
    expect(amountInput.parse("100.00000001")).toBe("100.00000001")
  })

  it("shows a pending request as pending virtual funding, not spendable cash", () => {
    const entry = fundingSchema.parse({
      id: "6f93caf1-821d-4d85-b5b4-fd79344c46f1",
      kind: "TOPUP",
      amount: "25.00000000",
      status: "PENDING_VALUATION",
      idempotency_key: "m1test_123",
      expected_version: 1,
      preflow_nav: null,
      issued_units: null,
      unit_residual: null,
      journal_tx_id: null,
      created_at: "2026-09-27T08:00:00+00:00",
      completed_at: null,
    })
    render(<FundingTable funding={[entry]} />)
    expect(screen.getByText("PENDING VALUATION")).toBeTruthy()
    expect(screen.getByText("25.00")).toBeTruthy()
    expect(
      screen.getByText("The starting contribution and your top-ups.")
    ).toBeTruthy()
    expect(screen.queryByText(/profit/i)).toBeNull()
  })
})
