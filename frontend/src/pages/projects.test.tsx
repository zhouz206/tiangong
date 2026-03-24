import { test, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import Projects from './projects';
import { useProjectStore } from '../stores/project';
import * as api from '../utils/api';

vi.mock('../utils/api', () => ({
  projectApi: {
    list: vi.fn(),
    create: vi.fn(),
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

test('Projects 页面渲染', async () => {
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

  renderWithRouter(<Projects />);

  expect(screen.getByText('项目列表')).toBeInTheDocument();
  expect(screen.getByText('管理你的所有项目')).toBeInTheDocument();
});

test('Projects 页面 - 搜索功能', async () => {
  const mockProjects = [
    { id: '1', name: 'SaaS 应用', description: '描述 1', progress: 50, phase: 'planning', status: 'active' },
    { id: '2', name: '博客系列', description: '描述 2', progress: 80, phase: 'executing', status: 'active' },
    { id: '3', name: '数据分析', description: '描述 3', progress: 30, phase: 'reviewing', status: 'active' },
  ];

  (useProjectStore as vi.Mock).mockReturnValue({
    projects: mockProjects,
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: false,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockResolvedValue({ projects: mockProjects });

  renderWithRouter(<Projects />);

  const searchInput = screen.getByPlaceholderText('搜索项目...');
  fireEvent.change(searchInput, { target: { value: 'SaaS' } });

  await waitFor(() => {
    expect(screen.getByText('SaaS 应用')).toBeInTheDocument();
    expect(screen.queryByText('博客系列')).not.toBeInTheDocument();
  });
});

test('Projects 页面 - 按阶段筛选', async () => {
  const mockProjects = [
    { id: '1', name: '项目 1', description: '描述 1', progress: 50, phase: 'planning', status: 'active' },
    { id: '2', name: '项目 2', description: '描述 2', progress: 80, phase: 'executing', status: 'active' },
    { id: '3', name: '项目 3', description: '描述 3', progress: 30, phase: 'reviewing', status: 'active' },
    { id: '4', name: '项目 4', description: '描述 4', progress: 100, phase: 'completed', status: 'active' },
  ];

  (useProjectStore as vi.Mock).mockReturnValue({
    projects: mockProjects,
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: false,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockResolvedValue({ projects: mockProjects });

  renderWithRouter(<Projects />);

  const filterSelect = screen.getAllByRole('combobox')[0];
  fireEvent.change(filterSelect, { target: { value: 'planning' } });

  await waitFor(() => {
    expect(screen.getByText('项目 1')).toBeInTheDocument();
    expect(screen.queryByText('项目 2')).not.toBeInTheDocument();
  });
});

test('Projects 页面 - 新建项目', async () => {
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

  renderWithRouter(<Projects />);

  fireEvent.click(screen.getByText('+ 新建项目'));

  await waitFor(() => {
    expect(screen.getByText('新建项目')).toBeInTheDocument();
  });

  fireEvent.change(screen.getByPlaceholderText('我的项目'), {
    target: { value: '新项目' },
  });
  fireEvent.change(screen.getByPlaceholderText('项目描述...'), {
    target: { value: '新项目的描述' },
  });
  fireEvent.click(screen.getByText('创建'));

  await waitFor(() => {
    expect(mockAddProject).toHaveBeenCalled();
  });
});

test('Projects 页面 - 刷新按钮', async () => {
  const mockSetProjects = vi.fn();
  const mockSetLoading = vi.fn();
  const mockSetError = vi.fn();

  (useProjectStore as vi.Mock).mockReturnValue({
    projects: [],
    setProjects: mockSetProjects,
    addProject: vi.fn(),
    loading: false,
    setLoading: mockSetLoading,
    error: null,
    setError: mockSetError,
  });

  (api.projectApi.list as vi.Mock).mockResolvedValue({
    projects: [{ id: '1', name: '刷新项目', description: '描述', progress: 50, phase: 'planning', status: 'active' }],
  });

  renderWithRouter(<Projects />);

  fireEvent.click(screen.getByText('刷新'));

  await waitFor(() => {
    expect(api.projectApi.list).toHaveBeenCalled();
  });
});

test('Projects 页面 - 空状态显示', async () => {
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

  renderWithRouter(<Projects />);

  await waitFor(() => {
    expect(screen.getByText('暂无项目')).toBeInTheDocument();
    expect(screen.getByText('创建第一个项目')).toBeInTheDocument();
  });
});

test('Projects 页面 - 加载状态', async () => {
  (useProjectStore as vi.Mock).mockReturnValue({
    projects: [],
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: true,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockImplementation(() => new Promise(() => {}));

  renderWithRouter(<Projects />);

  await waitFor(() => {
    expect(screen.getByText('加载项目中...')).toBeInTheDocument();
  });
});

test('Projects 页面 - 点击项目卡片导航到详情页', async () => {
  const mockProjects = [
    { id: 'proj-123', name: '测试项目', description: '描述', progress: 50, phase: 'planning', status: 'active' },
  ];

  (useProjectStore as vi.Mock).mockReturnValue({
    projects: mockProjects,
    setProjects: vi.fn(),
    addProject: vi.fn(),
    loading: false,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
  });

  (api.projectApi.list as vi.Mock).mockResolvedValue({ projects: mockProjects });

  renderWithRouter(<Projects />);

  await waitFor(() => {
    expect(screen.getByText('测试项目')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('测试项目'));

  expect(mockNavigate).toHaveBeenCalledWith('/projects/proj-123');
});
