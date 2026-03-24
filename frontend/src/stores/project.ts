import { create } from 'zustand';

interface Project {
  id: string;
  name: string;
  description: string;
  progress: number;
  phase: string;
  status: string;
}

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  loading: boolean;
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  updateProjectProgress: (id: string, progress: number) => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  currentProject: null,
  loading: false,
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (project) => set({ currentProject: project }),
  updateProjectProgress: (id, progress) => set((state) => ({
    projects: state.projects.map(p => p.id === id ? { ...p, progress } : p)
  }))
}));
