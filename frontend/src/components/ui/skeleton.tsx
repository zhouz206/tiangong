import * as React from "react"

import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-primary/10", className)}
      {...props}
    />
  )
}

interface SkeletonCardProps {
  showHeader?: boolean
  showAvatar?: boolean
  lines?: number
}

function SkeletonCard({
  showHeader = true,
  showAvatar = false,
  lines = 2,
}: SkeletonCardProps) {
  return (
    <div className="rounded-lg border p-4 space-y-3">
      {showHeader && (
        <div className="flex items-center gap-2">
          {showAvatar && <Skeleton className="h-8 w-8 rounded-full" />}
          <div className="space-y-1 flex-1">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      )}
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} className="h-3 w-full" />
      ))}
    </div>
  )
}

function SkeletonTable() {
  return (
    <div className="space-y-3">
      <div className="flex gap-3">
        <Skeleton className="h-10 flex-1" />
        <Skeleton className="h-10 w-32" />
      </div>
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  )
}

function SkeletonList({ items = 5 }: { items?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: items }).map((_, i) => (
        <Skeleton key={i} className="h-16 w-full" />
      ))}
    </div>
  )
}

export { Skeleton, SkeletonCard, SkeletonTable, SkeletonList }
