import type { ReactNode } from "react"
import { cn } from "@/lib/utils"
import { limitLevel } from "./geometry"
import type { Level } from "./geometry"

// The Cockpit's small drawings (ExecPlan 0048 section 4.3): rings, pips, a gauge and status dots, in
// SVG and CSS on the theme's tokens. They are pictures of numbers, so each is an image with
// a sentence for screen readers; the exact figures sit in its tooltip or beside it. The time series
// stay Lightweight Charts.

// A circle of circumference 100, so a percentage is its own dash length.
const R = 15.9155

const RING_SIZE = {
  xs: "size-4",
  sm: "size-9",
  lg: "size-24",
} as const

const FILL_TONE: Record<Level | "accent", string> = {
  accent: "stroke-chart-2",
  calm: "stroke-chart-2",
  warning: "stroke-warning",
  danger: "stroke-destructive",
}

/**
 * A ring filled to `value` (0 to 1) with a tick at `tick`, such as a coin flip's 50%. Its centre
 * holds an icon or a figure. Without a value it is an empty track.
 */
export function Ring({
  value,
  label,
  size = "sm",
  tick,
  tone = "accent",
  className,
  children,
}: {
  value: number | null
  label: string
  size?: keyof typeof RING_SIZE
  tick?: number
  tone?: Level | "accent"
  className?: string
  children?: ReactNode
}) {
  const width = size === "lg" ? 2.6 : size === "xs" ? 6 : 3.4
  const angle = tick === undefined ? null : tick * 2 * Math.PI
  return (
    <span
      role="img"
      aria-label={label}
      className={cn(
        "relative inline-grid shrink-0 place-items-center text-muted-foreground",
        RING_SIZE[size],
        className
      )}
    >
      <svg
        viewBox="0 0 36 36"
        aria-hidden="true"
        className="absolute inset-0 size-full -rotate-90 overflow-visible"
      >
        <circle
          cx="18"
          cy="18"
          r={R}
          className="fill-none stroke-muted"
          strokeWidth={width}
        />
        {value !== null && value > 0 && (
          <circle
            cx="18"
            cy="18"
            r={R}
            pathLength={100}
            strokeDasharray={`${Math.min(100, value * 100)} 100`}
            strokeLinecap="round"
            className={cn("fill-none", FILL_TONE[tone])}
            strokeWidth={width}
          />
        )}
        {angle !== null && (
          <line
            x1={18 + (R - 2.6) * Math.cos(angle)}
            y1={18 + (R - 2.6) * Math.sin(angle)}
            x2={18 + (R + 2.6) * Math.cos(angle)}
            y2={18 + (R + 2.6) * Math.sin(angle)}
            className="stroke-foreground"
            strokeWidth={1.6}
          />
        )}
      </svg>
      {children !== undefined && (
        <span className="relative flex flex-col items-center leading-none">
          {children}
        </span>
      )}
    </span>
  )
}

/** A row of pips, `filled` of them on: since ExecPlan 0060, how many of the rule's anchors are up. */
export function Pips({
  filled,
  total = 3,
  label,
}: {
  filled: number
  total?: number
  label: string
}) {
  return (
    <span
      role="img"
      aria-label={label}
      className="inline-flex items-center gap-[3px]"
    >
      {Array.from({ length: total }, (_, index) => (
        <span
          key={index}
          className={cn(
            "size-[7px] rounded-full",
            index < filled
              ? "bg-chart-2"
              : "ring-[1.5px] ring-muted-foreground/75 ring-inset"
          )}
        />
      ))}
    </span>
  )
}

const ARC = "M10 60A48 48 0 0 1 106 60"

/**
 * A half dial filling toward a limit: violet under half, amber from half, red from 80%, with ticks at
 * both. `children` sits in its middle, such as a lock when a latch has tripped.
 */
export function Gauge({
  fraction,
  label,
  caption,
  children,
}: {
  fraction: number | null
  label: string
  caption: string
  children?: ReactNode
}) {
  const level = fraction === null ? "calm" : limitLevel(fraction)
  return (
    <figure
      role="img"
      aria-label={label}
      className="flex w-22 shrink-0 flex-col items-center @lg/main:w-29"
    >
      <svg
        viewBox="0 0 116 66"
        aria-hidden="true"
        className="block h-auto w-full overflow-visible"
      >
        <path d={ARC} className="fill-none stroke-muted" strokeWidth={9} />
        <path
          d={ARC}
          pathLength={100}
          strokeDasharray="0 50 30 100"
          className="fill-none stroke-warning opacity-30"
          strokeWidth={9}
        />
        <path
          d={ARC}
          pathLength={100}
          strokeDasharray="0 80 20 100"
          className="fill-none stroke-destructive opacity-30"
          strokeWidth={9}
        />
        {fraction !== null && fraction > 0 && (
          <path
            d={ARC}
            pathLength={100}
            strokeDasharray={`${fraction * 100} 100`}
            className={cn("fill-none", FILL_TONE[level])}
            strokeWidth={9}
          />
        )}
        <line
          x1="58"
          y1="7"
          x2="58"
          y2="2"
          className="stroke-foreground"
          strokeWidth={1.5}
          strokeLinecap="round"
        />
        <line
          x1="100.9"
          y1="28.8"
          x2="104.9"
          y2="25.9"
          className="stroke-foreground"
          strokeWidth={1.5}
          strokeLinecap="round"
        />
      </svg>
      {children !== undefined && (
        <span className="-mt-7 grid h-6 place-items-center text-foreground">
          {children}
        </span>
      )}
      <figcaption className="text-xs text-muted-foreground">
        {caption}
      </figcaption>
    </figure>
  )
}

export type DotTone = "ok" | "warning" | "danger" | "off"

const DOT: Record<DotTone, string> = {
  ok: "bg-chart-2",
  warning: "bg-warning",
  danger: "bg-destructive",
  off: "ring-[1.5px] ring-muted-foreground ring-inset",
}

/** A status dot; `live` adds a slow ping behind it (none with reduced motion). */
export function StatusDot({
  tone,
  live = false,
  className,
}: {
  tone: DotTone
  live?: boolean
  className?: string
}) {
  return (
    <span
      aria-hidden="true"
      className={cn("relative inline-flex size-2 shrink-0", className)}
    >
      {live && (
        <span
          className={cn(
            "absolute inset-0 rounded-full opacity-75 motion-safe:animate-ping",
            DOT[tone]
          )}
        />
      )}
      <span
        className={cn("relative inline-flex size-2 rounded-full", DOT[tone])}
      />
    </span>
  )
}

/** A small square holding an icon: violet for what acts, muted for what waits. */
export function IconTile({
  accent = false,
  size = "sm",
  children,
}: {
  accent?: boolean
  size?: "sm" | "lg"
  children: ReactNode
}) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "grid shrink-0 place-items-center",
        size === "lg" ? "size-11 rounded-lg" : "size-7 rounded-md",
        accent ? "bg-chart-2/15 text-chart-2" : "bg-muted text-foreground"
      )}
    >
      {children}
    </span>
  )
}

/** The violet glow behind a hero card's content (the design's hero glow): decorative only. */
export function HeroGlow() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 bg-[radial-gradient(90%_70%_at_0%_0%,color-mix(in_oklab,var(--chart-2)_13%,transparent),transparent_62%),radial-gradient(60%_50%_at_100%_0%,color-mix(in_oklab,var(--chart-1)_16%,transparent),transparent_70%)]"
    />
  )
}
