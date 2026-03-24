import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Clock, CheckCircle, AlertCircle, PlayCircle,
  Plus, Search, Filter, Trash2, Edit
} from 'lucide-react'
import { cn } from '@/lib/utils'

export interface Task {
  id: string
  title: string
  description?: string
  status: 'pending' | 'in_progress' | 'blocked' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assignee?: {
    id: string
    name: string
    role: string
  }
  project_id: string
  upstream_task_id?: string
  due_date?: string
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
  output?: unknown
}

interface TaskListProps {
  tasks: Task[]
  onTaskClick?: (task: Task) => void
  onStatusChange?: (taskId: string, status: Task['status']) => void
  onCreateTask?: () => void
  onEditTask?: (task: Task) => void
  onDeleteTask?: (taskId: string) => void
}

const statusConfig: Record<Task['status'], { label: string; icon: React.ComponentType<React.SVGProps<SVGSVGElement>>; color: string }> = {
  pending: { label: '待处理', icon: Clock, color: 'bg-yellow-500' },
  in_progress: { label: '执行中', icon: PlayCircle, color: 'bg-blue-500' },
  blocked: { label: '已阻塞', icon: AlertCircle, color: 'bg-red-500' },
  completed: { label: '已完成', icon: CheckCircle, color: 'bg-green-500' },
  cancelled: { label: '已取消', icon: AlertCircle, color: 'bg-gray-500' },
}

const priorityConfig: Record<Task['priority'], { label: string; color: string }> = {
  low: { label: '低', color: 'text-gray-500' },
  medium: { label: '中', color: 'text-blue-500' },
  high: { label: '高', color: 'text-orange-500' },
  urgent: { label: '紧急', color: 'text-red-500' },
}

