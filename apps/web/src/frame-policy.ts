// ExecPlan 0026 section 5.12: every response of the server entry forbids framing, so no page (one that approves an
// operating policy included) can be drawn inside another site's frame. CSP Level 3 defines
// `frame-ancestors 'none'`, which is ignored in a <meta> element and so is sent as a header;
// `X-Frame-Options: DENY` is its older equivalent, which a browser that enforces the CSP directive
// ignores (CSP3 "Relation to X-Frame-Options"). Both are sent; they say the same thing.
export const FRAME_ANCESTORS = "frame-ancestors 'none'"
export const FRAME_OPTIONS = "DENY"

/**
 * The response with the frame policy. A policy the response already has is kept: a second
 * Content-Security-Policy header is a second policy, and each one is enforced. A response whose
 * headers cannot change (a redirect made with `Response.redirect`, for one) is copied first.
 */
export function framed(response: Response): Response {
  let target = response
  try {
    target.headers.set("X-Frame-Options", FRAME_OPTIONS)
  } catch {
    target = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: new Headers(response.headers),
    })
    target.headers.set("X-Frame-Options", FRAME_OPTIONS)
  }
  target.headers.append("Content-Security-Policy", FRAME_ANCESTORS)
  return target
}
