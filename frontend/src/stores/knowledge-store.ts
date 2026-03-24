import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

export interface KnowledgeDocument {
  id: string
  title: string
  content: string
  type: 'project_doc' | 'discussion' | 'reference' | 'experience' | 'code_snippet'
  category?: string
  tags: string[]
  project_id?: string
  created_at: string
  updated_at: string
}

interface KnowledgeState {
  documents: KnowledgeDocument[]
  categories: string[]
  tags: string[]
  loading: boolean
  error: string | null
  setDocuments: (documents: KnowledgeDocument[]) => void
  addDocument: (document: KnowledgeDocument) => void
  updateDocument: (id: string, updates: Partial<KnowledgeDocument>) => void
  deleteDocument: (id: string) => void
  setCategories: (categories: string[]) => void
  setTags: (tags: string[]) => void
  searchDocuments: (query: string) => Promise<KnowledgeDocument[]>
  clearError: () => void
}

export const useKnowledgeStore = create<KnowledgeState>()(
  devtools((set) => ({
    documents: [],
    categories: [],
    tags: [],
    loading: false,
    error: null,

    setDocuments: (documents) => set({ documents, error: null }),

    addDocument: (document) =>
      set((state) => ({ documents: [...state.documents, document] })),

    updateDocument: (id, updates) =>
      set((state) => ({
        documents: state.documents.map((d) =>
          d.id === id ? { ...d, ...updates } : d
        ),
      })),

    deleteDocument: (id) =>
      set((state) => ({
        documents: state.documents.filter((d) => d.id !== id),
      })),

    setCategories: (categories) => set({ categories }),

    setTags: (tags) => set({ tags }),

    searchDocuments: async (_query: string) => {
      set({ loading: true, error: null })
      try {
        // TODO: Replace with actual API call
        // const response = await api.get('/knowledge/search', { params: { q: query } })
        // set({ documents: response.data, loading: false })
        set({ loading: false })
        return []
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Search failed',
          loading: false,
        })
        return []
      }
    },

    clearError: () => set({ error: null }),
  }))
)
