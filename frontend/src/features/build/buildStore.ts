import { create } from 'zustand';
import { crawlApi, CrawlTask } from './api/crawl';
import { KnowledgeFile } from '../../api/knowledge';

const POLL_INTERVAL = 3000;
const MAX_POLL_FAILURES = 3;
const TERMINAL_STATES = ['SUCCESS', 'FAILED', 'completed', 'failed'];

interface BuildState {
  // UI State
  activeTab: 'crawl' | 'review';

  // Crawl Tab
  selectedKnowledgeId: string | null;
  crawlUrls: string;
  tasks: CrawlTask[];
  activeTaskId: string | null;
  isPolling: boolean;
  pollingErrorCount: number;

  // Batch Import Modal
  isImportModalOpen: boolean;
  previewUrls: string[];

  // Review Tab
  pendingFiles: KnowledgeFile[];
  pendingReviewCount: number;
  selectedFile: KnowledgeFile | null;
  fileContent: string;
  isSaving: boolean;
  isIndexing: boolean;

  // Actions
  setActiveTab: (tab: 'crawl' | 'review') => void;
  setSelectedKnowledgeId: (id: string | null) => void;
  setCrawlUrls: (urls: string) => void;
  openImportModal: () => void;
  closeImportModal: () => void;
  setPreviewUrls: (urls: string[]) => void;
  submitBatchCrawl: (urls: string[]) => Promise<string | null>;
  fetchTasks: () => Promise<void>;
  startPolling: (taskId: string) => void;
  stopPolling: () => void;
  fetchTaskProgress: (taskId: string) => Promise<void>;
  removeTask: (taskId: string) => Promise<void>;
  retryFailedUrls: (taskId: string) => Promise<string | null>;
  clearCompletedTasks: () => Promise<void>;
  fetchPendingFiles: () => Promise<void>;
  fetchFileContent: (fileId: string) => Promise<void>;
  updateFileContent: (fileId: string, content: string) => Promise<void>;
  triggerIndex: (fileId: string) => Promise<void>;
  clearSelectedFile: () => void;
}

let pollIntervalId: ReturnType<typeof setInterval> | null = null;

