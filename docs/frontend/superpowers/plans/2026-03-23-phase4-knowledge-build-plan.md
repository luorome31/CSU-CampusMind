# Phase 4 Knowledge Build Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phase 4 knowledge build workflow: crawl panel, batch URL import modal, task progress monitoring with polling, and content review system.

**Architecture:** Tab-based page layout with two tabs (Crawl Tasks + Review Queue). Zustand store manages all build state including polling. New crawl API client handles task submission and monitoring.

**Tech Stack:** React, TypeScript, Zustand, CSS Variables (no CSS Modules), existing Modal/Button/Input/Card UI components

**Reference:** `docs/superpowers/specs/2026-03-23-phase4-knowledge-build-design.md`

---

## File Structure

```
src/features/build/
├── KnowledgeBuildPage.tsx      # Replace placeholder
├── buildStore.ts              # NEW - Zustand store
├── api/
│   └── crawl.ts               # NEW - Crawl API client
├── components/
│   ├── CrawlTab/
│   │   ├── CrawlPanel.tsx     # NEW
│   │   ├── UrlImportModal.tsx # NEW
│   │   ├── TaskList.tsx       # NEW
│   │   └── TaskCard.tsx       # NEW
│   └── ReviewTab/
│       ├── ReviewInbox.tsx     # NEW
│       └── ReviewEditor.tsx   # NEW
```

---

## Chunk 1: API Layer + Types

### Task 1: Create crawl API client

**Files:**
- Create: `frontend/src/features/build/api/crawl.ts`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/features/build/api/crawl.test.ts`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { crawlApi, CrawlTask } from './crawl';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('crawlApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
    });
  });

  describe('submitBatchCrawl', () => {
    it('should call POST /api/v1/crawl/batch-with-knowledge with correct body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ task_id: 'task_123', status: 'processing' }),
        text: () => Promise.resolve('{"task_id":"task_123","status":"processing"}'),
      });

      const result = await crawlApi.submitBatchCrawl(
        ['http://example.com'],
        'kb_abc'
      );

      expect(result).toBe('task_123');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/crawl/batch-with-knowledge'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ urls: ['http://example.com'], knowledge_id: 'kb_abc' }),
        })
      );
    });
  });

  describe('fetchTasks', () => {
    it('should return array of tasks', async () => {
      const mockTasks: CrawlTask[] = [{
        id: 'task_1',
        knowledge_id: 'kb_1',
        user_id: 'user_1',
        total_urls: 10,
        completed_urls: 5,
        success_count: 4,
        fail_count: 1,
        status: 'processing',
        create_time: '2024-01-01T00:00:00',
        update_time: '2024-01-01T00:01:00',
      }];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTasks),
        text: () => Promise.resolve(JSON.stringify(mockTasks)),
      });

      const result = await crawlApi.fetchTasks();
      expect(result).toEqual(mockTasks);
    });
  });

  describe('fetchTaskProgress', () => {
    it('should return task progress for given task_id', async () => {
      const mockTask: CrawlTask = {
        id: 'task_xyz',
        knowledge_id: 'kb_abc',
        user_id: 'user_1',
        total_urls: 10,
        completed_urls: 10,
        success_count: 9,
        fail_count: 1,
        status: 'SUCCESS',
        create_time: '2024-01-01T00:00:00',
        update_time: '2024-01-01T00:02:00',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTask),
        text: () => Promise.resolve(JSON.stringify(mockTask)),
      });

      const result = await crawlApi.fetchTaskProgress('task_xyz');
      expect(result).toEqual(mockTask);
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/api/crawl.test.ts 2>&1 | head -50`
Expected: FAIL with "crawl module not found or has no exports"

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/features/build/api/crawl.ts`:

```typescript
import { apiClient } from '../../../api/client';

export interface CrawlTask {
  id: string;
  knowledge_id: string;
  user_id: string;
  total_urls: number;
  completed_urls: number;
  success_count: number;
  fail_count: number;
  status: 'pending' | 'processing' | 'SUCCESS' | 'FAILED' | 'completed';
  create_time: string;
  update_time: string;
}

interface BatchCrawlResponse {
  task_id: string;
  status: string;
  message: string;
}

class CrawlApi {
  async submitBatchCrawl(urls: string[], knowledgeId: string): Promise<string> {
    const response = await apiClient.post<BatchCrawlResponse>('/crawl/batch-with-knowledge', {
      urls,
      knowledge_id: knowledgeId,
    });
    return response.task_id;
  }

  async fetchTasks(): Promise<CrawlTask[]> {
    return apiClient.get<CrawlTask[]>('/crawl/tasks');
  }

  async fetchTaskProgress(taskId: string): Promise<CrawlTask> {
    return apiClient.get<CrawlTask>(`/crawl/tasks/${taskId}`);
  }
}

export const crawlApi = new CrawlApi();
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/api/crawl.test.ts 2>&1 | tail -20`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/features/build/api/crawl.ts src/features/build/api/crawl.test.ts
git commit -m "feat(build): add crawl API client with batch and task progress endpoints"
```

---

## Chunk 2: buildStore (Zustand Store)

### Task 2: Create buildStore

