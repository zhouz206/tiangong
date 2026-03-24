import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

export type AgentRole =
  | 'manager'
  | 'researcher'
  | 'coder'
  | 'designer'
  | 'writer'
  | 'reviewer'
  | 'data_analyst'
  | 'knowledge_manager'

export type AgentStatus = 'idle' | 'working' | 'waiting' | 'error'

export interface Agent {
  id: string
  name: string
  role: AgentRole
  description: string
  status: AgentStatus
  model: string
  project_id?: string
  upstream_agents?: string[]
  downstream_agents?: string[]
  capabilities?: string[]
  created_at: string
  updated_at: string
}

interface AgentState {
  agents: Agent[]
  loading: boolean
  error: string | null
  setAgents: (agents: Agent[]) => void
  updateAgentStatus: (id: string, status: AgentStatus) => void
  addAgent: (agent: Agent) => void
  removeAgent: (id: string) => void
  clearError: () => void
}

export const useAgentStore = create<AgentState>()(
  devtools((set) => ({
    agents: [],
    loading: false,
    error: null,

    setAgents: (agents) => set({ agents, error: null }),

    updateAgentStatus: (id, status) =>
      set((state) => ({
        agents: state.agents.map((a) =>
          a.id === id ? { ...a, status } : a
        ),
      })),

    addAgent: (agent) =>
      set((state) => ({ agents: [...state.agents, agent] })),

    removeAgent: (id) =>
      set((state) => ({
        agents: state.agents.filter((a) => a.id !== id),
      })),

    clearError: () => set({ error: null }),
  }))
)
