import { create } from 'zustand';
import { knowledgeApi, KnowledgeBase, KnowledgeFile } from '../../api/knowledge';

interface KnowledgeListState {
  knowledgeBases: KnowledgeBase[];
  currentKB: KnowledgeBase | null;
  files: KnowledgeFile[];
  currentFile: KnowledgeFile | null;
  currentFileContent: string;
  isLoadingKBs: boolean;
  isLoadingFiles: boolean;
  isLoadingContent: boolean;
  error: string | null;
}

interface KnowledgeListActions {
  fetchKnowledgeBases: () => Promise<void>;
  fetchFiles: (kbId: string) => Promise<void>;
  fetchFileContent: (fileId: string) => Promise<void>;
  createKnowledgeBase: (name: string, description?: string) => Promise<void>;
  setCurrentKB: (kb: KnowledgeBase | null) => void;
  clearError: () => void;
}

type KnowledgeListStore = KnowledgeListState & KnowledgeListActions;

export const knowledgeListStore = create<KnowledgeListStore>((set, get) => ({
  knowledgeBases: [],
  currentKB: null,
  files: [],
  currentFile: null,
  currentFileContent: '',
  isLoadingKBs: false,
  isLoadingFiles: false,
  isLoadingContent: false,
  error: null,

  fetchKnowledgeBases: async () => {
    set({ isLoadingKBs: true, error: null });
    try {
      const kb = await knowledgeApi.fetchKnowledgeBases();
      set({ knowledgeBases: kb, isLoadingKBs: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch knowledge bases', isLoadingKBs: false });
    }
  },

  fetchFiles: async (kbId: string) => {
    set({ isLoadingFiles: true, error: null });
    try {
      const files = await knowledgeApi.fetchFiles(kbId);
      set({ files, isLoadingFiles: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch files', isLoadingFiles: false });
    }
  },

  fetchFileContent: async (fileId: string) => {
    set({ isLoadingContent: true, error: null });
    try {
      const file = get().files.find(f => f.id === fileId) || null;
      const content = await knowledgeApi.fetchFileContent(fileId);
      set({ currentFile: file, currentFileContent: content, isLoadingContent: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch file content', isLoadingContent: false });
    }
  },

  createKnowledgeBase: async (name: string, description?: string) => {
    set({ isLoadingKBs: true, error: null });
    try {
      const newKB = await knowledgeApi.createKnowledgeBase(name, description);
      set({ knowledgeBases: [...get().knowledgeBases, newKB], isLoadingKBs: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to create knowledge base', isLoadingKBs: false });
    }
  },

  setCurrentKB: (kb) => set({ currentKB: kb }),

  clearError: () => set({ error: null }),
}));