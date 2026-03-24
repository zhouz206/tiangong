import { test, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Knowledge from './knowledge';
import { useKnowledgeStore } from '../stores/knowledge';
import * as api from '../utils/api';

vi.mock('../utils/api', () => ({
  knowledgeApi: {
    search: vi.fn(),
    getCategories: vi.fn(),
    getTags: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: vi.fn(),
  },
}));

vi.mock('../stores/knowledge', () => ({
  useKnowledgeStore: vi.fn(),
}));

beforeEach(() => {
  vi.clearAllMocks();
  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: [],
    categories: [],
    tags: [],
    searchQuery: '',
    setDocuments: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: vi.fn(),
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: vi.fn(),
  });
});

test('Knowledge 页面渲染', async () => {
  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: [],
    categories: [],
    tags: [],
    searchQuery: '',
    setDocuments: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: vi.fn(),
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: vi.fn(),
  });

  (api.knowledgeApi.search as vi.Mock).mockResolvedValue({ documents: [] });
  (api.knowledgeApi.getCategories as vi.Mock).mockResolvedValue({ categories: [] });
  (api.knowledgeApi.getTags as vi.Mock).mockResolvedValue({ tags: [] });

  render(<Knowledge />);

  expect(screen.getByText('知识库')).toBeInTheDocument();
  expect(screen.getByText('管理和搜索项目知识')).toBeInTheDocument();
});

test('Knowledge 页面 - 显示文档列表', async () => {
  const mockDocuments = [
    { id: '1', title: '项目需求文档', category: '技术文档', tags: ['需求', '规划'], created_at: '2026-03-20' },
    { id: '2', title: '架构设计文档', category: '技术文档', tags: ['架构', '设计'], created_at: '2026-03-21' },
  ];

  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: mockDocuments,
    categories: ['技术文档'],
    tags: ['需求', '架构'],
    searchQuery: '',
    setDocuments: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: vi.fn(),
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: vi.fn(),
  });

  (api.knowledgeApi.search as vi.Mock).mockResolvedValue({ documents: mockDocuments });
  (api.knowledgeApi.getCategories as vi.Mock).mockResolvedValue({ categories: ['技术文档'] });
  (api.knowledgeApi.getTags as vi.Mock).mockResolvedValue({ tags: ['需求', '架构'] });

  render(<Knowledge />);

  await waitFor(() => {
    expect(screen.getByText('项目需求文档')).toBeInTheDocument();
    expect(screen.getByText('架构设计文档')).toBeInTheDocument();
  });
});

test('Knowledge 页面 - 搜索功能', async () => {
  const mockDocuments = [
    { id: '1', title: '项目需求文档', category: '技术文档', tags: ['需求'], created_at: '2026-03-20' },
    { id: '2', title: '架构设计文档', category: '技术文档', tags: ['架构'], created_at: '2026-03-21' },
    { id: '3', title: 'API 接口文档', category: '技术文档', tags: ['API'], created_at: '2026-03-22' },
  ];

  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: mockDocuments,
    categories: ['技术文档'],
    tags: ['需求', '架构', 'API'],
    searchQuery: '',
    setDocuments: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: vi.fn(),
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: vi.fn(),
  });

  (api.knowledgeApi.search as vi.Mock).mockResolvedValue({ documents: mockDocuments });
  (api.knowledgeApi.getCategories as vi.Mock).mockResolvedValue({ categories: ['技术文档'] });
  (api.knowledgeApi.getTags as vi.Mock).mockResolvedValue({ tags: ['需求', '架构', 'API'] });

  render(<Knowledge />);

  await waitFor(() => {
    expect(screen.getByText('项目需求文档')).toBeInTheDocument();
  });

  const searchInput = screen.getByPlaceholderText('搜索文档...');
  fireEvent.change(searchInput, { target: { value: 'API' } });

  await waitFor(() => {
    expect(screen.getByText('API 接口文档')).toBeInTheDocument();
    expect(screen.queryByText('项目需求文档')).not.toBeInTheDocument();
  });
});

test('Knowledge 页面 - 按分类筛选', async () => {
  const mockDocuments = [
    { id: '1', title: '需求文档', category: '技术文档', tags: ['需求'], created_at: '2026-03-20' },
    { id: '2', title: '用户手册', category: '产品文档', tags: ['用户'], created_at: '2026-03-21' },
  ];

  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: mockDocuments,
    categories: ['技术文档', '产品文档'],
    tags: ['需求', '用户'],
    searchQuery: '',
    setDocuments: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: vi.fn(),
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: vi.fn(),
  });

  (api.knowledgeApi.search as vi.Mock).mockResolvedValue({ documents: mockDocuments });
  (api.knowledgeApi.getCategories as vi.Mock).mockResolvedValue({ categories: ['技术文档', '产品文档'] });
  (api.knowledgeApi.getTags as vi.Mock).mockResolvedValue({ tags: ['需求', '用户'] });

  render(<Knowledge />);

  await waitFor(() => {
    expect(screen.getByText('需求文档')).toBeInTheDocument();
  });

  const categorySelect = screen.getAllByRole('combobox')[0];
  fireEvent.change(categorySelect, { target: { value: '产品文档' } });

  await waitFor(() => {
    expect(screen.getByText('用户手册')).toBeInTheDocument();
    expect(screen.queryByText('需求文档')).not.toBeInTheDocument();
  });
});

