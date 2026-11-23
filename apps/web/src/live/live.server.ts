import "@tanstack/react-start/server-only"
import { privateStream } from "@/account/account.server"

// The browser's live trades (ExecPlan 0047 section 4.3; the spot account's since ExecPlan 0060): the
// engine's event stream, passed through unchanged. Only this server holds the service key; the browser
// names nothing but its last event's id, which EventSource sends by itself when it reconnects.
const EVENT_ID = /^(0|[1-9][0-9]{0,18})$/

function unavailable(status: number, text: string) {
  return new Response(text, {
    status,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
    },
  })
}

export async function liveStream(request: Request): Promise<Response> {
  const last = request.headers.get("last-event-id")
  if (last !== null && !EVENT_ID.test(last))
    return unavailable(400, "Invalid event id")
  let engine: Response
  try {
    engine = await privateStream(
      "/v1/spot/live",
      {
        Accept: "text/event-stream",
        ...(last === null ? {} : { "Last-Event-ID": last }),
      },
      request.signal
    )
  } catch {
    return unavailable(503, "Live trades unavailable")
  }
  const type = engine.headers.get("content-type") ?? ""
  if (
    engine.status !== 200 ||
    engine.body === null ||
    !type.startsWith("text/event-stream")
  ) {
    // The engine refused (its listener down, or every stream taken): the browser polls meanwhile.
    void engine.body?.cancel().catch(() => {})
    return unavailable(503, "Live trades unavailable")
  }
  return new Response(engine.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Accel-Buffering": "no",
    },
  })
}
