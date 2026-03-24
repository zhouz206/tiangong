// API 服务封装

import { api } from './api'
import type { Project, ProjectStatus, ProjectPhase } from '@/stores/project-store'
import type { Agent, AgentRole, AgentStatus } from '@/stores/agent-store'
import type { KnowledgeDocument } from '@/stores/knowledge-store'
import type { ModelConfig, AgentConfig } from '@/stores/settings-store'

// Workspace API
export const workspaceApi = {
  getList: () => api.get<{ id: string; name: string }[]>('/workspaces'),
  getById: (id: string) => api.get(`/workspaces/${id}`),
  create: (data: { name: string; description?: string }) =>
    api.post('/workspaces', data),
  update: (id: string, data: { name?: string; description?: string }) =>
    api.put(`/workspaces/${id}`, data),
  delete: (id: string) => api.delete(`/workspaces/${id}`),
  getMembers: (id: string) => api.get(`/workspaces/${id}/members`),
  addMember: (id: string, data: { user_id: string; role: string }) =>
    api.post(`/workspaces/${id}/members`, data),
  removeMember: (id: string, userId: string) =>
    api.delete(`/workspaces/${id}/members/${userId}`),
}

// Project API
export const projectApi = {
  getList: (workspaceId: string) =>
    api.get<Project[]>(`/workspaces/${workspaceId}/projects`),
  getById: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (data: {
    workspace_id: string
    name: string
    description?: string
    template_id?: string
  }) => api.post('/projects', data),
  update: (id: string, data: Partial<Project>) =>
    api.put(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
  updateStatus: (id: string, status: ProjectStatus) =>
    api.patch(`/projects/${id}/status`, { status }),
  updatePhase: (id: string, phase: ProjectPhase) =>
    api.patch(`/projects/${id}/phase`, { phase }),
  getTasks: (id: string) => api.get(`/projects/${id}/tasks`),
  getAgents: (id: string) => api.get<Agent[]>(`/projects/${id}/agents`),
}

// Agent API
export const agentApi = {
  getList: (projectId?: string) =>
    api.get<Agent[]>(`/agents${projectId ? `?project_id=${projectId}` : ''}`),
  getById: (id: string) => api.get<Agent>(`/agents/${id}`),
  create: (data: {
    project_id: string
    name: string
    role: AgentRole
    model: string
  }) => api.post('/agents', data),
  update: (id: string, data: Partial<Agent>) =>
    api.put(`/agents/${id}`, data),
  delete: (id: string) => api.delete(`/agents/${id}`),
  updateStatus: (id: string, status: AgentStatus) =>
    api.patch(`/agents/${id}/status`, { status }),
  execute: (id: string, task: string) =>
    api.post(`/agents/${id}/execute`, { task }),
}

// Knowledge API
export const knowledgeApi = {
  getList: (projectId?: string) =>
    api.get<KnowledgeDocument[]>(
      `/knowledge${projectId ? `?project_id=${projectId}` : ''}`
    ),
  getById: (id: string) => api.get<KnowledgeDocument>(`/knowledge/${id}`),
  create: (data: {
    title: string
    content: string
    type: KnowledgeDocument['type']
    project_id?: string
    tags?: string[]
  }) => api.post('/knowledge', data),
  update: (id: string, data: Partial<KnowledgeDocument>) =>
    api.put(`/knowledge/${id}`, data),
  delete: (id: string) => api.delete(`/knowledge/${id}`),
  search: (query: string, projectId?: string) =>
    api.get<KnowledgeDocument[]>('/knowledge/search', {
      params: { q: query, project_id: projectId },
    }),
  getCategories: (projectId?: string) =>
    api.get<string[]>('/knowledge/categories', {
      params: { project_id: projectId },
    }),
  getTags: (projectId?: string) =>
    api.get<string[]>('/knowledge/tags', {
      params: { project_id: projectId },
    }),
}

// Model API
export const modelApi = {
  getList: () => api.get<ModelConfig[]>('/models'),
  getById: (id: string) => api.get<ModelConfig>(`/models/${id}`),
  create: (data: Omit<ModelConfig, 'id'>) => api.post('/models', data),
  update: (id: string, data: Partial<ModelConfig>) =>
    api.put(`/models/${id}`, data),
  delete: (id: string) => api.delete(`/models/${id}`),
  test: (id: string) => api.post(`/models/${id}/test`),
}

// Agent Template API
export const agentTemplateApi = {
  getList: () => api.get<AgentConfig[]>('/agent-templates'),
  getById: (id: string) => api.get<AgentConfig>(`/agent-templates/${id}`),
  create: (data: Omit<AgentConfig, 'id'>) =>
    api.post('/agent-templates', data),
  update: (id: string, data: Partial<AgentConfig>) =>
    api.put(`/agent-templates/${id}`, data),
  delete: (id: string) => api.delete(`/agent-templates/${id}`),
}

// Stats API
export const statsApi = {
  getOverview: () =>
    api.get<{
      total_projects: number
      active_projects: number
      total_agents: number
      total_tasks: number
      token_usage: number
      cost: number
    }>('/stats/overview'),
  getProjectStats: (projectId: string) =>
    api.get(`/stats/projects/${projectId}`),
  getTokenUsage: (startDate?: string, endDate?: string) =>
    api.get('/stats/token-usage', { params: { start: startDate, end: endDate } }),
}
