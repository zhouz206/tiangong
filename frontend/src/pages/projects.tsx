import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ProjectCard } from '../components/cards';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { useProjectStore } from '../stores/project';

// Mock 数据
const mockProjects = [
  { id: '1', name: 'SaaS 应用开发', description: '构建现代化的 SaaS 应用，包括前端、后端和数据库设计', progress: 75, phase: 'executing', status: 'active' },
  { id: '2', name: '技术博客系列', description: 'AI Agent 开发教程，共 10 篇', progress: 30, phase: 'planning', status: 'active' },
  { id: '3', name: '数据分析平台', description: '数据可视化和分析平台', progress: 100, phase: 'completed', status: 'completed' },
  { id: '4', name: '移动应用开发', description: 'iOS 和 Android 跨平台应用', progress: 60, phase: 'executing', status: 'active' },
  { id: '5', name: 'API 网关', description: '微服务 API 网关开发', progress: 45, phase: 'executing', status: 'active' },
];

export default function Projects() {
  const navigate = useNavigate();
  const { projects, setProjects } = useProjectStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPhase, setFilterPhase] = useState('all');
  
  // 初始化 mock 数据
  React.useEffect(() => {
    if (projects.length === 0) {
      setProjects(mockProjects);
    }
  }, []);
  
  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPhase = filterPhase === 'all' || project.phase === filterPhase;
    return matchesSearch && matchesPhase;
  });
  
  const phaseOptions = [
    { value: 'all', label: '全部阶段' },
    { value: 'planning', label: '规划中' },
    { value: 'executing', label: '执行中' },
    { value: 'reviewing', label: '审查中' },
    { value: 'completed', label: '已完成' }
  ];
  
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">项目列表</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">管理你的所有项目</p>
        </div>
        <Button onClick={() => navigate('/projects/new')}>
          + 新建项目
        </Button>
      </div>
      
      {/* 搜索和筛选 */}
      <div className="flex flex-col md:flex-row gap-4">
        <Input
          placeholder="搜索项目..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          }
        />
        <select
          value={filterPhase}
          onChange={(e) => setFilterPhase(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white"
        >
          {phaseOptions.map(option => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
      </div>
      
      {/* 统计信息 */}
      <div className="flex gap-4 text-sm text-gray-600 dark:text-gray-400">
        <span>共 {filteredProjects.length} 个项目</span>
        {searchQuery && <span>• 搜索："{searchQuery}"</span>}
        {filterPhase !== 'all' && <span>• 筛选：{filterPhase}</span>}
      </div>
      
      {/* 项目列表 */}
      {filteredProjects.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <svg className="w-16 h-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
          <p className="mt-4 text-gray-600 dark:text-gray-400">暂无项目</p>
          <Button className="mt-4" onClick={() => navigate('/projects/new')}>
            创建第一个项目
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map(project => (
            <ProjectCard 
              key={project.id} 
              {...project}
              onClick={() => navigate(`/projects/${project.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
