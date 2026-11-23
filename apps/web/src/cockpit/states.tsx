import { Clock, CloudOff, RotateCw } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import type { ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { CardTitle } from "@/components/ui/card"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import { cn } from "@/lib/utils"

// Every Cockpit widget has the same four states (ExecPlan 0048 section 4.5): loading (a Skeleton the
// size of what comes), empty, an error with a retry, and stale (dimmed, with a clock and the age).

/** A card's title: a muted icon, then the word. */
export function CardHeading({
  icon: Icon,
  children,
  level = 2,
}: {
  icon: LucideIcon
  children: ReactNode
  level?: 2 | 3
}) {
  return (
    <CardTitle
      role="heading"
      aria-level={level}
      className="flex min-h-7 items-center gap-2"
    >
      <Icon className="size-4 text-muted-foreground" aria-hidden="true" />
      {children}
    </CardTitle>
  )
}

/** A read that failed: what could not be read, and a retry. Nothing is guessed in its place. */
export function ReadFailed({
  what,
  onRetry,
  icon: Icon = CloudOff,
}: {
  what: string
  onRetry: () => void
  icon?: LucideIcon
}) {
  return (
    <Empty className="border border-dashed p-4">
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Icon />
        </EmptyMedia>
        <EmptyTitle>{`Couldn't load ${what}`}</EmptyTitle>
      </EmptyHeader>
      <EmptyContent>
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RotateCw data-icon="inline-start" />
          Retry
        </Button>
      </EmptyContent>
    </Empty>
  )
}

/** Nothing yet: an icon, a short title and at most one short line. */
export function NothingYet({
  icon: Icon,
  title,
  detail,
  children,
}: {
  icon: LucideIcon
  title: string
  detail?: string
  children?: ReactNode
}) {
  return (
    <Empty className="border border-dashed p-4">
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Icon />
        </EmptyMedia>
        <EmptyTitle>{title}</EmptyTitle>
        {detail && <EmptyDescription>{detail}</EmptyDescription>}
      </EmptyHeader>
      {children && <EmptyContent>{children}</EmptyContent>}
    </Empty>
  )
}

/** A value the app does not have now, with a clock and why on hover. */
export function StaleTag({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-xs text-muted-foreground",
        className
      )}
    >
      <Clock className="size-3" aria-hidden="true" />
      {children}
    </span>
  )
}

/** Dimmed and desaturated: what a stale widget shows until its read is fresh again. */
export const STALE = "opacity-45 saturate-30"

/** A small picture or figure whose exact words are on hover and focus, and are its accessible name. */
export function Hint({
  label,
  children,
  className,
}: {
  label: string
  children: ReactNode
  className?: string
}) {
  return (
    <Tooltip>
      <TooltipTrigger
        aria-label={label}
        className={cn(
          "inline-flex items-center gap-1 rounded-md outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
          className
        )}
      >
        {children}
      </TooltipTrigger>
      <TooltipContent>{label}</TooltipContent>
    </Tooltip>
  )
}
