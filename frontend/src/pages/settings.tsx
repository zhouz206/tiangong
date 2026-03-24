import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Sun, Moon, Monitor, Database, Bot, Globe, Key, Save, Plus } from 'lucide-react'
import { useSettingsStore, ModelConfig } from '@/stores/settings-store'
import { useTheme } from 'next-themes'
import { useToast } from '@/hooks/use-toast'

export default function Settings() {
  const { toast } = useToast()
  const { theme, setTheme } = useTheme()
  const {
    models,
    addModel,
    apiBaseUrl,
    setApiBaseUrl,
    wsUrl,
    setWsUrl,
  } = useSettingsStore()

  const [newModel, setNewModel] = useState<Partial<ModelConfig>>({
    provider: 'openai',
    enabled: true,
  })

  const saveSettings = () => {
    toast({
      title: '设置已保存',
      description: '配置已更新',
    })
  }

  const addModelConfig = () => {
    if (!newModel.name || !newModel.model_name) {
      toast({
        title: '信息不完整',
        description: '请填写模型名称和模型 ID',
        variant: 'destructive',
      })
      return
    }

    addModel({
      id: Date.now().toString(),
      name: newModel.name!,
      provider: newModel.provider as any,
      model_name: newModel.model_name!,
      api_key: newModel.api_key,
      endpoint: newModel.endpoint,
      priority: newModel.priority || 1,
      enabled: newModel.enabled !== false,
    })

    setNewModel({ provider: 'openai', enabled: true })

    toast({
      title: '添加成功',
      description: '模型配置已添加',
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">设置</h1>
        <p className="text-muted-foreground">配置系统参数和偏好设置</p>
      </div>

      {/* Theme Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sun className="h-5 w-5" />
            <CardTitle>外观</CardTitle>
          </div>
          <CardDescription>调整界面主题和显示设置</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>主题模式</Label>
            <div className="flex gap-2 mt-2">
              <Button
                variant={theme === 'light' ? 'default' : 'outline'}
                onClick={() => setTheme('light')}
              >
                <Sun className="h-4 w-4 mr-2" />
                浅色
              </Button>
              <Button
                variant={theme === 'dark' ? 'default' : 'outline'}
                onClick={() => setTheme('dark')}
              >
                <Moon className="h-4 w-4 mr-2" />
                深色
              </Button>
              <Button
                variant={theme === 'system' ? 'default' : 'outline'}
                onClick={() => setTheme('system')}
              >
                <Monitor className="h-4 w-4 mr-2" />
                系统
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* API Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            <CardTitle>API 配置</CardTitle>
          </div>
          <CardDescription>后端服务连接设置</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>API 地址</Label>
            <Input
              value={apiBaseUrl}
              onChange={(e) => setApiBaseUrl(e.target.value)}
              placeholder="http://localhost:8000"
            />
          </div>
          <div className="space-y-2">
            <Label>WebSocket 地址</Label>
            <Input
              value={wsUrl}
              onChange={(e) => setWsUrl(e.target.value)}
              placeholder="ws://localhost:8000/ws"
            />
          </div>
          <Button onClick={saveSettings}>
            <Save className="h-4 w-4 mr-2" />
            保存配置
          </Button>
        </CardContent>
      </Card>

      {/* Model Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            <CardTitle>模型配置</CardTitle>
          </div>
          <CardDescription>添加和管理 LLM 模型</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Existing Models */}
          {models.length > 0 && (
            <div className="space-y-2">
              <Label>已配置的模型</Label>
              {models.map((model) => (
                <div
                  key={model.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <p className="font-medium">{model.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {model.provider} / {model.model_name}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-1 rounded-full text-xs ${
                        model.enabled
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {model.enabled ? '已启用' : '已禁用'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Add New Model */}
          <div className="space-y-3 pt-4 border-t">
            <Label>添加新模型</Label>
            <div className="grid gap-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-sm">模型名称</Label>
                  <Input
                    value={newModel.name || ''}
                    onChange={(e) =>
                      setNewModel({ ...newModel, name: e.target.value })
                    }
                    placeholder="例如：GPT-4o"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-sm">模型 ID</Label>
                  <Input
                    value={newModel.model_name || ''}
                    onChange={(e) =>
                      setNewModel({ ...newModel, model_name: e.target.value })
                    }
                    placeholder="例如：gpt-4o"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-sm">提供商</Label>
                  <select
                    value={newModel.provider}
                    onChange={(e) =>
                      setNewModel({ ...newModel, provider: e.target.value as any })
                    }
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="qwen">通义千问</option>
                    <option value="ollama">Ollama</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label className="text-sm">优先级</Label>
                  <Input
                    type="number"
                    value={newModel.priority || 1}
                    onChange={(e) =>
                      setNewModel({ ...newModel, priority: parseInt(e.target.value) })
                    }
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-sm">API Key</Label>
                <div className="relative">
                  <Key className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="password"
                    value={newModel.api_key || ''}
                    onChange={(e) =>
                      setNewModel({ ...newModel, api_key: e.target.value })
                    }
                    className="pl-10"
                    placeholder="sk-..."
                  />
                </div>
              </div>
              <Button onClick={addModelConfig} className="w-full">
                <Plus className="h-4 w-4 mr-2" />
                添加模型
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Agent Templates */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            <CardTitle>Agent 模板</CardTitle>
          </div>
          <CardDescription>配置预定义的 Agent 角色模板</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            此功能开发中...
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
