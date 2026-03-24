import React from 'react';
import { AgentCard } from '../components/cards';
import { useAgentStore } from '../stores/agent';

export default function Agents() {
  const { agents } = useAgentStore();
  
  const defaultAgents = [
    { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle' as const, description: '协调进度、需求澄清、回顾总结' },
    { id: '2', role: '研究员', name: '研究员 Agent', status: 'working' as const, description: '信息搜集、分析整理' },
    { id: '3', role: '程序员', name: '程序员 Agent', status: 'working' as const, description: '代码编写、调试、测试' },
    { id: '4', role: '设计师', name: '设计师 Agent', status: 'idle' as const, description: 'UI/UX 设计、原型制作' },
    { id: '5', role: '文案', name: '文案 Agent', status: 'idle' as const, description: '内容撰写、编辑、校对' },
    { id: '6', role: '审核员', name: '审核员 Agent', status: 'blocked' as const, description: '质量检查、代码审查' },
    { id: '7', role: '数据分析师', name: '数据分析师 Agent', status: 'idle' as const, description: '数据处理、可视化' },
    { id: '8', role: '知识管理员', name: '知识管理员 Agent', status: 'idle' as const, description: '文档整理、知识归档' }
  ];
  
  const agentList = agents.length > 0 ? agents : defaultAgents;
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Agent 管理</h1>
        <Button>配置 Agent</Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agentList.map(agent => (
          <AgentCard key={agent.id} {...agent} />
        ))}
      </div>
    </div>
  );
}

// 占位 Button 组件
function Button({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <button className={`px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 ${className}`}>
      {children}
    </button>
  );
}
