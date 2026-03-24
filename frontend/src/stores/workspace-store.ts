import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export interface Workspace {
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
  member_count: number
  project_count: number
}

interface WorkspaceState {
  currentWorkspace: Workspace | null
  workspaces: Workspace[]
  loading: boolean
  error: string | null
  setCurrentWorkspace: (workspace: Workspace) => void
  fetchWorkspaces: () => Promise<void>
  clearError: () => void
}

export const useWorkspaceStore = create<WorkspaceState>()(
  devtools(
    persist(
      (set) => ({
        currentWorkspace: null,
        workspaces: [],
        loading: false,
        error: null,

        setCurrentWorkspace: (workspace) =>
          set({ currentWorkspace: workspace, error: null }),

        fetchWorkspaces: async () => {
          set({ loading: true, error: null })
          try {
            // TODO: Replace with actual API call
            // const response = await api.get('/workspaces')
            // set({ workspaces: response.data, loading: false })
            set({ loading: false })
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch workspaces',
              loading: false
            })
          }
        },

        clearError: () => set({ error: null }),
      }),
      { name: 'workspace-storage' }
    )
  )
)
