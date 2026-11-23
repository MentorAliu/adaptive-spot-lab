import { createFileRoute } from "@tanstack/react-router"
import { createCsrfMiddleware } from "@tanstack/react-start"
import { liveStream } from "@/live/live.server"

// ExecPlan 0047 section 4.3: the live trades' event stream. Besides the app's Host check, Start's CSRF
// middleware refuses a request that its Fetch Metadata does not name same-origin, so no other site's
// page can open it; the page's own EventSource is same-origin.
export const Route = createFileRoute("/api/live")({
  server: {
    middleware: [createCsrfMiddleware()],
    handlers: {
      GET: ({ request }) => liveStream(request),
    },
  },
})
