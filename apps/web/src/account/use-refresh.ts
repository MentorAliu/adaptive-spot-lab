import { useQueryClient } from "@tanstack/react-query"
import { useRouter } from "@tanstack/react-router"
import { workspaceQueryOptions } from "./workspace.query"

export function useRefreshWorkspace() {
  const queryClient = useQueryClient()
  const router = useRouter()
  return async () => {
    await queryClient.invalidateQueries({
      queryKey: workspaceQueryOptions.queryKey,
    })
    await router.invalidate()
  }
}
