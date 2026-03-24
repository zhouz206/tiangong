import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus, Search } from 'lucide-react'
import { useProjectStore, Project } from '@/stores/project-store'
import { useWorkspaceStore } from '@/stores/workspace-store'
import { useNavigate } from 'react-router-dom'
import { projectApi } from '@/utils/api-services'
import { useToast } from '@/hooks/use-toast'
import { NewProjectDialog } from '@/components/NewProjectDialog'
import { LoadingState } from '@/components/LoadingState'
import { EmptyState } from '@/components/EmptyState'

export default function Projects() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { projects, setProjects, addProject } = useProjectStore()
  const { currentWorkspace } = useWorkspaceStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [newProjectOpen, setNewProjectOpen] = useState(false)

  useEffect(() => {
    if (currentWorkspace) {
      loadProjects()
    }
  }, [currentWorkspace])

  const loadProjects = async () => {
    if (!currentWorkspace) return
    try {
      setLoading(true)
      const result = await projectApi.getList(currentWorkspace.id)
      setProjects(result.data)
    } catch (error) {
      toast({
        title: '加载失败',
        description: '无法加载项目列表',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProject = async (data: {
    name: string
    description: string
    template_id: string
    agents: { role: string; name: string; model?: string }[]
  }) => {
    if (!currentWorkspace) return
    try {
      const result = await projectApi.create({
        workspace_id: currentWorkspace.id,
        name: data.name,
        description: data.description,
        template_id: data.template_id,
      })
      addProject(result.data as Project)
      setNewProjectOpen(false)
      toast({
        title: '创建成功',
        description: `项目"${data.name}"已创建`,
      })
    } catch (error) {
      toast({
        title: '创建失败',
        description: '无法创建新项目',
        variant: 'destructive',
      })
    }
  }

  const filteredProjects = projects.filter((project) =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'paused': return 'bg-yellow-500'
      case 'completed': return 'bg-blue-500'
      case 'cancelled': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
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

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">项目</h1>
          <p className="text-sm sm:text-base text-muted-foreground">管理和创建 AI 协作项目</p>
        </div>
        <Button onClick={() => setNewProjectOpen(true)} className="w-full sm:w-auto">
          <Plus className="mr-2 h-4 w-4" />
          <span className="hidden sm:inline">新建项目</span>
          <span className="sm:hidden">新建</span>
        </Button>
      </div>

      {/* Search - 移动端优化 */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="搜索项目..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Projects Grid - 响应式布局优化 */}
      {loading ? (
        <LoadingState type="card" count={6} />
      ) : filteredProjects.length === 0 ? (
        <EmptyState
          icon="folder"
          title={searchQuery ? '没有找到匹配的项目' : '暂无项目'}
          description={searchQuery ? '尝试其他搜索条件' : '创建一个新项目开始你的 AI 协作之旅'}
          actionLabel={!searchQuery ? '新建项目' : undefined}
          onAction={() => setNewProjectOpen(true)}
        />
      ) : (
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {filteredProjects.map((project) => (
            <Card
              key={project.id}
              className="cursor-pointer transition-colors hover:bg-accent"
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className={`h-3 w-3 rounded-full ${getStatusColor(project.status)}`}
                    />
                    <CardTitle className="text-lg">{project.name}</CardTitle>
                  </div>
                </div>
                <CardDescription className="line-clamp-2">
                  {project.description || '无描述'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    阶段：{getPhaseLabel(project.phase)}
                  </span>
                  <span className="text-muted-foreground">
                    {new Date(project.created_at).toLocaleDateString('zh-CN')}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <NewProjectDialog
        open={newProjectOpen}
        onOpenChange={setNewProjectOpen}
        onSubmit={handleCreateProject}
      />
    </div>
  )
}
