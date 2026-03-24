import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { StatCard, ProjectCard } from '../components/cards';
import { Button } from '../components/ui/button';
import { useProjectStore } from '../stores/project';
import { projectApi } from '../utils/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { projects, setProjects, loading, error } = useProjectStore();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  
  // 加载项目数据
  React.useEffect(() => {
    loadProjects();
  }, []);
  
  const loadProjects = async () => {
    try {
      const data = await projectApi.list();
      setProjects(data.projects || []);
    } catch (err) {
      console.error('加载项目失败:', err);
      // 使用 mock 数据降级
      setProjects([
        { id: '1', name: 'SaaS 应用开发', description: '构建现代化的 SaaS 应用', progress: 75, phase: 'executing', status: 'active' },
        { id: '2', name: '技术博客系列', description: 'AI Agent 开发教程', progress: 50, phase: 'planning', status: 'active' },
      ]);
    }
  };
  
  const stats = {
    totalProjects: projects.length,
    activeProjects: projects.filter(p => p.status === 'active').length,
    completedProjects: projects.filter(p => p.phase === 'completed').length,
    totalTasks: 156
  };
  
  return (
    <div className="space-y-8">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">仪表盘</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">欢迎回来，这是你的项目概览</p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)} disabled={loading}>
          {loading ? '加载中...' : '+ 新建项目'}
        </Button>
      </div>
      
      {/* 错误提示 */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}
      
      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="总项目数" value={stats.totalProjects} change="+2 本月" />
        <StatCard title="进行中" value={stats.activeProjects} />
        <StatCard title="已完成" value={stats.completedProjects} />
        <StatCard title="总任务数" value={stats.totalTasks} />
      </div>
      
      {/* 最近项目 */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">最近项目</h2>
          <Button variant="outline" onClick={() => navigate('/projects')}>
            查看全部 →
          </Button>
        </div>
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600 dark:text-gray-400">加载中...</p>
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
            <form onSubmit={async (e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              try {
                const newProject = await projectApi.create({
                  name: formData.get('name'),
                  description: formData.get('description'),
                  template: formData.get('template') || 'software'
                });
                setProjects([...projects, newProject]);
                setCreateDialogOpen(false);
                navigate(`/projects/${newProject.id}`);
              } catch (err) {
                alert('创建失败：' + err.message);
              }
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">项目名称</label>
                  <input name="name" required className="w-full px-3 py-2 border rounded-md dark:bg-gray-700" placeholder="我的项目" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">描述</label>
                  <textarea name="description" className="w-full px-3 py-2 border rounded-md dark:bg-gray-700" placeholder="项目描述..." />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">模板</label>
                  <select name="template" className="w-full px-3 py-2 border rounded-md dark:bg-gray-700">
                    <option value="software">软件开发</option>
                    <option value="content">内容创作</option>
                    <option value="analysis">数据分析</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)} className="flex-1">取消</Button>
                <Button type="submit" className="flex-1" disabled={loading}>创建</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
