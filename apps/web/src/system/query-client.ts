import { QueryClient } from "@tanstack/react-query"

export function createRequestQueryClient() {
  return new QueryClient()
}
