import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Agent {
  id: string;
  role: string;
  name: string;
  status: 'idle' | 'working' | 'blocked';
  description?: string;
  skills?: string[];
}

interface AgentState {
  agents: Agent[];
  loading: boolean;
  error: string | null;
  setAgents: (agents: Agent[]) => void;
  addAgent: (agent: Agent) => void;
  updateAgent: (id: string, data: Partial<Agent>) => void;
  deleteAgent: (id: string) => void;
  updateAgentStatus: (id: string, status: Agent['status']) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAgentStore = create<AgentState>()(
  persist(
    (set) => ({
      agents: [],
      loading: false,
      error: null,
      setAgents: (agents) => set({ agents, error: null }),
      addAgent: (agent) => set((state) => ({ agents: [...state.agents, agent] })),
      updateAgent: (id, data) => set((state) => ({
        agents: state.agents.map(a => a.id === id ? { ...a, ...data } : a)
      })),
      deleteAgent: (id) => set((state) => ({
        agents: state.agents.filter(a => a.id !== id)
      })),
      updateAgentStatus: (id, status) => set((state) => ({
        agents: state.agents.map(a => a.id === id ? { ...a, status } : a)
      })),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error })
    }),
    {
      name: 'agent-storage',
      partialize: (state) => ({ agents: state.agents })
    }
  )
);
