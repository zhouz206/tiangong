import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Calendar, Flag, User, Plus, X } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import type { Agent } from '@/stores/agent-store'

export interface TaskData {
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assignee_id?: string
  due_date?: string
  upstream_task_ids?: string[]
}

interface CreateTaskDialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  onSubmit: (data: TaskData) => void
  agents?: Agent[]
}

const priorityOptions = [
  { value: 'low', label: '低', color: 'text-gray-500' },
  { value: 'medium', label: '中', color: 'text-blue-500' },
  { value: 'high', label: '高', color: 'text-orange-500' },
  { value: 'urgent', label: '紧急', color: 'text-red-500' },
] as const

export function CreateTaskDialog({ open, onOpenChange, onSubmit, agents = [] }: CreateTaskDialogProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<TaskData['priority']>('medium')
  const [assigneeId, setAssigneeId] = useState<string>('')
  const [dueDate, setDueDate] = useState<string>('')

  const handleSubmit = () => {
    onSubmit({
      title,
      description,
      priority,
      assignee_id: assigneeId || undefined,
      due_date: dueDate || undefined,
    })
    // Reset form
    setTitle('')
    setDescription('')
    setPriority('medium')
    setAssigneeId('')
    setDueDate('')
  }

  const isFormValid = title.trim() !== ''

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            新建任务
          </DialogTitle>
          <DialogDescription>
            创建新任务并分配给 Agent 执行
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">任务标题</Label>
            <Input
              id="title"
              placeholder="输入任务标题..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoFocus
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">任务描述</Label>
            <Textarea
              id="description"
              placeholder="详细描述任务目标和要求..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
            />
          </div>

          {/* Priority */}
          <div className="space-y-2">
            <Label>优先级</Label>
            <Select value={priority} onValueChange={(value: TaskData['priority']) => setPriority(value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {priorityOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <div className="flex items-center gap-2">
                      <Flag className={`h-4 w-4 ${option.color}`} />
                      {option.label}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Assignee */}
          <div className="space-y-2">
            <Label>执行 Agent</Label>
            <Select value={assigneeId} onValueChange={setAssigneeId}>
              <SelectTrigger>
                <SelectValue placeholder="选择执行 Agent..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">不分配</SelectItem>
                {agents.map((agent) => (
                  <SelectItem key={agent.id} value={agent.id}>
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      {agent.name} ({agent.role})
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {agents.length === 0 && (
              <p className="text-xs text-muted-foreground">
                暂无可用 Agent，请先在项目详情中添加 Agent
              </p>
            )}
          </div>

          {/* Due Date */}
          <div className="space-y-2">
            <Label htmlFor="dueDate">截止日期</Label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                id="dueDate"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Info Card */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <Flag className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium">任务执行说明</p>
                  <ul className="text-muted-foreground mt-1 space-y-1">
                    <li>• 任务创建后将自动分配给指定的 Agent</li>
                    <li>• Agent 会根据任务描述执行相应操作</li>
                    <li>• 可在任务详情页查看执行进度和结果</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange?.(false)}>
            取消
          </Button>
          <Button onClick={handleSubmit} disabled={!isFormValid}>
            创建任务
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
