import axios from 'axios';

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

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// API 服务层
export const projectApi = {
  list: () => apiClient.get('/projects'),
  get: (id: string) => apiClient.get(`/projects/${id}`),
  create: (data: any) => apiClient.post('/projects', data),
  update: (id: string, data: any) => apiClient.put(`/projects/${id}`, data),
  delete: (id: string) => apiClient.delete(`/projects/${id}`)
};

export const agentApi = {
  list: () => apiClient.get('/agents'),
  getStatus: (id: string) => apiClient.get(`/agents/${id}/status`),
  executeTask: (id: string, task: any) => apiClient.post(`/agents/${id}/tasks`, task)
};

export const knowledgeApi = {
  search: (query: string) => apiClient.get('/knowledge/search', { params: { q: query } }),
  addDocument: (data: any) => apiClient.post('/knowledge/documents', data),
  getCategories: () => apiClient.get('/knowledge/categories'),
  getTags: () => apiClient.get('/knowledge/tags')
};

export const trackingApi = {
  getProjectStatus: (id: string) => apiClient.get(`/tracking/project/${id}/status`),
  getTaskLogs: (taskId: string) => apiClient.get(`/tracking/task/${taskId}/logs`)
};
