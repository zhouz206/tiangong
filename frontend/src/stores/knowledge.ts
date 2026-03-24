import { create } from 'zustand';

interface KnowledgeDocument {
  id: string;
  title: string;
  category: string;
  tags: string[];
}

interface KnowledgeState {
  documents: KnowledgeDocument[];
  categories: string[];
  tags: string[];
  searchQuery: string;
  setDocuments: (documents: KnowledgeDocument[]) => void;
  setCategories: (categories: string[]) => void;
  setTags: (tags: string[]) => void;
  setSearchQuery: (query: string) => void;
}

export const useKnowledgeStore = create<KnowledgeState>((set) => ({
  documents: [],
  categories: [],
  tags: [],
  searchQuery: '',
  setDocuments: (documents) => set({ documents }),
  setCategories: (categories) => set({ categories }),
  setTags: (tags) => set({ tags }),
  setSearchQuery: (query) => set({ searchQuery: query })
}));
