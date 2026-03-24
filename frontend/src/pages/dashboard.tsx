import React from 'react';
import { useNavigate } from 'react-router-dom';
import { StatCard, ProjectCard } from '../components/cards';
import { Button } from '../components/ui/button';
import { useProjectStore } from '../stores/project';

// Mock 数据
const mockProjects = [
  { id: '1', name: 'SaaS 应用开发', description: '构建现代化的 SaaS 应用', progress: 75, phase: 'executing', status: 'active' },
  { id: '2', name: '技术博客系列', description: 'AI Agent 开发教程', progress: 50, phase: 'planning', status: 'active' },
  { id: '3', name: '数据分析平台', description: '数据可视化和分析', progress: 100, phase: 'completed', status: 'completed' },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const { projects, setProjects } = useProjectStore();
  
  // 初始化 mock 数据
  React.useEffect(() => {
    if (projects.length === 0) {
      setProjects(mockProjects);
    }
  }, []);
  
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
        <Button onClick={() => navigate('/projects/new')}>
          + 新建项目
        </Button>
      </div>
      
      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="总项目数" 
          value={stats.totalProjects} 
          change="+2 本月"
          icon={
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
          }
        />
        <StatCard 
          title="进行中" 
          value={stats.activeProjects}
          icon={
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
        />
        <StatCard 
          title="已完成" 
          value={stats.completedProjects}
          icon={
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <StatCard 
          title="总任务数" 
          value={stats.totalTasks}
          change="12 待处理"
          icon={
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          }
        />
      </div>
      
      {/* 最近项目 */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">最近项目</h2>
          <Button variant="outline" onClick={() => navigate('/projects')}>
            查看全部 →
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.slice(0, 6).map(project => (
            <ProjectCard 
              key={project.id} 
              {...project}
              onClick={() => navigate(`/projects/${project.id}`)}
            />
          ))}
        </div>
      </div>
      
      {/* 快速操作 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">快速操作</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button variant="outline" onClick={() => navigate('/projects/new')}>
            📁 新建项目
          </Button>
          <Button variant="outline" onClick={() => navigate('/agents')}>
            🤖 查看 Agent
          </Button>
          <Button variant="outline" onClick={() => navigate('/knowledge')}>
            📚 知识库
          </Button>
          <Button variant="outline" onClick={() => navigate('/settings')}>
            ⚙️ 设置
          </Button>
        </div>
      </div>
    </div>
  );
}
