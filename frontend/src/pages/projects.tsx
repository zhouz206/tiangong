import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ProjectCard } from '../components/cards';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Loading } from '../components/ui/loading';
import { useProjectStore, type Project } from '../stores/project';
import { projectApi } from '../utils/api';

export default function Projects() {
  const navigate = useNavigate();
  const { projects, setProjects, addProject, loading, setLoading, error, setError } = useProjectStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPhase, setFilterPhase] = useState('all');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [creating, setCreating] = useState(false);

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

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPhase = filterPhase === 'all' || project.phase === filterPhase;
    return matchesSearch && matchesPhase;
  });

  const phaseLabels: Record<string, string> = {
    planning: '规划中',
    executing: '执行中',
    reviewing: '审查中',
    completed: '已完成'
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">项目列表</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">管理你的所有项目</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadProjects} disabled={loading}>
            {loading ? '刷新中...' : '刷新'}
          </Button>
          <Button onClick={() => setCreateDialogOpen(true)} disabled={loading}>
            + 新建项目
          </Button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p className="text-yellow-600 dark:text-yellow-400">{error}</p>
        </div>
      )}

      {/* 搜索和筛选 */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Input
            placeholder="搜索项目..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
          <svg className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <select
          value={filterPhase}
          onChange={(e) => setFilterPhase(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white"
        >
          <option value="all">全部阶段</option>
          <option value="planning">规划中</option>
          <option value="executing">执行中</option>
          <option value="reviewing">审查中</option>
          <option value="completed">已完成</option>
        </select>
      </div>

      {/* 统计信息 */}
      <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
        <span>共 {filteredProjects.length} 个项目</span>
        {searchQuery && <span>• 搜索："{searchQuery}"</span>}
        {filterPhase !== 'all' && <span>• 筛选：{phaseLabels[filterPhase] || filterPhase}</span>}
        {projects.length > 0 && (
          <>
            <span>• 规划中：{projects.filter(p => p.phase === 'planning').length}</span>
            <span>• 执行中：{projects.filter(p => p.phase === 'executing').length}</span>
            <span>• 已完成：{projects.filter(p => p.phase === 'completed').length}</span>
          </>
        )}
      </div>

      {/* 项目列表 */}
      {loading && projects.length === 0 ? (
        <div className="text-center py-12">
          <Loading size="lg" text="加载项目中..." />
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <p className="text-gray-600 dark:text-gray-400">
            {searchQuery || filterPhase !== 'all' ? '没有找到匹配的项目' : '暂无项目'}
          </p>
          {!searchQuery && filterPhase === 'all' && (
            <Button className="mt-4" onClick={() => setCreateDialogOpen(true)}>创建第一个项目</Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map(project => (
            <ProjectCard
              key={project.id}
              id={project.id}
              name={project.name}
              description={project.description}
              progress={project.progress}
              phase={project.phase}
              status={project.status}
              onClick={() => navigate(`/projects/${project.id}`)}
            />
          ))}
        </div>
      )}

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
