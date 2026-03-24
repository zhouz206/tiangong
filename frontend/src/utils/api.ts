import axios, { AxiosError } from 'axios';

const API_BASE = '/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 - 返回 response.data
apiClient.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(new Error(error.response?.data ? JSON.stringify(error.response.data) : error.message || '请求失败'));
  }
);

export default apiClient;

// API 服务层
// 注意：由于响应拦截器返回 response.data，类型需要特殊处理
export const projectApi = {
  list: async () => {
    const result = await apiClient.get('/projects');
    return result as any;
  },
  get: async (id: string) => {
    const result = await apiClient.get(`/projects/${id}`);
    return result as any;
  },
  create: async (data: { name: string; description: string; template?: string }) => {
    const result = await apiClient.post('/projects', data);
    return result as any;
  },
  update: async (id: string, data: any) => {
    const result = await apiClient.put(`/projects/${id}`, data);
    return result as any;
  },
  delete: async (id: string) => {
    const result = await apiClient.delete(`/projects/${id}`);
    return result as any;
  },
  updatePhase: async (id: string, phase: string) => {
    const result = await apiClient.patch(`/projects/${id}/phase`, { phase });
    return result as any;
  },
  updateTaskStatus: async (_projectId: string, taskId: string, status: string) => {
    const result = await apiClient.patch(`/projects/tasks/${taskId}`, { status });
    return result as any;
  }
};

export const agentApi = {
  list: async () => {
    const result = await apiClient.get('/agents');
    return result as any;
  },
  getStatus: async (id: string) => {
    const result = await apiClient.get(`/agents/${id}/status`);
    return result as any;
  },
  executeTask: async (id: string, task: any) => {
    const result = await apiClient.post(`/agents/${id}/tasks`, task);
    return result as any;
  },
  configure: async (id: string, config: any) => {
    const result = await apiClient.put(`/agents/${id}/config`, config);
    return result as any;
  }
};

export const knowledgeApi = {
  search: async (query: string) => {
    const result = await apiClient.get('/knowledge/search', { params: { q: query } });
    return result as any;
  },
  addDocument: async (data: { title: string; category: string; tags: string[]; content?: string }) => {
    const result = await apiClient.post('/knowledge/documents', data);
    return result as any;
  },
  getCategories: async () => {
    const result = await apiClient.get('/knowledge/categories');
    return result as any;
  },
  getTags: async () => {
    const result = await apiClient.get('/knowledge/tags');
    return result as any;
  },
  deleteDocument: async (id: string) => {
    const result = await apiClient.delete(`/knowledge/documents/${id}`);
    return result as any;
  }
};

export const trackingApi = {
  getProjectStatus: async (id: string) => {
    const result = await apiClient.get(`/tracking/project/${id}/status`);
    return result as any;
  },
  getTaskLogs: async (taskId: string) => {
    const result = await apiClient.get(`/tracking/task/${taskId}/logs`);
    return result as any;
  }
};
