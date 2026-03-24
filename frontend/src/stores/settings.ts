import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Theme = 'light' | 'dark' | 'system';

interface SettingsState {
  theme: Theme;
  apiEndpoint: string;
  modelConfig: Record<string, string>;
  setTheme: (theme: Theme) => void;
  setApiEndpoint: (endpoint: string) => void;
  setModelConfig: (config: Record<string, string>) => void;
  updateModelConfig: (key: string, value: string) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'system',
      apiEndpoint: 'http://localhost:8000',
      modelConfig: {
        model: 'qwen-3.5-plus',
        temperature: '0.7'
      },
      setTheme: (theme) => set({ theme }),
      setApiEndpoint: (endpoint) => set({ apiEndpoint: endpoint }),
      setModelConfig: (config) => set({ modelConfig: config }),
      updateModelConfig: (key, value) => set((state) => ({
        modelConfig: { ...state.modelConfig, [key]: value }
      }))
    }),
    {
      name: 'settings-storage'
    }
  )
);
