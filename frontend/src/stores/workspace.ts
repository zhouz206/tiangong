import { create } from 'zustand';

interface WorkspaceState {
  currentWorkspaceId: string | null;
  workspaces: Array<{ id: string; name: string }>;
  setCurrentWorkspace: (id: string) => void;
  setWorkspaces: (workspaces: Array<{ id: string; name: string }>) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  currentWorkspaceId: null,
  workspaces: [],
  setCurrentWorkspace: (id) => set({ currentWorkspaceId: id }),
  setWorkspaces: (workspaces) => set({ workspaces })
}));
