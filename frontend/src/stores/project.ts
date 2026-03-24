import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  loading: boolean;
  error: string | null;
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
  updateProject: (id: string, data: Partial<Project>) => void;
  deleteProject: (id: string) => void;
  updateProjectProgress: (id: string, progress: number) => void;
  updateProjectPhase: (id: string, phase: Project['phase']) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set) => ({
      projects: [],
      currentProject: null,
      loading: false,
      error: null,
      setProjects: (projects) => set({ projects, error: null }),
      setCurrentProject: (project) => set({ currentProject: project }),
      addProject: (project) => set((state) => ({ projects: [...state.projects, project] })),
      updateProject: (id, data) => set((state) => ({
        projects: state.projects.map(p => p.id === id ? { ...p, ...data } : p),
        currentProject: state.currentProject?.id === id ? { ...state.currentProject, ...data } : state.currentProject
      })),
      deleteProject: (id) => set((state) => ({
        projects: state.projects.filter(p => p.id !== id),
        currentProject: state.currentProject?.id === id ? null : state.currentProject
      })),
      updateProjectProgress: (id, progress) => set((state) => ({
        projects: state.projects.map(p => p.id === id ? { ...p, progress } : p),
        currentProject: state.currentProject?.id === id ? { ...state.currentProject, progress } : state.currentProject
      })),
      updateProjectPhase: (id, phase) => set((state) => ({
        projects: state.projects.map(p => p.id === id ? { ...p, phase } : p),
        currentProject: state.currentProject?.id === id ? { ...state.currentProject, phase } : state.currentProject
      })),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error })
    }),
    {
      name: 'project-storage',
      partialize: (state) => ({ projects: state.projects, currentProject: state.currentProject })
    }
  )
);
