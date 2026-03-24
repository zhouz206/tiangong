/** @vitest-environment jsdom */
import { test, expect, vi, beforeEach, afterEach } from 'vitest';
import apiClient, { projectApi, agentApi, knowledgeApi, trackingApi } from './api';

// Mock axios
vi.mock('axios', () => {
  const mockGet = vi.fn();
  const mockPost = vi.fn();
  const mockPut = vi.fn();
  const mockPatch = vi.fn();
  const mockDelete = vi.fn();

  return {
    default: {
      create: vi.fn(() => ({
        defaults: {
          baseURL: '/api',
          timeout: 30000,
          headers: {
            'Content-Type': 'application/json',
          },
        },
        interceptors: {
          request: {
            use: vi.fn(),
          },
          response: {
            use: vi.fn(),
          },
        },
        get: mockGet,
        post: mockPost,
        put: mockPut,
        patch: mockPatch,
        delete: mockDelete,
      })),
      get: mockGet,
      post: mockPost,
      put: mockPut,
      patch: mockPatch,
      delete: mockDelete,
    },
  };
});

// Mock localStorage
const mockLocalStorage = {
  store: {} as Record<string, string>,
  getItem: vi.fn((key: string) => mockLocalStorage.store[key] || null),
  setItem: vi.fn((key: string, value: string) => {
    mockLocalStorage.store[key] = value;
  }),
  removeItem: vi.fn((key: string) => {
    delete mockLocalStorage.store[key];
  }),
  clear: vi.fn(() => {
    mockLocalStorage.store = {};
  }),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

// Mock window.location
const mockLocation = {
  href: '',
};
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

beforeEach(() => {
  vi.clearAllMocks();
  mockLocalStorage.store = {};
  mockLocation.href = '';
});

afterEach(() => {
  vi.restoreAllMocks();
});

test('API 客户端 - 基础配置', () => {
  expect(apiClient.defaults.baseURL).toBe('/api');
  expect(apiClient.defaults.timeout).toBe(30000);
  expect(apiClient.defaults.headers?.['Content-Type']).toBe('application/json');
});

test('projectApi - list', async () => {
  const mockGet = vi.fn().mockResolvedValue({ projects: [{ id: '1', name: '项目 1' }] });
  apiClient.get = mockGet;

  const result = await projectApi.list();

  expect(mockGet).toHaveBeenCalledWith('/projects');
  expect(result).toEqual({ projects: [{ id: '1', name: '项目 1' }] });
});

test('projectApi - get', async () => {
  const mockGet = vi.fn().mockResolvedValue({ project: { id: '1', name: '项目 1' } });
  apiClient.get = mockGet;

  const result = await projectApi.get('1');

  expect(mockGet).toHaveBeenCalledWith('/projects/1');
  expect(result).toEqual({ project: { id: '1', name: '项目 1' } });
});

test('projectApi - create', async () => {
  const mockPost = vi.fn().mockResolvedValue({ project: { id: '1', name: '新项目' } });
  apiClient.post = mockPost;
  const newData = { name: '新项目', description: '描述', template: 'software' };

  const result = await projectApi.create(newData);

  expect(mockPost).toHaveBeenCalledWith('/projects', newData);
  expect(result).toEqual({ project: { id: '1', name: '新项目' } });
});

test('projectApi - update', async () => {
  const mockPut = vi.fn().mockResolvedValue({ project: { id: '1', name: '更新后' } });
  apiClient.put = mockPut;
  const updateData = { name: '更新后' };

  const result = await projectApi.update('1', updateData);

  expect(mockPut).toHaveBeenCalledWith('/projects/1', updateData);
  expect(result).toEqual({ project: { id: '1', name: '更新后' } });
});

test('projectApi - delete', async () => {
  const mockDelete = vi.fn().mockResolvedValue({ success: true });
  apiClient.delete = mockDelete;

  const result = await projectApi.delete('1');

  expect(mockDelete).toHaveBeenCalledWith('/projects/1');
  expect(result).toEqual({ success: true });
});

test('projectApi - updatePhase', async () => {
  const mockPatch = vi.fn().mockResolvedValue({ project: { id: '1', phase: 'executing' } });
  apiClient.patch = mockPatch;

  const result = await projectApi.updatePhase('1', 'executing');

  expect(mockPatch).toHaveBeenCalledWith('/projects/1/phase', { phase: 'executing' });
  expect(result).toEqual({ project: { id: '1', phase: 'executing' } });
});

test('projectApi - updateTaskStatus', async () => {
  const mockPatch = vi.fn().mockResolvedValue({ task: { id: 't1', status: 'completed' } });
  apiClient.patch = mockPatch;

  const result = await projectApi.updateTaskStatus('p1', 't1', 'completed');

  expect(mockPatch).toHaveBeenCalledWith('/projects/tasks/t1', { status: 'completed' });
  expect(result).toEqual({ task: { id: 't1', status: 'completed' } });
});

test('agentApi - list', async () => {
  const mockGet = vi.fn().mockResolvedValue({ agents: [{ id: '1', name: 'Agent 1' }] });
  apiClient.get = mockGet;

  const result = await agentApi.list();

  expect(mockGet).toHaveBeenCalledWith('/agents');
  expect(result).toEqual({ agents: [{ id: '1', name: 'Agent 1' }] });
});

test('agentApi - getStatus', async () => {
  const mockGet = vi.fn().mockResolvedValue({ status: 'working', taskId: 't1' });
  apiClient.get = mockGet;

  const result = await agentApi.getStatus('1');

  expect(mockGet).toHaveBeenCalledWith('/agents/1/status');
  expect(result).toEqual({ status: 'working', taskId: 't1' });
});

test('agentApi - executeTask', async () => {
  const mockPost = vi.fn().mockResolvedValue({ task: { id: 't1', status: 'queued' } });
  apiClient.post = mockPost;
  const taskData = { title: '新任务', description: '描述', priority: 'high' };

  const result = await agentApi.executeTask('1', taskData);

  expect(mockPost).toHaveBeenCalledWith('/agents/1/tasks', taskData);
  expect(result).toEqual({ task: { id: 't1', status: 'queued' } });
});

test('agentApi - configure', async () => {
  const mockPut = vi.fn().mockResolvedValue({ success: true });
  apiClient.put = mockPut;
  const configData = { name: '新名称', enabled: true, maxConcurrentTasks: 5, autoAssign: true };

  const result = await agentApi.configure('1', configData);

  expect(mockPut).toHaveBeenCalledWith('/agents/1/config', configData);
  expect(result).toEqual({ success: true });
});

test('knowledgeApi - search', async () => {
  const mockGet = vi.fn().mockResolvedValue({ documents: [{ id: '1', title: '文档 1' }] });
  apiClient.get = mockGet;

  const result = await knowledgeApi.search('搜索词');

  expect(mockGet).toHaveBeenCalledWith('/knowledge/search', { params: { q: '搜索词' } });
  expect(result).toEqual({ documents: [{ id: '1', title: '文档 1' }] });
});

test('knowledgeApi - addDocument', async () => {
  const mockPost = vi.fn().mockResolvedValue({ document: { id: '1', title: '新文档' } });
  apiClient.post = mockPost;
  const docData = { title: '新文档', category: '技术文档', tags: ['需求'], content: '内容' };

  const result = await knowledgeApi.addDocument(docData);

  expect(mockPost).toHaveBeenCalledWith('/knowledge/documents', docData);
  expect(result).toEqual({ document: { id: '1', title: '新文档' } });
});

test('knowledgeApi - getCategories', async () => {
  const mockGet = vi.fn().mockResolvedValue({ categories: ['技术文档', '产品文档'] });
  apiClient.get = mockGet;

  const result = await knowledgeApi.getCategories();

  expect(mockGet).toHaveBeenCalledWith('/knowledge/categories');
  expect(result).toEqual({ categories: ['技术文档', '产品文档'] });
});

test('knowledgeApi - getTags', async () => {
  const mockGet = vi.fn().mockResolvedValue({ tags: ['需求', '架构', 'API'] });
  apiClient.get = mockGet;

  const result = await knowledgeApi.getTags();

  expect(mockGet).toHaveBeenCalledWith('/knowledge/tags');
  expect(result).toEqual({ tags: ['需求', '架构', 'API'] });
});

test('knowledgeApi - deleteDocument', async () => {
  const mockDelete = vi.fn().mockResolvedValue({ success: true });
  apiClient.delete = mockDelete;

  const result = await knowledgeApi.deleteDocument('1');

  expect(mockDelete).toHaveBeenCalledWith('/knowledge/documents/1');
  expect(result).toEqual({ success: true });
});

test('trackingApi - getProjectStatus', async () => {
  const mockGet = vi.fn().mockResolvedValue({ status: 'active', progress: 50 });
  apiClient.get = mockGet;

  const result = await trackingApi.getProjectStatus('1');

  expect(mockGet).toHaveBeenCalledWith('/tracking/project/1/status');
  expect(result).toEqual({ status: 'active', progress: 50 });
});

test('trackingApi - getTaskLogs', async () => {
  const mockGet = vi.fn().mockResolvedValue({ logs: [{ id: '1', action: 'started' }] });
  apiClient.get = mockGet;

  const result = await trackingApi.getTaskLogs('t1');

  expect(mockGet).toHaveBeenCalledWith('/tracking/task/t1/logs');
  expect(result).toEqual({ logs: [{ id: '1', action: 'started' }] });
});
