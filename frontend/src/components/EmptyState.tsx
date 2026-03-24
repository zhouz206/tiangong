import { ReactNode } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FolderOpen, Inbox, FileText, HelpCircle, Plus, RefreshCw } from 'lucide-react'

export type EmptyStateType = 'folder' | 'inbox' | 'file' | 'help' | 'search'

interface EmptyStateProps {
  icon?: EmptyStateType | ReactNode
  title: string
  description?: string
  actionLabel?: string
  onAction?: () => void
  secondaryActionLabel?: string
  onSecondaryAction?: () => void
}

const iconMap: Record<EmptyStateType, ReactNode> = {
  folder: <FolderOpen className="h-12 w-12" />,
  inbox: <Inbox className="h-12 w-12" />,
  file: <FileText className="h-12 w-12" />,
  help: <HelpCircle className="h-12 w-12" />,
  search: <Inbox className="h-12 w-12" />,
}

export function EmptyState({
  icon = 'inbox',
  title,
  description,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
}: EmptyStateProps) {
  const IconComponent = typeof icon === 'string' ? iconMap[icon as EmptyStateType] : icon

  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-center justify-center py-10">
        <div className="text-muted-foreground mb-4">{IconComponent}</div>
        <h3 className="text-lg font-medium mb-1">{title}</h3>
        {description && (
          <p className="text-sm text-muted-foreground text-center mb-4 max-w-md">
            {description}
          </p>
        )}
        <div className="flex gap-2">
          {actionLabel && onAction && (
            <Button onClick={onAction}>
              <Plus className="h-4 w-4 mr-2" />
              {actionLabel}
            </Button>
          )}
          {secondaryActionLabel && onSecondaryAction && (
            <Button variant="outline" onClick={onSecondaryAction}>
              <RefreshCw className="h-4 w-4 mr-2" />
              {secondaryActionLabel}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
