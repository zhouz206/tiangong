import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

export type ProjectStatus = 'active' | 'paused' | 'completed' | 'cancelled'
export type ProjectPhase = 'planning' | 'execution' | 'review' | 'done'

export interface Project {
  id: string
  name: string
  description: string
  status: ProjectStatus
  phase: ProjectPhase
  workspace_id: string
  template_id?: string
  created_at: string
  updated_at: string
  task_count?: number
  agent_count?: number
}

interface ProjectState {
  projects: Project[]
  currentProject: Project | null
  loading: boolean
  error: string | null
  setProjects: (projects: Project[]) => void
  setCurrentProject: (project: Project) => void
  addProject: (project: Project) => void
  updateProject: (id: string, updates: Partial<Project>) => void
  deleteProject: (id: string) => void
  fetchProjects: (workspaceId: string) => Promise<void>
  clearError: () => void
}

export const useProjectStore = create<ProjectState>()(
  devtools((set) => ({
    projects: [],
    currentProject: null,
    loading: false,
    error: null,

    setProjects: (projects) => set({ projects, error: null }),

    setCurrentProject: (project) => set({ currentProject: project, error: null }),

    addProject: (project) =>
      set((state) => ({ projects: [...state.projects, project] })),

    updateProject: (id, updates) =>
      set((state) => ({
        projects: state.projects.map((p) =>
          p.id === id ? { ...p, ...updates } : p
        ),
        currentProject: state.currentProject?.id === id
          ? { ...state.currentProject, ...updates }
          : state.currentProject,
      })),

    deleteProject: (id) =>
      set((state) => ({
        projects: state.projects.filter((p) => p.id !== id),
        currentProject: state.currentProject?.id === id ? null : state.currentProject,
      })),

    fetchProjects: async (_workspaceId: string) => {
      set({ loading: true, error: null })
      try {
        // TODO: Replace with actual API call
        // const response = await api.get(`/workspaces/${workspaceId}/projects`)
        // set({ projects: response.data, loading: false })
        set({ loading: false })
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch projects',
          loading: false,
        })
      }
    },

    clearError: () => set({ error: null }),
  }))
)
