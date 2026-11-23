import { z } from "zod"

export const amountInput = z
  .string()
  .regex(
    /^(?:0|[1-9][0-9]{0,21})(?:\.[0-9]{1,8})?$/,
    "Enter a positive decimal with at most 8 places"
  )
  .refine((value) => !/^0(?:\.0+)?$/.test(value), "Amount must be positive")

export const confirmInput = z.object({
  amount: amountInput,
  expected_version: z.number().int().nonnegative(),
  draft_hash: z.string().regex(/^[a-f0-9]{64}$/),
  idempotency_key: z.string().regex(/^[A-Za-z0-9_-]{8,80}$/),
})

export const idInput = z.object({ id: z.uuid() })
export const keyInput = z.object({
  key: z.string().regex(/^[A-Za-z0-9_-]{8,80}$/),
})

// The owner drafts top-ups only: the initial contribution is the app's (ExecPlan 0042).
export const draftSchema = z.object({
  account_id: z.literal(1),
  amount: z.string(),
  denomination: z.literal("USDT (virtual)"),
  kind: z.literal("TOPUP"),
  version: z.number().int(),
  draft_hash: z.string(),
  valuation_status: z.enum(["VALID", "UNAVAILABLE"]),
})

export const accountSchema = z.object({
  id: z.literal(1),
  denomination: z.literal("USDT (virtual)"),
  initialized: z.boolean(),
  version: z.number().int(),
  cash: z.string(),
  reserved: z.string(),
  available: z.string(),
  contributions: z.string(),
  equity: z.string().nullable(),
  valuation_status: z.enum(["VALID", "UNAVAILABLE"]),
  units: z.string(),
  nav: z.string().nullable(),
  high_water_nav: z.string().nullable(),
  pnl: z.string().nullable(),
  paused: z.boolean(),
  reconciliation_failed: z.boolean(),
  // ExecPlan 0060: the USDT alone while no Bitcoin is held, else the latest stored valuation at the
  // best bid.
  valuation_source: z.enum(["CASH_ONLY", "PERSISTED_VALUATION", "UNAVAILABLE"]),
  valued_at: z.string().nullable(),
  // Bitcoin first; any other coin is M3 to M10's dust, kept with its postings and not valued.
  holdings: z.array(
    z.object({
      asset: z.string().regex(/^[A-Z0-9]{2,10}$/),
      quantity: z.string(),
      reserved: z.string(),
      available: z.string(),
      valued: z.boolean(),
    })
  ),
})

export const fundingSchema = z.object({
  id: z.uuid(),
  kind: z.enum(["INITIALIZE", "TOPUP"]),
  amount: z.string(),
  status: z.enum(["PENDING_VALUATION", "POSTED", "CANCELED"]),
  idempotency_key: z.string(),
  expected_version: z.number().int(),
  preflow_nav: z.string().nullable(),
  issued_units: z.string().nullable(),
  unit_residual: z.string().nullable(),
  journal_tx_id: z.uuid().nullable(),
  created_at: z.string(),
  completed_at: z.string().nullable(),
})

// The account and its latest funding requests, read with no sign-in (ExecPlan 0042).
export const workspaceSchema = z.strictObject({
  account: accountSchema,
  funding: z.array(fundingSchema),
})

export type Account = z.infer<typeof accountSchema>
export type Funding = z.infer<typeof fundingSchema>
export type FundingDraft = z.infer<typeof draftSchema>
export type Workspace = z.infer<typeof workspaceSchema>
