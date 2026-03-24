import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FolderKanban, Bot, BookOpen, TrendingUp, Clock } from 'lucide-react'
import { statsApi } from '@/utils/api-services'
import { useToast } from '@/hooks/use-toast'

export default function Dashboard() {
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total_projects: 0,
    active_projects: 0,
    total_agents: 0,
    total_tasks: 0,
    token_usage: 0,
    cost: 0,
  })

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const result = await statsApi.getOverview()
      setStats(result.data)
    } catch (error) {
      toast({
        title: '加载失败',
        description: '无法加载统计数据',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: '总项目数',
      value: stats.total_projects,
      description: `${stats.active_projects} 进行中`,
      icon: FolderKanban,
      trend: '+12%',
    },
    {
      title: 'Agent 数量',
      value: stats.total_agents,
      description: '8 个角色可用',
      icon: Bot,
      trend: '+2',
    },
    {
      title: '知识库文档',
      value: '0',
      description: '待归档',
      icon: BookOpen,
    },
    {
      title: 'Token 使用',
      value: stats.token_usage.toLocaleString(),
      description: `成本：$${stats.cost.toFixed(2)}`,
      icon: TrendingUp,
      trend: '+18%',
    },
  ]

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">仪表盘</h1>
        <p className="text-muted-foreground">欢迎使用天工 AI 协作平台</p>
      </div>

      {/* Stats Grid - 响应式布局优化 */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{loading ? '-' : stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
              {stat.trend && (
                <p className="text-xs text-green-600 mt-1">{stat.trend}</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions - 响应式布局优化 */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>快速开始</CardTitle>
            <CardDescription>创建新项目或查看现有项目</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button className="w-full">创建新项目</Button>
              <Button variant="outline" className="w-full">查看项目列表</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>最近活动</CardTitle>
            <CardDescription>最近的项目动态</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span>暂无活动</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>成本分析</CardTitle>
            <CardDescription>本月 Token 使用情况</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${stats.cost.toFixed(2)}</div>
            <p className="text-sm text-muted-foreground">
              平均每项目 ${(stats.total_projects > 0 ? stats.cost / stats.total_projects : 0).toFixed(2)}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