export function TaskList({
  tasks,
  onTaskClick,
  onStatusChange,
  onCreateTask,
  onEditTask,
  onDeleteTask,
}: TaskListProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || task.status === statusFilter
    const matchesPriority = priorityFilter === 'all' || task.priority === priorityFilter
    return matchesSearch && matchesStatus && matchesPriority
  })

  const groupedTasks = {
    pending: filteredTasks.filter((t) => t.status === 'pending'),
    in_progress: filteredTasks.filter((t) => t.status === 'in_progress'),
    blocked: filteredTasks.filter((t) => t.status === 'blocked'),
    completed: filteredTasks.filter((t) => t.status === 'completed'),
  }

  const handleStatusChange = (taskId: string, newStatus: Task['status']) => {
    onStatusChange?.(taskId, newStatus)
  }

  return (
    <div className="space-y-4">
      {/* Header Actions */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="搜索任务..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="flex items-center gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[120px]">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue placeholder="状态" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部状态</SelectItem>
              <SelectItem value="pending">待处理</SelectItem>
              <SelectItem value="in_progress">执行中</SelectItem>
              <SelectItem value="blocked">已阻塞</SelectItem>
              <SelectItem value="completed">已完成</SelectItem>
            </SelectContent>
          </Select>

          <Select value={priorityFilter} onValueChange={setPriorityFilter}>
            <SelectTrigger className="w-[100px]">
              <SelectValue placeholder="优先级" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部</SelectItem>
              <SelectItem value="urgent">紧急</SelectItem>
              <SelectItem value="high">高</SelectItem>
              <SelectItem value="medium">中</SelectItem>
              <SelectItem value="low">低</SelectItem>
            </SelectContent>
          </Select>

          <Button onClick={onCreateTask}>
            <Plus className="h-4 w-4 mr-2" />
            新建任务
          </Button>
        </div>
      </div>

      {/* Tabs View */}
      <Tabs defaultValue="all" className="w-full">
        <TabsList>
          <TabsTrigger value="all">全部 ({filteredTasks.length})</TabsTrigger>
          <TabsTrigger value="pending">待处理 ({groupedTasks.pending.length})</TabsTrigger>
          <TabsTrigger value="in_progress">执行中 ({groupedTasks.in_progress.length})</TabsTrigger>
          <TabsTrigger value="blocked">阻塞 ({groupedTasks.blocked.length})</TabsTrigger>
          <TabsTrigger value="completed">完成 ({groupedTasks.completed.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredTasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onClick={() => onTaskClick?.(task)}
                onStatusChange={handleStatusChange}
                onEdit={() => onEditTask?.(task)}
                onDelete={() => onDeleteTask?.(task.id)}
              />
            ))}
          </div>
        </TabsContent>

        {(['pending', 'in_progress', 'blocked', 'completed'] as const).map((status) => (
          <TabsContent key={status} value={status} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {groupedTasks[status].map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onClick={() => onTaskClick?.(task)}
                  onStatusChange={handleStatusChange}
                  onEdit={() => onEditTask?.(task)}
                  onDelete={() => onDeleteTask?.(task.id)}
                />
              ))}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}

interface TaskCardProps {
  task: Task
  onClick?: () => void
  onStatusChange?: (taskId: string, status: Task['status']) => void
  onEdit?: () => void
  onDelete?: () => void
}

function TaskCard({ task, onClick, onStatusChange, onEdit, onDelete }: TaskCardProps) {
  const StatusIcon = statusConfig[task.status].icon

  const getDueDateStatus = (dueDate?: string) => {
    if (!dueDate) return null
    const now = new Date()
    const due = new Date(dueDate)
    const diff = due.getTime() - now.getTime()
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24))

    if (days < 0) return { text: `逾期 ${Math.abs(days)}天`, color: 'text-red-500' }
    if (days === 0) return { text: '今天到期', color: 'text-orange-500' }
    if (days <= 3) return { text: `${days}天后到期`, color: 'text-yellow-500' }
    return { text: `${days}天后到期`, color: 'text-muted-foreground' }
  }

  const dueDateStatus = getDueDateStatus(task.due_date)

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:shadow-md',
        task.status === 'completed' && 'opacity-75'
      )}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className={cn('h-2 w-2 rounded-full', statusConfig[task.status].color)} />
            <CardTitle className="text-base font-medium">{task.title}</CardTitle>
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0"
              onClick={(e) => { e.stopPropagation(); onEdit?.() }}
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-destructive"
              onClick={(e) => { e.stopPropagation(); onDelete?.() }}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
        {task.description && (
          <CardDescription className="line-clamp-2">
            {task.description}
          </CardDescription>
        )}
      </CardHeader>

      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <Badge variant="secondary" className={priorityConfig[task.priority].color}>
            {priorityConfig[task.priority].label}
          </Badge>

          {task.assignee && (
            <Badge variant="outline">
              {task.assignee.name}
            </Badge>
          )}
        </div>

        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-1">
            <StatusIcon className="h-3 w-3 text-muted-foreground" />
            <span className="text-muted-foreground">
              {statusConfig[task.status].label}
            </span>
          </div>

          {dueDateStatus && (
            <span className={dueDateStatus.color}>{dueDateStatus.text}</span>
          )}
        </div>

        {/* Quick Status Change */}
        <div className="flex gap-1 pt-2 border-t">
          {task.status !== 'completed' && task.status !== 'cancelled' && (
            <>
              <Button
                variant="outline"
                size="sm"
                className="flex-1 h-7 text-xs"
                onClick={(e) => {
                  e.stopPropagation()
                  onStatusChange?.(task.id, 'in_progress')
                }}
              >
                开始
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="flex-1 h-7 text-xs"
                onClick={(e) => {
                  e.stopPropagation()
                  onStatusChange?.(task.id, 'completed')
                }}
              >
                完成
              </Button>
            </>
          )}
          {task.status === 'completed' && (
            <Button
              variant="outline"
              size="sm"
              className="flex-1 h-7 text-xs"
              onClick={(e) => {
                e.stopPropagation()
                onStatusChange?.(task.id, 'pending')
              }}
            >
              重新开始
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
