import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Loading } from '../components/ui/loading';
import { useProjectStore, type Project } from '../stores/project';
import { projectApi } from '../utils/api';

// Mock 数据用于降级
const mockProject: Project = {
  id: '1',
  name: 'SaaS 应用开发',
  description: '构建一个现代化的 SaaS 应用，包括前端、后端和数据库设计',
  progress: 65,
  phase: 'executing',
  status: 'active',
  created_at: '2026-03-01',
  milestones: [
    { id: 'm1', name: 'M1 核心引擎', progress: 100, status: 'completed' },
    { id: 'm2', name: 'M2 模型集成', progress: 100, status: 'completed' },
    { id: 'm3', name: 'M3 Agent 能力', progress: 80, status: 'active' },
    { id: 'm4', name: 'M4 知识库', progress: 50, status: 'active' },
  ],
  tasks: [
    { id: '1', title: '需求分析', status: 'completed', assignee: '项目经理' },
    { id: '2', title: '架构设计', status: 'completed', assignee: '架构师' },
    { id: '3', title: '前端开发', status: 'in_progress', assignee: '程序员' },
    { id: '4', title: '后端开发', status: 'in_progress', assignee: '程序员' },
    { id: '5', title: '测试', status: 'pending', assignee: '测试工程师' },
  ]
};

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentProject, setCurrentProject, updateProject, updateProjectProgress, updateProjectPhase } = useProjectStore();

  const [project, setProject] = useState<Project>(currentProject || mockProject);
  const [loading, setLoading] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [taskDialogOpen, setTaskDialogOpen] = useState(false);
  const [phaseDialogOpen, setPhaseDialogOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    if (id) {
      loadProject(id);
    }
    return () => {
      if (currentProject?.id !== id) {
        setCurrentProject(null);
      }
    };
  }, [id]);

  const loadProject = async (projectId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await projectApi.get(projectId);
      const loadedProject = data.project || data;
      setProject(loadedProject);
      setCurrentProject(loadedProject);
    } catch (err) {
      console.error('加载项目失败:', err);
      setError('加载项目失败，使用本地数据');
      if (currentProject?.id === projectId) {
        setProject(currentProject);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEditProject = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    try {
      const updatedData = {
        name: formData.get('name') as string,
        description: formData.get('description') as string
      };
      await projectApi.update(project.id, updatedData);
      updateProject(project.id, updatedData);
      setProject({ ...project, ...updatedData });
      setEditDialogOpen(false);
    } catch (err) {
      updateProject(project.id, { name: formData.get('name') as string, description: formData.get('description') as string });
      setProject({ ...project, name: formData.get('name') as string, description: formData.get('description') as string });
      setEditDialogOpen(false);
    }
  };

  const handleAddTask = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const newTask = {
      id: `task-${Date.now()}`,
      title: formData.get('title') as string,
      status: 'pending',
      assignee: formData.get('assignee') as string
    };

    try {
      // API 调用（失败时降级）
      await projectApi.update(project.id, { tasks: [...(project.tasks || []), newTask] });
    } catch (err) {
      console.error('添加任务失败:', err);
    }

    // 更新本地状态
    const updatedTasks = [...(project.tasks || []), newTask];
    const updatedProject = { ...project, tasks: updatedTasks };
    updateProject(project.id, { tasks: updatedTasks });
    setProject(updatedProject);
    setTaskDialogOpen(false);
  };

  const handleTaskStatusChange = async (taskId: string, newStatus: string) => {
    const task = project.tasks?.find(t => t.id === taskId);
    if (!task) return;

    try {
      await projectApi.updateTaskStatus(project.id, taskId, newStatus);
    } catch (err) {
      console.error('更新任务状态失败:', err);
    }

    // 更新本地状态
    const updatedTasks = project.tasks?.map(t =>
      t.id === taskId ? { ...t, status: newStatus } : t
    );

    // 计算新的进度
    const completedCount = updatedTasks?.filter(t => t.status === 'completed').length || 0;
    const newProgress = Math.round((completedCount / (updatedTasks?.length || 1)) * 100);

    const updatedProject = { ...project, tasks: updatedTasks, progress: newProgress };
    updateProject(project.id, { tasks: updatedTasks, progress: newProgress });
    updateProjectProgress(project.id, newProgress);
    setProject(updatedProject);
  };

  const handlePhaseChange = async (newPhase: Project['phase']) => {
    try {
      await projectApi.updatePhase(project.id, newPhase);
    } catch (err) {
      console.error('更新阶段失败:', err);
    }

    updateProjectPhase(project.id, newPhase);
    updateProject(project.id, { phase: newPhase });
    setProject({ ...project, phase: newPhase });
    setPhaseDialogOpen(false);
  };

  const getStatusColor = (status: string): 'default' | 'success' | 'warning' | 'error' => {
    const colors: Record<string, 'default' | 'success' | 'warning' | 'error'> = {
      completed: 'success',
      in_progress: 'warning',
      pending: 'default',
      blocked: 'error'
    };
    return colors[status] || 'default';
  };

  const getPhaseColor = (phase: string): 'default' | 'success' | 'warning' => {
    const colors: Record<string, 'default' | 'success' | 'warning'> = {
      planning: 'default',
      executing: 'warning',
      reviewing: 'warning',
      completed: 'success'
    };
    return colors[phase] || 'default';
  };

  if (loading && !project) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="加载项目中..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-start flex-wrap gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <Button variant="outline" onClick={() => navigate('/projects')}>
              ← 返回
            </Button>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{project.name}</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2 ml-14">{project.description}</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Badge variant={getPhaseColor(project.phase)}>{project.phase}</Badge>
          <Button variant="outline" onClick={() => setPhaseDialogOpen(true)}>切换阶段</Button>
          <Button variant="outline" onClick={() => setEditDialogOpen(true)}>编辑</Button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p className="text-yellow-600 dark:text-yellow-400">{error}</p>
        </div>
      )}

      {/* 进度条 */}
      <Card>
        <CardHeader>
          <CardTitle>项目进度</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">整体进度</span>
            <span className="text-sm font-bold text-blue-600">{project.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
            <div
              className="bg-blue-600 h-4 rounded-full transition-all duration-500"
              style={{ width: `${project.progress}%` }}
            ></div>
          </div>
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {project.milestones?.filter(m => m.status === 'completed').length || 0}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">已完成里程碑</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {project.tasks?.filter(t => t.status === 'completed').length || 0}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">已完成任务</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {project.tasks?.filter(t => t.status === 'in_progress').length || 0}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">进行中任务</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {project.tasks?.filter(t => t.status === 'pending').length || 0}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">待处理任务</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 里程碑 */}
      {project.milestones && project.milestones.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>里程碑</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {project.milestones.map(milestone => (
                <div key={milestone.id} className="flex items-center gap-4">
                  <div className="w-32 text-sm font-medium text-gray-900 dark:text-white">
                    {milestone.name}
                  </div>
                  <div className="flex-1">
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          milestone.status === 'completed' ? 'bg-green-600' : 'bg-blue-600'
                        }`}
                        style={{ width: `${milestone.progress}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="w-16 text-right text-sm text-gray-600 dark:text-gray-400">
                    {milestone.progress}%
                  </div>
                  <Badge variant={milestone.status === 'completed' ? 'success' : 'warning'}>
                    {milestone.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 任务列表 */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>任务列表</CardTitle>
            <Button size="sm" onClick={() => setTaskDialogOpen(true)}>+ 添加任务</Button>
          </div>
        </CardHeader>
        <CardContent>
          {project.tasks && project.tasks.length > 0 ? (
            <div className="space-y-3">
              {project.tasks.map(task => (
                <div
                  key={task.id}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1">
                    <button
                      onClick={() => handleTaskStatusChange(task.id, task.status === 'completed' ? 'pending' : 'completed')}
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                        task.status === 'completed' ? 'bg-green-600 border-green-600' :
                        task.status === 'in_progress' ? 'border-yellow-600' :
                        'border-gray-400'
                      }`}
                    >
                      {task.status === 'completed' && (
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                    <div>
                      <p className={`font-medium ${
                        task.status === 'completed' ? 'text-gray-500 line-through' : 'text-gray-900 dark:text-white'
                      }`}>
                        {task.title}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">负责人：{task.assignee || '未分配'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <select
                      value={task.status}
                      onChange={(e) => handleTaskStatusChange(task.id, e.target.value)}
                      className="text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-700"
                    >
                      <option value="pending">待处理</option>
                      <option value="in_progress">进行中</option>
                      <option value="completed">已完成</option>
                      <option value="blocked">已阻塞</option>
                    </select>
                    <Badge variant={getStatusColor(task.status)}>{task.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-600 dark:text-gray-400">
              暂无任务，点击"添加任务"创建第一个任务
            </div>
          )}
        </CardContent>
      </Card>

      {/* 编辑项目对话框 */}
      {editDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">编辑项目</h2>
            <form onSubmit={handleEditProject}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">项目名称</label>
                  <input
                    name="name"
                    required
                    defaultValue={project.name}
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">描述</label>
                  <textarea
                    name="description"
                    defaultValue={project.description}
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    rows={3}
                  />
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)} className="flex-1">取消</Button>
                <Button type="submit" className="flex-1">保存</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 添加任务对话框 */}
      {taskDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">添加任务</h2>
            <form onSubmit={handleAddTask}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">任务标题</label>
                  <input
                    name="title"
                    required
                    placeholder="输入任务标题"
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">负责人</label>
                  <input
                    name="assignee"
                    placeholder="输入负责人"
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button type="button" variant="outline" onClick={() => setTaskDialogOpen(false)} className="flex-1">取消</Button>
                <Button type="submit" className="flex-1">添加</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 切换阶段对话框 */}
      {phaseDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">切换项目阶段</h2>
            <div className="space-y-2">
              {(['planning', 'executing', 'reviewing', 'completed'] as const).map(phase => (
                <button
                  key={phase}
                  onClick={() => handlePhaseChange(phase)}
                  className={`w-full p-4 text-left rounded-lg border-2 transition-colors ${
                    project.phase === phase
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {phase === 'planning' && '📋 规划中'}
                      {phase === 'executing' && '⚙️ 执行中'}
                      {phase === 'reviewing' && '🔍 审查中'}
                      {phase === 'completed' && '✅ 已完成'}
                    </span>
                    {project.phase === phase && (
                      <Badge variant="success">当前</Badge>
                    )}
                  </div>
                </button>
              ))}
            </div>
            <div className="mt-6">
              <Button variant="outline" onClick={() => setPhaseDialogOpen(false)} className="w-full">取消</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
