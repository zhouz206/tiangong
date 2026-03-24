import { create } from 'zustand';

interface SettingsState {
  theme: 'light' | 'dark' | 'system';
  apiEndpoint: string;
  modelConfig: Record<string, string>;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  setApiEndpoint: (endpoint: string) => void;
  setModelConfig: (config: Record<string, string>) => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  theme: 'system',
  apiEndpoint: 'http://localhost:8000',
  modelConfig: {},
  setTheme: (theme) => set({ theme }),
  setApiEndpoint: (endpoint) => set({ apiEndpoint: endpoint }),
  setModelConfig: (config) => set({ modelConfig: config })
}));
