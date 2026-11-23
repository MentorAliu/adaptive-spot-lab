import {
  createCsrfMiddleware,
  createMiddleware,
  createStart,
} from "@tanstack/react-start"
import { getRequestHeader } from "@tanstack/react-start/server"

const hostMiddleware = createMiddleware().server(async ({ next }) => {
  const host = getRequestHeader("host")?.toLowerCase()
  const hostname = host?.split(":")[0]
  if (!hostname || !["127.0.0.1", "localhost", "web"].includes(hostname)) {
    throw new Response("Untrusted host", { status: 421 })
  }
  return next()
})

export const startInstance = createStart(() => ({
  requestMiddleware: [
    hostMiddleware,
    createCsrfMiddleware({
      filter: (context) => context.handlerType === "serverFn",
    }),
  ],
}))
