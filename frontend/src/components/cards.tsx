import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  icon?: React.ReactNode;
}

export function StatCard({ title, value, change, icon }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {change}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

interface ProjectCardProps {
  id: string;
  name: string;
  description: string;
  progress: number;
  phase: string;
  status: string;
  onClick?: () => void;
}

export function ProjectCard({ name, description, progress, phase, onClick }: ProjectCardProps) {
  const phaseColors: Record<string, 'default' | 'success' | 'warning'> = {
    planning: 'default',
    executing: 'warning',
    reviewing: 'warning',
    completed: 'success'
  };

  const handleClick = () => {
    if (onClick) onClick();
  };

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={handleClick}>
      <CardHeader>
        <CardTitle>{name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{description}</p>
        <div className="flex items-center justify-between">
          <Badge variant={phaseColors[phase] || 'default'}>{phase}</Badge>
          <span className="text-sm text-gray-500">{progress}%</span>
        </div>
        <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </CardContent>
    </Card>
  );
}

interface AgentCardProps {
  role: string;
  name: string;
  status: 'idle' | 'working' | 'blocked';
  description: string;
}

export function AgentCard({ role, name, status, description }: AgentCardProps) {
  const statusColors: Record<string, 'default' | 'success' | 'error'> = {
    idle: 'default',
    working: 'success',
    blocked: 'error'
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{name}</CardTitle>
          <Badge variant={statusColors[status]}>{status}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 dark:text-gray-400">{role}</p>
        <p className="text-sm mt-2">{description}</p>
      </CardContent>
    </Card>
  );
}
