import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import {
  Clock,
  CheckCircle,
  AlertCircle,
  PlayCircle,
  User,
  Calendar,
  Flag,
  Link2,
  FileText,
  RefreshCw,
  Play,
  Pause,
  StopCircle,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Task } from './TaskList'

interface AgentMessage {
  id: string
  agent_id: string
  agent_name: string
  content: string
  message_type: 'text' | 'status' | 'result'
  timestamp: string
}

interface TaskDetailProps {
  task: Task | null
  open: boolean
  onOpenChange: (open: boolean) => void
  messages?: AgentMessage[]
  onExecute?: (taskId: string) => void
  onPause?: (taskId: string) => void
  onCancel?: (taskId: string) => void
}

const statusConfig: Record<Task['status'], { label: string; icon: React.ComponentType<React.SVGProps<SVGSVGElement>>; color: string }> = {
  pending: { label: '待处理', icon: Clock, color: 'text-yellow-500' },
  in_progress: { label: '执行中', icon: PlayCircle, color: 'text-blue-500' },
  blocked: { label: '已阻塞', icon: AlertCircle, color: 'text-red-500' },
  completed: { label: '已完成', icon: CheckCircle, color: 'text-green-500' },
  cancelled: { label: '已取消', icon: AlertCircle, color: 'text-gray-500' },
}

const priorityConfig: Record<Task['priority'], { label: string; color: string }> = {
  low: { label: '低', color: 'text-gray-500' },
  medium: { label: '中', color: 'text-blue-500' },
  high: { label: '高', color: 'text-orange-500' },
  urgent: { label: '紧急', color: 'text-red-500' },
}

export function TaskDetail({
  task,
  open,
  onOpenChange,
  messages = [],
  onExecute,
  onPause,
  onCancel,
}: TaskDetailProps) {
  const [activeTab, setActiveTab] = useState<'details' | 'log' | 'result'>('details')

  if (!task) return null

  const StatusIcon = statusConfig[task.status].icon
  const PriorityIcon = Flag

  const formatDate = (dateString?: string) => {
    if (!dateString) return '未设置'
    return new Date(dateString).toLocaleString('zh-CN')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="flex items-center gap-2 font-semibold text-lg">
              <StatusIcon className={cn('h-5 w-5', statusConfig[task.status].color)} />
              {task.title}
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {task.description || '无描述'}
            </p>
          </div>
          <Badge variant="secondary" className={priorityConfig[task.priority].color}>
            <PriorityIcon className="h-3 w-3 mr-1" />
            {priorityConfig[task.priority].label}
          </Badge>
        </div>

        <div className="flex items-center gap-2 border-b pb-2">
          <Button
            variant={activeTab === 'details' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('details')}
          >
            详情
          </Button>
          <Button
            variant={activeTab === 'log' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('log')}
          >
            执行日志
          </Button>
          <Button
            variant={activeTab === 'result' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('result')}
          >
            结果
          </Button>
        </div>

        <ScrollArea className="flex-1">
          {activeTab === 'details' && (
            <div className="space-y-4 py-4">
              {/* Status and Assignee */}
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      状态
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Badge variant={task.status === 'completed' ? 'default' : 'secondary'}>
                      {statusConfig[task.status].label}
                    </Badge>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <User className="h-4 w-4" />
                      执行者
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {task.assignee ? (
                      <div>
                        <p className="font-medium">{task.assignee.name}</p>
                        <p className="text-sm text-muted-foreground">{task.assignee.role}</p>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">未分配</span>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Time Info */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    时间信息
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">创建时间</span>
                    <span>{formatDate(task.created_at)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">开始时间</span>
                    <span>{formatDate(task.started_at)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">截止时间</span>
                    <span>{formatDate(task.due_date)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">完成时间</span>
                    <span>{formatDate(task.completed_at)}</span>
                  </div>
                </CardContent>
              </Card>

              {/* Dependencies */}
              {task.upstream_task_id && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <Link2 className="h-4 w-4" />
                      依赖关系
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">上游任务:</span>
                      <Badge variant="outline">{task.upstream_task_id}</Badge>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Actions */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">操作</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-2">
                    {task.status === 'pending' && (
                      <Button size="sm" onClick={() => onExecute?.(task.id)}>
                        <Play className="h-4 w-4 mr-2" />
                        执行
                      </Button>
                    )}
                    {task.status === 'in_progress' && (
                      <>
                        <Button variant="outline" size="sm" onClick={() => onPause?.(task.id)}>
                          <Pause className="h-4 w-4 mr-2" />
                          暂停
                        </Button>
                        <Button variant="destructive" size="sm" onClick={() => onCancel?.(task.id)}>
                          <StopCircle className="h-4 w-4 mr-2" />
                          取消
                        </Button>
                      </>
                    )}
                    {task.status === 'blocked' && (
                      <Button size="sm" onClick={() => onExecute?.(task.id)}>
                        <RefreshCw className="h-4 w-4 mr-2" />
                        重试
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'log' && (
            <div className="py-4 space-y-3">
              {messages.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>暂无执行日志</p>
                </div>
              ) : (
                messages.map((message) => (
                  <Card key={message.id}>
                    <CardContent className="p-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-xs">
                              {message.agent_name}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {new Date(message.timestamp).toLocaleString('zh-CN')}
                            </span>
                          </div>
                          <p className="text-sm">{message.content}</p>
                        </div>
                        <Badge
                          variant={
                            message.message_type === 'result'
                              ? 'default'
                              : message.message_type === 'status'
                              ? 'secondary'
                              : 'outline'
                          }
                          className="text-xs"
                        >
                          {message.message_type === 'text' && '文本'}
                          {message.message_type === 'status' && '状态'}
                          {message.message_type === 'result' && '结果'}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}

          {activeTab === 'result' && (
            <div className="py-4">
              <div className="text-center text-muted-foreground py-8">
                <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>暂无产出结果</p>
                <p className="text-sm mt-2">任务完成后将显示产出结果</p>
              </div>
            </div>
          )}
        </ScrollArea>
        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            关闭
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
