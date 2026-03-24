import React from 'react';
import { AgentCard } from '../components/cards';
import { Button } from '../components/ui/button';
import { useAgentStore } from '../stores/agent';

// Mock 数据
const mockAgents = [
  { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle' as const, description: '协调进度、需求澄清、回顾总结', skills: ['需求分析', '任务分配', '进度跟踪'] },
  { id: '2', role: '研究员', name: '研究员 Agent', status: 'working' as const, description: '信息搜集、分析整理', skills: ['信息检索', '数据分析', '报告生成'] },
  { id: '3', role: '程序员', name: '程序员 Agent', status: 'working' as const, description: '代码编写、调试、测试', skills: ['Python', 'JavaScript', '代码审查'] },
  { id: '4', role: '设计师', name: '设计师 Agent', status: 'idle' as const, description: 'UI/UX 设计、原型制作', skills: ['UI 设计', '原型设计', '用户研究'] },
  { id: '5', role: '文案', name: '文案 Agent', status: 'idle' as const, description: '内容撰写、编辑、校对', skills: ['技术写作', '编辑', '校对'] },
  { id: '6', role: '审核员', name: '审核员 Agent', status: 'blocked' as const, description: '质量检查、代码审查', skills: ['代码审查', '质量检查', '安全审计'] },
  { id: '7', role: '数据分析师', name: '数据分析师 Agent', status: 'idle' as const, description: '数据处理、可视化', skills: ['数据分析', '数据可视化', '统计分析'] },
  { id: '8', role: '知识管理员', name: '知识管理员 Agent', status: 'idle' as const, description: '文档整理、知识归档', skills: ['知识管理', '文档分类', '语义搜索'] },
];

export default function Agents() {
  const { agents, setAgents } = useAgentStore();
  
  React.useEffect(() => {
    if (agents.length === 0) {
      setAgents(mockAgents);
    }
  }, []);
  
  const agentList = agents.length > 0 ? agents : mockAgents;
  
  const statusCounts = {
    idle: agentList.filter(a => a.status === 'idle').length,
    working: agentList.filter(a => a.status === 'working').length,
    blocked: agentList.filter(a => a.status === 'blocked').length,
  };
  
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Agent 管理</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">管理你的 AI Agent 团队</p>
        </div>
        <Button>配置 Agent</Button>
      </div>
      
      {/* 统计信息 */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-400">空闲</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{statusCounts.idle}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">工作中</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{statusCounts.working}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">阻塞</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{statusCounts.blocked}</p>
        </div>
      </div>
      
      {/* Agent 列表 */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Agent 团队</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agentList.map(agent => (
            <AgentCard key={agent.id} {...agent} />
          ))}
        </div>
      </div>
    </div>
  );
}
