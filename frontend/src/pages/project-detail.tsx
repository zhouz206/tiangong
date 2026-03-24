import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Play, Pause, CheckCircle, Bot, FileText, Plus } from 'lucide-react'
import { useProjectStore, Project } from '@/stores/project-store'
import { useAgentStore } from '@/stores/agent-store'
import { projectApi, agentApi } from '@/utils/api-services'
import { useToast } from '@/hooks/use-toast'
import { TaskList, type Task } from '@/components/TaskList'
import { TaskDetail } from '@/components/TaskDetail'
import { CreateTaskDialog, type TaskData } from '@/components/CreateTaskDialog'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { WebSocketStatusIndicator } from '@/components/WebSocketStatusIndicator'
import { connectWebSocket, getWebSocketClient } from '@/utils/websocket'

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()
  const { currentProject, setCurrentProject, updateProject } = useProjectStore()
  const { agents, setAgents } = useAgentStore()
  const [loading, setLoading] = useState(true)
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [taskDetailOpen, setTaskDetailOpen] = useState(false)
  const [createTaskOpen, setCreateTaskOpen] = useState(false)
  const [taskMessages, setTaskMessages] = useState<Array<{
    id: string
    agent_id: string
    agent_name: string
    content: string
    message_type: 'text' | 'status' | 'result'
    timestamp: string
  }>>([])

  useEffect(() => {
    // Connect WebSocket on mount
    connectWebSocket()

    const client = getWebSocketClient()

    // Subscribe to task updates
    const unsubscribeTask = client.on('task_update', (msg) => {
      const payload = msg.payload as { task_id: string; status: string; progress?: number }
      setTasks(prev => prev.map(t =>
        t.id === payload.task_id
          ? { ...t, status: payload.status as Task['status'] }
          : t
      ))
    })

    // Subscribe to agent messages
    const unsubscribeAgent = client.on('agent_message', (msg) => {
      const payload = msg.payload as { agent_id: string; agent_name: string; content: string; message_type: 'text' | 'status' | 'result' }
      setTaskMessages(prev => [...prev, {
        id: `${Date.now()}`,
        agent_id: payload.agent_id,
        agent_name: payload.agent_name,
        content: payload.content,
        message_type: payload.message_type,
        timestamp: msg.timestamp,
      }])
    })

    return () => {
      unsubscribeTask()
      unsubscribeAgent()
    }
  }, [])

  useEffect(() => {
    if (id) {
      loadProject()
      loadAgents()
      loadTasks()
    }
  }, [id])

  const loadProject = async () => {
    if (!id) return
    try {
      setLoading(true)
      const result = await projectApi.getById(id)
      setCurrentProject(result.data)
    } catch (error) {
      toast({
        title: '加载失败',
        description: '无法加载项目详情',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const loadAgents = async () => {
    if (!id) return
    try {
      const result = await agentApi.getList(id)
      setAgents(result.data)
    } catch (error) {
      console.error('Failed to load agents:', error)
    }
  }

  const loadTasks = async () => {
    if (!id) return
    try {
      // TODO: Replace with actual API call when available
      // const result = await taskApi.getList(id)
      // setTasks(result.data)
      // Mock data for now
      setTasks([])
    } catch (error) {
      console.error('Failed to load tasks:', error)
    }
  }

  const handleTaskStatusChange = async (taskId: string, newStatus: Task['status']) => {
    try {
      // TODO: Replace with actual API call
      // await taskApi.updateStatus(taskId, newStatus)
      setTasks(prev => prev.map(t =>
        t.id === taskId ? { ...t, status: newStatus } : t
      ))
      toast({
        title: '状态已更新',
        description: `任务状态已更新为 ${newStatus}`,
      })
    } catch (error) {
      toast({
        title: '更新失败',
        description: '无法更新任务状态',
        variant: 'destructive',
      })
    }
  }

  const handleCreateTask = () => {
    setCreateTaskOpen(true)
  }

  const handleCreateTaskSubmit = async (data: TaskData) => {
    if (!id) return
    try {
      // TODO: Replace with actual API call when task API is available
      // const result = await taskApi.create({ ...data, project_id: id })
      const newTask: Task = {
        id: `task-${Date.now()}`,
        title: data.title,
        description: data.description,
        status: 'pending',
        priority: data.priority,
        project_id: id,
        assignee: data.assignee_id ? agents.find(a => a.id === data.assignee_id) : undefined,
        due_date: data.due_date,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      setTasks(prev => [...prev, newTask])
      setCreateTaskOpen(false)
      toast({
        title: '创建成功',
        description: `任务"${data.title}"已创建`,
      })
    } catch (error) {
      toast({
        title: '创建失败',
        description: '无法创建任务',
        variant: 'destructive',
      })
    }
  }

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task)
    setTaskDetailOpen(true)
  }

  const getStatusLabel = (status: Project['status']) => {
    const labels = {
      active: '进行中',
      paused: '已暂停',
      completed: '已完成',
      cancelled: '已取消',
    }
    return labels[status]
  }

  const getPhaseLabel = (phase: Project['phase']) => {
    const labels = {
      planning: '规划',
      execution: '执行',
      review: '审查',
      done: '完成',
    }
    return labels[phase]
  }

  const updateProjectStatus = async (status: Project['status']) => {
    if (!id) return
    try {
      await projectApi.updateStatus(id, status)
      updateProject(id, { status })
      toast({
        title: '状态已更新',
        description: `项目状态已更新为 ${status}`,
      })
    } catch (error) {
      toast({
        title: '更新失败',
        description: '无法更新项目状态',
        variant: 'destructive',
      })
    }
  }

  const updateProjectPhase = async (phase: Project['phase']) => {
    if (!id) return
    try {
      await projectApi.updatePhase(id, phase)
      updateProject(id, { phase })
      toast({
        title: '阶段已更新',
        description: `项目阶段已更新为 ${phase}`,
      })
    } catch (error) {
      toast({
        title: '更新失败',
        description: '无法更新项目阶段',
        variant: 'destructive',
      })
    }
  }

  return (
    <ErrorBoundary>
      <div className="space-y-4 sm:space-y-6">
        {/* Header - 移动端优化 */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate('/projects')}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="space-y-1">
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">{currentProject?.name || '加载中...'}</h1>
              <p className="text-sm text-muted-foreground line-clamp-1">{currentProject?.description}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <WebSocketStatusIndicator />
            {currentProject && currentProject.status === 'active' ? (
              <Button variant="outline" onClick={() => updateProjectStatus('paused')} className="flex-1 sm:flex-none">
                <Pause className="mr-2 h-4 w-4" />
                <span className="hidden sm:inline">暂停</span>
              </Button>
            ) : currentProject && currentProject.status === 'paused' ? (
              <Button onClick={() => updateProjectStatus('active')} className="flex-1 sm:flex-none">
                <Play className="mr-2 h-4 w-4" />
                <span className="hidden sm:inline">继续</span>
              </Button>
            ) : null}
          </div>
        </div>

        {/* Status Cards - 响应式布局优化 */}
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>状态</CardDescription>
              <CardTitle className="text-2xl">{getStatusLabel(currentProject?.status || 'active')}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>阶段</CardDescription>
              <CardTitle className="text-2xl">{getPhaseLabel(currentProject?.phase || 'planning')}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Agent</CardDescription>
              <CardTitle className="text-2xl">{agents.length}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>任务</CardDescription>
              <CardTitle className="text-2xl">{tasks.length}</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Phase Selection - 移动端优化 */}
        <Card>
          <CardHeader>
            <CardTitle>项目阶段</CardTitle>
            <CardDescription>切换项目当前阶段</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {(['planning', 'execution', 'review', 'done'] as const).map((phase) => (
                <Button
                  key={phase}
                  variant={currentProject?.phase === phase ? 'default' : 'outline'}
                  onClick={() => updateProjectPhase(phase)}
                  className="flex-col h-auto py-3 min-h-[88px]"
                >
                  {phase === 'planning' && <FileText className="h-5 w-5 mb-1" />}
                  {phase === 'execution' && <Play className="h-5 w-5 mb-1" />}
                  {phase === 'review' && <CheckCircle className="h-5 w-5 mb-1" />}
                  {phase === 'done' && <CheckCircle className="h-5 w-5 mb-1" />}
                  {getPhaseLabel(phase)}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Agents */}
        <Card>
          <CardHeader>
            <CardTitle>项目 Agent</CardTitle>
            <CardDescription>参与此项目的 AI Agent</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {agents.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">暂无 Agent</p>
              ) : (
                agents.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <Bot className="h-8 w-8 text-primary" />
                      <div>
                        <p className="font-medium">{agent.name}</p>
                        <p className="text-sm text-muted-foreground">{agent.role}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        agent.status === 'working' ? 'bg-green-100 text-green-700' :
                        agent.status === 'idle' ? 'bg-gray-100 text-gray-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {agent.status === 'working' && '工作中'}
                        {agent.status === 'idle' && '空闲'}
                        {agent.status === 'waiting' && '等待中'}
                        {agent.status === 'error' && '错误'}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Tasks */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>任务列表</CardTitle>
                <CardDescription>管理和跟踪项目任务</CardDescription>
              </div>
              <Button onClick={handleCreateTask}>
                <Plus className="h-4 w-4 mr-2" />
                新建任务
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <TaskList
              tasks={tasks}
              onTaskClick={handleTaskClick}
              onStatusChange={handleTaskStatusChange}
              onCreateTask={handleCreateTask}
              onEditTask={(task) => {
                setSelectedTask(task)
                setTaskDetailOpen(true)
              }}
              onDeleteTask={(taskId) => {
                setTasks(prev => prev.filter(t => t.id !== taskId))
                toast({
                  title: '删除成功',
                  description: '任务已删除',
                })
              }}
            />
          </CardContent>
        </Card>
      </div>

      {/* Task Detail Dialog */}
      <TaskDetail
        task={selectedTask}
        open={taskDetailOpen}
        onOpenChange={setTaskDetailOpen}
        messages={taskMessages}
        onExecute={(taskId) => {
          handleTaskStatusChange(taskId, 'in_progress')
        }}
        onPause={(taskId) => {
          handleTaskStatusChange(taskId, 'pending')
        }}
        onCancel={(taskId) => {
          handleTaskStatusChange(taskId, 'cancelled')
        }}
      />

      {/* Create Task Dialog */}
      <CreateTaskDialog
        open={createTaskOpen}
        onOpenChange={setCreateTaskOpen}
        onSubmit={handleCreateTaskSubmit}
        agents={agents}
      />
    </ErrorBoundary>
  )
}
