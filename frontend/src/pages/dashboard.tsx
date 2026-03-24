import React from 'react';
import { StatCard, ProjectCard } from '../components/cards';
import { Button } from '../components/ui/button';
import { useProjectStore } from '../stores/project';

export default function Dashboard() {
  const { projects } = useProjectStore();
  
  const stats = {
    totalProjects: projects.length,
    activeProjects: projects.filter(p => p.status === 'active').length,
    completedProjects: projects.filter(p => p.phase === 'completed').length,
    totalTasks: 156
  };
  
  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">仪表盘</h1>
        <Button>新建项目</Button>
      </div>
      
      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="总项目数" value={stats.totalProjects} change="+2 本月" />
        <StatCard title="进行中" value={stats.activeProjects} />
        <StatCard title="已完成" value={stats.completedProjects} />
        <StatCard title="总任务数" value={stats.totalTasks} />
      </div>
      
      {/* 最近项目 */}
      <div>
        <h2 className="text-xl font-semibold mb-4">最近项目</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.slice(0, 6).map(project => (
            <ProjectCard key={project.id} {...project} />
          ))}
        </div>
      </div>
      
      {/* 快速操作 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">快速操作</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button variant="outline">新建项目</Button>
          <Button variant="outline">查看 Agent</Button>
          <Button variant="outline">知识库</Button>
          <Button variant="outline">设置</Button>
        </div>
      </div>
    </div>
  );
}
