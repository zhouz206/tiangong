/** @vitest-environment jsdom */
import { test, expect, beforeEach } from 'vitest';
import { useAgentStore, type Agent } from './agent';

beforeEach(() => {
  useAgentStore.setState({
    agents: [],
    loading: false,
    error: null,
  });
});

test('Agent Store - 初始状态', () => {
  const state = useAgentStore.getState();
  expect(state.agents).toEqual([]);
  expect(state.loading).toBe(false);
  expect(state.error).toBeNull();
});

test('Agent Store - setAgents', () => {
  const mockAgents: Agent[] = [
    { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle', description: '描述 1' },
    { id: '2', role: '程序员', name: '程序员 Agent', status: 'working', description: '描述 2' },
  ];

  useAgentStore.getState().setAgents(mockAgents);

  const state = useAgentStore.getState();
  expect(state.agents).toEqual(mockAgents);
  expect(state.error).toBeNull();
});

test('Agent Store - addAgent', () => {
  useAgentStore.getState().setAgents([
    { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle', description: '描述 1' },
  ]);

  const newAgent: Agent = {
    id: '2',
    role: '设计师',
    name: '设计师 Agent',
    status: 'idle',
    description: '新 Agent',
  };

  useAgentStore.getState().addAgent(newAgent);

  const state = useAgentStore.getState();
  expect(state.agents).toHaveLength(2);
  expect(state.agents[1]).toEqual(newAgent);
});

test('Agent Store - updateAgent', () => {
  useAgentStore.getState().setAgents([
    { id: '1', role: '项目经理', name: '原名称', status: 'idle', description: '描述' },
  ]);

  useAgentStore.getState().updateAgent('1', { name: '新名称', status: 'working' });

  const state = useAgentStore.getState();
  expect(state.agents[0].name).toBe('新名称');
  expect(state.agents[0].status).toBe('working');
});

test('Agent Store - updateAgent 不存在的 ID', () => {
  useAgentStore.getState().setAgents([
    { id: '1', role: '项目经理', name: '名称', status: 'idle', description: '描述' },
  ]);

  useAgentStore.getState().updateAgent('999', { name: '新名称' });

  const state = useAgentStore.getState();
  expect(state.agents).toHaveLength(1);
  expect(state.agents[0].name).toBe('名称');
});

test('Agent Store - deleteAgent', () => {
  useAgentStore.getState().setAgents([
    { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle', description: '描述 1' },
    { id: '2', role: '程序员', name: '程序员 Agent', status: 'working', description: '描述 2' },
  ]);

  useAgentStore.getState().deleteAgent('1');

  const state = useAgentStore.getState();
  expect(state.agents).toHaveLength(1);
  expect(state.agents[0].id).toBe('2');
});

test('Agent Store - updateAgentStatus', () => {
  useAgentStore.getState().setAgents([
    { id: '1', role: '项目经理', name: '名称', status: 'idle', description: '描述' },
  ]);

  useAgentStore.getState().updateAgentStatus('1', 'working');

  const state = useAgentStore.getState();
  expect(state.agents[0].status).toBe('working');
});

test('Agent Store - updateAgentStatus 所有状态', () => {
  useAgentStore.getState().setAgents([
    { id: '1', role: '角色', name: '名称', status: 'idle', description: '描述' },
  ]);

  useAgentStore.getState().updateAgentStatus('1', 'working');
  expect(useAgentStore.getState().agents[0].status).toBe('working');

  useAgentStore.getState().updateAgentStatus('1', 'blocked');
  expect(useAgentStore.getState().agents[0].status).toBe('blocked');

  useAgentStore.getState().updateAgentStatus('1', 'idle');
  expect(useAgentStore.getState().agents[0].status).toBe('idle');
});

test('Agent Store - setLoading', () => {
  useAgentStore.getState().setLoading(true);
  expect(useAgentStore.getState().loading).toBe(true);

  useAgentStore.getState().setLoading(false);
  expect(useAgentStore.getState().loading).toBe(false);
});

test('Agent Store - setError', () => {
  useAgentStore.getState().setError('错误信息');
  expect(useAgentStore.getState().error).toBe('错误信息');

  useAgentStore.getState().setError(null);
  expect(useAgentStore.getState().error).toBeNull();
});

test('Agent Store - addAgent 技能字段', () => {
  const agentWithSkills: Agent = {
    id: '1',
    role: '程序员',
    name: '程序员 Agent',
    status: 'idle',
    description: '负责开发',
    skills: ['Python', 'JavaScript', '代码审查'],
  };

  useAgentStore.getState().addAgent(agentWithSkills);

  const state = useAgentStore.getState();
  expect(state.agents[0].skills).toEqual(['Python', 'JavaScript', '代码审查']);
});
