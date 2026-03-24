import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Loading } from '../components/ui/loading';
import { useAgentStore, type Agent } from '../stores/agent';
import { agentApi } from '../utils/api';

// Mock 数据用于降级
const mockAgents: Agent[] = [
  { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle', description: '协调进度、需求澄清、回顾总结', skills: ['需求分析', '任务分配', '进度跟踪'] },
  { id: '2', role: '研究员', name: '研究员 Agent', status: 'working', description: '信息搜集、分析整理', skills: ['信息检索', '数据分析', '报告生成'] },
  { id: '3', role: '程序员', name: '程序员 Agent', status: 'working', description: '代码编写、调试、测试', skills: ['Python', 'JavaScript', '代码审查'] },
  { id: '4', role: '设计师', name: '设计师 Agent', status: 'idle', description: 'UI/UX 设计、原型制作', skills: ['UI 设计', '原型设计', '用户研究'] },
  { id: '5', role: '文案', name: '文案 Agent', status: 'idle', description: '内容撰写、编辑、校对', skills: ['技术写作', '编辑', '校对'] },
  { id: '6', role: '审核员', name: '审核员 Agent', status: 'blocked', description: '质量检查、代码审查', skills: ['代码审查', '质量检查', '安全审计'] },
  { id: '7', role: '数据分析师', name: '数据分析师 Agent', status: 'idle', description: '数据处理、可视化', skills: ['数据分析', '数据可视化', '统计分析'] },
  { id: '8', role: '知识管理员', name: '知识管理员 Agent', status: 'idle', description: '文档整理、知识归档', skills: ['知识管理', '文档分类', '语义搜索'] },
];

export default function Agents() {
  const { agents, setAgents, updateAgentStatus } = useAgentStore();
  const [loading, setLoading] = useState(false);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [assignTaskDialogOpen, setAssignTaskDialogOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await agentApi.list();
      setAgents(data.agents || data);
    } catch (err) {
      console.error('加载 Agent 失败:', err);
      setError('加载失败，使用本地数据');
      if (agents.length === 0) {
        setAgents(mockAgents);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleConfigureAgent = (agent: Agent) => {
    setSelectedAgent(agent);
    setConfigDialogOpen(true);
  };

  const handleAssignTask = (agent: Agent) => {
    setSelectedAgent(agent);
    setAssignTaskDialogOpen(true);
  };

  const handleSaveConfig = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedAgent) return;

    const formData = new FormData(e.currentTarget);
    const config = {
      name: formData.get('name') as string,
      enabled: formData.get('enabled') === 'on',
      maxConcurrentTasks: Number(formData.get('maxConcurrentTasks')),
      autoAssign: formData.get('autoAssign') === 'on'
    };

    try {
      await agentApi.configure(selectedAgent.id, config);
    } catch (err) {
      console.error('保存配置失败:', err);
    }

    // 更新本地状态
    updateAgentStatus(selectedAgent.id, selectedAgent.status);
    setConfigDialogOpen(false);
    setSelectedAgent(null);
  };

  const handleAssignTaskSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedAgent) return;

    const formData = new FormData(e.currentTarget);
    const task = {
      title: formData.get('title') as string,
      description: formData.get('description') as string,
      priority: formData.get('priority') as string
    };

    try {
      await agentApi.executeTask(selectedAgent.id, task);
    } catch (err) {
      console.error('分配任务失败:', err);
    }

    // 更新状态为 working
    updateAgentStatus(selectedAgent.id, 'working');
    setAssignTaskDialogOpen(false);
    setSelectedAgent(null);
  };

  const handleStatusChange = (agentId: string, newStatus: Agent['status']) => {
    updateAgentStatus(agentId, newStatus);
  };

  const agentList = agents.length > 0 ? agents : mockAgents;

  const statusCounts = {
    idle: agentList.filter(a => a.status === 'idle').length,
    working: agentList.filter(a => a.status === 'working').length,
    blocked: agentList.filter(a => a.status === 'blocked').length,
  };

  if (loading && agents.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="加载 Agent..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Agent 管理</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">管理你的 AI Agent 团队</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadAgents} disabled={loading}>
            {loading ? '刷新中...' : '刷新'}
          </Button>
          <Button onClick={() => setConfigDialogOpen(true)}>配置 Agent</Button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p className="text-yellow-600 dark:text-yellow-400">{error}</p>
        </div>
      )}

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
            <Card key={agent.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{agent.name}</CardTitle>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{agent.role}</p>
                  </div>
                  <Badge variant={agent.status === 'working' ? 'success' : agent.status === 'blocked' ? 'error' : 'default'}>
                    {agent.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">{agent.description}</p>

                {agent.skills && agent.skills.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-500 mb-2">技能</p>
                    <div className="flex flex-wrap gap-1">
                      {agent.skills.map(skill => (
                        <span key={skill} className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-2 pt-2 border-t dark:border-gray-700">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 text-xs"
                    onClick={() => handleConfigureAgent(agent)}
                  >
                    配置
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 text-xs"
                    onClick={() => handleAssignTask(agent)}
                    disabled={agent.status === 'blocked'}
                  >
                    分配任务
                  </Button>
                </div>

                <div className="flex gap-2 pt-2 border-t dark:border-gray-700">
                  <select
                    value={agent.status}
                    onChange={(e) => handleStatusChange(agent.id, e.target.value as Agent['status'])}
                    className="w-full text-xs px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600"
                  >
                    <option value="idle">空闲</option>
                    <option value="working">工作中</option>
                    <option value="blocked">阻塞</option>
                  </select>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* 配置 Agent 对话框 */}
      {configDialogOpen && !selectedAgent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">配置 Agent</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">选择一个 Agent 进行配置</p>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {agentList.map(agent => (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent)}
                  className="w-full p-3 text-left rounded-lg border hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{agent.name}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{agent.role}</p>
                  </div>
                  <Badge variant={agent.status === 'working' ? 'success' : agent.status === 'blocked' ? 'error' : 'default'}>
                    {agent.status}
                  </Badge>
                </button>
              ))}
            </div>
            <div className="mt-6">
              <Button variant="outline" onClick={() => setConfigDialogOpen(false)} className="w-full">取消</Button>
            </div>
          </div>
        </div>
      )}

      {/* 单个 Agent 配置对话框 */}
      {configDialogOpen && selectedAgent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">配置 {selectedAgent.name}</h2>
            <form onSubmit={handleSaveConfig}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">名称</label>
                  <input
                    name="name"
                    defaultValue={selectedAgent.name}
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">最大并发任务数</label>
                  <input
                    name="maxConcurrentTasks"
                    type="number"
                    min="1"
                    max="10"
                    defaultValue="3"
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    name="enabled"
                    type="checkbox"
                    defaultChecked
                    id="enabled"
                    className="w-4 h-4"
                  />
                  <label htmlFor="enabled" className="text-sm text-gray-700 dark:text-gray-300">启用 Agent</label>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    name="autoAssign"
                    type="checkbox"
                    defaultChecked
                    id="autoAssign"
                    className="w-4 h-4"
                  />
                  <label htmlFor="autoAssign" className="text-sm text-gray-700 dark:text-gray-300">自动分配任务</label>
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button type="button" variant="outline" onClick={() => {
                  setConfigDialogOpen(false);
                  setSelectedAgent(null);
                }} className="flex-1">取消</Button>
                <Button type="submit" className="flex-1">保存</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 分配任务对话框 */}
      {assignTaskDialogOpen && selectedAgent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">分配任务给 {selectedAgent.name}</h2>
            <form onSubmit={handleAssignTaskSubmit}>
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
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">任务描述</label>
                  <textarea
                    name="description"
                    placeholder="详细描述任务内容"
                    rows={3}
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">优先级</label>
                  <select
                    name="priority"
                    defaultValue="medium"
                    className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="low">低</option>
                    <option value="medium">中</option>
                    <option value="high">高</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button type="button" variant="outline" onClick={() => {
                  setAssignTaskDialogOpen(false);
                  setSelectedAgent(null);
                }} className="flex-1">取消</Button>
                <Button type="submit" className="flex-1">分配</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
