import { create } from 'zustand';
import { knowledgeApi, KnowledgeBase, KnowledgeFile } from '../../api/knowledge';

interface KnowledgeState {
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

interface KnowledgeActions {
  fetchKnowledgeBases: () => Promise<void>;
  fetchFiles: (kbId: string) => Promise<void>;
  fetchFileContent: (fileId: string) => Promise<void>;
  setCurrentKB: (kb: KnowledgeBase | null) => void;
  clearError: () => void;
}

type KnowledgeStore = KnowledgeState & KnowledgeActions;

export const useKnowledgeStore = create<KnowledgeStore>((set, get) => ({
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
      set({ error: err instanceof Error ? err.message : 'Failed to fetch', isLoadingKBs: false });
    }
  },

  fetchFiles: async (kbId: string) => {
    set({ isLoadingFiles: true, error: null });
    try {
      // API 暂缺，用空数组代替，等后端实现
      set({ files: [], isLoadingFiles: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch files', isLoadingFiles: false });
    }
  },

  fetchFileContent: async (fileId: string) => {
    set({ isLoadingContent: true, error: null });
    const file = get().files.find(f => f.id === fileId) || null;
    try {
      const content = await knowledgeApi.getFileContent(fileId);
      set({ currentFile: file, currentFileContent: content, isLoadingContent: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch content', isLoadingContent: false });
    }
  },

  setCurrentKB: (kb) => set({ currentKB: kb }),
  clearError: () => set({ error: null }),
}));