import React, { useState } from 'react';
import { ProjectCard } from '../components/cards';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useProjectStore } from '../stores/project';

export default function Projects() {
  const { projects } = useProjectStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPhase, setFilterPhase] = useState('all');
  
  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPhase = filterPhase === 'all' || project.phase === filterPhase;
    return matchesSearch && matchesPhase;
  });
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">项目列表</h1>
        <Button>新建项目</Button>
      </div>
      
      {/* 搜索和筛选 */}
      <div className="flex flex-col md:flex-row gap-4">
        <Input
          placeholder="搜索项目..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1"
        />
        <select
          value={filterPhase}
          onChange={(e) => setFilterPhase(e.target.value)}
          className="px-4 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
        >
          <option value="all">全部阶段</option>
          <option value="planning">规划中</option>
          <option value="executing">执行中</option>
          <option value="reviewing">审查中</option>
          <option value="completed">已完成</option>
        </select>
      </div>
      
      {/* 项目列表 */}
      {filteredProjects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">暂无项目</p>
          <Button className="mt-4">创建第一个项目</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map(project => (
            <ProjectCard key={project.id} {...project} />
          ))}
        </div>
      )}
    </div>
  );
}