export const buildStore = create<BuildState>((set, get) => ({
  // Initial state
  activeTab: 'crawl',
  selectedKnowledgeId: null,
  crawlUrls: '',
  tasks: [],
  activeTaskId: null,
  isPolling: false,
  pollingErrorCount: 0,
  isImportModalOpen: false,
  previewUrls: [],
  pendingFiles: [],
  pendingReviewCount: 0,
  selectedFile: null,
  fileContent: '',
  isSaving: false,
  isIndexing: false,

  // UI Actions
  setActiveTab: (tab) => set({ activeTab: tab }),

  setSelectedKnowledgeId: (id) => set({ selectedKnowledgeId: id }),

  setCrawlUrls: (urls) => set({ crawlUrls: urls }),

  openImportModal: () => set({ isImportModalOpen: true }),

  closeImportModal: () => set({ isImportModalOpen: false, previewUrls: [] }),

  setPreviewUrls: (urls) => set({ previewUrls: urls }),

  // Crawl Actions
  submitBatchCrawl: async (urls) => {
    const { selectedKnowledgeId } = get();
    if (!selectedKnowledgeId || urls.length === 0) return null;

    try {
      const taskId = await crawlApi.submitBatchCrawl(urls, selectedKnowledgeId);
      set({ activeTaskId: taskId });
      // Refresh task list
      await get().fetchTasks();
      // Start polling
      get().startPolling(taskId);
      return taskId;
    } catch (error) {
      console.error('Failed to submit batch crawl:', error);
      return null;
    }
  },

  fetchTasks: async () => {
    try {
      const tasks = await crawlApi.fetchTasks();
      set({ tasks });
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  },

  startPolling: (taskId) => {
    // Clear any existing polling
    if (pollIntervalId) {
      clearInterval(pollIntervalId);
    }

    set({ isPolling: true, pollingErrorCount: 0, activeTaskId: taskId });

    pollIntervalId = setInterval(async () => {
      const { stopPolling } = get();

      try {
        const task = await crawlApi.fetchTaskProgress(taskId);

        // Update task in list
        set((state) => ({
          tasks: state.tasks.map((t) => (t.id === taskId ? task : t)),
          pollingErrorCount: 0,
        }));

        // Check for terminal state
        if (TERMINAL_STATES.includes(task.status)) {
          stopPolling();
          // Refresh pending files count
          get().fetchPendingFiles();
        }
      } catch (error) {
        const { pollingErrorCount } = get();
        const newCount = pollingErrorCount + 1;

        if (newCount >= MAX_POLL_FAILURES) {
          stopPolling();
          console.error('Polling stopped due to network errors');
        } else {
          set({ pollingErrorCount: newCount });
        }
      }
    }, POLL_INTERVAL);
  },

  stopPolling: () => {
    if (pollIntervalId) {
      clearInterval(pollIntervalId);
      pollIntervalId = null;
    }
    set({ isPolling: false, pollingErrorCount: 0 });
  },

  fetchTaskProgress: async (taskId) => {
    try {
      const task = await crawlApi.fetchTaskProgress(taskId);
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === taskId ? task : t)),
      }));
    } catch (error) {
      console.error('Failed to fetch task progress:', error);
    }
  },

  removeTask: async (taskId) => {
    try {
      await crawlApi.deleteTask(taskId);
      set((state) => ({
        tasks: state.tasks.filter((t) => t.id !== taskId),
      }));
    } catch (error) {
      console.error('Failed to remove task:', error);
    }
  },

  retryFailedUrls: async (taskId) => {
    const task = get().tasks.find((t) => t.id === taskId);
    if (!task?.knowledge_id || !task.failed_urls?.length) return null;

    try {
      const failedUrls = task.failed_urls.map((f) => f.url);
      const newTaskId = await get().submitBatchCrawl(failedUrls);
      return newTaskId;
    } catch (error) {
      console.error('Failed to retry failed URLs:', error);
      return null;
    }
  },

  clearCompletedTasks: async () => {
    const { tasks, removeTask } = get();
    const terminalTasks = tasks.filter((t) =>
      TERMINAL_STATES.includes(t.status)
    );

    for (const task of terminalTasks) {
      await removeTask(task.id);
    }
  },

  // Review Actions
  fetchPendingFiles: async () => {
    try {
      const token = sessionStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const response = await fetch(`${baseUrl}/knowledge_file/pending_verify`, {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      if (response.ok) {
        const files = await response.json();
        set({ pendingFiles: files, pendingReviewCount: files.length });
      }
    } catch (error) {
      console.error('Failed to fetch pending files:', error);
    }
  },

  fetchFileContent: async (fileId) => {
    const { pendingFiles } = get();
    const file = pendingFiles.find((f) => f.id === fileId) || null;

    try {
      const token = sessionStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const response = await fetch(`${baseUrl}/knowledge_file/${fileId}/content`, {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      if (response.ok) {
        const content = await response.text();
        set({ selectedFile: file, fileContent: content });
      }
    } catch (error) {
      console.error('Failed to fetch file content:', error);
    }
  },

  updateFileContent: async (fileId, content) => {
    set({ isSaving: true });

    try {
      const token = sessionStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const response = await fetch(`${baseUrl}/knowledge_file/${fileId}/content`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ content }),
      });

      if (response.ok) {
        // Update file status in pendingFiles
        set((state) => ({
          pendingFiles: state.pendingFiles.map((f) =>
            f.id === fileId ? { ...f, status: 'verified' as const } : f
          ),
          isSaving: false,
        }));
      } else {
        set({ isSaving: false });
      }
    } catch (error) {
      console.error('Failed to update file content:', error);
      set({ isSaving: false });
    }
  },

  triggerIndex: async (fileId) => {
    set({ isIndexing: true });

    try {
      const token = sessionStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const response = await fetch(`${baseUrl}/knowledge_file/${fileId}/trigger_index`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ enable_vector: true, enable_keyword: true }),
      });

      if (response.ok) {
        // Remove from pending list (don't clear selectedFile yet, let component handle toast first)
        set((state) => ({
          pendingFiles: state.pendingFiles.filter((f) => f.id !== fileId),
          pendingReviewCount: Math.max(0, state.pendingReviewCount - 1),
          isIndexing: false,
        }));
      } else {
        set({ isIndexing: false });
      }
    } catch (error) {
      console.error('Failed to trigger index:', error);
      set({ isIndexing: false });
    }
  },

  clearSelectedFile: () => set({ selectedFile: null, fileContent: '' }),
}));