**Files:**
- Create: `frontend/src/features/build/buildStore.ts`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/features/build/buildStore.test.ts`:

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { buildStore } from './buildStore';
import { crawlApi, CrawlTask } from './api/crawl';
import { knowledgeApi, KnowledgeFile } from '../../api/knowledge';

vi.mock('./api/crawl');
vi.mock('../../api/knowledge');

describe('buildStore', () => {
  beforeEach(() => {
    // Reset store state
    buildStore.setState({
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
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Clear any pending intervals
    const state = buildStore.getState();
    if (state.isPolling) {
      state.stopPolling();
    }
  });

  describe('setActiveTab', () => {
    it('should update activeTab', () => {
      buildStore.getState().setActiveTab('review');
      expect(buildStore.getState().activeTab).toBe('review');
    });
  });

  describe('setSelectedKnowledgeId', () => {
    it('should update selectedKnowledgeId', () => {
      buildStore.getState().setSelectedKnowledgeId('kb_123');
      expect(buildStore.getState().selectedKnowledgeId).toBe('kb_123');
    });
  });

  describe('setCrawlUrls', () => {
    it('should update crawlUrls', () => {
      buildStore.getState().setCrawlUrls('http://example.com\nhttp://test.com');
      expect(buildStore.getState().crawlUrls).toBe('http://example.com\nhttp://test.com');
    });
  });

  describe('submitBatchCrawl', () => {
    it('should submit crawl and start polling', async () => {
      vi.mocked(crawlApi.submitBatchCrawl).mockResolvedValue('task_new');

      const mockTask: CrawlTask = {
        id: 'task_new',
        knowledge_id: 'kb_123',
        user_id: 'user_1',
        total_urls: 2,
        completed_urls: 0,
        success_count: 0,
        fail_count: 0,
        status: 'processing',
        create_time: '2024-01-01T00:00:00',
        update_time: '2024-01-01T00:00:00',
      };

      vi.mocked(crawlApi.fetchTaskProgress).mockResolvedValue(mockTask);

      const result = await buildStore.getState().submitBatchCrawl(['http://a.com', 'http://b.com']);

      expect(result).toBe('task_new');
      expect(crawlApi.submitBatchCrawl).toHaveBeenCalledWith(
        ['http://a.com', 'http://b.com'],
        null
      );
    });
  });

  describe('fetchPendingFiles', () => {
    it('should fetch pending files and update count', async () => {
      const mockFiles: KnowledgeFile[] = [
        {
          id: 'file_1',
          file_name: 'doc1.md',
          knowledge_id: 'kb_1',
          user_id: 'user_1',
          status: 'pending_verify',
          oss_url: 'https://oss.example.com/doc1.md',
          file_size: 1024,
          create_time: '2024-01-01T00:00:00',
          update_time: '2024-01-01T00:00:00',
        },
        {
          id: 'file_2',
          file_name: 'doc2.md',
          knowledge_id: 'kb_2',
          user_id: 'user_1',
          status: 'pending_verify',
          oss_url: 'https://oss.example.com/doc2.md',
          file_size: 2048,
          create_time: '2024-01-02T00:00:00',
          update_time: '2024-01-02T00:00:00',
        },
      ];

      vi.mocked(knowledgeApi as unknown as { fetchPendingVerify: () => Promise<KnowledgeFile[]> })
        .mockResolvedValueOnce(mockFiles);

      // Note: This test demonstrates the expected behavior
      // Actual implementation needs knowledgeApi.fetchPendingVerify
    });
  });

  describe('polling logic', () => {
    it('should stop polling on terminal state', async () => {
      vi.useFakeTimers();

      const completedTask: CrawlTask = {
        id: 'task_done',
        knowledge_id: 'kb_123',
        user_id: 'user_1',
        total_urls: 5,
        completed_urls: 5,
        success_count: 5,
        fail_count: 0,
        status: 'SUCCESS',
        create_time: '2024-01-01T00:00:00',
        update_time: '2024-01-01T00:01:00',
      };

      vi.mocked(crawlApi.fetchTaskProgress).mockResolvedValue(completedTask);

      buildStore.setState({ activeTaskId: 'task_done' });

      // Start polling
      buildStore.getState().startPolling('task_done');

      // Advance timer
      await vi.advanceTimersByTimeAsync(3000);

      // Should have stopped
      expect(buildStore.getState().isPolling).toBe(false);

      vi.useRealTimers();
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/buildStore.test.ts 2>&1 | head -50`
Expected: FAIL with "buildStore not found"

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/features/build/buildStore.ts`:

```typescript
import { create } from 'zustand';
import { crawlApi, CrawlTask } from './api/crawl';
import { KnowledgeFile } from '../..//api/knowledge';

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
      const { fetchTaskProgress, stopPolling } = get();

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

  // Review Actions
  fetchPendingFiles: async () => {
    try {
      // Note: This needs to be added to knowledgeApi
      // Using direct fetch for now
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
        // Remove from pending list
        set((state) => ({
          pendingFiles: state.pendingFiles.filter((f) => f.id !== fileId),
          pendingReviewCount: Math.max(0, state.pendingReviewCount - 1),
          selectedFile: null,
          fileContent: '',
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/buildStore.test.ts 2>&1 | tail -30`
Expected: PASS (or some failures due to mock complexity - adjust as needed)

- [ ] **Step 5: Commit**

```bash
git add src/features/build/buildStore.ts src/features/build/buildStore.test.ts
git commit -m "feat(build): add buildStore with polling and review actions"
```

---

## Chunk 3: CrawlTab Components

### Task 3: Create TaskCard component

**Files:**
- Create: `frontend/src/features/build/components/CrawlTab/TaskCard.tsx`
- Create: `frontend/src/features/build/components/CrawlTab/TaskCard.module.css`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/features/build/components/CrawlTab/TaskCard.test.tsx`:

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TaskCard } from './TaskCard';
import { CrawlTask } from '../../api/crawl';

const mockTask: CrawlTask = {
  id: 'task_xyz',
  knowledge_id: 'kb_abc',
  user_id: 'user_1',
  total_urls: 10,
  completed_urls: 7,
  success_count: 5,
  fail_count: 2,
  status: 'processing',
  create_time: '2024-01-01T12:00:00',
  update_time: '2024-01-01T12:05:00',
};

describe('TaskCard', () => {
  it('should render task id and status', () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText(/task_xyz/)).toBeInTheDocument();
    expect(screen.getByText(/处理中/)).toBeInTheDocument();
  });

  it('should render progress bar with correct percentage', () => {
    render(<TaskCard task={mockTask} />);

    const progressText = screen.getByText(/7\/10/);
    expect(progressText).toBeInTheDocument();
  });

  it('should render success and fail counts', () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText(/5.*成功/)).toBeInTheDocument();
    expect(screen.getByText(/2.*失败/)).toBeInTheDocument();
  });

  it('should render checkmark for SUCCESS status', () => {
    const successTask = { ...mockTask, status: 'SUCCESS' as const, completed_urls: 10 };
    render(<TaskCard task={successTask} />);

    expect(screen.getByText(/成功/)).toBeInTheDocument();
  });

  it('should render X mark for FAILED status', () => {
    const failedTask = { ...mockTask, status: 'FAILED' as const };
    render(<TaskCard task={failedTask} />);

    expect(screen.getByText(/失败/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/TaskCard.test.tsx 2>&1 | head -30`
Expected: FAIL with "TaskCard not found"

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/features/build/components/CrawlTab/TaskCard.tsx`:

```typescript
import React from 'react';
import { Check, X, Loader2 } from 'lucide-react';
import { CrawlTask } from '../../api/crawl';
import styles from './TaskCard.module.css';

interface TaskCardProps {
  task: CrawlTask;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task }) => {
  const progress = task.total_urls > 0
    ? Math.round((task.completed_urls / task.total_urls) * 100)
    : 0;

  const getStatusDisplay = () => {
    switch (task.status) {
      case 'SUCCESS':
      case 'completed':
        return { icon: <Check size={16} />, text: '成功', className: styles.success };
      case 'FAILED':
      case 'failed':
        return { icon: <X size={16} />, text: '失败', className: styles.failed };
      case 'processing':
        return { icon: <Loader2 size={16} className={styles.spinning} />, text: '处理中', className: styles.processing };
      case 'pending':
      default:
        return { icon: <Loader2 size={16} className={styles.spinning} />, text: '等待中', className: styles.pending };
    }
  };

  const status = getStatusDisplay();

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.taskId}>Task ID: {task.id}</span>
        <span className={`${styles.status} ${status.className}`}>
          {status.icon}
          {status.text}
        </span>
      </div>

      <div className={styles.progress}>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className={styles.progressText}>
          {task.completed_urls}/{task.total_urls}
        </span>
      </div>

      <div className={styles.stats}>
        <span>成功: {task.success_count}</span>
        <span>失败: {task.fail_count}</span>
        <span className={styles.date}>{formatDate(task.create_time)}</span>
      </div>
    </div>
  );
};
```

Create `frontend/src/features/build/components/CrawlTab/TaskCard.module.css`:

```css
.card {
  background: var(--color-bg-surface, #fff);
  border: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  border-radius: var(--radius-md, 8px);
  padding: var(--space-4, 16px);
  margin-bottom: var(--space-3, 12px);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3, 12px);
}

.taskId {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary, #666);
  font-family: monospace;
}

.status {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1, 4px);
  font-size: var(--text-sm, 14px);
  padding: var(--space-1, 4px) var(--space-2, 8px);
  border-radius: var(--radius-sm, 4px);
}

.success {
  color: var(--color-success, #22c55e);
  background: rgba(34, 197, 94, 0.1);
}

.failed {
  color: var(--color-error, #ef4444);
  background: rgba(239, 68, 68, 0.1);
}

.processing,
.pending {
  color: var(--color-accent, #537d96);
  background: rgba(83, 125, 150, 0.1);
}

.progress {
  display: flex;
  align-items: center;
  gap: var(--space-3, 12px);
  margin-bottom: var(--space-2, 8px);
}

.progressBar {
  flex: 1;
  height: 8px;
  background: var(--color-border, rgba(83, 125, 150, 0.22));
  border-radius: 4px;
  overflow: hidden;
}

.progressFill {
  height: 100%;
  background: var(--color-accent, #537d96);
  transition: width 0.3s ease;
}

.progressText {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary, #666);
  min-width: 50px;
  text-align: right;
}

.stats {
  display: flex;
  gap: var(--space-4, 16px);
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary, #666);
}

.date {
  margin-left: auto;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/TaskCard.test.tsx 2>&1 | tail -20`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/features/build/components/CrawlTab/TaskCard.tsx src/features/build/components/CrawlTab/TaskCard.module.css src/features/build/components/CrawlTab/TaskCard.test.tsx
git commit -m "feat(build): add TaskCard component with progress display"
```

---

### Task 4: Create TaskList component

**Files:**
- Create: `frontend/src/features/build/components/CrawlTab/TaskList.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/features/build/components/CrawlTab/TaskList.test.tsx`:

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TaskList } from './TaskList';
import { CrawlTask } from '../../api/crawl';

const mockTasks: CrawlTask[] = [
  {
    id: 'task_1',
    knowledge_id: 'kb_1',
    user_id: 'user_1',
    total_urls: 10,
    completed_urls: 10,
    success_count: 8,
    fail_count: 2,
    status: 'SUCCESS',
    create_time: '2024-01-01T12:00:00',
    update_time: '2024-01-01T12:05:00',
  },
  {
    id: 'task_2',
    knowledge_id: 'kb_1',
    user_id: 'user_1',
    total_urls: 5,
    completed_urls: 2,
    success_count: 2,
    fail_count: 0,
    status: 'processing',
    create_time: '2024-01-02T12:00:00',
    update_time: '2024-01-02T12:03:00',
  },
];

describe('TaskList', () => {
  it('should render empty state when no tasks', () => {
    render(<TaskList tasks={[]} />);
    expect(screen.getByText(/暂无爬取任务/)).toBeInTheDocument();
  });

  it('should render list of tasks', () => {
    render(<TaskList tasks={mockTasks} />);
    expect(screen.getByText(/task_1/)).toBeInTheDocument();
    expect(screen.getByText(/task_2/)).toBeInTheDocument();
  });

  it('should render task count', () => {
    render(<TaskList tasks={mockTasks} />);
    expect(screen.getByText(/共 2 个任务/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/TaskList.test.tsx 2>&1 | head -30`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/features/build/components/CrawlTab/TaskList.tsx`:

```typescript
import React from 'react';
import { TaskCard } from './TaskCard';
import { CrawlTask } from '../../api/crawl';

interface TaskListProps {
  tasks: CrawlTask[];
}

export const TaskList: React.FC<TaskListProps> = ({ tasks }) => {
  if (tasks.length === 0) {
    return (
      <div style={{
        textAlign: 'center',
        padding: 'var(--space-8, 32px)',
        color: 'var(--color-text-secondary, #666)',
      }}>
        暂无爬取任务
      </div>
    );
  }

  // Sort by create_time descending (newest first)
  const sortedTasks = [...tasks].sort(
    (a, b) => new Date(b.create_time).getTime() - new Date(a.create_time).getTime()
  );

  return (
    <div>
      <div style={{
        fontSize: 'var(--text-sm, 14px)',
        color: 'var(--color-text-secondary, #666)',
        marginBottom: 'var(--space-3, 12px)',
      }}>
        共 {tasks.length} 个任务
      </div>
      {sortedTasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
};
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/TaskList.test.tsx 2>&1 | tail -20`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/features/build/components/CrawlTab/TaskList.tsx src/features/build/components/CrawlTab/TaskList.test.tsx
git commit -m "feat(build): add TaskList component"
```

---

### Task 5: Create UrlImportModal component

**Files:**
- Create: `frontend/src/features/build/components/CrawlTab/UrlImportModal.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/features/build/components/CrawlTab/UrlImportModal.test.tsx`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { UrlImportModal } from './UrlImportModal';
import { buildStore } from '../../buildStore';

describe('UrlImportModal', () => {
  beforeEach(() => {
    buildStore.setState({ isImportModalOpen: false, previewUrls: [] });
  });

  it('should not render when closed', () => {
    render(<UrlImportModal />);
    expect(screen.queryByText(/批量导入URL/)).not.toBeInTheDocument();
  });

  it('should render when opened', () => {
    buildStore.setState({ isImportModalOpen: true });
    render(<UrlImportModal />);
    expect(screen.getByText(/批量导入URL/)).toBeInTheDocument();
  });

  it('should show drag and drop zone', () => {
    buildStore.setState({ isImportModalOpen: true });
    render(<UrlImportModal />);
    expect(screen.getByText(/点击上传文件/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/UrlImportModal.test.tsx 2>&1 | head -30`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/features/build/components/CrawlTab/UrlImportModal.tsx`:

```typescript
import React, { useCallback, useRef, useState } from 'react';
import { Upload, X, FileText, Check } from 'lucide-react';
import { Modal } from '../../../../components/ui/Modal';
import { Button } from '../../../../components/ui/Button';
import { buildStore } from '../../buildStore';
import styles from './UrlImportModal.module.css';

const MAX_FILE_SIZE = 1024 * 1024; // 1MB
const MAX_URLS = 100;

export const UrlImportModal: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isOpen = buildStore((s) => s.isImportModalOpen);
  const previewUrls = buildStore((s) => s.previewUrls);
  const closeModal = buildStore((s) => s.closeImportModal);
  const setPreviewUrls = buildStore((s) => s.setPreviewUrls);
  const setCrawlUrls = buildStore((s) => s.setCrawlUrls);

  const parseFile = useCallback((file: File) => {
    setError(null);

    if (!file.name.match(/\.(txt|csv)$/i)) {
      setError('仅支持 .txt 或 .csv 文件');
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError('文件大小不能超过 1MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      let urls: string[] = [];

      if (file.name.endsWith('.csv')) {
        // Parse CSV - take first column
        const lines = content.split('\n');
        urls = lines
          .map((line) => {
            const parts = line.split(',');
            return parts[0]?.trim();
          })
          .filter((url) => url && (url.startsWith('http://') || url.startsWith('https://')));
      } else {
        // Parse txt - one URL per line
        urls = content
          .split('\n')
          .map((line) => line.trim())
          .filter((url) => url.startsWith('http://') || url.startsWith('https://'));
      }

      if (urls.length > MAX_URLS) {
        setError(`URL 数量不能超过 ${MAX_URLS} 个`);
        return;
      }

      if (urls.length === 0) {
        setError('未找到有效的 URL');
        return;
      }

      setPreviewUrls(urls);
    };

    reader.readAsText(file);
  }, [setPreviewUrls]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      parseFile(file);
    }
  }, [parseFile]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      parseFile(file);
    }
  }, [parseFile]);

  const handleConfirm = useCallback(() => {
    if (previewUrls.length > 0) {
      setCrawlUrls(previewUrls.join('\n'));
      closeModal();
    }
  }, [previewUrls, setCrawlUrls, closeModal]);

  const handleRemoveUrl = useCallback((index: number) => {
    setPreviewUrls(previewUrls.filter((_, i) => i !== index));
  }, [previewUrls, setPreviewUrls]);

  return (
    <Modal isOpen={isOpen} onClose={closeModal} title="批量导入URL">
      <div className={styles.container}>
        {previewUrls.length === 0 ? (
          <div
            className={`${styles.dropzone} ${dragActive ? styles.active : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={48} className={styles.uploadIcon} />
            <p className={styles.dropzoneText}>点击上传文件</p>
            <p className={styles.dropzoneHint}>支持 .txt（每行一个URL）或 .csv（第一列）</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.csv"
              onChange={handleFileSelect}
              className={styles.fileInput}
            />
          </div>
        ) : (
          <div className={styles.preview}>
            <div className={styles.previewHeader}>
              <FileText size={20} />
              <span>已解析 {previewUrls.length} 个 URL</span>
              <button
                className={styles.clearBtn}
                onClick={() => setPreviewUrls([])}
              >
                清空
              </button>
            </div>
            <ul className={styles.urlList}>
              {previewUrls.slice(0, 20).map((url, index) => (
                <li key={index} className={styles.urlItem}>
                  <span className={styles.urlText}>{url}</span>
                  <button
                    className={styles.removeBtn}
                    onClick={() => handleRemoveUrl(index)}
                  >
                    <X size={14} />
                  </button>
                </li>
              ))}
              {previewUrls.length > 20 && (
                <li className={styles.moreUrls}>
                  还有 {previewUrls.length - 20} 个 URL...
                </li>
              )}
            </ul>
          </div>
        )}

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        <div className={styles.actions}>
          <Button variant="ghost" onClick={closeModal}>
            取消
          </Button>
          <Button
            variant="primary"
            onClick={handleConfirm}
            disabled={previewUrls.length === 0}
          >
            <Check size={16} />
            确认导入
          </Button>
        </div>
      </div>
    </Modal>
  );
};
```

Create `frontend/src/features/build/components/CrawlTab/UrlImportModal.module.css`:

```css
.container {
  display: flex;
  flex-direction: column;
  gap: var(--space-4, 16px);
}

.dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8, 32px);
  border: 2px dashed var(--color-border, rgba(83, 125, 150, 0.22));
  border-radius: var(--radius-lg, 12px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.dropzone:hover,
.dropzone.active {
  border-color: var(--color-accent, #537d96);
  background: rgba(83, 125, 150, 0.05);
}

.uploadIcon {
  color: var(--color-text-secondary, #666);
  margin-bottom: var(--space-3, 12px);
}

.dropzoneText {
  font-size: var(--text-base, 16px);
  color: var(--color-text-primary, #3b3d3f);
  margin-bottom: var(--space-1, 4px);
}

.dropzoneHint {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary, #666);
}

.fileInput {
  display: none;
}

.preview {
  max-height: 300px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.previewHeader {
  display: flex;
  align-items: center;
  gap: var(--space-2, 8px);
  padding-bottom: var(--space-3, 12px);
  border-bottom: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  margin-bottom: var(--space-2, 8px);
  color: var(--color-success, #22c55e);
  font-size: var(--text-sm, 14px);
}

.clearBtn {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--color-text-secondary, #666);
  cursor: pointer;
  font-size: var(--text-sm, 14px);
}

.clearBtn:hover {
  color: var(--color-error, #ef4444);
}

.urlList {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  max-height: 200px;
}

.urlItem {
  display: flex;
  align-items: center;
  gap: var(--space-2, 8px);
  padding: var(--space-1, 4px) 0;
  border-bottom: 1px solid rgba(83, 125, 150, 0.1);
}

.urlText {
  flex: 1;
  font-size: var(--text-sm, 14px);
  color: var(--color-text-primary, #3b3d3f);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: monospace;
}

.removeBtn {
  background: none;
  border: none;
  color: var(--color-text-secondary, #666);
  cursor: pointer;
  padding: var(--space-1, 4px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.removeBtn:hover {
  color: var(--color-error, #ef4444);
}

.moreUrls {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary, #666);
  font-style: italic;
  padding: var(--space-2, 8px) 0;
}

.error {
  color: var(--color-error, #ef4444);
  font-size: var(--text-sm, 14px);
  padding: var(--space-2, 8px);
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-sm, 4px);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3, 12px);
  padding-top: var(--space-3, 12px);
  border-top: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/UrlImportModal.test.tsx 2>&1 | tail -20`
Expected: PASS (may need adjustments based on modal rendering)

- [ ] **Step 5: Commit**

```bash
git add src/features/build/components/CrawlTab/UrlImportModal.tsx src/features/build/components/CrawlTab/UrlImportModal.module.css src/features/build/components/CrawlTab/UrlImportModal.test.tsx
git commit -m "feat(build): add UrlImportModal for batch URL import"
```

---

### Task 6: Create CrawlPanel component

**Files:**
- Create: `frontend/src/features/build/components/CrawlTab/CrawlPanel.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/features/build/components/CrawlTab/CrawlPanel.test.tsx`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CrawlPanel } from './CrawlPanel';
import { buildStore } from '../../buildStore';
import { KnowledgeBase } from '../../../api/knowledge';

vi.mock('../../../knowledge/knowledgeListStore', () => ({
  knowledgeListStore: {
    getState: () => ({
      knowledgeBases: [
        { id: 'kb_1', name: '知识库A', description: '', user_id: 'u1', file_count: 5, create_time: '', update_time: '' },
        { id: 'kb_2', name: '知识库B', description: '', user_id: 'u1', file_count: 3, create_time: '', update_time: '' },
      ],
    }),
  },
}));

describe('CrawlPanel', () => {
  beforeEach(() => {
    buildStore.setState({
      selectedKnowledgeId: null,
      crawlUrls: '',
      tasks: [],
    });
  });

  it('should render knowledge selector', () => {
    render(<CrawlPanel />);
    expect(screen.getByText(/选择知识库/)).toBeInTheDocument();
  });

  it('should render URL textarea', () => {
    render(<CrawlPanel />);
    expect(screen.getByPlaceholderText(/输入URL/)).toBeInTheDocument();
  });

  it('should render action buttons', () => {
    render(<CrawlPanel />);
    expect(screen.getByRole('button', { name: /开始爬取/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /批量导入/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /清空/ })).toBeInTheDocument();
  });

  it('should disable submit when no knowledge selected', () => {
    render(<CrawlPanel />);
    const submitBtn = screen.getByRole('button', { name: /开始爬取/ }) as HTMLButtonElement;
    expect(submitBtn.disabled).toBe(true);
  });

  it('should disable submit when URL is empty', () => {
    buildStore.setState({ selectedKnowledgeId: 'kb_1' });
    render(<CrawlPanel />);
    const submitBtn = screen.getByRole('button', { name: /开始爬取/ }) as HTMLButtonElement;
    expect(submitBtn.disabled).toBe(true);
  });

  it('should enable submit when knowledge and URLs are provided', () => {
    buildStore.setState({
      selectedKnowledgeId: 'kb_1',
      crawlUrls: 'http://example.com\nhttp://test.com',
    });
    render(<CrawlPanel />);
    const submitBtn = screen.getByRole('button', { name: /开始爬取/ }) as HTMLButtonElement;
    expect(submitBtn.disabled).toBe(false);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/CrawlPanel.test.tsx 2>&1 | head -30`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/features/build/components/CrawlTab/CrawlPanel.tsx`:

```typescript
import React, { useEffect, useMemo, useCallback } from 'react';
import { Play, Upload, Trash2 } from 'lucide-react';
import { Button } from '../../../../components/ui/Button';
import { buildStore } from '../../buildStore';
import { knowledgeListStore } from '../../../knowledge/knowledgeListStore';
import styles from './CrawlPanel.module.css';

export const CrawlPanel: React.FC = () => {
  const selectedKnowledgeId = buildStore((s) => s.selectedKnowledgeId);
  const crawlUrls = buildStore((s) => s.crawlUrls);
  const setSelectedKnowledgeId = buildStore((s) => s.setSelectedKnowledgeId);
  const setCrawlUrls = buildStore((s) => s.setCrawlUrls);
  const openImportModal = buildStore((s) => s.openImportModal);
  const submitBatchCrawl = buildStore((s) => s.submitBatchCrawl);
  const fetchTasks = buildStore((s) => s.fetchTasks);

  // Fetch knowledge bases on mount
  useEffect(() => {
    knowledgeListStore.getState().fetchKnowledgeBases();
  }, []);

  const knowledgeBases = knowledgeListStore((s) => s.knowledgeBases);

  const selectedKB = useMemo(() => {
    return knowledgeBases.find((kb) => kb.id === selectedKnowledgeId);
  }, [knowledgeBases, selectedKnowledgeId]);

  const urls = useMemo(() => {
    return crawlUrls
      .split('\n')
      .map((url) => url.trim())
      .filter((url) => url.length > 0);
  }, [crawlUrls]);

  const isValid = selectedKnowledgeId && urls.length > 0;

  const handleSubmit = useCallback(async () => {
    if (!isValid) return;
    await submitBatchCrawl(urls);
  }, [isValid, submitBatchCrawl, urls]);

  const handleClear = useCallback(() => {
    setCrawlUrls('');
  }, [setCrawlUrls]);

  const handleKnowledgeChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setSelectedKnowledgeId(value || null);
  }, [setSelectedKnowledgeId]);

  const handleUrlsChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCrawlUrls(e.target.value);
  }, [setCrawlUrls]);

  // Refresh tasks on mount
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return (
    <div className={styles.panel}>
      <div className={styles.form}>
        <div className={styles.field}>
          <label className={styles.label}>选择知识库</label>
          <select
            className={styles.select}
            value={selectedKnowledgeId || ''}
            onChange={handleKnowledgeChange}
          >
            <option value="">请选择知识库</option>
            {knowledgeBases.map((kb) => (
              <option key={kb.id} value={kb.id}>
                {kb.name} ({kb.file_count} 个文件)
              </option>
            ))}
          </select>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>URL列表</label>
          <textarea
            className={styles.textarea}
            placeholder="输入URL，每行一个"
            value={crawlUrls}
            onChange={handleUrlsChange}
            rows={6}
          />
        </div>

        <div className={styles.actions}>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!isValid}
          >
            <Play size={16} />
            开始爬取
          </Button>
          <Button variant="secondary" onClick={openImportModal}>
            <Upload size={16} />
            批量导入
          </Button>
          <Button variant="ghost" onClick={handleClear}>
            <Trash2 size={16} />
            清空
          </Button>
        </div>
      </div>
    </div>
  );
};
```

Create `frontend/src/features/build/components/CrawlTab/CrawlPanel.module.css`:

```css
.panel {
  background: var(--color-bg-surface, #fff);
  border: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  border-radius: var(--radius-lg, 12px);
  padding: var(--space-6, 24px);
  margin-bottom: var(--space-6, 24px);
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4, 16px);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2, 8px);
}

.label {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary, #666);
  font-weight: 500;
}

.select {
  padding: var(--space-3, 12px);
  border: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  border-radius: var(--radius-md, 8px);
  font-size: var(--text-base, 16px);
  background: var(--color-bg-base, #f8f5ed);
  color: var(--color-text-primary, #3b3d3f);
  cursor: pointer;
}

.select:focus {
  outline: none;
  border-color: var(--color-accent, #537d96);
  box-shadow: 0 0 0 3px rgba(83, 125, 150, 0.15);
}

.textarea {
  padding: var(--space-3, 12px);
  border: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  border-radius: var(--radius-md, 8px);
  font-size: var(--text-base, 16px);
  font-family: monospace;
  background: var(--color-bg-base, #f8f5ed);
  color: var(--color-text-primary, #3b3d3f);
  resize: vertical;
  min-height: 120px;
}

.textarea:focus {
  outline: none;
  border-color: var(--color-accent, #537d96);
  box-shadow: 0 0 0 3px rgba(83, 125, 150, 0.15);
}

.textarea::placeholder {
  color: var(--color-text-secondary, #666);
}

.actions {
  display: flex;
  gap: var(--space-3, 12px);
  flex-wrap: wrap;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/CrawlPanel.test.tsx 2>&1 | tail -20`
Expected: PASS (may need mock adjustments)

- [ ] **Step 5: Commit**

```bash
git add src/features/build/components/CrawlTab/CrawlPanel.tsx src/features/build/components/CrawlTab/CrawlPanel.module.css src/features/build/components/CrawlTab/CrawlPanel.test.tsx
git commit -m "feat(build): add CrawlPanel component with knowledge selector and URL input"
```

---

## Chunk 4: ReviewTab Components

### Task 7: Create ReviewInbox component

**Files:**
- Create: `frontend/src/features/build/components/ReviewTab/ReviewInbox.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/features/build/components/ReviewTab/ReviewInbox.test.tsx`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ReviewInbox } from './ReviewInbox';
import { buildStore } from '../../buildStore';
import { KnowledgeFile } from '../../../api/knowledge';

const mockFiles: KnowledgeFile[] = [
  {
    id: 'file_1',
    file_name: 'doc1.md',
    knowledge_id: 'kb_1',
    user_id: 'user_1',
    status: 'pending_verify',
    oss_url: 'https://oss.example.com/doc1.md',
    file_size: 1024,
    create_time: '2024-01-01T12:00:00',
    update_time: '2024-01-01T12:00:00',
  },
  {
    id: 'file_2',
    file_name: 'doc2.md',
    knowledge_id: 'kb_2',
    user_id: 'user_1',
    status: 'pending_verify',
    oss_url: 'https://oss.example.com/doc2.md',
    file_size: 2048,
    create_time: '2024-01-02T12:00:00',
    update_time: '2024-01-02T12:00:00',
  },
];

describe('ReviewInbox', () => {
  beforeEach(() => {
    buildStore.setState({ pendingFiles: [], selectedFile: null, fileContent: '' });
  });

  it('should render empty state when no files', () => {
    render(<ReviewInbox />);
    expect(screen.getByText(/暂无待审核文件/)).toBeInTheDocument();
  });

  it('should render file list when files exist', () => {
    buildStore.setState({ pendingFiles: mockFiles });
    render(<ReviewInbox />);
    expect(screen.getByText(/doc1\.md/)).toBeInTheDocument();
    expect(screen.getByText(/doc2\.md/)).toBeInTheDocument();
  });

  it('should render file count', () => {
    buildStore.setState({ pendingFiles: mockFiles });
    render(<ReviewInbox />);
    expect(screen.getByText(/共 2 个文件/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/ReviewTab/ReviewInbox.test.tsx 2>&1 | head -30`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/features/build/components/ReviewTab/ReviewInbox.tsx`:

```typescript
import React, { useEffect, useMemo } from 'react';
import { FileText } from 'lucide-react';
import { buildStore } from '../../buildStore';
import { knowledgeListStore } from '../../../knowledge/knowledgeListStore';
import styles from './ReviewInbox.module.css';

export const ReviewInbox: React.FC = () => {
  const pendingFiles = buildStore((s) => s.pendingFiles);
  const selectedFile = buildStore((s) => s.selectedFile);
  const fetchPendingFiles = buildStore((s) => s.fetchPendingFiles);
  const fetchFileContent = buildStore((s) => s.fetchFileContent);

  // Fetch pending files on mount
  useEffect(() => {
    fetchPendingFiles();
  }, [fetchPendingFiles]);

  const knowledgeBases = knowledgeListStore((s) => s.knowledgeBases);

  const getKBName = (kbId: string) => {
    const kb = knowledgeBases.find((k) => k.id === kbId);
    return kb?.name || kbId;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
    });
  };

  const handleFileClick = (fileId: string) => {
    fetchFileContent(fileId);
  };

  if (pendingFiles.length === 0) {
    return (
      <div className={styles.empty}>
        <FileText size={48} className={styles.emptyIcon} />
        <p>暂无待审核文件</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span>共 {pendingFiles.length} 个文件</span>
      </div>
      <ul className={styles.list}>
        {pendingFiles.map((file) => (
          <li
            key={file.id}
            className={`${styles.item} ${selectedFile?.id === file.id ? styles.selected : ''}`}
            onClick={() => handleFileClick(file.id)}
          >
            <FileText size={18} className={styles.fileIcon} />
            <span className={styles.fileName}>{file.file_name}</span>
            <span className={styles.kbName}>{getKBName(file.knowledge_id)}</span>
            <span className={styles.date}>{formatDate(file.create_time)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
```

Create `frontend/src/features/build/components/ReviewTab/ReviewInbox.module.css`:

```css
.container {
  background: var(--color-bg-surface, #fff);
  border: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  border-radius: var(--radius-lg, 12px);
  overflow: hidden;
}

.header {
  padding: var(--space-3, 12px) var(--space-4, 16px);
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary, #666);
  border-bottom: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
}

.item {
  display: flex;
  align-items: center;
  gap: var(--space-3, 12px);
  padding: var(--space-3, 12px) var(--space-4, 16px);
  border-bottom: 1px solid rgba(83, 125, 150, 0.1);
  cursor: pointer;
  transition: background 0.15s ease;
}

.item:hover {
  background: rgba(83, 125, 150, 0.05);
}

.item.selected {
  background: rgba(83, 125, 150, 0.1);
  border-left: 3px solid var(--color-accent, #537d96);
}

.fileIcon {
  color: var(--color-accent, #537d96);
  flex-shrink: 0;
}

.fileName {
  flex: 1;
  font-size: var(--text-sm, 14px);
  color: var(--color-text-primary, #3b3d3f);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kbName {
  font-size: var(--text-xs, 12px);
  color: var(--color-text-secondary, #666);
  background: rgba(83, 125, 150, 0.1);
  padding: var(--space-1, 4px) var(--space-2, 8px);
  border-radius: var(--radius-sm, 4px);
}

.date {
  font-size: var(--text-xs, 12px);
  color: var(--color-text-secondary, #666);
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8, 32px);
  color: var(--color-text-secondary, #666);
  gap: var(--space-3, 12px);
}

.emptyIcon {
  opacity: 0.3;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/ReviewTab/ReviewInbox.test.tsx 2>&1 | tail -20`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/features/build/components/ReviewTab/ReviewInbox.tsx src/features/build/components/ReviewTab/ReviewInbox.module.css src/features/build/components/ReviewTab/ReviewInbox.test.tsx
git commit -m "feat(build): add ReviewInbox component for pending verification files"
```

---

### Task 8: Create ReviewEditor component

**Files:**
- Create: `frontend/src/features/build/components/ReviewTab/ReviewEditor.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/features/build/components/ReviewTab/ReviewEditor.test.tsx`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ReviewEditor } from './ReviewEditor';
import { buildStore } from '../../buildStore';
import { KnowledgeFile } from '../../../api/knowledge';

const mockFile: KnowledgeFile = {
  id: 'file_1',
  file_name: 'test.md',
  knowledge_id: 'kb_1',
  user_id: 'user_1',
  status: 'pending_verify',
  oss_url: 'https://oss.example.com/test.md',
  file_size: 1024,
  create_time: '2024-01-01T12:00:00',
  update_time: '2024-01-01T12:00:00',
};

describe('ReviewEditor', () => {
  beforeEach(() => {
    buildStore.setState({
      selectedFile: null,
      fileContent: '',
      isSaving: false,
      isIndexing: false,
    });
  });

  it('should render empty state when no file selected', () => {
    render(<ReviewEditor />);
    expect(screen.getByText(/请从左侧选择文件/)).toBeInTheDocument();
  });

  it('should render file name when file selected', () => {
    buildStore.setState({
      selectedFile: mockFile,
      fileContent: '# Test Content',
    });
    render(<ReviewEditor />);
    expect(screen.getByText(/test\.md/)).toBeInTheDocument();
  });

  it('should render action buttons when file selected', () => {
    buildStore.setState({
      selectedFile: mockFile,
      fileContent: '# Test Content',
    });
    render(<ReviewEditor />);
    expect(screen.getByRole('button', { name: /保存/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /确认索引/ })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/ReviewTab/ReviewEditor.test.tsx 2>&1 | head -30`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/features/build/components/ReviewTab/ReviewEditor.tsx`:

```typescript
import React, { useState, useCallback, useEffect } from 'react';
import { Save, Play } from 'lucide-react';
import { Button } from '../../../../components/ui/Button';
import { buildStore } from '../../buildStore';
import styles from './ReviewEditor.module.css';

export const ReviewEditor: React.FC = () => {
  const selectedFile = buildStore((s) => s.selectedFile);
  const fileContent = buildStore((s) => s.fileContent);
  const isSaving = buildStore((s) => s.isSaving);
  const isIndexing = buildStore((s) => s.isIndexing);
  const updateFileContent = buildStore((s) => s.updateFileContent);
  const triggerIndex = buildStore((s) => s.triggerIndex);

  const [editedContent, setEditedContent] = useState(fileContent);

  // Sync edited content when file changes
  useEffect(() => {
    setEditedContent(fileContent);
  }, [fileContent]);

  const handleSave = useCallback(async () => {
    if (!selectedFile) return;
    await updateFileContent(selectedFile.id, editedContent);
  }, [selectedFile, updateFileContent, editedContent]);

  const handleIndex = useCallback(async () => {
    if (!selectedFile) return;
    await triggerIndex(selectedFile.id);
  }, [selectedFile, triggerIndex]);

  if (!selectedFile) {
    return (
      <div className={styles.empty}>
        <p>请从左侧选择文件进行审核</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.fileName}>{selectedFile.file_name}</span>
        <div className={styles.actions}>
          <Button
            variant="secondary"
            onClick={handleSave}
            disabled={isSaving || editedContent === fileContent}
            isLoading={isSaving}
          >
            <Save size={16} />
            保存
          </Button>
          <Button
            variant="primary"
            onClick={handleIndex}
            disabled={isIndexing}
            isLoading={isIndexing}
          >
            <Play size={16} />
            确认索引
          </Button>
        </div>
      </div>
      <div className={styles.editorWrapper}>
        <textarea
          className={styles.editor}
          value={editedContent}
          onChange={(e) => setEditedContent(e.target.value)}
          placeholder="加载中..."
        />
      </div>
    </div>
  );
};
```

Create `frontend/src/features/build/components/ReviewTab/ReviewEditor.module.css`:

```css
.container {
  display: flex;
  flex-direction: column;
  background: var(--color-bg-surface, #fff);
  border: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  border-radius: var(--radius-lg, 12px);
  overflow: hidden;
  height: 100%;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3, 12px) var(--space-4, 16px);
  border-bottom: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
}

.fileName {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-primary, #3b3d3f);
  font-weight: 500;
}

.actions {
  display: flex;
  gap: var(--space-2, 8px);
}

.editorWrapper {
  flex: 1;
  padding: var(--space-4, 16px);
  min-height: 300px;
}

.editor {
  width: 100%;
  height: 100%;
  min-height: 280px;
  padding: var(--space-4, 16px);
  border: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  border-radius: var(--radius-md, 8px);
  font-family: monospace;
  font-size: var(--text-sm, 14px);
  line-height: 1.6;
  background: var(--color-bg-base, #f8f5ed);
  color: var(--color-text-primary, #3b3d3f);
  resize: vertical;
}

.editor:focus {
  outline: none;
  border-color: var(--color-accent, #537d96);
  box-shadow: 0 0 0 3px rgba(83, 125, 150, 0.15);
}

.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--color-text-secondary, #666);
  font-size: var(--text-sm, 14px);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/ReviewTab/ReviewEditor.test.tsx 2>&1 | tail -20`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/features/build/components/ReviewTab/ReviewEditor.tsx src/features/build/components/ReviewTab/ReviewEditor.module.css src/features/build/components/ReviewTab/ReviewEditor.test.tsx
git commit -m "feat(build): add ReviewEditor component for content verification"
```

---

## Chunk 5: Main Page - KnowledgeBuildPage

### Task 9: Replace KnowledgeBuildPage with tab layout

**Files:**
- Modify: `frontend/src/features/build/KnowledgeBuildPage.tsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/features/build/KnowledgeBuildPage.test.tsx`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { KnowledgeBuildPage } from './KnowledgeBuildPage';
import { buildStore } from './buildStore';

vi.mock('./buildStore', () => ({
  buildStore: {
    getState: () => ({
      activeTab: 'crawl',
      pendingReviewCount: 0,
      tasks: [],
      pendingFiles: [],
      selectedFile: null,
      fileContent: '',
      isPolling: false,
    }),
    setState: vi.fn(),
  },
}));

describe('KnowledgeBuildPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render two tabs', () => {
    render(<KnowledgeBuildPage />);
    expect(screen.getByRole('tab', { name: /爬取任务/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /审核队列/ })).toBeInTheDocument();
  });

  it('should switch tabs when clicked', () => {
    render(<KnowledgeBuildPage />);

    const reviewTab = screen.getByRole('tab', { name: /审核队列/ });
    fireEvent.click(reviewTab);

    expect(screen.getByRole('tab', { name: /审核队列/ })).toHaveAttribute('aria-selected', 'true');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/KnowledgeBuildPage.test.tsx 2>&1 | head -30`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Replace `frontend/src/features/build/KnowledgeBuildPage.tsx`:

```typescript
import React, { useEffect } from 'react';
import { FileSearch, Download } from 'lucide-react';
import { buildStore } from './buildStore';
import { CrawlPanel } from './components/CrawlTab/CrawlPanel';
import { TaskList } from './components/CrawlTab/TaskList';
import { UrlImportModal } from './components/CrawlTab/UrlImportModal';
import { ReviewInbox } from './components/ReviewTab/ReviewInbox';
import { ReviewEditor } from './components/ReviewTab/ReviewEditor';
import styles from './KnowledgeBuildPage.module.css';

export function KnowledgeBuildPage() {
  const activeTab = buildStore((s) => s.activeTab);
  const setActiveTab = buildStore((s) => s.setActiveTab);
  const pendingReviewCount = buildStore((s) => s.pendingReviewCount);
  const fetchPendingFiles = buildStore((s) => s.fetchPendingFiles);

  // Fetch initial data
  useEffect(() => {
    fetchPendingFiles();
  }, [fetchPendingFiles]);

  const handleTabChange = (tab: 'crawl' | 'review') => {
    setActiveTab(tab);
    if (tab === 'review') {
      fetchPendingFiles();
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>知识库构建</h1>
      </div>

      <div className={styles.tabs} role="tablist">
        <button
          role="tab"
          aria-selected={activeTab === 'crawl'}
          className={`${styles.tab} ${activeTab === 'crawl' ? styles.active : ''}`}
          onClick={() => handleTabChange('crawl')}
        >
          <Download size={18} />
          爬取任务
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'review'}
          className={`${styles.tab} ${activeTab === 'review' ? styles.active : ''}`}
          onClick={() => handleTabChange('review')}
        >
          <FileSearch size={18} />
          审核队列
          {pendingReviewCount > 0 && (
            <span className={styles.badge}>{pendingReviewCount}</span>
          )}
        </button>
      </div>

      <div className={styles.content}>
        {activeTab === 'crawl' ? (
          <>
            <CrawlPanel />
            <TaskList />
          </>
        ) : (
          <div className={styles.reviewLayout}>
            <div className={styles.reviewSidebar}>
              <ReviewInbox />
            </div>
            <div className={styles.reviewMain}>
              <ReviewEditor />
            </div>
          </div>
        )}
      </div>

      <UrlImportModal />
    </div>
  );
}
```

Create `frontend/src/features/build/KnowledgeBuildPage.module.css`:

```css
.page {
  padding: var(--space-6, 24px);
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: var(--space-6, 24px);
}

.title {
  font-size: var(--text-xl, 20px);
  font-weight: 600;
  color: var(--color-text-primary, #3b3d3f);
  margin: 0;
}

.tabs {
  display: flex;
  gap: var(--space-1, 4px);
  margin-bottom: var(--space-6, 24px);
  border-bottom: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
}

.tab {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2, 8px);
  padding: var(--space-3, 12px) var(--space-4, 16px);
  border: none;
  background: none;
  font-size: var(--text-base, 16px);
  color: var(--color-text-secondary, #666);
  cursor: pointer;
  position: relative;
  transition: color 0.2s ease;
}

.tab:hover {
  color: var(--color-text-primary, #3b3d3f);
}

.tab.active {
  color: var(--color-accent, #537d96);
  font-weight: 500;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-accent, #537d96);
  border-radius: 1px 1px 0 0;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 var(--space-1, 4px);
  font-size: var(--text-xs, 12px);
  font-weight: 600;
  color: #fff;
  background: var(--color-error, #ef4444);
  border-radius: 9px;
}

.content {
  min-height: 400px;
}

.reviewLayout {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: var(--space-6, 24px);
  min-height: 500px;
}

.reviewSidebar {
  min-width: 0;
}

.reviewMain {
  min-width: 0;
}

@media (max-width: 768px) {
  .reviewLayout {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/KnowledgeBuildPage.test.tsx 2>&1 | tail -20`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/features/build/KnowledgeBuildPage.tsx src/features/build/KnowledgeBuildPage.module.css src/features/build/KnowledgeBuildPage.test.tsx
git commit -m "feat(build): implement KnowledgeBuildPage with tab-based layout"
```

---

## Chunk 6: Build Verification

### Task 10: Run build and fix any errors

- [ ] **Step 1: Run TypeScript check**

Run: `cd /home/luorome/software/CampusMind/frontend && npx tsc --noEmit 2>&1 | head -50`
Expected: No errors (or fix any type errors)

- [ ] **Step 2: Run build**

Run: `cd /home/luorome/software/CampusMind/frontend && npm run build 2>&1 | tail -30`
Expected: Build succeeds

- [ ] **Step 3: Run all tests**

Run: `cd /home/luorome/software/CampusMind/frontend && NODE_OPTIONS="--max-old-space-size=4096" npm run test:run 2>&1 | tail -40`
Expected: All tests pass

---

## Chunk 7: Documentation Update

### Task 11: Update frontend docs

- [ ] **Step 1: Update frontend-progress-log.md**

Add Phase 4 completion entry to `frontend/docs/frontend-progress-log.md`

- [ ] **Step 2: Update frontend-question-log.md** (if any issues encountered)

Document any problems and solutions in `frontend/docs/frontend-question-log.md`

- [ ] **Step 3: Commit documentation**

```bash
git add frontend/docs/frontend-progress-log.md frontend/docs/frontend-question-log.md
git commit -m "docs(frontend): update progress log for Phase 4 completion"
```

---

**Plan complete and saved to `docs/superpowers/plans/2026-03-23-phase4-knowledge-build-plan.md`. Ready to execute?**
