import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { Plus, X, Zap, Settings, GitBranch } from 'lucide-react'
import type { Agent, AgentRole } from '@/stores/agent-store'
import type { ModelConfig } from '@/stores/settings-store'
import { cn } from '@/lib/utils'

export interface AgentConfigData {
  id?: string
  name: string
  role: AgentRole
  model_id: string
  temperature: number
  max_tokens: number
  upstream_agent_ids?: string[]
  downstream_agent_ids?: string[]
  capabilities?: string[]
}

interface AgentConfigFormProps {
  agent?: Agent
  models: ModelConfig[]
  availableAgents: Agent[]
  onSubmit: (data: AgentConfigData) => void
  onCancel?: () => void
}

const roleLabels: Record<AgentRole, string> = {
  manager: '项目经理',
  researcher: '研究员',
  coder: '开发工程师',
  designer: '设计师',
  writer: '内容作者',
  reviewer: '审查员',
  data_analyst: '数据分析师',
  knowledge_manager: '知识管理员',
}

const roleDescriptions: Record<AgentRole, string> = {
  manager: '负责任务分解、进度跟踪和团队协调',
  researcher: '负责信息搜集、市场调研和竞品分析',
  coder: '负责代码编写、测试和技术实现',
  designer: '负责 UI/UX 设计和视觉创意',
  writer: '负责文档撰写、内容创作和编辑',
  reviewer: '负责代码审查、质量把关和测试验证',
  data_analyst: '负责数据处理、分析和可视化',
  knowledge_manager: '负责知识库管理、文档整理和检索',
}

const defaultCapabilities: Record<AgentRole, string[]> = {
  manager: ['task_decomposition', 'scheduling', 'coordination'],
  researcher: ['web_search', 'data_collection', 'summarization'],
  coder: ['code_generation', 'debugging', 'testing'],
  designer: ['ui_design', 'prototyping', 'visual_design'],
  writer: ['content_writing', 'editing', 'translation'],
  reviewer: ['code_review', 'testing', 'quality_assurance'],
  data_analyst: ['data_processing', 'statistical_analysis', 'visualization'],
  knowledge_manager: ['document_management', 'tagging', 'search'],
}

