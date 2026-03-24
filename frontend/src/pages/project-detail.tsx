import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useProjectStore } from '../stores/project';

// Mock 数据
const mockProject = {
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
  const { currentProject, setCurrentProject } = useProjectStore();
  
  const project = currentProject || mockProject;
  
  React.useEffect(() => {
    setCurrentProject(project);
  }, []);
  
  const getStatusColor = (status: string) => {
    const colors: Record<string, 'default' | 'success' | 'warning' | 'error'> = {
      completed: 'success',
      in_progress: 'warning',
      pending: 'default',
      blocked: 'error'
    };
    return colors[status] || 'default';
  };
  
  const getPhaseColor = (phase: string) => {
    const colors: Record<string, 'default' | 'success' | 'warning'> = {
      planning: 'default',
      executing: 'warning',
      reviewing: 'warning',
      completed: 'success'
    };
    return colors[phase] || 'default';
  };
  
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => navigate('/projects')}>
              ← 返回
            </Button>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{project.name}</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2 ml-14">{project.description}</p>
        </div>
        <div className="flex gap-2">
          <Badge variant={getPhaseColor(project.phase)}>{project.phase}</Badge>
          <Button variant="outline">编辑</Button>
        </div>
      </div>
      
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
          <div className="mt-4 grid grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {project.milestones?.filter(m => m.status === 'completed').length}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">已完成里程碑</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {project.tasks?.filter(t => t.status === 'completed').length}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">已完成任务</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {project.tasks?.filter(t => t.status === 'in_progress').length}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">进行中任务</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {project.tasks?.filter(t => t.status === 'pending').length}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">待处理任务</p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* 里程碑 */}
      <Card>
        <CardHeader>
          <CardTitle>里程碑</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {project.milestones?.map(milestone => (
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
      
      {/* 任务列表 */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>任务列表</CardTitle>
            <Button size="sm">+ 添加任务</Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {project.tasks?.map(task => (
              <div 
                key={task.id} 
                className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    task.status === 'completed' ? 'bg-green-600' :
                    task.status === 'in_progress' ? 'bg-yellow-600' :
                    'bg-gray-400'
                  }`} />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{task.title}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">负责人：{task.assignee}</p>
                  </div>
                </div>
                <Badge variant={getStatusColor(task.status)}>{task.status}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