test('Knowledge 页面 - 点击标签筛选', async () => {
  const mockDocuments = [
    { id: '1', title: '需求文档', category: '技术文档', tags: ['需求', '规划'], created_at: '2026-03-20' },
    { id: '2', title: '设计文档', category: '技术文档', tags: ['架构', '设计'], created_at: '2026-03-21' },
  ];

  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: mockDocuments,
    categories: ['技术文档'],
    tags: ['需求', '规划', '架构', '设计'],
    searchQuery: '',
    setDocuments: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: vi.fn(),
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: vi.fn(),
  });

  (api.knowledgeApi.search as vi.Mock).mockResolvedValue({ documents: mockDocuments });
  (api.knowledgeApi.getCategories as vi.Mock).mockResolvedValue({ categories: ['技术文档'] });
  (api.knowledgeApi.getTags as vi.Mock).mockResolvedValue({ tags: ['需求', '规划', '架构', '设计'] });

  render(<Knowledge />);

  await waitFor(() => {
    expect(screen.getByText('需求文档')).toBeInTheDocument();
  });

  const tagBadge = screen.getByText('需求');
  fireEvent.click(tagBadge);

  await waitFor(() => {
    expect(screen.getByText('需求文档')).toBeInTheDocument();
    expect(screen.queryByText('设计文档')).not.toBeInTheDocument();
  });
});

test('Knowledge 页面 - 上传文档', async () => {
  const mockAddDocument = vi.fn();

  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: [],
    categories: ['技术文档'],
    tags: ['需求'],
    searchQuery: '',
    setDocuments: vi.fn(),
    addDocument: mockAddDocument,
    deleteDocument: vi.fn(),
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: vi.fn(),
  });

  (api.knowledgeApi.search as vi.Mock).mockResolvedValue({ documents: [] });
  (api.knowledgeApi.getCategories as vi.Mock).mockResolvedValue({ categories: ['技术文档'] });
  (api.knowledgeApi.getTags as vi.Mock).mockResolvedValue({ tags: ['需求'] });
  (api.knowledgeApi.addDocument as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  render(<Knowledge />);

  await waitFor(() => {
    expect(screen.getByText('上传文档')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('上传文档'));

  await waitFor(() => {
    expect(screen.getByText('上传文档')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('输入文档标题')).toBeInTheDocument();
  });

  fireEvent.change(screen.getByPlaceholderText('输入文档标题'), {
    target: { value: '新文档' },
  });
  fireEvent.change(screen.getByPlaceholderText('例如：需求，规划，设计'), {
    target: { value: '需求，规划' },
  });

  fireEvent.click(screen.getByText('上传'));

  await waitFor(() => {
    expect(mockAddDocument).toHaveBeenCalled();
  });
});

test('Knowledge 页面 - 删除文档', async () => {
  const mockDocuments = [
    { id: '1', title: '待删除文档', category: '技术文档', tags: ['需求'], created_at: '2026-03-20' },
  ];
  const mockDeleteDocument = vi.fn();

  global.confirm = vi.fn(() => true);

  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: mockDocuments,
    categories: ['技术文档'],
    tags: ['需求'],
    searchQuery: '',
    setDocuments: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: mockDeleteDocument,
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: vi.fn(),
  });

  (api.knowledgeApi.search as vi.Mock).mockResolvedValue({ documents: mockDocuments });
  (api.knowledgeApi.getCategories as vi.Mock).mockResolvedValue({ categories: ['技术文档'] });
  (api.knowledgeApi.getTags as vi.Mock).mockResolvedValue({ tags: ['需求'] });
  (api.knowledgeApi.deleteDocument as vi.Mock).mockRejectedValue(new Error('API 不可用'));

  render(<Knowledge />);

  await waitFor(() => {
    expect(screen.getByText('待删除文档')).toBeInTheDocument();
  });

  const deleteButton = screen.getByTitle('删除文档');
  fireEvent.click(deleteButton);

  await waitFor(() => {
    expect(mockDeleteDocument).toHaveBeenCalledWith('1');
  });
});

test('Knowledge 页面 - 清除筛选', async () => {
  const mockDocuments = [
    { id: '1', title: '文档 1', category: '技术文档', tags: ['需求'], created_at: '2026-03-20' },
  ];
  const mockSetSearchQuery = vi.fn();

  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: mockDocuments,
    categories: ['技术文档'],
    tags: ['需求'],
    searchQuery: 'test',
    setDocuments: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: vi.fn(),
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: mockSetSearchQuery,
  });

  (api.knowledgeApi.search as vi.Mock).mockResolvedValue({ documents: mockDocuments });
  (api.knowledgeApi.getCategories as vi.Mock).mockResolvedValue({ categories: ['技术文档'] });
  (api.knowledgeApi.getTags as vi.Mock).mockResolvedValue({ tags: ['需求'] });

  render(<Knowledge />);

  await waitFor(() => {
    expect(screen.getByText('清除筛选')).toBeInTheDocument();
  });

  fireEvent.click(screen.getByText('清除筛选'));

  expect(mockSetSearchQuery).toHaveBeenCalledWith('');
});

test('Knowledge 页面 - 空状态显示', async () => {
  (useKnowledgeStore as vi.Mock).mockReturnValue({
    documents: [],
    categories: [],
    tags: [],
    searchQuery: '',
    setDocuments: vi.fn(),
    addDocument: vi.fn(),
    deleteDocument: vi.fn(),
    setCategories: vi.fn(),
    setTags: vi.fn(),
    setSearchQuery: vi.fn(),
  });

  (api.knowledgeApi.search as vi.Mock).mockResolvedValue({ documents: [] });
  (api.knowledgeApi.getCategories as vi.Mock).mockResolvedValue({ categories: [] });
  (api.knowledgeApi.getTags as vi.Mock).mockResolvedValue({ tags: [] });

  render(<Knowledge />);

  await waitFor(() => {
    expect(screen.getByText('暂无文档')).toBeInTheDocument();
    expect(screen.getByText('上传第一个文档')).toBeInTheDocument();
  });
});
