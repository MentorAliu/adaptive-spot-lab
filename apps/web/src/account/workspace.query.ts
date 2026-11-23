import { queryOptions } from "@tanstack/react-query"
import { getWorkspace } from "./account.functions"

export const workspaceQueryOptions = queryOptions({
  queryKey: ["owner", "workspace", "M1"] as const,
  queryFn: ({ signal }) => getWorkspace({ signal }),
  refetchInterval: 30_000,
  refetchOnWindowFocus: true,
  refetchOnReconnect: true,
})
