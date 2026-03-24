import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

export type Theme = 'light' | 'dark' | 'system'

export type ModelProvider = 'openai' | 'anthropic' | 'qwen' | 'ollama'

export interface ModelConfig {
  id: string
  name: string
  provider: ModelProvider
  model_name: string
  api_key?: string
  endpoint?: string
  context_limit?: number
  priority: number
  cost_per_token?: number
  offline?: boolean
  enabled: boolean
}

export interface AgentConfig {
  id: string
  name: string
  role: string
  system_prompt: string
  model: string
  temperature: number
  max_tokens: number
  skills?: { name: string; enabled: boolean }[]
  mcp_services?: { name: string }[]
}

interface SettingsState {
  // Theme
  theme: Theme
  setTheme: (theme: Theme) => void

  // Models
  models: ModelConfig[]
  setModels: (models: ModelConfig[]) => void
  addModel: (model: ModelConfig) => void
  updateModel: (id: string, updates: Partial<ModelConfig>) => void
  deleteModel: (id: string) => void

  // Agent templates
  agentTemplates: AgentConfig[]
  setAgentTemplates: (templates: AgentConfig[]) => void

  // API settings
  apiBaseUrl: string
  setApiBaseUrl: (url: string) => void

  // WebSocket settings
  wsUrl: string
  setWsUrl: (url: string) => void

  // Loading state
  loading: boolean
  error: string | null
  clearError: () => void
}

export const useSettingsStore = create<SettingsState>()(
  devtools(
    (set) => ({
      // Theme
      theme: 'system',
      setTheme: (theme) => set({ theme }),

      // Models
      models: [],
      setModels: (models) => set({ models, error: null }),
      addModel: (model) =>
        set((state) => ({ models: [...state.models, model] })),
      updateModel: (id, updates) =>
        set((state) => ({
          models: state.models.map((m) =>
            m.id === id ? { ...m, ...updates } : m
          ),
        })),
      deleteModel: (id) =>
        set((state) => ({
          models: state.models.filter((m) => m.id !== id),
        })),

      // Agent templates
      agentTemplates: [],
      setAgentTemplates: (templates) => set({ agentTemplates: templates }),

      // API settings
      apiBaseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      setApiBaseUrl: (url) => set({ apiBaseUrl: url }),

      // WebSocket settings
      wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
      setWsUrl: (url) => set({ wsUrl: url }),

      // Loading state
      loading: false,
      error: null,
      clearError: () => set({ error: null }),
    }),
    { name: 'settings-storage' }
  )
)
