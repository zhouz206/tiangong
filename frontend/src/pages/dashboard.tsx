import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { StatCard, ProjectCard } from '../components/cards';
import { Button } from '../components/ui/button';
import { Loading } from '../components/ui/loading';
import { useProjectStore, type Project } from '../stores/project';
import { projectApi } from '../utils/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { projects, setProjects, addProject, loading, setLoading, error, setError } = useProjectStore();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [creating, setCreating] = useState(false);

  // 加载项目数据
  React.useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await projectApi.list();
      setProjects(data.projects || data || []);
    } catch (err) {
      console.error('加载项目失败:', err);
      setError('加载失败，使用本地数据');
      // 使用 mock 数据降级
      if (projects.length === 0) {
        setProjects([
          { id: '1', name: 'SaaS 应用开发', description: '构建现代化 SaaS 应用', progress: 75, phase: 'executing', status: 'active' },
          { id: '2', name: '技术博客系列', description: 'AI Agent 开发教程', progress: 50, phase: 'planning', status: 'active' },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setCreating(true);
    const formData = new FormData(e.currentTarget);

    const newProject: Project = {
      id: `proj-${Date.now()}`,
      name: formData.get('name') as string,
      description: formData.get('description') as string,
      progress: 0,
      phase: 'planning',
      status: 'active',
      created_at: new Date().toISOString().split('T')[0]
    };

    try {
      const res = await projectApi.create({
        name: newProject.name,
        description: newProject.description,
        template: formData.get('template') as string || 'software'
      });
      const created = res.project || res;
      addProject(created);
      setCreateDialogOpen(false);
      navigate(`/projects/${created.id}`);
    } catch (err) {
      console.error('创建项目失败:', err);
      // 降级处理
      addProject(newProject);
      setCreateDialogOpen(false);
      navigate(`/projects/${newProject.id}`);
    } finally {
      setCreating(false);
    }
  };

  const stats = {
    totalProjects: projects.length,
    activeProjects: projects.filter(p => p.status === 'active').length,
    completedProjects: projects.filter(p => p.phase === 'completed').length,
    planningProjects: projects.filter(p => p.phase === 'planning').length
  };

  return (
    <div className="space-y-8">
      {/* 页面标题 */}
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">仪表盘</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">欢迎回来，这是你的项目概览</p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)} disabled={loading || creating}>
          {creating ? '创建中...' : loading ? '加载中...' : '+ 新建项目'}
        </Button>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p className="text-yellow-600 dark:text-yellow-400">{error}</p>
        </div>
      )}

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="总项目数" value={stats.totalProjects} change="+ 本月新增" />
        <StatCard title="进行中" value={stats.activeProjects} />
        <StatCard title="规划中" value={stats.planningProjects} />
        <StatCard title="已完成" value={stats.completedProjects} />
      </div>

      {/* 快速操作 */}
      <Card>
        <CardHeader>
          <CardTitle>快速操作</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" onClick={() => navigate('/projects')} className="h-20 flex-col gap-2">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              查看所有项目
            </Button>
            <Button variant="outline" onClick={() => navigate('/agents')} className="h-20 flex-col gap-2">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Agent 团队
            </Button>
            <Button variant="outline" onClick={() => navigate('/knowledge')} className="h-20 flex-col gap-2">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              知识库
            </Button>
            <Button variant="outline" onClick={() => navigate('/settings')} className="h-20 flex-col gap-2">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              设置
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 最近项目 */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">最近项目</h2>
          <Button variant="outline" onClick={() => navigate('/projects')}>
            查看全部 →
          </Button>
        </div>
        {loading && projects.length === 0 ? (
          <div className="text-center py-12">
            <Loading size="lg" text="加载项目中..." />
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <p className="text-gray-600 dark:text-gray-400">暂无项目</p>
            <Button className="mt-4" onClick={() => setCreateDialogOpen(true)}>
              创建第一个项目
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.slice(0, 6).map(project => (
              <ProjectCard
                key={project.id}
                {...project}
                onClick={() => navigate(`/projects/${project.id}`)}
              />
            ))}
          </div>
        )}
      </div>

      {/* 新建项目对话框 */}
      {createDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">新建项目</h2>
            <form onSubmit={handleCreateProject}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">项目名称</label>
                  <input
                    name="name"
                    required
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="我的项目"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">描述</label>
                  <textarea
                    name="description"
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="项目描述..."
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">模板</label>
                  <select
                    name="template"
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="software">软件开发</option>
                    <option value="content">内容创作</option>
                    <option value="analysis">数据分析</option>
                    <option value="research">研究项目</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)} className="flex-1">取消</Button>
                <Button type="submit" className="flex-1" disabled={creating}>
                  {creating ? '创建中...' : '创建'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// 添加缺失的 Card 组件
function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md ${className}`}>
      {children}
    </div>
  );
}

function CardHeader({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`px-6 py-4 border-b dark:border-gray-700 ${className}`}>{children}</div>;
}

function CardTitle({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <h3 className={`text-lg font-semibold ${className}`}>{children}</h3>;
}

function CardContent({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>;
}
