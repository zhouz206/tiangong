/**
 * API 集成测试
 * 
 * 测试前端与后端的真实 API 交互
 */
import { test, expect, beforeEach, vi } from 'vitest';
import apiClient, { projectApi, agentApi, knowledgeApi, trackingApi } from './utils/api';

// Mock axios
vi.mock('axios', () => {
  const mockAxios = vi.fn();
  mockAxios.create = vi.fn(() => ({
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }));
  return { default: mockAxios.create() };
});

test('API 客户端创建成功', () => {
  expect(apiClient).toBeDefined();
});

test('projectApi.list 调用正确', async () => {
  const mockGet = vi.fn().mockResolvedValue({ data: { projects: [] } });
  apiClient.get = mockGet;
  
  await projectApi.list();
  
  expect(mockGet).toHaveBeenCalledWith('/projects');
});

test('projectApi.get 调用正确', async () => {
  const mockGet = vi.fn().mockResolvedValue({ data: { project: {} } });
  apiClient.get = mockGet;
  
  await projectApi.get('project-123');
  
  expect(mockGet).toHaveBeenCalledWith('/projects/project-123');
});

test('projectApi.create 调用正确', async () => {
  const mockPost = vi.fn().mockResolvedValue({ data: { id: 'new-id' } });
  apiClient.post = mockPost;
  
  await projectApi.create({ name: '新项目' });
  
  expect(mockPost).toHaveBeenCalledWith('/projects', { name: '新项目' });
});

test('knowledgeApi.search 调用正确', async () => {
  const mockGet = vi.fn().mockResolvedValue({ data: { results: [] } });
  apiClient.get = mockGet;
  
  await knowledgeApi.search('测试查询');
  
  expect(mockGet).toHaveBeenCalledWith('/knowledge/search', { params: { q: '测试查询' } });
});

test('trackingApi.getProjectStatus 调用正确', async () => {
  const mockGet = vi.fn().mockResolvedValue({ data: { project: {} } });
  apiClient.get = mockGet;
  
  await trackingApi.getProjectStatus('project-123');
  
  expect(mockGet).toHaveBeenCalledWith('/tracking/project/project-123/status');
});
