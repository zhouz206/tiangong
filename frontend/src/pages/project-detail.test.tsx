import { test, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter, useParams, useNavigate } from 'react-router-dom';
import ProjectDetail from './project-detail';
import { useProjectStore } from '../stores/project';
import * as api from '../utils/api';

vi.mock('../utils/api', () => ({
  projectApi: {
    get: vi.fn(),
    update: vi.fn(),
    updatePhase: vi.fn(),
    updateTaskStatus: vi.fn(),
  },
}));

vi.mock('../stores/project', () => ({
  useProjectStore: vi.fn(),
}));

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: vi.fn(),
    useNavigate: () => mockNavigate,
  };
});

beforeEach(() => {
  vi.clearAllMocks();
  (useParams as vi.Mock).mockReturnValue({ id: 'test-project-id' });
  (useProjectStore as vi.Mock).mockReturnValue({
    currentProject: null,
    setCurrentProject: vi.fn(),
    updateProject: vi.fn(),
    updateProjectProgress: vi.fn(),
    updateProjectPhase: vi.fn(),
  });
});

const renderWithRouter = (ui: React.ReactElement) => {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

test('ProjectDetail 页面渲染', async () => {
  (api.projectApi.get as vi.Mock).mockResolvedValue({
    project: {
      id: 'test-project-id',
      name: '测试项目',
      description: '项目描述',
      progress: 50,
      phase: 'executing',
      status: 'active',
      tasks: [
        { id: '1', title: '任务 1', status: 'completed' },
        { id: '2', title: '任务 2', status: 'in_progress' },
      ],
      milestones: [
        { id: 'm1', name: '里程碑 1', progress: 100, status: 'completed' },
      ],
    },
  });

  renderWithRouter(<ProjectDetail />);

  await waitFor(() => {
    expect(screen.getByText('测试项目')).toBeInTheDocument();
  });

  expect(screen.getByText('项目描述')).toBeInTheDocument();
  expect(screen.getByText('项目进度')).toBeInTheDocument();
});

test('ProjectDetail 页面 - 显示任务列表', async () => {
  (api.projectApi.get as vi.Mock).mockResolvedValue({
    project: {
      id: 'test-project-id',
      name: '测试项目',
      description: '描述',
      progress: 40,
      phase: 'executing',
      status: 'active',
      tasks: [
        { id: '1', title: '需求分析', status: 'completed', assignee: '张三' },
        { id: '2', title: '架构设计', status: 'in_progress', assignee: '李四' },
        { id: '3', title: '前端开发', status: 'pending', assignee: '王五' },
      ],
    },
  });

  renderWithRouter(<ProjectDetail />);

  await waitFor(() => {
    expect(screen.getByText('任务列表')).toBeInTheDocument();
    expect(screen.getByText('需求分析')).toBeInTheDocument();
    expect(screen.getByText('架构设计')).toBeInTheDocument();
    expect(screen.getByText('前端开发')).toBeInTheDocument();
  });
});

test('ProjectDetail 页面 - 添加任务', async () => {
  const mockUpdateProject = vi.fn();
  (useProjectStore as vi.Mock).mockReturnValue({
    currentProject: {
      id: 'test-project-id',
      name: '测试项目',
      description: '描述',
      progress: 50,
      phase: 'executing',
      status: 'active',
      tasks: [],
    },
    setCurrentProject: vi.fn(),
    updateProject: mockUpdateProject,
    updateProjectProgress: vi.fn(),
    updateProjectPhase: vi.fn(),
  });

  (api.projectApi.get as vi.Mock).mockResolvedValue({
    project: { id: 'test-project-id', name: '测试项目', description: '描述', progress: 50, phase: 'executing', status: 'active', tasks: [] },
  });
  (api.projectApi.update as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  renderWithRouter(<ProjectDetail />);

  await waitFor(() => {
    expect(screen.getByText('+ 添加任务')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('+ 添加任务'));

  await waitFor(() => {
    expect(screen.getByPlaceholderText('输入任务标题')).toBeInTheDocument();
  });

  fireEvent.change(screen.getByPlaceholderText('输入任务标题'), {
    target: { value: '新任务' },
  });
  fireEvent.change(screen.getByPlaceholderText('输入负责人'), {
    target: { value: '负责人' },
  });

  fireEvent.click(screen.getByText('添加'));

  await waitFor(() => {
    expect(mockUpdateProject).toHaveBeenCalled();
  });
});

test('ProjectDetail 页面 - 切换任务状态', async () => {
  const mockUpdateProject = vi.fn();
  const mockUpdateProgress = vi.fn();

  (useProjectStore as vi.Mock).mockReturnValue({
    currentProject: {
      id: 'test-project-id',
      name: '测试项目',
      description: '描述',
      progress: 25,
      phase: 'executing',
      status: 'active',
      tasks: [{ id: '1', title: '任务 1', status: 'pending', assignee: '张三' }],
    },
    setCurrentProject: vi.fn(),
    updateProject: mockUpdateProject,
    updateProjectProgress: mockUpdateProgress,
    updateProjectPhase: vi.fn(),
  });

  (api.projectApi.get as vi.Mock).mockResolvedValue({
    project: {
      id: 'test-project-id',
      name: '测试项目',
      description: '描述',
      progress: 25,
      phase: 'executing',
      status: 'active',
      tasks: [{ id: '1', title: '任务 1', status: 'pending', assignee: '张三' }],
    },
  });
  (api.projectApi.updateTaskStatus as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  renderWithRouter(<ProjectDetail />);

  await waitFor(() => {
    expect(screen.getByText('任务 1')).toBeInTheDocument();
  });

  const statusSelect = screen.getByText('待处理').closest('select') as HTMLSelectElement;
  fireEvent.change(statusSelect, { target: { value: 'completed' } });

  await waitFor(() => {
    expect(mockUpdateProject).toHaveBeenCalled();
  });
});

test('ProjectDetail 页面 - 切换项目阶段', async () => {
  const mockUpdatePhase = vi.fn();
  const mockUpdateProject = vi.fn();

  (useProjectStore as vi.Mock).mockReturnValue({
    currentProject: {
      id: 'test-project-id',
      name: '测试项目',
      description: '描述',
      progress: 50,
      phase: 'planning',
      status: 'active',
      tasks: [],
    },
    setCurrentProject: vi.fn(),
    updateProject: mockUpdateProject,
    updateProjectProgress: vi.fn(),
    updateProjectPhase: mockUpdatePhase,
  });

  (api.projectApi.get as vi.Mock).mockResolvedValue({
    project: { id: 'test-project-id', name: '测试项目', description: '描述', progress: 50, phase: 'planning', status: 'active', tasks: [] },
  });
  (api.projectApi.updatePhase as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  renderWithRouter(<ProjectDetail />);

  await waitFor(() => {
    expect(screen.getByText('切换阶段')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('切换阶段'));

  await waitFor(() => {
    expect(screen.getByText('⚙️ 执行中')).toBeInTheDocument();
  }, { timeout: 3000 });

  fireEvent.click(screen.getByText('⚙️ 执行中'));

  await waitFor(() => {
    expect(mockUpdatePhase).toHaveBeenCalledWith('test-project-id', 'executing');
  });
});

test('ProjectDetail 页面 - 编辑项目', async () => {
  const mockUpdateProject = vi.fn();

  (useProjectStore as vi.Mock).mockReturnValue({
    currentProject: {
      id: 'test-project-id',
      name: '测试项目',
      description: '原描述',
      progress: 50,
      phase: 'executing',
      status: 'active',
      tasks: [],
    },
    setCurrentProject: vi.fn(),
    updateProject: mockUpdateProject,
    updateProjectProgress: vi.fn(),
    updateProjectPhase: vi.fn(),
  });

  (api.projectApi.get as vi.Mock).mockResolvedValue({
    project: { id: 'test-project-id', name: '测试项目', description: '原描述', progress: 50, phase: 'executing', status: 'active', tasks: [] },
  });
  (api.projectApi.update as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  renderWithRouter(<ProjectDetail />);

  await waitFor(() => {
    expect(screen.getByText('编辑')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('编辑'));

  await waitFor(() => {
    expect(screen.getByText('编辑项目')).toBeInTheDocument();
  });

  fireEvent.change(screen.getByDisplayValue('原描述'), {
    target: { value: '新描述' },
  });

  fireEvent.click(screen.getByText('保存'));

  await waitFor(() => {
    expect(mockUpdateProject).toHaveBeenCalled();
  });
});

test('ProjectDetail 页面 - 返回按钮', async () => {
  (api.projectApi.get as vi.Mock).mockResolvedValue({
    project: { id: 'test-project-id', name: '测试项目', description: '描述', progress: 50, phase: 'executing', status: 'active', tasks: [] },
  });

  renderWithRouter(<ProjectDetail />);

  await waitFor(() => {
    expect(screen.getByText('← 返回')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('← 返回'));

  expect(mockNavigate).toHaveBeenCalled();
});

test('ProjectDetail 页面 - 显示里程碑', async () => {
  (api.projectApi.get as vi.Mock).mockResolvedValue({
    project: {
      id: 'test-project-id',
      name: '测试项目',
      description: '描述',
      progress: 60,
      phase: 'executing',
      status: 'active',
      tasks: [],
      milestones: [
        { id: 'm1', name: 'M1 核心功能', progress: 100, status: 'completed' },
        { id: 'm2', name: 'M2 性能优化', progress: 50, status: 'active' },
      ],
    },
  });

  renderWithRouter(<ProjectDetail />);

  await waitFor(() => {
    expect(screen.getByText('里程碑')).toBeInTheDocument();
    expect(screen.getByText('M1 核心功能')).toBeInTheDocument();
    expect(screen.getByText('M2 性能优化')).toBeInTheDocument();
  });
});
