import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface KnowledgeDocument {
  id: string;
  title: string;
  category: string;
  tags: string[];
  content?: string;
  created_at?: string;
}

interface KnowledgeState {
  documents: KnowledgeDocument[];
  categories: string[];
  tags: string[];
  searchQuery: string;
  loading: boolean;
  error: string | null;
  setDocuments: (documents: KnowledgeDocument[]) => void;
  addDocument: (document: KnowledgeDocument) => void;
  deleteDocument: (id: string) => void;
  setCategories: (categories: string[]) => void;
  setTags: (tags: string[]) => void;
  setSearchQuery: (query: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useKnowledgeStore = create<KnowledgeState>()(
  persist(
    (set) => ({
      documents: [],
      categories: [],
      tags: [],
      searchQuery: '',
      loading: false,
      error: null,
      setDocuments: (documents) => set({ documents, error: null }),
      addDocument: (doc) => set((state) => ({ documents: [...state.documents, doc] })),
      deleteDocument: (id) => set((state) => ({
        documents: state.documents.filter(d => d.id !== id)
      })),
      setCategories: (categories) => set({ categories }),
      setTags: (tags) => set({ tags }),
      setSearchQuery: (query) => set({ searchQuery: query }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error })
    }),
    {
      name: 'knowledge-storage',
      partialize: (state) => ({ documents: state.documents, categories: state.categories, tags: state.tags })
    }
  )
);
