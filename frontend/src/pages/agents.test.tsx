import { test, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Agents from './agents';
import { useAgentStore } from '../stores/agent';
import * as api from '../utils/api';

vi.mock('../utils/api', () => ({
  agentApi: {
    list: vi.fn(),
    configure: vi.fn(),
    executeTask: vi.fn(),
  },
}));

vi.mock('../stores/agent', () => ({
  useAgentStore: vi.fn(),
}));

beforeEach(() => {
  vi.clearAllMocks();
  (useAgentStore as vi.Mock).mockReturnValue({
    agents: [],
    setAgents: vi.fn(),
    updateAgentStatus: vi.fn(),
  });
});

test('Agents 页面渲染', async () => {
  (useAgentStore as vi.Mock).mockReturnValue({
    agents: [],
    setAgents: vi.fn(),
    updateAgentStatus: vi.fn(),
  });

  (api.agentApi.list as vi.Mock).mockResolvedValue({ agents: [] });

  render(<Agents />);

  expect(screen.getByText('Agent 管理')).toBeInTheDocument();
  expect(screen.getByText('管理你的 AI Agent 团队')).toBeInTheDocument();
});

test('Agents 页面 - 显示 Agent 统计', async () => {
  const mockAgents = [
    { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle', description: '描述 1' },
    { id: '2', role: '程序员', name: '程序员 Agent', status: 'working', description: '描述 2' },
    { id: '3', role: '设计师', name: '设计师 Agent', status: 'working', description: '描述 3' },
    { id: '4', role: '测试员', name: '测试员 Agent', status: 'blocked', description: '描述 4' },
  ];

  (useAgentStore as vi.Mock).mockReturnValue({
    agents: mockAgents,
    setAgents: vi.fn(),
    updateAgentStatus: vi.fn(),
  });

  (api.agentApi.list as vi.Mock).mockResolvedValue({ agents: mockAgents });

  render(<Agents />);

  await waitFor(() => {
    expect(screen.getByText('2')).toBeInTheDocument(); // working
  });

  expect(screen.getByText('空闲')).toBeInTheDocument();
  expect(screen.getByText('工作中')).toBeInTheDocument();
  expect(screen.getByText('阻塞')).toBeInTheDocument();
});

test('Agents 页面 - 显示 Agent 列表', async () => {
  const mockAgents = [
    { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle', description: '负责项目管理', skills: ['需求分析', '任务分配'] },
    { id: '2', role: '程序员', name: '程序员 Agent', status: 'working', description: '负责开发', skills: ['Python', 'JavaScript'] },
  ];

  (useAgentStore as vi.Mock).mockReturnValue({
    agents: mockAgents,
    setAgents: vi.fn(),
    updateAgentStatus: vi.fn(),
  });

  (api.agentApi.list as vi.Mock).mockResolvedValue({ agents: mockAgents });

  render(<Agents />);

  await waitFor(() => {
    expect(screen.getByText('项目经理 Agent')).toBeInTheDocument();
    expect(screen.getByText('程序员 Agent')).toBeInTheDocument();
  });

  expect(screen.getByText('需求分析')).toBeInTheDocument();
  expect(screen.getByText('Python')).toBeInTheDocument();
});

test('Agents 页面 - 配置 Agent', async () => {
  const mockAgents = [
    { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle', description: '描述' },
  ];

  (useAgentStore as vi.Mock).mockReturnValue({
    agents: mockAgents,
    setAgents: vi.fn(),
    updateAgentStatus: vi.fn(),
  });

  (api.agentApi.list as vi.Mock).mockResolvedValue({ agents: mockAgents });
  (api.agentApi.configure as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  render(<Agents />);

  await waitFor(() => {
    expect(screen.getByText('配置 Agent')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('配置 Agent'));

  await waitFor(() => {
    expect(screen.getByText('配置 Agent')).toBeInTheDocument();
    expect(screen.getByText('选择一个 Agent 进行配置')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('项目经理 Agent'));

  await waitFor(() => {
    expect(screen.getByText('配置 项目经理 Agent')).toBeInTheDocument();
  });
});

test('Agents 页面 - 保存 Agent 配置', async () => {
  const mockAgents = [
    { id: '1', role: '项目经理', name: '项目经理 Agent', status: 'idle', description: '描述' },
  ];
  const mockUpdateAgentStatus = vi.fn();

  (useAgentStore as vi.Mock).mockReturnValue({
    agents: mockAgents,
    setAgents: vi.fn(),
    updateAgentStatus: mockUpdateAgentStatus,
  });

  (api.agentApi.list as vi.Mock).mockResolvedValue({ agents: mockAgents });
  (api.agentApi.configure as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  render(<Agents />);

  await waitFor(() => {
    expect(screen.getByText('配置 Agent')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('配置 Agent'));
  fireEvent.click(screen.getByText('项目经理 Agent'));

  await waitFor(() => {
    expect(screen.getByDisplayValue('项目经理 Agent')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('保存'));

  await waitFor(() => {
    expect(mockUpdateAgentStatus).toHaveBeenCalled();
  });
});

test('Agents 页面 - 分配任务给 Agent', async () => {
  const mockAgents = [
    { id: '1', role: '程序员', name: '程序员 Agent', status: 'idle', description: '描述' },
  ];
  const mockUpdateAgentStatus = vi.fn();

  (useAgentStore as vi.Mock).mockReturnValue({
    agents: mockAgents,
    setAgents: vi.fn(),
    updateAgentStatus: mockUpdateAgentStatus,
  });

  (api.agentApi.list as vi.Mock).mockResolvedValue({ agents: mockAgents });
  (api.agentApi.executeTask as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  render(<Agents />);

  await waitFor(() => {
    expect(screen.getByText('分配任务')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('分配任务'));

  await waitFor(() => {
    expect(screen.getByText('分配任务给 程序员 Agent')).toBeInTheDocument();
  });

  fireEvent.change(screen.getByPlaceholderText('输入任务标题'), {
    target: { value: '新任务' },
  });
  fireEvent.change(screen.getByPlaceholderText('详细描述任务内容'), {
    target: { value: '任务描述' },
  });

  fireEvent.click(screen.getByText('分配'));

  await waitFor(() => {
    expect(mockUpdateAgentStatus).toHaveBeenCalled();
  });
});

test('Agents 页面 - 切换 Agent 状态', async () => {
  const mockAgents = [
    { id: '1', role: '程序员', name: '程序员 Agent', status: 'idle', description: '描述' },
  ];
  const mockUpdateAgentStatus = vi.fn();

  (useAgentStore as vi.Mock).mockReturnValue({
    agents: mockAgents,
    setAgents: vi.fn(),
    updateAgentStatus: mockUpdateAgentStatus,
  });

  (api.agentApi.list as vi.Mock).mockResolvedValue({ agents: mockAgents });

  render(<Agents />);

  await waitFor(() => {
    expect(screen.getByText('程序员 Agent')).toBeInTheDocument();
  });

  const statusSelect = screen.getByDisplayValue('idle');
  fireEvent.change(statusSelect, { target: { value: 'working' } });

  expect(mockUpdateAgentStatus).toHaveBeenCalledWith('1', 'working');
});

test('Agents 页面 - 阻塞状态不能分配任务', async () => {
  const mockAgents = [
    { id: '1', role: '程序员', name: '程序员 Agent', status: 'blocked', description: '描述' },
  ];

  (useAgentStore as vi.Mock).mockReturnValue({
    agents: mockAgents,
    setAgents: vi.fn(),
    updateAgentStatus: vi.fn(),
  });

  (api.agentApi.list as vi.Mock).mockResolvedValue({ agents: mockAgents });

  render(<Agents />);

  await waitFor(() => {
    expect(screen.getByText('程序员 Agent')).toBeInTheDocument();
  });

  const assignButton = screen.getByText('分配任务');
  expect(assignButton).toBeDisabled();
});

test('Agents 页面 - 刷新按钮', async () => {
  (useAgentStore as vi.Mock).mockReturnValue({
    agents: [],
    setAgents: vi.fn(),
    updateAgentStatus: vi.fn(),
  });

  (api.agentApi.list as vi.Mock).mockResolvedValue({ agents: [] });

  render(<Agents />);

  fireEvent.click(screen.getByText('刷新'));

  await waitFor(() => {
    expect(api.agentApi.list).toHaveBeenCalled();
  });
});
