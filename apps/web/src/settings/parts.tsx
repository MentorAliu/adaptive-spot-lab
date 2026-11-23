import type { LucideIcon } from "lucide-react"
import type { ReactNode } from "react"
import { Card, CardContent } from "@/components/ui/card"
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemGroup,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"
import { cn } from "@/lib/utils"

// Settings' building blocks (ExecPlan 0048 part 3): a list of rows, each an icon, a word, at most one
// line under it and its control or state on the right; and a tile, a small card holding one labelled
// figure with its picture. Both keep the label and value as a term and its definition, so a screen
// reader reads them as pairs.

export function SettingsList({
  label,
  children,
}: {
  label: string
  children: ReactNode
}) {
  return (
    <ItemGroup
      aria-label={label}
      className="gap-0 divide-y has-data-[size=sm]:gap-0"
    >
      {children}
    </ItemGroup>
  )
}

export function SettingRow({
  icon: Icon,
  title,
  description,
  children,
}: {
  icon: LucideIcon
  title: string
  description?: ReactNode
  children?: ReactNode
}) {
  return (
    <Item
      role="listitem"
      size="sm"
      className="rounded-none px-0 py-3 first:pt-0 last:pb-0"
    >
      <ItemMedia
        variant="icon"
        className="size-8 rounded-md bg-muted text-foreground"
      >
        <Icon aria-hidden="true" />
      </ItemMedia>
      <ItemContent className="min-w-0">
        <ItemTitle>{title}</ItemTitle>
        {description && (
          <ItemDescription className="line-clamp-none">
            {description}
          </ItemDescription>
        )}
      </ItemContent>
      {children && <ItemActions>{children}</ItemActions>}
    </Item>
  )
}

/** A small card with one labelled figure: the label, the value, and a picture or a line beside it. */
export function Tile({
  icon: Icon,
  label,
  value,
  side,
  foot,
  className,
}: {
  icon?: LucideIcon
  label: string
  value: ReactNode
  side?: ReactNode
  foot?: ReactNode
  className?: string
}) {
  return (
    <Card size="sm" className={className}>
      <CardContent className="flex h-full items-start justify-between gap-3">
        <dl className="flex min-w-0 flex-1 flex-col gap-1">
          <dt className="flex items-center gap-1.5 text-xs text-muted-foreground">
            {Icon && <Icon className="size-3.5" aria-hidden="true" />}
            {label}
          </dt>
          <dd className="font-heading text-xl leading-tight font-semibold tabular-nums">
            {value}
          </dd>
          {foot && <dd className="text-xs text-muted-foreground">{foot}</dd>}
        </dl>
        {side}
      </CardContent>
    </Card>
  )
}

/** The tiles' grid: two across on a phone, up to four on a wide screen. */
export function Tiles({
  label,
  children,
  className,
}: {
  label: string
  children: ReactNode
  className?: string
}) {
  return (
    <div
      role="group"
      aria-label={label}
      className={cn(
        "grid grid-cols-1 gap-3 @md/main:grid-cols-2 @4xl/main:grid-cols-4",
        className
      )}
    >
      {children}
    </div>
  )
}
