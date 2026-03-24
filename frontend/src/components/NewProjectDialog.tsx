import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { FolderOpen, Code, BookOpen, BarChart, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface ProjectTemplate {
  id: string
  name: string
  description: string
  icon: 'code' | 'book' | 'chart'
  agents: { role: string; name: string }[]
}

interface NewProjectDialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  onSubmit: (data: {
    name: string
    description: string
    template_id: string
    agents: { role: string; name: string; model?: string }[]
  }) => void
}

const templates: ProjectTemplate[] = [
  {
    id: 'software',
    name: '软件开发',
    description: '代码开发、测试和部署项目',
    icon: 'code',
    agents: [
      { role: 'manager', name: '项目经理' },
      { role: 'coder', name: '开发工程师' },
      { role: 'reviewer', name: '代码审查员' },
    ],
  },
  {
    id: 'content',
    name: '内容创作',
    description: '写作、设计和创意内容项目',
    icon: 'book',
    agents: [
      { role: 'manager', name: '内容策划' },
      { role: 'writer', name: '内容作者' },
      { role: 'designer', name: '设计师' },
    ],
  },
  {
    id: 'analysis',
    name: '数据分析',
    description: '数据处理、分析和可视化项目',
    icon: 'chart',
    agents: [
      { role: 'manager', name: '分析主管' },
      { role: 'data_analyst', name: '数据分析师' },
      { role: 'researcher', name: '研究员' },
    ],
  },
]

const getIcon = (iconType: string) => {
  switch (iconType) {
    case 'code': return Code
    case 'book': return BookOpen
    case 'chart': return BarChart
    default: return FolderOpen
  }
}

export function NewProjectDialog({ open, onOpenChange, onSubmit }: NewProjectDialogProps) {
  const [step, setStep] = useState(1)
  const [selectedTemplate, setSelectedTemplate] = useState<string>('software')
  const [projectName, setProjectName] = useState('')
  const [description, setDescription] = useState('')
  const [agents, setAgents] = useState<{ role: string; name: string; model?: string }[]>([])

  const currentTemplate = templates.find((t) => t.id === selectedTemplate)

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId)
    const template = templates.find((t) => t.id === templateId)
    if (template) {
      setAgents(template.agents.map((a) => ({ ...a, model: undefined })))
    }
  }

  const handleAgentChange = (index: number, field: string, value: string) => {
    setAgents((prev) => prev.map((agent, i) =>
      i === index ? { ...agent, [field]: value } : agent
    ))
  }

  const handleSubmit = () => {
    onSubmit({
      name: projectName,
      description,
      template_id: selectedTemplate,
      agents,
    })
  }

  const isStep1Valid = selectedTemplate !== ''
  const isStep2Valid = projectName.trim() !== '' && agents.every((a) => a.name.trim() !== '')

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            创建新项目
          </DialogTitle>
          <DialogDescription>
            选择一个模板开始，然后配置您的项目和 Agent 团队
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Step Indicator */}
          <div className="flex items-center gap-2">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={cn(
                  'h-2 flex-1 rounded-full transition-colors',
                  s <= step ? 'bg-primary' : 'bg-muted'
                )}
              />
            ))}
          </div>

          {/* Step 1: Template Selection */}
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="font-medium">选择项目模板</h3>
              <div className="grid gap-3">
                {templates.map((template) => {
                  const Icon = getIcon(template.icon)
                  return (
                    <Card
                      key={template.id}
                      className={cn(
                        'cursor-pointer transition-all hover:border-primary',
                        selectedTemplate === template.id && 'border-primary bg-primary/5'
                      )}
                      onClick={() => handleTemplateSelect(template.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          <div className={cn(
                            'p-2 rounded-lg',
                            selectedTemplate === template.id ? 'bg-primary text-primary-foreground' : 'bg-muted'
                          )}>
                            <Icon className="h-5 w-5" />
                          </div>
                          <div>
                            <h4 className="font-medium">{template.name}</h4>
                            <p className="text-sm text-muted-foreground">{template.description}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </div>
          )}

          {/* Step 2: Project Info and Agent Config */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="space-y-4">
                <h3 className="font-medium">项目信息</h3>
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="project-name">项目名称</Label>
                    <Input
                      id="project-name"
                      placeholder="输入项目名称..."
                      value={projectName}
                      onChange={(e) => setProjectName(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">项目描述</Label>
                    <Textarea
                      id="description"
                      placeholder="简要描述项目目标..."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={3}
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium">Agent 配置</h3>
                <div className="space-y-3">
                  {agents.map((agent, index) => (
                    <Card key={index}>
                      <CardContent className="p-4">
                        <div className="grid grid-cols-3 gap-3">
                          <div>
                            <Label className="text-xs">角色</Label>
                            <p className="text-sm font-medium">{agent.role}</p>
                          </div>
                          <div>
                            <Label htmlFor={`agent-${index}-name`}>名称</Label>
                            <Input
                              id={`agent-${index}-name`}
                              value={agent.name}
                              onChange={(e) => handleAgentChange(index, 'name', e.target.value)}
                              placeholder="Agent 名称"
                            />
                          </div>
                          <div>
                            <Label htmlFor={`agent-${index}-model`}>模型</Label>
                            <Select
                              value={agent.model || 'default'}
                              onValueChange={(value: string) => handleAgentChange(index, 'model', value === 'default' ? '' : value)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="选择模型" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="default">默认</SelectItem>
                                <SelectItem value="claude-sonnet-4-6">Claude Sonnet 4.6</SelectItem>
                                <SelectItem value="claude-opus-4-6">Claude Opus 4.6</SelectItem>
                                <SelectItem value="claude-haiku-4-5-20251001">Claude Haiku 4.5</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Preview and Confirm */}
          {step === 3 && (
            <div className="space-y-4">
              <h3 className="font-medium">确认项目配置</h3>
              <Card>
                <CardHeader>
                  <CardTitle>{projectName}</CardTitle>
                  <CardDescription>{description || '无描述'}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">模板:</span>
                      <span className="text-sm font-medium">{currentTemplate?.name}</span>
                    </div>
                    <div>
                      <span className="text-sm text-muted-foreground">Agent 团队:</span>
                      <div className="mt-2 space-y-2">
                        {agents.map((agent, index) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">{agent.role}</span>
                            <span>{agent.name}</span>
                            <span className="text-muted-foreground text-xs">{agent.model || '默认'}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        <DialogFooter>
          {step > 1 && (
            <Button variant="outline" onClick={() => setStep(step - 1)}>
              上一步
            </Button>
          )}
          {step < 3 ? (
            <Button onClick={() => setStep(step + 1)} disabled={!isStep1Valid}>
              下一步
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={!isStep2Valid}>
              创建项目
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
