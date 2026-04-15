# Knowledge Build Module Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Knowledge Build module (Crawl + Review workflow) for mobile app

**Architecture:** Stack-based navigation from Home to BuildScreen. Segmented control for phase switching. Zustand store for state management. Axios API client for backend communication. 3-second polling for crawl task progress.

**Tech Stack:** React Native, Zustand, Axios, React Navigation, Lucide Icons

---

## File Structure

```
mobile/src/
├── api/
│   ├── crawl.ts              # Crawl task API (create/list/poll/delete/retry)
│   └── knowledge.ts         # Knowledge file API (pending_verify, content, trigger_index)
├── features/
│   └── build/
│       ├── buildStore.ts    # Zustand store
│       └── api/
│           └── index.ts     # Re-export crawl APIs
├── screens/
│   └── BuildScreen.tsx      # Main build screen
├── components/
│   └── build/
│       ├── SegmentedControl.tsx
│       ├── CrawlTab/
│       │   ├── CrawlPanel.tsx
│       │   ├── UrlImportModal.tsx
│       │   ├── TaskList.tsx
│       │   └── TaskCard.tsx
│       └── ReviewTab/
│           ├── FileSelectModal.tsx
│           ├── ReviewInbox.tsx
│           └── ReviewEditor.tsx
└── navigation/
    ├── TabNavigator.tsx     # Add BuildScreen to HomeStack
    └── types.ts             # Already has KnowledgeBuildScreenProps
```

---

## Chunk 1: API Layer

### Task 1: Create crawl API client

**Files:**
- Create: `mobile/src/api/crawl.ts`
- Test: `mobile/src/api/__tests__/crawl.test.ts`

- [ ] **Step 1: Create crawl API client**

```typescript
// mobile/src/api/crawl.ts
import { apiClient } from './client';

export interface FailedUrl {
  url: string;
  error: string;
  timestamp: string;
}

export interface CrawlTask {
  id: string;
  knowledge_id: string;
  user_id: string;
  total_urls: number;
  completed_urls: number;
  success_count: number;
  fail_count: number;
  status: 'pending' | 'processing' | 'SUCCESS' | 'FAILED' | 'completed' | 'failed';
  failed_urls?: FailedUrl[];
  create_time: string;
  update_time: string;
}

export const crawlApi = {
  async submitBatchCrawl(urls: string[], knowledgeId: string): Promise<string> {
    const response = await apiClient.post<{ task_id: string }>('/crawl/batch-with-knowledge', {
      urls,
      knowledge_id: knowledgeId,
    });
    return response.data.task_id;
  },

  async fetchTasks(): Promise<CrawlTask[]> {
    const response = await apiClient.get<{ tasks: CrawlTask[] }>('/crawl/tasks');
    return response.data.tasks || [];
  },

  async fetchTaskProgress(taskId: string): Promise<CrawlTask> {
    const response = await apiClient.get<CrawlTask>(`/crawl/tasks/${taskId}`);
    return response.data;
  },

  async deleteTask(taskId: string): Promise<void> {
    await apiClient.delete(`/crawl/tasks/${taskId}`);
  },

  async retryFailed(taskId: string): Promise<{ task_id: string }> {
    const response = await apiClient.post(`/crawl/tasks/${taskId}/retry-failed`, {});
    return response.data;
  },
};
```

- [ ] **Step 2: Write API tests**

