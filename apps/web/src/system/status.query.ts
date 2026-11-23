import { queryOptions } from "@tanstack/react-query"
import { getSystemStatus } from "./status.functions"

export const statusQueryOptions = queryOptions({
  queryKey: ["system", "status", "M0"] as const,
  queryFn: ({ signal }) => getSystemStatus({ signal }),
})
