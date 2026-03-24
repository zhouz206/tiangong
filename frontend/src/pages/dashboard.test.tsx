import { test, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './dashboard';
import { useProjectStore } from '../stores/project';
import * as api from '../utils/api';

// Mock API
vi.mock('../utils/api', () => ({
  projectApi: {
    list: vi.fn(),
    create: vi.fn(),
  },
}));

// Mock zustand store
vi.mock('../stores/project', () => ({
  useProjectStore: vi.fn(),
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

beforeEach(() => {
  vi.clearAllMocks();
  (useProjectStore as vi.Mock).mockReturnValue({
    projects: [],
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: false,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });
});

const renderWithRouter = (ui: React.ReactElement) => {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

test('Dashboard 页面渲染统计卡片', async () => {
  (useProjectStore as vi.Mock).mockReturnValue({
    projects: [
      { id: '1', name: '项目 1', description: '描述 1', progress: 50, phase: 'planning', status: 'active' },
      { id: '2', name: '项目 2', description: '描述 2', progress: 100, phase: 'completed', status: 'active' },
      { id: '3', name: '项目 3', description: '描述 3', progress: 30, phase: 'executing', status: 'blocked' },
    ],
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: false,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockResolvedValue({ projects: [] });

  renderWithRouter(<Dashboard />);

  expect(screen.getByText('仪表盘')).toBeInTheDocument();
  expect(screen.getByText(/总项目数/i)).toBeInTheDocument();
  expect(screen.getByText(/进行中/i)).toBeInTheDocument();
  expect(screen.getByText(/规划中/i)).toBeInTheDocument();
  expect(screen.getByText(/已完成/i)).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText('3')).toBeInTheDocument();
  });
});

test('Dashboard 页面 - 新建项目按钮打开对话框', async () => {
  (useProjectStore as vi.Mock).mockReturnValue({
    projects: [],
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: false,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockResolvedValue({ projects: [] });

  renderWithRouter(<Dashboard />);

  const createButton = screen.getByText('+ 新建项目');
  fireEvent.click(createButton);

  await waitFor(() => {
    expect(screen.getByText('新建项目')).toBeInTheDocument();
  });

  expect(screen.getByPlaceholderText('我的项目')).toBeInTheDocument();
  expect(screen.getByPlaceholderText('项目描述...')).toBeInTheDocument();
});

test('Dashboard 页面 - 创建新项目', async () => {
  const mockAddProject = vi.fn();
  (useProjectStore as vi.Mock).mockReturnValue({
    projects: [],
    setProjects: vi.fn(),
    addProject: mockAddProject,
    loading: false,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockResolvedValue({ projects: [] });
  (api.projectApi.create as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  renderWithRouter(<Dashboard />);

  fireEvent.click(screen.getByText('+ 新建项目'));

  await waitFor(() => {
    expect(screen.getByText('新建项目')).toBeInTheDocument();
  });

  fireEvent.change(screen.getByPlaceholderText('我的项目'), {
    target: { value: '测试项目' },
  });
  fireEvent.change(screen.getByPlaceholderText('项目描述...'), {
    target: { value: '这是一个测试项目' },
  });

  fireEvent.click(screen.getByText('创建'));

  await waitFor(() => {
    expect(mockAddProject).toHaveBeenCalled();
  });
});

test('Dashboard 页面 - 加载状态显示', async () => {
  (useProjectStore as vi.Mock).mockReturnValue({
    projects: [],
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: true,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockImplementation(
    () => new Promise(() => {})
  );

  renderWithRouter(<Dashboard />);

  await waitFor(() => {
    expect(screen.getByText('加载项目中...')).toBeInTheDocument();
  });
});

test('Dashboard 页面 - 显示错误提示', async () => {
  (useProjectStore as vi.Mock).mockReturnValue({
    projects: [],
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: false,
    setLoading: vi.fn(),
    error: '加载失败，使用本地数据',
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockRejectedValue(new Error('API 错误'));

  renderWithRouter(<Dashboard />);

  await waitFor(() => {
    expect(screen.getByText('加载失败，使用本地数据')).toBeInTheDocument();
  });
});

test('Dashboard 页面 - 空状态显示创建按钮', async () => {
  (useProjectStore as vi.Mock).mockReturnValue({
    projects: [],
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: false,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockResolvedValue({ projects: [] });

  renderWithRouter(<Dashboard />);

  await waitFor(() => {
    expect(screen.getByText('暂无项目')).toBeInTheDocument();
    expect(screen.getByText('创建第一个项目')).toBeInTheDocument();
  });
});
