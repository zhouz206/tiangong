import { create } from 'zustand';

interface Agent {
  id: string;
  role: string;
  name: string;
  status: 'idle' | 'working' | 'blocked';
}

interface AgentState {
  agents: Agent[];
  setAgents: (agents: Agent[]) => void;
  updateAgentStatus: (id: string, status: 'idle' | 'working' | 'blocked') => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  agents: [],
  setAgents: (agents) => set({ agents }),
  updateAgentStatus: (id, status) => set((state) => ({
    agents: state.agents.map(a => a.id === id ? { ...a, status } : a)
  }))
}));
