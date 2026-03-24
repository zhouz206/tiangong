// API 响应类型声明
// 由于 axios 拦截器返回 response.data，我们需要重新定义返回类型

export interface Project {
  id: string;
  name: string;
  description: string;
  progress: number;
  phase: 'planning' | 'executing' | 'reviewing' | 'completed';
  status: 'active' | 'archived' | 'blocked';
  created_at?: string;
  milestones?: Array<{ id: string; name: string; progress: number; status: string }>;
  tasks?: Array<{ id: string; title: string; status: string; assignee?: string }>;
}

export interface Agent {
  id: string;
  role: string;
  name: string;
  status: 'idle' | 'working' | 'blocked';
  description?: string;
  skills?: string[];
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  category: string;
  tags: string[];
  content?: string;
  created_at?: string;
}

// 扩展 axios 响应类型
declare module 'axios' {
  interface AxiosResponse<T = any> {
    data: T;
  }
}
