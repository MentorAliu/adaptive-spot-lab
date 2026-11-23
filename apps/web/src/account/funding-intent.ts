import { z } from "zod"
import { confirmInput } from "./schemas"

const databaseName = "asl_funding_intents_v1"
const storeName = "intents"
const scope = "owner:1"
const channelName = "asl_funding_intents"

const intentSchema = z.object({
  scope: z.literal(scope),
  format: z.literal(1),
  account_id: z.literal(1),
  // INITIALIZE is read only, from a record saved before ExecPlan 0042 (the account home clears it).
  kind: z.enum(["INITIALIZE", "TOPUP"]),
  payload: confirmInput,
  created_at: z.string().datetime(),
})

export type FundingIntent = z.infer<typeof intentSchema>

function openDatabase(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(databaseName, 1)
    request.onupgradeneeded = () => {
      request.result.createObjectStore(storeName, { keyPath: "scope" })
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
    request.onblocked = () => reject(new Error("Funding storage is blocked"))
  })
}

function announceChange() {
  if (typeof BroadcastChannel === "undefined") return
  const channel = new BroadcastChannel(channelName)
  channel.postMessage("changed")
  channel.close()
}

export function observeFundingIntent(onChange: () => void): () => void {
  if (typeof BroadcastChannel === "undefined") return () => {}
  const channel = new BroadcastChannel(channelName)
  channel.onmessage = onChange
  return () => channel.close()
}

export async function loadFundingIntent(): Promise<FundingIntent | null> {
  const database = await openDatabase()
  try {
    return await new Promise((resolve, reject) => {
      const transaction = database.transaction(storeName, "readonly")
      const request = transaction.objectStore(storeName).get(scope)
      request.onsuccess = () => {
        try {
          resolve(request.result ? intentSchema.parse(request.result) : null)
        } catch (error) {
          reject(error)
        }
      }
      request.onerror = () => reject(request.error)
      transaction.onerror = () => reject(transaction.error)
    })
  } finally {
    database.close()
  }
}

export async function saveFundingIntent(
  kind: "TOPUP",
  payload: FundingIntent["payload"]
): Promise<FundingIntent> {
  const intent = intentSchema.parse({
    scope,
    format: 1,
    account_id: 1,
    kind,
    payload,
    created_at: new Date().toISOString(),
  })
  const database = await openDatabase()
  try {
    await new Promise<void>((resolve, reject) => {
      const transaction = database.transaction(storeName, "readwrite")
      transaction.objectStore(storeName).add(intent)
      transaction.oncomplete = () => resolve()
      transaction.onerror = () => reject(transaction.error)
      transaction.onabort = () => reject(transaction.error)
    })
  } finally {
    database.close()
  }
  announceChange()
  return intent
}

export async function clearFundingIntent(key: string): Promise<void> {
  const database = await openDatabase()
  try {
    await new Promise<void>((resolve, reject) => {
      const transaction = database.transaction(storeName, "readwrite")
      const store = transaction.objectStore(storeName)
      const request = store.get(scope)
      request.onsuccess = () => {
        try {
          if (request.result === undefined) return
          const current = intentSchema.parse(request.result)
          if (current.payload.idempotency_key !== key) {
            transaction.abort()
            return
          }
          store.delete(scope)
        } catch {
          transaction.abort()
        }
      }
      transaction.oncomplete = () => resolve()
      transaction.onerror = () => reject(transaction.error)
      transaction.onabort = () => reject(transaction.error)
    })
  } finally {
    database.close()
  }
  announceChange()
}
