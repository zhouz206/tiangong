import * as React from "react"
import { cn } from "@/lib/utils"

export interface PopoverProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

const Popover = ({ open, onOpenChange, children }: PopoverProps) => {
  const triggerRef = React.useRef<HTMLButtonElement>(null)
  const [position, setPosition] = React.useState({ top: 0, left: 0 })

  React.useEffect(() => {
    if (open && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect()
      setPosition({
        top: rect.bottom + window.scrollY + 8,
        left: rect.left + window.scrollX,
      })
    }
  }, [open])

  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (open && !(e.target as Element).closest('[data-popover]')) {
        onOpenChange?.(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open, onOpenChange])

  const childrenArray = React.Children.toArray(children)
  const trigger = childrenArray.find(
    (child) => React.isValidElement(child) && (child as React.ReactElement).type === PopoverTrigger
  )
  const content = childrenArray.find(
    (child) => React.isValidElement(child) && (child as React.ReactElement).type === PopoverContent
  )

  return (
    <>
      {trigger && React.cloneElement(
        trigger as React.ReactElement<{ ref: React.Ref<HTMLButtonElement> }>,
        { ref: triggerRef }
      )}
      {open && content && (
        <div
          data-popover
          className="z-50 w-72 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none"
          style={{
            position: 'absolute',
            top: position.top,
            left: position.left,
          }}
        >
          {content}
        </div>
      )}
    </>
  )
}
Popover.displayName = "Popover"

const PopoverTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ComponentProps<"button">
>(({ className, ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
      className
    )}
    {...props}
  />
))
PopoverTrigger.displayName = "PopoverTrigger"

interface PopoverContentProps extends React.HTMLAttributes<HTMLDivElement> {
  align?: 'start' | 'center' | 'end'
  sideOffset?: number
}

const PopoverContent = React.forwardRef<
  HTMLDivElement,
  PopoverContentProps
>(({ className, align = "center", sideOffset = 4, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "z-50 w-72 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none",
      className
    )}
    {...props}
  />
))
PopoverContent.displayName = "PopoverContent"

export { Popover, PopoverTrigger, PopoverContent }