```typescript
// mobile/src/api/__tests__/crawl.test.ts
import { crawlApi } from '../crawl';

// Mock the apiClient
jest.mock('../client', () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    delete: jest.fn(),
  },
}));

import { apiClient } from '../client';

describe('crawlApi', () => {
  beforeEach(() => jest.clearAllMocks());

  describe('submitBatchCrawl', () => {
    it('should return task_id on success', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: { task_id: 'task-123' },
      });

      const result = await crawlApi.submitBatchCrawl(['http://example.com'], 'kb-1');

      expect(result).toBe('task-123');
      expect(apiClient.post).toHaveBeenCalledWith('/crawl/batch-with-knowledge', {
        urls: ['http://example.com'],
        knowledge_id: 'kb-1',
      });
    });
  });

  describe('fetchTasks', () => {
    it('should return tasks array', async () => {
      const mockTasks = [{ id: 'task-1', status: 'pending' }];
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { tasks: mockTasks },
      });

      const result = await crawlApi.fetchTasks();

      expect(result).toEqual(mockTasks);
    });
  });

  describe('deleteTask', () => {
    it('should call delete endpoint', async () => {
      (apiClient.delete as jest.Mock).mockResolvedValue({ data: {} });

      await crawlApi.deleteTask('task-123');

      expect(apiClient.delete).toHaveBeenCalledWith('/crawl/tasks/task-123');
    });
  });
});
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test -- --testPathPattern="crawl.test.ts" --run`
Expected: FAIL (file doesn't exist yet)

- [ ] **Step 4: Create the API file and tests**

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test -- --testPathPattern="crawl.test.ts" --run`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add mobile/src/api/crawl.ts mobile/src/api/__tests__/crawl.test.ts
git commit -m "feat(mobile-build): add crawl API client"
```

---

### Task 2: Create knowledge file API

**Files:**
- Create: `mobile/src/api/knowledge.ts`
- Test: `mobile/src/api/__tests__/knowledge.test.ts`

- [ ] **Step 1: Create knowledge file API**

```typescript
// mobile/src/api/knowledge.ts
import { apiClient } from './client';

export interface KnowledgeFile {
  id: string;
  kb_id: string;
  file_name: string;
  status: 'pending' | 'processing' | 'ready' | 'error';
  size?: number;
  create_time: string;
  update_time: string;
}

export const knowledgeApi = {
  async getPendingFiles(): Promise<KnowledgeFile[]> {
    const response = await apiClient.get<KnowledgeFile[]>('/knowledge_file/pending_verify');
    return response.data || [];
  },

  async getFileContent(fileId: string): Promise<string> {
    const response = await apiClient.get(`/knowledge_file/${fileId}/content`);
    return response.data;
  },

  async updateFileContent(fileId: string, content: string): Promise<void> {
    await apiClient.put(`/knowledge_file/${fileId}/content`, { content });
  },

  async triggerIndex(fileId: string): Promise<void> {
    await apiClient.post(`/knowledge_file/${fileId}/trigger_index`, {
      enable_vector: true,
      enable_keyword: true,
    });
  },
};
```

- [ ] **Step 2: Write API tests**

```typescript
// mobile/src/api/__tests__/knowledge.test.ts
import { knowledgeApi } from '../knowledge';

jest.mock('../client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
  },
}));

import { apiClient } from '../client';

describe('knowledgeApi', () => {
  beforeEach(() => jest.clearAllMocks());

  describe('getPendingFiles', () => {
    it('should return pending files array', async () => {
      const mockFiles = [{ id: 'file-1', file_name: 'test.md' }];
      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockFiles });

      const result = await knowledgeApi.getPendingFiles();

      expect(result).toEqual(mockFiles);
    });
  });

  describe('getFileContent', () => {
    it('should return file content string', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({ data: '# Hello World' });

      const result = await knowledgeApi.getFileContent('file-123');

      expect(result).toBe('# Hello World');
    });
  });

  describe('triggerIndex', () => {
    it('should call trigger_index endpoint', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({ data: {} });

      await knowledgeApi.triggerIndex('file-123');

      expect(apiClient.post).toHaveBeenCalledWith('/knowledge_file/file-123/trigger_index', {
        enable_vector: true,
        enable_keyword: true,
      });
    });
  });
});
```

- [ ] **Step 3: Create the API file and tests**

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test -- --testPathPattern="knowledge.test.ts" --run`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add mobile/src/api/knowledge.ts mobile/src/api/__tests__/knowledge.test.ts
git commit -m "feat(mobile-build): add knowledge file API client"
```

---

## Chunk 2: BuildStore

### Task 3: Create BuildStore

**Files:**
- Create: `mobile/src/features/build/buildStore.ts`
- Test: `mobile/src/features/build/__tests__/buildStore.test.ts`

- [ ] **Step 1: Create BuildStore**

```typescript
// mobile/src/features/build/buildStore.ts
import { create } from 'zustand';
import { crawlApi, CrawlTask } from '../../api/crawl';
import { knowledgeApi, KnowledgeFile } from '../../api/knowledge';

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

  // Import Modal
  isImportModalOpen: boolean;
  previewUrls: string[];

  // Review Tab
  pendingFiles: KnowledgeFile[];
  pendingReviewCount: number;
  selectedFile: KnowledgeFile | null;
  fileContent: string;
  isLoadingContent: boolean;
  isSaving: boolean;
  isIndexing: boolean;
  isPreview: boolean;

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
  removeTask: (taskId: string) => Promise<void>;
  retryFailedUrls: (taskId: string) => Promise<string | null>;
  clearCompletedTasks: () => Promise<void>;
  fetchPendingFiles: () => Promise<void>;
  fetchFileContent: (fileId: string) => Promise<void>;
  updateFileContent: (fileId: string, content: string) => Promise<void>;
  triggerIndex: (fileId: string) => Promise<void>;
  clearSelectedFile: () => void;
  setIsPreview: (value: boolean) => void;
}

let pollIntervalId: ReturnType<typeof setInterval> | null = null;

export const useBuildStore = create<BuildState>((set, get) => ({
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
  isLoadingContent: false,
  isSaving: false,
  isIndexing: false,
  isPreview: false,

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
      await get().fetchTasks();
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
    if (pollIntervalId) {
      clearInterval(pollIntervalId);
    }

    set({ isPolling: true, pollingErrorCount: 0, activeTaskId: taskId });

    pollIntervalId = setInterval(async () => {
      const { stopPolling } = get();

      try {
        const task = await crawlApi.fetchTaskProgress(taskId);

        set((state) => ({
          tasks: state.tasks.map((t) => (t.id === taskId ? task : t)),
          pollingErrorCount: 0,
        }));

        if (TERMINAL_STATES.includes(task.status)) {
          stopPolling();
          get().fetchPendingFiles();
        }
      } catch (error) {
        const { pollingErrorCount } = get();
        const newCount = pollingErrorCount + 1;

        if (newCount >= MAX_POLL_FAILURES) {
          stopPolling();
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
    const terminalTasks = tasks.filter((t) => TERMINAL_STATES.includes(t.status));

    for (const task of terminalTasks) {
      await removeTask(task.id);
    }
  },

  // Review Actions
  fetchPendingFiles: async () => {
    try {
      const files = await knowledgeApi.getPendingFiles();
      set({ pendingFiles: files, pendingReviewCount: files.length });
    } catch (error) {
      console.error('Failed to fetch pending files:', error);
    }
  },

  fetchFileContent: async (fileId) => {
    set({ isLoadingContent: true });
    const file = get().pendingFiles.find((f) => f.id === fileId) || null;

    try {
      const content = await knowledgeApi.getFileContent(fileId);
      set({ selectedFile: file, fileContent: content, isLoadingContent: false });
    } catch (error) {
      console.error('Failed to fetch file content:', error);
      set({ selectedFile: file, isLoadingContent: false });
    }
  },

  updateFileContent: async (fileId, content) => {
    set({ isSaving: true });

    try {
      await knowledgeApi.updateFileContent(fileId, content);
      set((state) => ({
        pendingFiles: state.pendingFiles.map((f) =>
          f.id === fileId ? { ...f, status: 'verified' as const } : f
        ),
        isSaving: false,
      }));
    } catch (error) {
      console.error('Failed to update file content:', error);
      set({ isSaving: false });
    }
  },

  triggerIndex: async (fileId) => {
    set({ isIndexing: true });

    try {
      await knowledgeApi.triggerIndex(fileId);
      set((state) => ({
        pendingFiles: state.pendingFiles.filter((f) => f.id !== fileId),
        pendingReviewCount: Math.max(0, state.pendingReviewCount - 1),
        selectedFile: null,
        fileContent: '',
        isIndexing: false,
      }));
    } catch (error) {
      console.error('Failed to trigger index:', error);
      set({ isIndexing: false });
    }
  },

  clearSelectedFile: () => set({ selectedFile: null, fileContent: '' }),
  setIsPreview: (value) => set({ isPreview: value }),
}));
```

- [ ] **Step 2: Write store tests**

```typescript
// mobile/src/features/build/__tests__/buildStore.test.ts
import { useBuildStore } from '../buildStore';

describe('buildStore', () => {
  beforeEach(() => {
    // Reset store state
    useBuildStore.setState({
      activeTab: 'crawl',
      selectedKnowledgeId: null,
      crawlUrls: '',
      tasks: [],
      activeTaskId: null,
      isPolling: false,
      pendingFiles: [],
      pendingReviewCount: 0,
      selectedFile: null,
      fileContent: '',
    });
  });

  describe('setActiveTab', () => {
    it('should update activeTab to review', () => {
      useBuildStore.getState().setActiveTab('review');
      expect(useBuildStore.getState().activeTab).toBe('review');
    });
  });

  describe('setSelectedKnowledgeId', () => {
    it('should update selectedKnowledgeId', () => {
      useBuildStore.getState().setSelectedKnowledgeId('kb-123');
      expect(useBuildStore.getState().selectedKnowledgeId).toBe('kb-123');
    });
  });

  describe('setCrawlUrls', () => {
    it('should update crawlUrls', () => {
      useBuildStore.getState().setCrawlUrls('http://example.com\nhttp://test.com');
      expect(useBuildStore.getState().crawlUrls).toBe('http://example.com\nhttp://test.com');
    });
  });

  describe('clearSelectedFile', () => {
    it('should clear selectedFile and fileContent', () => {
      useBuildStore.setState({
        selectedFile: { id: 'file-1', kb_id: 'kb-1', file_name: 'test.md', status: 'pending', create_time: '', update_time: '' },
        fileContent: '# content',
      });

      useBuildStore.getState().clearSelectedFile();

      expect(useBuildStore.getState().selectedFile).toBeNull();
      expect(useBuildStore.getState().fileContent).toBe('');
    });
  });
});
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test -- --testPathPattern="buildStore.test.ts" --run`
Expected: FAIL

- [ ] **Step 4: Create the store and tests**

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test -- --testPathPattern="buildStore.test.ts" --run`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add mobile/src/features/build/buildStore.ts mobile/src/features/build/__tests__/buildStore.test.ts
git commit -m "feat(mobile-build): add build store with Zustand"
```

---

## Chunk 3: Basic Components

### Task 4: Create SegmentedControl

**Files:**
- Create: `mobile/src/components/build/SegmentedControl.tsx`
- Test: `mobile/src/components/build/__tests__/SegmentedControl.test.tsx`

- [ ] **Step 1: Write failing test**

```typescript
// mobile/src/components/build/__tests__/SegmentedControl.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { SegmentedControl } from '../SegmentedControl';

describe('SegmentedControl', () => {
  it('should render two tabs', () => {
    const { getByText } = render(
      <SegmentedControl
        options={[
          { value: 'crawl', label: '爬取任务' },
          { value: 'review', label: '审核队列' },
        ]}
        value="crawl"
        onChange={() => {}}
      />
    );

    expect(getByText('爬取任务')).toBeTruthy();
    expect(getByText('审核队列')).toBeTruthy();
  });

  it('should call onChange with correct value when tab clicked', () => {
    const onChange = jest.fn();
    const { getByText } = render(
      <SegmentedControl
        options={[
          { value: 'crawl', label: '爬取任务' },
          { value: 'review', label: '审核队列' },
        ]}
        value="crawl"
        onChange={onChange}
      />
    );

    fireEvent.press(getByText('审核队列'));
    expect(onChange).toHaveBeenCalledWith('review');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test -- --testPathPattern="SegmentedControl.test.tsx" --run`
Expected: FAIL

- [ ] **Step 3: Create SegmentedControl component**

```typescript
// mobile/src/components/build/SegmentedControl.tsx
import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { colors, typography, spacing, elevation } from '../../styles';

interface Option {
  value: string;
  label: string;
}

interface SegmentedControlProps {
  options: Option[];
  value: string;
  onChange: (value: string) => void;
}

export function SegmentedControl({ options, value, onChange }: SegmentedControlProps) {
  return (
    <View style={styles.container}>
      {options.map((option) => {
        const isSelected = option.value === value;
        return (
          <Pressable
            key={option.value}
            style={[styles.tab, isSelected && styles.tabSelected]}
            onPress={() => onChange(option.value)}
          >
            <Text style={[styles.tabText, isSelected && styles.tabTextSelected]}>
              {option.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: colors.accentLight,
    borderRadius: elevation.radiusLg,
    padding: 2,
  },
  tab: {
    flex: 1,
    paddingVertical: spacing[2],
    paddingHorizontal: spacing[3],
    borderRadius: elevation.radiusMd,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabSelected: {
    backgroundColor: colors.backgroundCard,
    ...elevation.shadowCard,
  },
  tabText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.textMuted,
  },
  tabTextSelected: {
    color: colors.text,
    fontWeight: typography.fontSemiBold,
  },
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test -- --testPathPattern="SegmentedControl.test.tsx" --run`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add mobile/src/components/build/SegmentedControl.tsx mobile/src/components/build/__tests__/SegmentedControl.test.tsx
git commit -m "feat(mobile-build): add SegmentedControl component"
```

---

### Task 5: Create TaskCard

**Files:**
- Create: `mobile/src/components/build/CrawlTab/TaskCard.tsx`
- Test: `mobile/src/components/build/CrawlTab/__tests__/TaskCard.test.tsx`

- [ ] **Step 1: Write failing test**

```typescript
// mobile/src/components/build/CrawlTab/__tests__/TaskCard.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { TaskCard } from '../TaskCard';

const mockTask = {
  id: 'task-123',
  knowledge_id: 'kb-1',
  user_id: 'user-1',
  total_urls: 10,
  completed_urls: 5,
  success_count: 4,
  fail_count: 1,
  status: 'processing',
  create_time: '2024-04-15T10:00:00Z',
  update_time: '2024-04-15T10:05:00Z',
};

describe('TaskCard', () => {
  it('should render task progress', () => {
    const { getByText } = render(
      <TaskCard task={mockTask} onDelete={jest.fn()} onRetry={jest.fn()} />
    );

    expect(getByText('5/10')).toBeTruthy();
  });

  it('should render status text', () => {
    const { getByText } = render(
      <TaskCard task={mockTask} onDelete={jest.fn()} onRetry={jest.fn()} />
    );

    expect(getByText('处理中')).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test -- --testPathPattern="TaskCard.test.tsx" --run`
Expected: FAIL

- [ ] **Step 3: Create TaskCard component**

```typescript
// mobile/src/components/build/CrawlTab/TaskCard.tsx
import React, { useState } from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { Check, X, Loader2, Trash2, RotateCw, ChevronDown, ChevronUp } from 'lucide-react-native';
import { CrawlTask } from '../../../api/crawl';
import { colors, typography, spacing, elevation } from '../../../styles';

interface TaskCardProps {
  task: CrawlTask;
  onDelete?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
}

const TERMINAL_STATES = ['SUCCESS', 'FAILED', 'completed', 'failed'];

export function TaskCard({ task, onDelete, onRetry }: TaskCardProps) {
  const [showFailedDetails, setShowFailedDetails] = useState(false);

  const progress = task.total_urls > 0
    ? Math.round((task.completed_urls / task.total_urls) * 100)
    : 0;

  const isTerminal = TERMINAL_STATES.includes(task.status);
  const hasFailedUrls = (task.failed_urls?.length ?? 0) > 0;
  const canRetry = isTerminal && hasFailedUrls && task.knowledge_id;

  const getStatusDisplay = () => {
    if (task.success_count === 0 && task.fail_count > 0) {
      return { icon: <X size={14} color={colors.error} />, text: '失败', style: styles.statusFailed };
    }

    if (task.status === 'completed' || task.status === 'SUCCESS') {
      if (task.fail_count === 0) {
        return { icon: <Check size={14} color={colors.success} />, text: '成功', style: styles.statusSuccess };
      } else {
        return { icon: <X size={14} color={colors.warning} />, text: '部分成功', style: styles.statusPartial };
      }
    }

    switch (task.status) {
      case 'FAILED':
        return { icon: <X size={14} color={colors.error} />, text: '失败', style: styles.statusFailed };
      case 'processing':
        return { icon: <Loader2 size={14} color={colors.accent} />, text: '处理中', style: styles.statusProcessing };
      case 'pending':
      default:
        return { icon: <Loader2 size={14} color={colors.textMuted} />, text: '等待中', style: styles.statusPending };
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
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.taskId}>Task: {task.id.slice(0, 8)}</Text>
        <View style={styles.actions}>
          {canRetry && onRetry && (
            <Pressable style={styles.actionBtn} onPress={() => onRetry(task.id)}>
              <RotateCw size={14} color={colors.accent} />
              <Text style={styles.actionText}>重试</Text>
            </Pressable>
          )}
          {isTerminal && onDelete && (
            <Pressable style={styles.actionBtn} onPress={() => onDelete(task.id)}>
              <Trash2 size={14} color={colors.error} />
            </Pressable>
          )}
          <View style={[styles.statusBadge, status.style]}>
            {status.icon}
            <Text style={[styles.statusText, status.style]}>{status.text}</Text>
          </View>
        </View>
      </View>

      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
        <Text style={styles.progressText}>{task.completed_urls}/{task.total_urls}</Text>
      </View>

      <View style={styles.stats}>
        <Text style={styles.statText}>成功: {task.success_count}</Text>
        <Text style={[styles.statText, task.fail_count > 0 && styles.failStat]}>失败: {task.fail_count}</Text>
        <Text style={styles.dateText}>{formatDate(task.create_time)}</Text>
      </View>

      {hasFailedUrls && (
        <Pressable
          style={styles.failedToggle}
          onPress={() => setShowFailedDetails(!showFailedDetails)}
        >
          {showFailedDetails ? (
            <ChevronUp size={12} color={colors.textMuted} />
          ) : (
            <ChevronDown size={12} color={colors.textMuted} />
          )}
          <Text style={styles.failedToggleText}>查看失败详情 ({task.failed_urls?.length})</Text>
        </Pressable>
      )}

      {showFailedDetails && (
        <View style={styles.failedList}>
          {task.failed_urls?.map((failed, idx) => (
            <View key={idx} style={styles.failedItem}>
              <Text style={styles.failedUrl} numberOfLines={1}>{failed.url}</Text>
              <Text style={styles.failedError}>{failed.error}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusLg,
    padding: spacing[4],
    marginBottom: spacing[3],
    ...elevation.shadowCard,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing[3],
  },
  taskId: {
    fontSize: typography.textSm,
    color: colors.textMuted,
    fontFamily: 'monospace',
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[2],
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[1],
    gap: 2,
  },
  actionText: {
    fontSize: typography.textXs,
    color: colors.accent,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing[2],
    paddingVertical: spacing[1],
    borderRadius: elevation.radiusMd,
    gap: 4,
  },
  statusSuccess: { backgroundColor: colors.successBg },
  statusFailed: { backgroundColor: colors.errorBg },
  statusPartial: { backgroundColor: colors.warningBg },
  statusProcessing: { backgroundColor: colors.accentLight },
  statusPending: { backgroundColor: colors.backgroundGlass },
  statusText: {
    fontSize: typography.textXs,
    fontWeight: typography.fontMedium,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing[2],
  },
  progressBar: {
    flex: 1,
    height: 6,
    backgroundColor: colors.backgroundGlass,
    borderRadius: 3,
    marginRight: spacing[2],
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.accent,
    borderRadius: 3,
  },
  progressText: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    fontFamily: 'monospace',
  },
  stats: {
    flexDirection: 'row',
    gap: spacing[4],
  },
  statText: {
    fontSize: typography.textXs,
    color: colors.textSecondary,
  },
  failStat: {
    color: colors.error,
  },
  dateText: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    marginLeft: 'auto',
  },
  failedToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing[2],
    paddingTop: spacing[2],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
    gap: 4,
  },
  failedToggleText: {
    fontSize: typography.textXs,
    color: colors.textMuted,
  },
  failedList: {
    marginTop: spacing[2],
    paddingTop: spacing[2],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  failedItem: {
    paddingVertical: spacing[1],
  },
  failedUrl: {
    fontSize: typography.textXs,
    color: colors.text,
    fontFamily: 'monospace',
  },
  failedError: {
    fontSize: typography.textXs,
    color: colors.error,
  },
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test -- --testPathPattern="TaskCard.test.tsx" --run`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add mobile/src/components/build/CrawlTab/TaskCard.tsx mobile/src/components/build/CrawlTab/__tests__/TaskCard.test.tsx
git commit -m "feat(mobile-build): add TaskCard component"
```

---

## Chunk 4: CrawlTab Components

### Task 6: Create CrawlPanel and TaskList

**Files:**
- Create: `mobile/src/components/build/CrawlTab/CrawlPanel.tsx`
- Create: `mobile/src/components/build/CrawlTab/TaskList.tsx`
- Test: `mobile/src/components/build/CrawlTab/__tests__/CrawlPanel.test.tsx`

- [ ] **Step 1: Create CrawlPanel**

```typescript
// mobile/src/components/build/CrawlTab/CrawlPanel.tsx
import React, { useEffect, useMemo, useCallback } from 'react';
import { View, Text, TextInput, ScrollView, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import { Play, Upload, Trash2 } from 'lucide-react-native';
import { useBuildStore } from '../../../features/build/buildStore';
import { colors, typography, spacing, elevation } from '../../../styles';

interface CrawlPanelProps {
  knowledgeBases: Array<{ id: string; name: string; file_count: number }>;
  onSelectKnowledge: (id: string) => void;
  selectedKnowledgeId: string | null;
  onOpenImportModal: () => void;
}

export function CrawlPanel({
  knowledgeBases,
  onSelectKnowledge,
  selectedKnowledgeId,
  onOpenImportModal,
}: CrawlPanelProps) {
  const crawlUrls = useBuildStore((s) => s.crawlUrls);
  const setCrawlUrls = useBuildStore((s) => s.setCrawlUrls);
  const submitBatchCrawl = useBuildStore((s) => s.submitBatchCrawl);
  const isPolling = useBuildStore((s) => s.isPolling);

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

  const selectedKB = knowledgeBases.find((kb) => kb.id === selectedKnowledgeId);

  return (
    <View style={styles.panel}>
      <View style={styles.form}>
        <View style={styles.field}>
          <Text style={styles.label}>知识库选择</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.kbList}>
            <Pressable
              style={[
                styles.kbChip,
                selectedKnowledgeId === null && styles.kbChipSelected,
              ]}
              onPress={() => onSelectKnowledge('')}
            >
              <Text style={[
                styles.kbChipText,
                selectedKnowledgeId === null && styles.kbChipTextSelected,
              ]}>
                全部
              </Text>
            </Pressable>
            {knowledgeBases.map((kb) => (
              <Pressable
                key={kb.id}
                style={[
                  styles.kbChip,
                  selectedKnowledgeId === kb.id && styles.kbChipSelected,
                ]}
                onPress={() => onSelectKnowledge(kb.id)}
              >
                <Text style={[
                  styles.kbChipText,
                  selectedKnowledgeId === kb.id && styles.kbChipTextSelected,
                ]}>
                  {kb.name}
                </Text>
              </Pressable>
            ))}
          </ScrollView>
          {selectedKB && (
            <Text style={styles.kbInfo}>{selectedKB.file_count} 个文件</Text>
          )}
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>URL列表</Text>
          <TextInput
            style={styles.textarea}
            placeholder="输入URL，每行一个"
            placeholderTextColor={colors.textMuted}
            value={crawlUrls}
            onChangeText={setCrawlUrls}
            multiline
            numberOfLines={6}
            textAlignVertical="top"
          />
        </View>

        <View style={styles.actions}>
          <Pressable
            style={[styles.btn, styles.btnPrimary, !isValid && styles.btnDisabled]}
            onPress={handleSubmit}
            disabled={!isValid || isPolling}
          >
            {isPolling ? (
              <ActivityIndicator size="small" color={colors.background} />
            ) : (
              <>
                <Play size={16} color={colors.background} />
                <Text style={styles.btnPrimaryText}>开始爬取</Text>
              </>
            )}
          </Pressable>
          <Pressable style={[styles.btn, styles.btnSecondary]} onPress={onOpenImportModal}>
            <Upload size={16} color={colors.accent} />
            <Text style={styles.btnSecondaryText}>批量导入</Text>
          </Pressable>
          <Pressable style={[styles.btn, styles.btnGhost]} onPress={handleClear}>
            <Trash2 size={16} color={colors.textMuted} />
            <Text style={styles.btnGhostText}>清空</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    padding: spacing[4],
  },
  form: {
    gap: spacing[4],
  },
  field: {
    gap: spacing[2],
  },
  label: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  kbList: {
    flexDirection: 'row',
    gap: spacing[2],
  },
  kbChip: {
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[2],
    backgroundColor: colors.backgroundGlass,
    borderRadius: elevation.radiusFull,
    borderWidth: 1,
    borderColor: colors.border,
  },
  kbChipSelected: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  kbChipText: {
    fontSize: typography.textSm,
    color: colors.text,
  },
  kbChipTextSelected: {
    color: colors.background,
  },
  kbInfo: {
    fontSize: typography.textXs,
    color: colors.textMuted,
  },
  textarea: {
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing[3],
    fontSize: typography.textSm,
    color: colors.text,
    minHeight: 120,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing[2],
    flexWrap: 'wrap',
  },
  btn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing[1],
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderRadius: elevation.radiusMd,
    minHeight: spacing.buttonHeightMd,
  },
  btnPrimary: {
    backgroundColor: colors.accent,
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnPrimaryText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.background,
  },
  btnSecondary: {
    backgroundColor: colors.accentLight,
  },
  btnSecondaryText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.accent,
  },
  btnGhost: {
    backgroundColor: 'transparent',
  },
  btnGhostText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
});
```

- [ ] **Step 2: Create TaskList**

```typescript
// mobile/src/components/build/CrawlTab/TaskList.tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { TaskCard } from './TaskCard';
import { useBuildStore } from '../../../features/build/buildStore';
import { colors, typography, spacing } from '../../../styles';

interface TaskListProps {
  onDelete?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
}

export function TaskList({ onDelete, onRetry }: TaskListProps) {
  const tasks = useBuildStore((s) => s.tasks);
  const removeTask = useBuildStore((s) => s.removeTask);
  const retryFailedUrls = useBuildStore((s) => s.retryFailedUrls);

  const handleDelete = onDelete || removeTask;
  const handleRetry = onRetry || retryFailedUrls;

  if (tasks.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>暂无爬取任务</Text>
      </View>
    );
  }

  // Sort by create_time descending (newest first)
  const sortedTasks = [...tasks].sort(
    (a, b) => new Date(b.create_time).getTime() - new Date(a.create_time).getTime()
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>任务列表 ({tasks.length})</Text>
      {sortedTasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onDelete={handleDelete}
          onRetry={handleRetry}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: spacing[4],
  },
  header: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
    marginBottom: spacing[3],
  },
  empty: {
    padding: spacing[8],
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
});
```

- [ ] **Step 3: Write tests for CrawlPanel**

- [ ] **Step 4: Run tests to verify they pass**

- [ ] **Step 5: Commit**

---

### Task 7: Create UrlImportModal

**Files:**
- Create: `mobile/src/components/build/CrawlTab/UrlImportModal.tsx`
- Test: `mobile/src/components/build/CrawlTab/__tests__/UrlImportModal.test.tsx`

- [ ] **Step 1: Create UrlImportModal**

```typescript
// mobile/src/components/build/CrawlTab/UrlImportModal.tsx
import React, { useState } from 'react';
import { View, Text, TextInput, Modal, Pressable, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { X } from 'lucide-react-native';
import { useBuildStore } from '../../../features/build/buildStore';
import { colors, typography, spacing, elevation } from '../../../styles';

export function UrlImportModal() {
  const isOpen = useBuildStore((s) => s.isImportModalOpen);
  const previewUrls = useBuildStore((s) => s.previewUrls);
  const setPreviewUrls = useBuildStore((s) => s.setPreviewUrls);
  const closeModal = useBuildStore((s) => s.closeImportModal);
  const submitBatchCrawl = useBuildStore((s) => s.submitBatchCrawl);
  const selectedKnowledgeId = useBuildStore((s) => s.selectedKnowledgeId);

  const [inputText, setInputText] = useState('');

  const handleImport = () => {
    const urls = inputText
      .split('\n')
      .map((url) => url.trim())
      .filter((url) => url.length > 0);
    setPreviewUrls(urls);
  };

  const handleConfirm = async () => {
    if (previewUrls.length > 0 && selectedKnowledgeId) {
      await submitBatchCrawl(previewUrls);
      closeModal();
      setInputText('');
      setPreviewUrls([]);
    }
  };

  const handleClose = () => {
    closeModal();
    setInputText('');
    setPreviewUrls([]);
  };

  return (
    <Modal visible={isOpen} animationType="slide" transparent>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.overlay}
      >
        <Pressable style={styles.backdrop} onPress={handleClose} />
        <View style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.title}>批量导入URL</Text>
            <Pressable onPress={handleClose} style={styles.closeBtn}>
              <X size={20} color={colors.text} />
            </Pressable>
          </View>

          <TextInput
            style={styles.textarea}
            placeholder="输入URL，每行一个"
            placeholderTextColor={colors.textMuted}
            value={inputText}
            onChangeText={setInputText}
            multiline
            numberOfLines={8}
            textAlignVertical="top"
          />

          <View style={styles.actions}>
            <Pressable style={styles.btnSecondary} onPress={handleImport}>
              <Text style={styles.btnSecondaryText}>预览</Text>
            </Pressable>
            <Pressable
              style={[styles.btnPrimary, previewUrls.length === 0 && styles.btnDisabled]}
              onPress={handleConfirm}
              disabled={previewUrls.length === 0}
            >
              <Text style={styles.btnPrimaryText}>导入 ({previewUrls.length})</Text>
            </Pressable>
          </View>

          {previewUrls.length > 0 && (
            <View style={styles.preview}>
              <Text style={styles.previewTitle}>预览 ({previewUrls.length})</Text>
              {previewUrls.slice(0, 5).map((url, idx) => (
                <Text key={idx} style={styles.previewUrl} numberOfLines={1}>
                  {url}
                </Text>
              ))}
              {previewUrls.length > 5 && (
                <Text style={styles.previewMore}>...还有 {previewUrls.length - 5} 个</Text>
              )}
            </View>
          )}
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  container: {
    backgroundColor: colors.backgroundCard,
    borderTopLeftRadius: elevation.radiusXl,
    borderTopRightRadius: elevation.radiusXl,
    padding: spacing[4],
    maxHeight: '80%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing[4],
  },
  title: {
    fontSize: typography.textBase,
    fontWeight: typography.fontSemiBold,
    color: colors.text,
  },
  closeBtn: {
    padding: spacing[1],
  },
  textarea: {
    backgroundColor: colors.background,
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing[3],
    fontSize: typography.textSm,
    color: colors.text,
    minHeight: 160,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing[2],
    marginTop: spacing[4],
  },
  btnPrimary: {
    flex: 1,
    backgroundColor: colors.accent,
    paddingVertical: spacing[3],
    borderRadius: elevation.radiusMd,
    alignItems: 'center',
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnPrimaryText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.background,
  },
  btnSecondary: {
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
  },
  btnSecondaryText: {
    fontSize: typography.textSm,
    color: colors.text,
  },
  preview: {
    marginTop: spacing[4],
    padding: spacing[3],
    backgroundColor: colors.background,
    borderRadius: elevation.radiusMd,
  },
  previewTitle: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    marginBottom: spacing[2],
  },
  previewUrl: {
    fontSize: typography.textXs,
    color: colors.text,
    fontFamily: 'monospace',
    paddingVertical: 2,
  },
  previewMore: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    marginTop: spacing[1],
  },
});
```

- [ ] **Step 2: Write tests**

- [ ] **Step 3: Run tests to verify they pass**

- [ ] **Step 4: Commit**

---

## Chunk 5: ReviewTab Components

### Task 8: Create FileSelectModal

**Files:**
- Create: `mobile/src/components/build/ReviewTab/FileSelectModal.tsx`
- Test: `mobile/src/components/build/ReviewTab/__tests__/FileSelectModal.test.tsx`

- [ ] **Step 1: Create FileSelectModal**

```typescript
// mobile/src/components/build/ReviewTab/FileSelectModal.tsx
import React from 'react';
import { View, Text, Modal, Pressable, FlatList, StyleSheet } from 'react-native';
import { X, FileText } from 'lucide-react-native';
import { KnowledgeFile } from '../../../api/knowledge';
import { colors, typography, spacing, elevation } from '../../../styles';

interface FileSelectModalProps {
  visible: boolean;
  files: KnowledgeFile[];
  onSelect: (file: KnowledgeFile) => void;
  onClose: () => void;
}

export function FileSelectModal({ visible, files, onSelect, onClose }: FileSelectModalProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
    });
  };

  const renderItem = ({ item }: { item: KnowledgeFile }) => (
    <Pressable
      style={styles.fileItem}
      onPress={() => {
        onSelect(item);
        onClose();
      }}
    >
      <FileText size={18} color={colors.accent} />
      <Text style={styles.fileName} numberOfLines={1}>
        {item.file_name}
      </Text>
      <Text style={styles.fileDate}>{formatDate(item.create_time)}</Text>
    </Pressable>
  );

  return (
    <Modal visible={visible} animationType="slide" transparent>
      <View style={styles.overlay}>
        <Pressable style={styles.backdrop} onPress={onClose} />
        <View style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.title}>选择文件</Text>
            <Pressable onPress={onClose} style={styles.closeBtn}>
              <X size={20} color={colors.text} />
            </Pressable>
          </View>

          <FlatList
            data={files}
            keyExtractor={(item) => item.id}
            renderItem={renderItem}
            ItemSeparatorComponent={() => <View style={styles.separator} />}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Text style={styles.emptyText}>暂无待审核文件</Text>
              </View>
            }
          />

          <View style={styles.footer}>
            <Pressable style={styles.cancelBtn} onPress={onClose}>
              <Text style={styles.cancelText}>取消</Text>
            </Pressable>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  container: {
    backgroundColor: colors.backgroundCard,
    borderTopLeftRadius: elevation.radiusXl,
    borderTopRightRadius: elevation.radiusXl,
    maxHeight: '70%',
    paddingBottom: spacing[4],
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing[4],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  title: {
    fontSize: typography.textBase,
    fontWeight: typography.fontSemiBold,
    color: colors.text,
  },
  closeBtn: {
    padding: spacing[1],
  },
  fileItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[4],
    gap: spacing[3],
  },
  fileName: {
    flex: 1,
    fontSize: typography.textSm,
    color: colors.text,
  },
  fileDate: {
    fontSize: typography.textXs,
    color: colors.textMuted,
  },
  separator: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: colors.border,
    marginLeft: spacing[4] + 18 + spacing[3],
  },
  empty: {
    padding: spacing[8],
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
  footer: {
    padding: spacing[4],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  cancelBtn: {
    padding: spacing[3],
    alignItems: 'center',
    borderRadius: elevation.radiusMd,
    backgroundColor: colors.background,
  },
  cancelText: {
    fontSize: typography.textSm,
    color: colors.text,
  },
});
```

- [ ] **Step 2: Write tests**

- [ ] **Step 3: Run tests to verify they pass**

- [ ] **Step 4: Commit**

---

### Task 9: Create ReviewInbox and ReviewEditor

**Files:**
- Create: `mobile/src/components/build/ReviewTab/ReviewInbox.tsx`
- Create: `mobile/src/components/build/ReviewTab/ReviewEditor.tsx`
- Test: `mobile/src/components/build/ReviewTab/__tests__/ReviewEditor.test.tsx`

- [ ] **Step 1: Create ReviewInbox**

```typescript
// mobile/src/components/build/ReviewTab/ReviewInbox.tsx
import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { ClipboardList } from 'lucide-react-native';
import { colors, typography, spacing, elevation } from '../../../styles';

interface ReviewInboxProps {
  count: number;
  onPress: () => void;
}

export function ReviewInbox({ count, onPress }: ReviewInboxProps) {
  const isDisabled = count === 0;

  return (
    <Pressable
      style={[styles.container, isDisabled && styles.disabled]}
      onPress={onPress}
      disabled={isDisabled}
    >
      <ClipboardList size={18} color={isDisabled ? colors.textMuted : colors.accent} />
      <Text style={[styles.text, isDisabled && styles.textDisabled]}>待审核文件</Text>
      <View style={[styles.badge, isDisabled && styles.badgeDisabled]}>
        <Text style={[styles.badgeText, isDisabled && styles.badgeTextDisabled]}>{count}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusMd,
    padding: spacing[3],
    gap: spacing[2],
    ...elevation.shadowCard,
  },
  disabled: {
    opacity: 0.6,
  },
  text: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  textDisabled: {
    color: colors.textMuted,
  },
  badge: {
    backgroundColor: colors.accent,
    borderRadius: elevation.radiusFull,
    paddingHorizontal: spacing[2],
    minWidth: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  badgeDisabled: {
    backgroundColor: colors.textMuted,
  },
  badgeText: {
    fontSize: typography.textXs,
    fontWeight: typography.fontBold,
    color: colors.background,
  },
  badgeTextDisabled: {
    color: colors.background,
  },
});
```

- [ ] **Step 2: Create ReviewEditor**

```typescript
// mobile/src/components/build/ReviewTab/ReviewEditor.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet, ActivityIndicator, ScrollView } from 'react-native';
import { Save, Play, Eye, Edit3 } from 'lucide-react-native';
import { useBuildStore } from '../../../features/build/buildStore';
import { colors, typography, spacing, elevation } from '../../../styles';

export function ReviewEditor() {
  const selectedFile = useBuildStore((s) => s.selectedFile);
  const fileContent = useBuildStore((s) => s.fileContent);
  const isLoadingContent = useBuildStore((s) => s.isLoadingContent);
  const isSaving = useBuildStore((s) => s.isSaving);
  const isIndexing = useBuildStore((s) => s.isIndexing);
  const isPreview = useBuildStore((s) => s.isPreview);
  const updateFileContent = useBuildStore((s) => s.updateFileContent);
  const triggerIndex = useBuildStore((s) => s.triggerIndex);
  const setIsPreview = useBuildStore((s) => s.setIsPreview);

  const [editedContent, setEditedContent] = useState(fileContent);

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
      <View style={styles.empty}>
        <Text style={styles.emptyText}>请从上方选择文件进行审核</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.fileName} numberOfLines={1}>
          {selectedFile.file_name}
        </Text>
        <View style={styles.actions}>
          <View style={styles.modeToggle}>
            <Pressable
              style={[styles.modeBtn, !isPreview && styles.modeBtnActive]}
              onPress={() => setIsPreview(false)}
            >
              <Edit3 size={14} color={!isPreview ? colors.accent : colors.textMuted} />
            </Pressable>
            <Pressable
              style={[styles.modeBtn, isPreview && styles.modeBtnActive]}
              onPress={() => setIsPreview(true)}
            >
              <Eye size={14} color={isPreview ? colors.accent : colors.textMuted} />
            </Pressable>
          </View>
        </View>
      </View>

      <View style={styles.editorWrapper}>
        {isLoadingContent ? (
          <View style={styles.loading}>
            <ActivityIndicator size="small" color={colors.accent} />
          </View>
        ) : isPreview ? (
          <ScrollView style={styles.preview}>
            <Text style={styles.previewText}>{editedContent}</Text>
          </ScrollView>
        ) : (
          <TextInput
            style={styles.editor}
            value={editedContent}
            onChangeText={setEditedContent}
            multiline
            textAlignVertical="top"
            placeholder="加载中..."
            placeholderTextColor={colors.textMuted}
          />
        )}
      </View>

      <View style={styles.footer}>
        <Pressable
          style={[styles.btn, styles.btnSecondary, editedContent === fileContent && styles.btnDisabled]}
          onPress={handleSave}
          disabled={isSaving || editedContent === fileContent}
        >
          {isSaving ? (
            <ActivityIndicator size="small" color={colors.accent} />
          ) : (
            <>
              <Save size={14} color={colors.accent} />
              <Text style={styles.btnSecondaryText}>保存</Text>
            </>
          )}
        </Pressable>
        <Pressable
          style={[styles.btn, styles.btnPrimary, isIndexing && styles.btnDisabled]}
          onPress={handleIndex}
          disabled={isIndexing}
        >
          {isIndexing ? (
            <ActivityIndicator size="small" color={colors.background} />
          ) : (
            <>
              <Play size={14} color={colors.background} />
              <Text style={styles.btnPrimaryText}>确认索引</Text>
            </>
          )}
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusLg,
    overflow: 'hidden',
    ...elevation.shadowCard,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: spacing[3],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  fileName: {
    flex: 1,
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing[2],
  },
  modeToggle: {
    flexDirection: 'row',
    backgroundColor: colors.backgroundGlass,
    borderRadius: elevation.radiusMd,
    padding: 2,
  },
  modeBtn: {
    padding: spacing[1],
    borderRadius: elevation.radiusSm,
  },
  modeBtnActive: {
    backgroundColor: colors.backgroundCard,
  },
  editorWrapper: {
    flex: 1,
    minHeight: 200,
  },
  editor: {
    flex: 1,
    padding: spacing[3],
    fontSize: typography.textSm,
    color: colors.text,
    fontFamily: 'monospace',
  },
  preview: {
    flex: 1,
    padding: spacing[3],
  },
  previewText: {
    fontSize: typography.textSm,
    color: colors.text,
    lineHeight: 22,
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  footer: {
    flexDirection: 'row',
    gap: spacing[2],
    padding: spacing[3],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  btn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing[1],
    paddingVertical: spacing[2],
    borderRadius: elevation.radiusMd,
    minHeight: 40,
  },
  btnPrimary: {
    backgroundColor: colors.accent,
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnPrimaryText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.background,
  },
  btnSecondary: {
    backgroundColor: colors.accentLight,
  },
  btnSecondaryText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.accent,
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing[8],
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
});
```

- [ ] **Step 3: Write tests**

- [ ] **Step 4: Run tests to verify they pass**

- [ ] **Step 5: Commit**

---

## Chunk 6: BuildScreen

### Task 10: Create BuildScreen

**Files:**
- Create: `mobile/src/screens/BuildScreen.tsx`
- Test: `mobile/src/screens/__tests__/BuildScreen.test.tsx`

- [ ] **Step 1: Create BuildScreen**

```typescript
// mobile/src/screens/BuildScreen.tsx
import React, { useEffect, useCallback } from 'react';
import { View, StyleSheet, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ChevronLeft } from 'lucide-react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SegmentedControl } from '../components/build/SegmentedControl';
import { CrawlPanel } from '../components/build/CrawlTab/CrawlPanel';
import { TaskList } from '../components/build/CrawlTab/TaskList';
import { UrlImportModal } from '../components/build/CrawlTab/UrlImportModal';
import { ReviewInbox } from '../components/build/ReviewTab/ReviewInbox';
import { ReviewEditor } from '../components/build/ReviewTab/ReviewEditor';
import { FileSelectModal } from '../components/build/ReviewTab/FileSelectModal';
import { useBuildStore } from '../features/build/buildStore';
import { colors, spacing } from '../styles';
import type { HomeStackParamList } from '../navigation/types';

type NavigationProp = NativeStackNavigationProp<HomeStackParamList, 'KnowledgeBuild'>;

// Mock knowledge bases for demo
const MOCK_KB_LIST = [
  { id: 'kb-1', name: '教务处', file_count: 12 },
  { id: 'kb-2', name: '图书馆', file_count: 8 },
  { id: 'kb-3', name: '就业中心', file_count: 5 },
];

export function BuildScreen() {
  const navigation = useNavigation<NavigationProp>();

  const activeTab = useBuildStore((s) => s.activeTab);
  const setActiveTab = useBuildStore((s) => s.setActiveTab);
  const selectedKnowledgeId = useBuildStore((s) => s.selectedKnowledgeId);
  const setSelectedKnowledgeId = useBuildStore((s) => s.setSelectedKnowledgeId);
  const openImportModal = useBuildStore((s) => s.openImportModal);
  const fetchPendingFiles = useBuildStore((s) => s.fetchPendingFiles);
  const fetchFileContent = useBuildStore((s) => s.fetchFileContent);
  const pendingFiles = useBuildStore((s) => s.pendingFiles);
  const pendingReviewCount = useBuildStore((s) => s.pendingReviewCount);
  const fetchTasks = useBuildStore((s) => s.fetchTasks);

  const [showFileModal, setShowFileModal] = React.useState(false);

  useEffect(() => {
    fetchTasks();
    fetchPendingFiles();
  }, [fetchTasks, fetchPendingFiles]);

  const handleTabChange = useCallback((tab: string) => {
    setActiveTab(tab as 'crawl' | 'review');
    if (tab === 'review' && pendingFiles.length > 0) {
      // Auto-select first file when switching to review
      fetchFileContent(pendingFiles[0].id);
    }
  }, [setActiveTab, fetchFileContent, pendingFiles]);

  const handleSelectFile = useCallback((file: any) => {
    fetchFileContent(file.id);
  }, [fetchFileContent]);

  const handleBack = () => {
    navigation.goBack();
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Pressable onPress={handleBack} style={styles.backBtn}>
          <ChevronLeft size={24} color={colors.text} />
        </Pressable>
        <View style={styles.segmentContainer}>
          <SegmentedControl
            options={[
              { value: 'crawl', label: '爬取任务' },
              { value: 'review', label: '审核队列' },
            ]}
            value={activeTab}
            onChange={handleTabChange}
          />
        </View>
        <View style={styles.placeholder} />
      </View>

      <View style={styles.content}>
        {activeTab === 'crawl' ? (
          <View style={styles.crawlContent}>
            <CrawlPanel
              knowledgeBases={MOCK_KB_LIST}
              onSelectKnowledge={setSelectedKnowledgeId}
              selectedKnowledgeId={selectedKnowledgeId}
              onOpenImportModal={openImportModal}
            />
            <TaskList />
          </View>
        ) : (
          <View style={styles.reviewContent}>
            <View style={styles.inboxContainer}>
              <ReviewInbox
                count={pendingReviewCount}
                onPress={() => setShowFileModal(true)}
              />
            </View>
            <View style={styles.editorContainer}>
              <ReviewEditor />
            </View>
          </View>
        )}
      </View>

      <UrlImportModal />

      <FileSelectModal
        visible={showFileModal}
        files={pendingFiles}
        onSelect={handleSelectFile}
        onClose={() => setShowFileModal(false)}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[2],
    gap: spacing[3],
  },
  backBtn: {
    padding: spacing[1],
  },
  segmentContainer: {
    flex: 1,
  },
  placeholder: {
    width: 32,
  },
  content: {
    flex: 1,
  },
  crawlContent: {
    flex: 1,
  },
  reviewContent: {
    flex: 1,
    padding: spacing[4],
    gap: spacing[3],
  },
  inboxContainer: {
    marginBottom: spacing[2],
  },
  editorContainer: {
    flex: 1,
  },
});
```

- [ ] **Step 2: Write tests**

- [ ] **Step 3: Run tests to verify they pass**

- [ ] **Step 4: Commit**

---

## Chunk 7: Navigation Integration

### Task 11: Update TabNavigator

**Files:**
- Modify: `mobile/src/navigation/TabNavigator.tsx`

- [ ] **Step 1: Add BuildScreen import and HomeStack update**

```typescript
// Add import
import { BuildScreen } from '../screens/BuildScreen';

// In HomeStackNavigator function, add KnowledgeBuild screen
function HomeStackNavigator() {
  return (
    <HomeStack.Navigator screenOptions={{ headerShown: false }}>
      <HomeStack.Screen name="Home" component={HomeScreen} />
      <HomeStack.Screen name="KnowledgeBuild" component={BuildScreen} />
    </HomeStack.Navigator>
  );
}
```

- [ ] **Step 2: Test the navigation works**

- [ ] **Step 3: Commit**

```bash
git add mobile/src/navigation/TabNavigator.tsx
git commit -m "feat(mobile-build): add KnowledgeBuild to HomeStack"
```

---

### Task 12: Update FeatureGrid to navigate to KnowledgeBuild

**Files:**
- Modify: `mobile/src/components/home/FeatureGrid.tsx`

- [ ] **Step 1: Update navigation to KnowledgeBuild**

```typescript
// Update the second Pressable in FeatureGrid
<Pressable
  style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
  onPress={() => {
    const parent = navigation.getParent();
    if (parent) {
      parent.navigate('HomeTab', {
        screen: 'KnowledgeBuild',
      });
    }
  }}
>
```

- [ ] **Step 2: Test navigation works**

- [ ] **Step 3: Commit**

```bash
git add mobile/src/components/home/FeatureGrid.tsx
git commit -m "feat(mobile-build): link FeatureGrid to KnowledgeBuild"
```

---

## Chunk 8: Update Progress Logs

### Task 13: Update feature-list.json and progress-log.md

**Files:**
- Modify: `mobile/docs/feature-list.json`
- Modify: `mobile/docs/progress-log.md`

- [ ] **Step 1: Update feature status in feature-list.json**

Update build module features from "pending" to "completed":
- F-030: BuildStore
- F-031: CrawlPanel + UrlImportModal
- F-032: TaskList + TaskCard
- F-033: ReviewInbox + ReviewEditor
- F-034: BuildScreen

- [ ] **Step 2: Update progress-log.md**

Add entry for build module completion

- [ ] **Step 3: Commit**

```bash
git add mobile/docs/feature-list.json mobile/docs/progress-log.md
git commit -m "docs(mobile): mark build module as completed"
```

---

## Summary

**Total Tasks:** 13 tasks across 8 chunks

**Dependencies:**
- Chunk 1 (API) → Chunk 2 (Store)
- Chunk 2 (Store) → Chunk 3 (Basic Components)
- Chunk 3 (Basic Components) → Chunk 4 (CrawlTab) → Chunk 6 (BuildScreen)
- Chunk 3 (Basic Components) → Chunk 5 (ReviewTab) → Chunk 6 (BuildScreen)
- Chunk 6 (BuildScreen) → Chunk 7 (Navigation)

**Testing Strategy:**
- API tests: Mock axios, verify correct endpoints called
- Store tests: Verify state mutations
- Component tests: Render verification, interaction testing
- Integration: Manual navigation testing

**Design Tokens Used:**
- colors: background, accent, text, textMuted, border, success/error/warning
- typography: textSm/textXs, fontMedium/fontSemiBold
- spacing: spacing[2]-spacing[4]
- elevation: radiusMd/radiusLg, shadowCard

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-15-mobile-build-module-plan.md`. Ready to execute?**
