import React from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useProjectStore } from '../stores/project';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const { currentProject } = useProjectStore();
  
  const project = currentProject || {
    id: id || '',
    name: 'SaaS 应用开发',
    description: '构建一个现代化的 SaaS 应用',
    progress: 65,
    phase: 'executing',
    status: 'active'
  };
  
  const tasks = [
    { id: '1', title: '需求分析', status: 'completed', assignee: '项目经理' },
    { id: '2', title: '架构设计', status: 'completed', assignee: '架构师' },
    { id: '3', title: '前端开发', status: 'in_progress', assignee: '程序员' },
    { id: '4', title: '后端开发', status: 'in_progress', assignee: '程序员' },
    { id: '5', title: '测试', status: 'pending', assignee: '测试工程师' }
  ];
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">{project.name}</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">{project.description}</p>
        </div>
        <div className="flex gap-2">
          <Badge variant={project.phase === 'completed' ? 'success' : 'warning'}>{project.phase}</Badge>
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
            <span className="text-sm text-gray-600">整体进度</span>
            <span className="text-sm font-medium">{project.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div className="bg-blue-600 h-3 rounded-full transition-all" style={{ width: `${project.progress}%` }}></div>
          </div>
        </CardContent>
      </Card>
      
      {/* 任务列表 */}
      <Card>
        <CardHeader>
          <CardTitle>任务列表</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {tasks.map(task => (
              <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
                <div>
                  <p className="font-medium">{task.title}</p>
                  <p className="text-sm text-gray-500">负责人：{task.assignee}</p>
                </div>
                <Badge variant={task.status === 'completed' ? 'success' : task.status === 'in_progress' ? 'warning' : 'default'}>
                  {task.status}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