export function AgentConfigForm({
  agent,
  models,
  availableAgents,
  onSubmit,
  onCancel,
}: AgentConfigFormProps) {
  const [name, setName] = useState(agent?.name || '')
  const [role, setRole] = useState<AgentRole>(agent?.role || 'coder')
  const [modelId, setModelId] = useState(agent?.model || '')
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(4096)
  const [upstreamAgents, setUpstreamAgents] = useState<string[]>(
    agent?.upstream_agents || []
  )
  const [downstreamAgents, setDownstreamAgents] = useState<string[]>(
    agent?.downstream_agents || []
  )
  const [capabilities, setCapabilities] = useState<string[]>(
    agent?.capabilities || defaultCapabilities[agent?.role || 'coder']
  )

  useEffect(() => {
    if (agent) {
      setName(agent.name)
      setRole(agent.role)
      setModelId(agent.model)
      setUpstreamAgents(agent.upstream_agents || [])
      setDownstreamAgents(agent.downstream_agents || [])
      setCapabilities(agent.capabilities || [])
    }
  }, [agent])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      id: agent?.id,
      name,
      role,
      model_id: modelId,
      temperature,
      max_tokens: maxTokens,
      upstream_agent_ids: upstreamAgents,
      downstream_agent_ids: downstreamAgents,
      capabilities,
    })
  }

  const toggleUpstreamAgent = (agentId: string) => {
    setUpstreamAgents((prev) =>
      prev.includes(agentId)
        ? prev.filter((id) => id !== agentId)
        : [...prev, agentId]
    )
  }

  const toggleDownstreamAgent = (agentId: string) => {
    setDownstreamAgents((prev) =>
      prev.includes(agentId)
        ? prev.filter((id) => id !== agentId)
        : [...prev, agentId]
    )
  }

  const toggleCapability = (cap: string) => {
    setCapabilities((prev) =>
      prev.includes(cap)
        ? prev.filter((c) => c !== cap)
        : [...prev, cap]
    )
  }

  const otherAgents = availableAgents.filter(
    (a) => a.id !== agent?.id
  )

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid gap-6">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              基本信息
            </CardTitle>
            <CardDescription>配置 Agent 的角色和基础设置</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Agent 名称</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="例如：前端开发工程师"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="role">角色</Label>
              <Select
                value={role}
                onValueChange={(value: AgentRole) => {
                  setRole(value)
                  setCapabilities(defaultCapabilities[value])
                }}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(roleLabels).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                {roleDescriptions[role]}
              </p>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="model">绑定模型</Label>
              <Select value={modelId} onValueChange={setModelId}>
                <SelectTrigger>
                  <SelectValue placeholder="选择模型" />
                </SelectTrigger>
                <SelectContent>
                  {models.map((model) => (
                    <SelectItem key={model.id} value={model.id}>
                      {model.name} ({model.provider})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Model Parameters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              模型参数
            </CardTitle>
            <CardDescription>调整模型生成的温度和最大 token 数</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Temperature: {temperature.toFixed(2)}</Label>
                <span className="text-sm text-muted-foreground">
                  {temperature < 0.3 ? '更确定' : temperature > 0.7 ? '更创意' : '平衡'}
                </span>
              </div>
              <Slider
                value={[temperature]}
                onValueChange={([value]: [number]) => setTemperature(value)}
                min={0}
                max={1}
                step={0.01}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                较低值使输出更确定，较高值使输出更有创意性
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Max Tokens: {maxTokens}</Label>
              </div>
              <Slider
                value={[maxTokens]}
                onValueChange={([value]: [number]) => setMaxTokens(value)}
                min={256}
                max={8192}
                step={256}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                限制单次响应的最大 token 数量
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Dependencies */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitBranch className="h-5 w-5" />
              上下游依赖
            </CardTitle>
            <CardDescription>配置 Agent 之间的协作关系</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>上游 Agent（数据输入来源）</Label>
              <div className="flex flex-wrap gap-2">
                {otherAgents.map((a) => (
                  <Badge
                    key={`upstream-${a.id}`}
                    variant={upstreamAgents.includes(a.id) ? 'default' : 'outline'}
                    className={cn(
                      'cursor-pointer',
                      upstreamAgents.includes(a.id) && 'bg-primary'
                    )}
                    onClick={() => toggleUpstreamAgent(a.id)}
                  >
                    {a.name}
                  </Badge>
                ))}
                {otherAgents.length === 0 && (
                  <span className="text-sm text-muted-foreground">暂无其他 Agent</span>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label>下游 Agent（数据输出目标）</Label>
              <div className="flex flex-wrap gap-2">
                {otherAgents.map((a) => (
                  <Badge
                    key={`downstream-${a.id}`}
                    variant={downstreamAgents.includes(a.id) ? 'default' : 'outline'}
                    className={cn(
                      'cursor-pointer',
                      downstreamAgents.includes(a.id) && 'bg-primary'
                    )}
                    onClick={() => toggleDownstreamAgent(a.id)}
                  >
                    {a.name}
                  </Badge>
                ))}
                {otherAgents.length === 0 && (
                  <span className="text-sm text-muted-foreground">暂无其他 Agent</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Capabilities */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              能力标签
            </CardTitle>
            <CardDescription>定义 Agent 的专长能力</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {capabilities.map((cap) => (
                <Badge
                  key={cap}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => toggleCapability(cap)}
                >
                  {cap}
                  <X className="ml-1 h-3 w-3" />
                </Badge>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  const cap = prompt('输入新的能力标签：')
                  if (cap && !capabilities.includes(cap)) {
                    setCapabilities([...capabilities, cap])
                  }
                }}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-end gap-3">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            取消
          </Button>
        )}
        <Button type="submit">
          {agent ? '更新配置' : '创建 Agent'}
        </Button>
      </div>
    </form>
  )
}
