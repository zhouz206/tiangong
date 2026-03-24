import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Trash2, Play, Settings } from 'lucide-react'
import { useAgentStore, Agent } from '@/stores/agent-store'
import { useProjectStore } from '@/stores/project-store'
import { useSettingsStore } from '@/stores/settings-store'
import { agentApi } from '@/utils/api-services'
import { useToast } from '@/hooks/use-toast'
import { AgentConfigForm, type AgentConfigData } from '@/components/AgentConfigForm'
import { LoadingState } from '@/components/LoadingState'
import { EmptyState } from '@/components/EmptyState'
import { Dialog, DialogContent } from '@/components/ui/dialog'

export default function Agents() {
  const { toast } = useToast()
  const { agents, setAgents, removeAgent, addAgent } = useAgentStore()
  const { currentProject } = useProjectStore()
  const { models } = useSettingsStore()
  const [loading, setLoading] = useState(true)
  const [configDialogOpen, setConfigDialogOpen] = useState(false)
  const [editingAgent, setEditingAgent] = useState<Agent | undefined>()

  useEffect(() => {
    loadAgents()
  }, [currentProject])

  const loadAgents = async () => {
    try {
      setLoading(true)
      const result = await agentApi.getList(currentProject?.id)
      setAgents(result.data)
    } catch (error) {
      toast({
        title: '加载失败',
        description: '无法加载 Agent 列表',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAgent = async (data: AgentConfigData) => {
    if (!currentProject) return
    try {
      const result = await agentApi.create({
        project_id: currentProject.id,
        name: data.name,
        role: data.role,
        model: data.model_id,
      })
      addAgent(result.data as Agent)
      setConfigDialogOpen(false)
      toast({
        title: '创建成功',
        description: `Agent"${data.name}"已创建`,
      })
    } catch (error) {
      toast({
        title: '创建失败',
        description: '无法创建 Agent',
        variant: 'destructive',
      })
    }
  }

  const handleUpdateAgent = async (data: AgentConfigData) => {
    if (!data.id) return
    try {
      const result = await agentApi.update(data.id, {
        name: data.name,
        role: data.role,
        model: data.model_id,
      })
      const updatedAgent = result.data as Agent
      setAgents(agents.map((a: Agent) => a.id === data.id ? updatedAgent : a))
      setConfigDialogOpen(false)
      setEditingAgent(undefined)
      toast({
        title: '更新成功',
        description: `Agent"${data.name}"已更新`,
      })
    } catch (error) {
      toast({
        title: '更新失败',
        description: '无法更新 Agent',
        variant: 'destructive',
      })
    }
  }

  const handleSubmit = async (data: AgentConfigData) => {
    if (editingAgent) {
      await handleUpdateAgent(data)
    } else {
      await handleCreateAgent(data)
    }
  }

  const deleteAgent = async (id: string) => {
    try {
      await agentApi.delete(id)
      removeAgent(id)
      toast({
        title: '删除成功',
        description: 'Agent 已删除',
      })
    } catch (error) {
      toast({
        title: '删除失败',
        description: '无法删除 Agent',
        variant: 'destructive',
      })
    }
  }

  const getRoleIcon = (role: Agent['role']) => {
    const icons = {
      manager: '📋',
      researcher: '🔍',
      coder: '💻',
      designer: '🎨',
      writer: '✍️',
      reviewer: '🔬',
      data_analyst: '📊',
      knowledge_manager: '📚',
    }
    return icons[role] || '🤖'
  }

  const getRoleName = (role: Agent['role']) => {
    const names = {
      manager: '项目经理',
      researcher: '研究员',
      coder: '程序员',
      designer: '设计师',
      writer: '文案',
      reviewer: '审核员',
      data_analyst: '数据分析师',
      knowledge_manager: '知识管理员',
    }
    return names[role]
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Agent</h1>
          <p className="text-sm sm:text-base text-muted-foreground">管理和配置 AI Agent</p>
        </div>
        <Button onClick={() => { setEditingAgent(undefined); setConfigDialogOpen(true) }} className="w-full sm:w-auto">
          <Plus className="mr-2 h-4 w-4" />
          <span className="hidden sm:inline">添加 Agent</span>
          <span className="sm:hidden">添加</span>
        </Button>
      </div>

      {/* Agent Grid - 响应式布局优化 */}
      {loading ? (
        <LoadingState type="card" count={6} />
      ) : agents.length === 0 ? (
        <EmptyState
          icon="file"
          title="暂无 Agent"
          description="为当前项目添加一个 AI Agent 助手"
          actionLabel="添加 Agent"
          onAction={() => setConfigDialogOpen(true)}
        />
      ) : (
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <Card key={agent.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{getRoleIcon(agent.role)}</span>
                    <div>
                      <CardTitle className="text-lg">{agent.name}</CardTitle>
                      <CardDescription>{getRoleName(agent.role)}</CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">状态</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      agent.status === 'working' ? 'bg-green-100 text-green-700' :
                      agent.status === 'idle' ? 'bg-gray-100 text-gray-700' :
                      agent.status === 'error' ? 'bg-red-100 text-red-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {agent.status === 'working' && '工作中'}
                      {agent.status === 'idle' && '空闲'}
                      {agent.status === 'waiting' && '等待中'}
                      {agent.status === 'error' && '错误'}
                    </span>
                  </div>

                  <div className="text-sm text-muted-foreground">
                    模型：{agent.model}
                  </div>

                  <div className="flex flex-wrap gap-2 pt-2">
                    <Button variant="outline" size="sm" className="flex-1 min-w-[44px]">
                      <Play className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1 min-w-[44px]"
                      onClick={() => { setEditingAgent(agent); setConfigDialogOpen(true) }}
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="min-w-[44px]"
                      onClick={() => deleteAgent(agent.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Role Templates - 移动端优化 */}
      <Card>
        <CardHeader>
          <CardTitle>可用角色</CardTitle>
          <CardDescription>点击添加对应角色的 Agent</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {(['manager', 'researcher', 'coder', 'designer', 'writer', 'reviewer', 'data_analyst', 'knowledge_manager'] as const).map((role) => (
              <Button
                key={role}
                variant="outline"
                className="flex-col h-auto py-3 min-h-[88px]"
                onClick={() => {
                  setEditingAgent(undefined)
                  setConfigDialogOpen(true)
                }}
              >
                <span className="text-2xl mb-1">{getRoleIcon(role)}</span>
                <span className="text-xs text-center">{getRoleName(role)}</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Agent Config Dialog */}
      <Dialog open={configDialogOpen} onOpenChange={setConfigDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <AgentConfigForm
            agent={editingAgent}
            models={models}
            availableAgents={agents.filter(a => a.id !== editingAgent?.id)}
            onSubmit={handleSubmit}
            onCancel={() => { setConfigDialogOpen(false); setEditingAgent(undefined) }}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
