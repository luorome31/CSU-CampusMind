# Phase 3: Knowledge List & Detail View Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现知识库浏览功能，包括知识库列表、文件列表和文件详情查看页面

**Architecture:** 采用 Zustand 状态管理 + React Router 路由 + API 客户端分层架构。页面通过路由跳转，状态通过 store 集中管理。

**Tech Stack:** React, TypeScript, Zustand, React Router, react-markdown, react-syntax-highlighter

---

## File Structure

```
frontend/src/
├── api/
│   └── knowledge.ts                    # 知识库 API 客户端
├── features/knowledge/
│   ├── KnowledgeListPage.tsx           # 知识库列表页
│   ├── KnowledgeListPage.css
│   ├── KnowledgeFileListPage.tsx       # 文件列表页
│   ├── KnowledgeFileListPage.css
│   ├── KnowledgeFileDetailPage.tsx     # 文件详情页
│   ├── KnowledgeFileDetailPage.css
│   ├── knowledgeListStore.ts           # Zustand store
│   └── knowledgeListStore.test.ts     # Store 测试
└── components/knowledge/
    ├── KnowledgeCard/
    │   ├── KnowledgeCard.tsx
    │   ├── KnowledgeCard.css
    │   └── KnowledgeCard.test.tsx
    ├── FileTable/
    │   ├── FileTable.tsx
    │   ├── FileTable.css
    │   └── FileTable.test.tsx
    └── FileContentViewer/
        ├── FileContentViewer.tsx
        ├── FileContentViewer.css
        └── FileContentViewer.test.tsx
```

---

## Dependencies

需要安装 `react-syntax-highlighter`：
```bash
cd frontend && npm install react-syntax-highlighter && npm install -D @types/react-syntax-highlighter
```

---

## Chunk 1: API Layer & Types

### Task 1: Create knowledge API client

**Files:**
- Create: `frontend/src/api/knowledge.ts`
- Test: `frontend/src/api/knowledge.test.ts`

- [ ] **Step 1: Write failing test**

```typescript
// frontend/src/api/knowledge.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { knowledgeApi } from './knowledge';

describe('knowledgeApi', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('fetchKnowledgeBases calls correct endpoint', async () => {
    const mockResponse = [
      { id: 'kb1', name: 'KB 1', description: 'desc', user_id: 'user1', create_time: '', update_time: '' }
    ];
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
      text: async () => JSON.stringify(mockResponse),
    });

    const result = await knowledgeApi.fetchKnowledgeBases('user1');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/users/user1/knowledge'),
      expect.any(Object)
    );
  });

  it('fetchFiles calls correct endpoint', async () => {
    const mockResponse = [{ id: 'file1', file_name: 'test.md' }];
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
      text: async () => JSON.stringify(mockResponse),
    });

    const result = await knowledgeApi.fetchFiles('kb1');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/knowledge/kb1/files'),
      expect.any(Object)
    );
  });

  it('fetchFileContent returns raw markdown string', async () => {
    const markdownContent = '# Hello\n\nThis is markdown.';
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      text: async () => markdownContent,
    });

    const result = await knowledgeApi.fetchFileContent('file1');
    expect(result).toBe(markdownContent);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm run test:run -- api/knowledge.test.ts
```
Expected: FAIL - knowledgeApi not defined

- [ ] **Step 3: Write minimal implementation**

```typescript
// frontend/src/api/knowledge.ts
import { apiClient } from './client';

export interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  user_id: string;
  create_time: string;
  update_time: string;
}

export interface KnowledgeFile {
  id: string;
  file_name: string;
  knowledge_id: string;
  user_id: string;
  status: 'process' | 'success' | 'fail' | 'pending_verify' | 'verified' | 'indexing' | 'indexed';
  oss_url: string;
  file_size: number;
  create_time: string;
  update_time: string;
}

class KnowledgeApi {
  async fetchKnowledgeBases(userId: string): Promise<KnowledgeBase[]> {
    return apiClient.get<KnowledgeBase[]>(`/users/${userId}/knowledge`);
  }

  async fetchFiles(knowledgeId: string): Promise<KnowledgeFile[]> {
    return apiClient.get<KnowledgeFile[]>(`/knowledge/${knowledgeId}/files`);
  }

  async fetchFileContent(fileId: string): Promise<string> {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/knowledge_file/${fileId}/content`);
    return response.text();
  }
}

export const knowledgeApi = new KnowledgeApi();
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm run test:run -- api/knowledge.test.ts
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/knowledge.ts frontend/src/api/knowledge.test.ts
git commit -m "feat(api): add knowledge API client"
```

---

## Chunk 2: State Management (Zustand Store)

### Task 2: Create knowledgeListStore

**Files:**
- Create: `frontend/src/features/knowledge/knowledgeListStore.ts`
- Test: `frontend/src/features/knowledge/knowledgeListStore.test.ts`

- [ ] **Step 1: Write failing test**

```typescript
// frontend/src/features/knowledge/knowledgeListStore.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { knowledgeListStore } from './knowledgeListStore';
import * as knowledgeApi from '../../api/knowledge';

vi.mock('../../api/knowledge');

describe('knowledgeListStore', () => {
  beforeEach(() => {
    // Reset store state
    knowledgeListStore.setState({
      knowledgeBases: [],
      currentKB: null,
      files: [],
      currentFile: null,
      currentFileContent: '',
      isLoadingKBs: false,
      isLoadingFiles: false,
      isLoadingContent: false,
      error: null,
    });
  });

  it('fetchKnowledgeBases loads KBs successfully', async () => {
    const mockKBs: knowledgeApi.KnowledgeBase[] = [
      { id: 'kb1', name: 'KB 1', description: 'desc', user_id: 'user1', create_time: '', update_time: '' }
    ];
    vi.mocked(knowledgeApi.knowledgeApi.fetchKnowledgeBases).mockResolvedValue(mockKBs);

    await knowledgeListStore.getState().fetchKnowledgeBases();

    expect(knowledgeListStore.getState().knowledgeBases).toEqual(mockKBs);
    expect(knowledgeListStore.getState().isLoadingKBs).toBe(false);
  });

  it('fetchKnowledgeBases handles error', async () => {
    vi.mocked(knowledgeApi.knowledgeApi.fetchKnowledgeBases).mockRejectedValue(new Error('API Error'));

    await knowledgeListStore.getState().fetchKnowledgeBases();

    expect(knowledgeListStore.getState().error).toBe('API Error');
    expect(knowledgeListStore.getState().isLoadingKBs).toBe(false);
  });

  it('fetchFiles loads files for given KB', async () => {
    const mockFiles: knowledgeApi.KnowledgeFile[] = [
      { id: 'f1', file_name: 'test.md', knowledge_id: 'kb1', user_id: 'u1', status: 'success', oss_url: '', file_size: 1024, create_time: '', update_time: '' }
    ];
    vi.mocked(knowledgeApi.knowledgeApi.fetchFiles).mockResolvedValue(mockFiles);

    await knowledgeListStore.getState().fetchFiles('kb1');

    expect(knowledgeListStore.getState().files).toEqual(mockFiles);
  });

  it('fetchFileContent loads content and sets currentFile', async () => {
    const mockFile: knowledgeApi.KnowledgeFile = {
      id: 'f1', file_name: 'test.md', knowledge_id: 'kb1', user_id: 'u1',
      status: 'success', oss_url: '', file_size: 1024, create_time: '', update_time: ''
    };
    const mockContent = '# Markdown Content';
    vi.mocked(knowledgeApi.knowledgeApi.fetchFileContent).mockResolvedValue(mockContent);
    vi.mocked(knowledgeApi.knowledgeApi.fetchFiles).mockResolvedValue([mockFile]);

    await knowledgeListStore.getState().fetchFileContent('f1');

    expect(knowledgeListStore.getState().currentFileContent).toBe(mockContent);
  });

  it('clearError resets error state', async () => {
    knowledgeListStore.setState({ error: 'Some error' });
    knowledgeListStore.getState().clearError();
    expect(knowledgeListStore.getState().error).toBeNull();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm run test:run -- features/knowledge/knowledgeListStore.test.ts
```
Expected: FAIL - knowledgeListStore not defined

- [ ] **Step 3: Write minimal implementation**

```typescript
// frontend/src/features/knowledge/knowledgeListStore.ts
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
      // Get user_id from sessionStorage (same pattern as client.ts)
      const userStr = sessionStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : null;
      const userId = user?.id || 'system';
      const kb = await knowledgeApi.fetchKnowledgeBases(userId);
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
      // Find the file in current files list
      const file = get().files.find(f => f.id === fileId) || null;
      const content = await knowledgeApi.fetchFileContent(fileId);
      set({ currentFile: file, currentFileContent: content, isLoadingContent: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch file content', isLoadingContent: false });
    }
  },

  setCurrentKB: (kb) => set({ currentKB: kb }),

  clearError: () => set({ error: null }),
}));
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm run test:run -- features/knowledge/knowledgeListStore.test.ts
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/knowledge/knowledgeListStore.ts frontend/src/features/knowledge/knowledgeListStore.test.ts
git commit -m "feat(knowledge): add knowledgeListStore with fetchKnowledgeBases, fetchFiles, fetchFileContent"
```

---

## Chunk 3: UI Components

### Task 3: Create KnowledgeCard component

**Files:**
- Create: `frontend/src/components/knowledge/KnowledgeCard/KnowledgeCard.tsx`
- Create: `frontend/src/components/knowledge/KnowledgeCard/KnowledgeCard.css`
- Create: `frontend/src/components/knowledge/KnowledgeCard/KnowledgeCard.test.tsx`

- [ ] **Step 1: Write failing test**

```tsx
// frontend/src/components/knowledge/KnowledgeCard/KnowledgeCard.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KnowledgeCard } from './KnowledgeCard';
import type { KnowledgeBase } from '../../../api/knowledge';

describe('KnowledgeCard', () => {
  const mockKB: KnowledgeBase = {
    id: 'kb1',
    name: 'Test Knowledge Base',
    description: 'This is a test knowledge base',
    user_id: 'user1',
    create_time: '2024-01-01T00:00:00',
    update_time: '2024-01-02T00:00:00',
  };

  it('renders KB name and description', () => {
    render(<KnowledgeCard knowledge={mockKB} fileCount={5} onClick={() => {}} />);
    expect(screen.getByText('Test Knowledge Base')).toBeInTheDocument();
    expect(screen.getByText('This is a test knowledge base')).toBeInTheDocument();
  });

  it('renders file count badge', () => {
    render(<KnowledgeCard knowledge={mockKB} fileCount={5} onClick={() => {}} />);
    expect(screen.getByText('5 个文件')).toBeInTheDocument();
  });

  it('calls onClick when card is clicked', () => {
    const handleClick = vi.fn();
    render(<KnowledgeCard knowledge={mockKB} fileCount={5} onClick={handleClick} />);
    screen.getByText('Test Knowledge Base').click();
    expect(handleClick).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm run test:run -- KnowledgeCard.test.tsx
```
Expected: FAIL - KnowledgeCard not defined

- [ ] **Step 3: Write minimal implementation**

```tsx
// frontend/src/components/knowledge/KnowledgeCard/KnowledgeCard.tsx
import { Card } from '../../ui';
import './KnowledgeCard.css';

export interface KnowledgeCardProps {
  knowledge: {
    id: string;
    name: string;
    description: string;
  };
  fileCount: number;
  onClick: () => void;
}

export function KnowledgeCard({ knowledge, fileCount, onClick }: KnowledgeCardProps) {
  return (
    <Card
      className="knowledge-card"
      onClick={onClick}
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <div className="knowledge-card-header">
        <h3 className="knowledge-card-title">{knowledge.name}</h3>
        <span className="knowledge-card-badge">{fileCount} 个文件</span>
      </div>
      <p className="knowledge-card-description">{knowledge.description}</p>
    </Card>
  );
}
```

```css
/* frontend/src/components/knowledge/KnowledgeCard/KnowledgeCard.css */
.knowledge-card {
  cursor: pointer;
  transition: transform var(--ease-default, cubic-bezier(0.16, 1, 0.3, 1)),
              box-shadow var(--ease-default, cubic-bezier(0.16, 1, 0.3, 1));
}

.knowledge-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card-hover, 0 8px 18px rgba(45, 43, 40, 0.1));
}

.knowledge-card:focus-visible {
  outline: 2px solid var(--accent, #537D96);
  outline-offset: 2px;
}

.knowledge-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3, 0.75rem);
  margin-bottom: var(--space-3, 0.75rem);
}

.knowledge-card-title {
  font-size: var(--text-lg, 1.125rem);
  font-weight: 600;
  color: var(--text, #3B3D3F);
  margin: 0;
  line-height: 1.4;
}

.knowledge-card-badge {
  font-size: var(--text-xs, 0.75rem);
  color: var(--text-muted, #8E9196);
  background: var(--bg-inset, #E8E5DD);
  padding: var(--space-1, 0.25rem) var(--space-2, 0.5rem);
  border-radius: var(--radius-full, 9999px);
  white-space: nowrap;
}

.knowledge-card-description {
  font-size: var(--text-sm, 0.875rem);
  color: var(--text-light, #6B6F73);
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm run test:run -- KnowledgeCard.test.tsx
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/knowledge/KnowledgeCard/
git commit -m "feat(knowledge): add KnowledgeCard component"
```

---

### Task 4: Create FileTable component

**Files:**
- Create: `frontend/src/components/knowledge/FileTable/FileTable.tsx`
- Create: `frontend/src/components/knowledge/FileTable/FileTable.css`
- Create: `frontend/src/components/knowledge/FileTable/FileTable.test.tsx`

- [ ] **Step 1: Write failing test**

```tsx
// frontend/src/components/knowledge/FileTable/FileTable.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FileTable } from './FileTable';
import type { KnowledgeFile } from '../../../api/knowledge';

describe('FileTable', () => {
  const mockFiles: KnowledgeFile[] = [
    { id: 'f1', file_name: 'doc.md', knowledge_id: 'kb1', user_id: 'u1', status: 'success', oss_url: '', file_size: 1024, create_time: '2024-01-01', update_time: '2024-01-02' },
    { id: 'f2', file_name: 'notes.md', knowledge_id: 'kb1', user_id: 'u1', status: 'process', oss_url: '', file_size: 512, create_time: '2024-01-01', update_time: '2024-01-03' },
  ];

  it('renders file rows', () => {
    render(<FileTable files={mockFiles} onFileClick={() => {}} />);
    expect(screen.getByText('doc.md')).toBeInTheDocument();
    expect(screen.getByText('notes.md')).toBeInTheDocument();
  });

  it('renders status badges', () => {
    render(<FileTable files={mockFiles} onFileClick={() => {}} />);
    expect(screen.getByText('成功')).toBeInTheDocument();
    expect(screen.getByText('处理中')).toBeInTheDocument();
  });

  it('calls onFileClick when row clicked', () => {
    const handleClick = vi.fn();
    render(<FileTable files={mockFiles} onFileClick={handleClick} />);
    screen.getByText('doc.md').click();
    expect(handleClick).toHaveBeenCalledWith(mockFiles[0]);
  });

  it('formats file size correctly', () => {
    render(<FileTable files={mockFiles} onFileClick={() => {}} />);
    expect(screen.getByText('1.0 KB')).toBeInTheDocument();
    expect(screen.getByText('0.5 KB')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm run test:run -- FileTable.test.tsx
```
Expected: FAIL - FileTable not defined

- [ ] **Step 3: Write minimal implementation**

```tsx
// frontend/src/components/knowledge/FileTable/FileTable.tsx
import { Badge } from '../../ui';
import type { KnowledgeFile } from '../../../api/knowledge';
import './FileTable.css';

export interface FileTableProps {
  files: KnowledgeFile[];
  onFileClick: (file: KnowledgeFile) => void;
}

const STATUS_LABELS: Record<KnowledgeFile['status'], string> = {
  process: '处理中',
  indexing: '索引中',
  success: '成功',
  verified: '已验证',
  indexed: '已索引',
  fail: '失败',
  pending_verify: '待验证',
};

const STATUS_VARIANT: Record<KnowledgeFile['status'], 'success' | 'error' | 'warning' | 'info'> = {
  process: 'info',
  indexing: 'info',
  success: 'success',
  verified: 'success',
  indexed: 'success',
  fail: 'error',
  pending_verify: 'warning',
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateStr: string): string {
  return dateStr.split('T')[0];
}

export function FileTable({ files, onFileClick }: FileTableProps) {
  if (files.length === 0) {
    return <div className="file-table-empty">暂无文件</div>;
  }

  return (
    <div className="file-table-wrapper">
      <table className="file-table">
        <thead>
          <tr>
            <th>文件名</th>
            <th>状态</th>
            <th>大小</th>
            <th>更新时间</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr
              key={file.id}
              className="file-table-row"
              onClick={() => onFileClick(file)}
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && onFileClick(file)}
            >
              <td className="file-table-name">{file.file_name}</td>
              <td className="file-table-status">
                <Badge variant={STATUS_VARIANT[file.status]} size="sm">
                  {STATUS_LABELS[file.status]}
                </Badge>
              </td>
              <td className="file-table-size">{formatFileSize(file.file_size)}</td>
              <td className="file-table-date">{formatDate(file.update_time)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

```css
/* frontend/src/components/knowledge/FileTable/FileTable.css */
.file-table-wrapper {
  overflow-x: auto;
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--border, rgba(83, 125, 150, 0.22));
  background: var(--bg-card, #FCFAF5);
}

.file-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm, 0.875rem);
}

.file-table th {
  text-align: left;
  padding: var(--space-3, 0.75rem) var(--space-4, 1rem);
  font-weight: 500;
  color: var(--text-muted, #8E9196);
  background: var(--bg-inset, #E8E5DD);
  border-bottom: 1px solid var(--border, rgba(83, 125, 150, 0.22));
}

.file-table td {
  padding: var(--space-3, 0.75rem) var(--space-4, 1rem);
  color: var(--text, #3B3D3F);
  border-bottom: 1px solid var(--border-subtle, rgba(45, 43, 40, 0.08));
}

.file-table-row {
  cursor: pointer;
  transition: background-color var(--ease-default, cubic-bezier(0.16, 1, 0.3, 1));
}

.file-table-row:hover {
  background: var(--overlay-subtle, rgba(0, 0, 0, 0.03));
}

.file-table-row:focus-visible {
  outline: 2px solid var(--accent, #537D96);
  outline-offset: -2px;
}

.file-table-row:last-child td {
  border-bottom: none;
}

.file-table-name {
  font-weight: 500;
}

.file-table-status {
  white-space: nowrap;
}

.file-table-size {
  color: var(--text-light, #6B6F73);
}

.file-table-date {
  color: var(--text-light, #6B6F73);
}

.file-table-empty {
  text-align: center;
  padding: var(--space-8, 2rem);
  color: var(--text-muted, #8E9196);
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm run test:run -- FileTable.test.tsx
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/knowledge/FileTable/
git commit -m "feat(knowledge): add FileTable component with status badges"
```

---

### Task 5: Create FileContentViewer component

**Files:**
- Create: `frontend/src/components/knowledge/FileContentViewer/FileContentViewer.tsx`
- Create: `frontend/src/components/knowledge/FileContentViewer/FileContentViewer.css`
- Create: `frontend/src/components/knowledge/FileContentViewer/FileContentViewer.test.tsx`

- [ ] **Step 1: Write failing test**

```tsx
// frontend/src/components/knowledge/FileContentViewer/FileContentViewer.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FileContentViewer } from './FileContentViewer';

describe('FileContentViewer', () => {
  const markdownContent = '# Hello\n\nThis is **bold** and `code`.';

  it('renders markdown content', () => {
    render(<FileContentViewer content={markdownContent} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('This is bold and code.')).toBeInTheDocument();
  });

  it('renders read-only badge', () => {
    render(<FileContentViewer content={markdownContent} />);
    expect(screen.getByText('只读')).toBeInTheDocument();
  });

  it('renders code blocks with syntax highlighting', () => {
    const contentWithCode = '# Code\n\n```python\ndef hello():\n    print("world")\n```';
    render(<FileContentViewer content={contentWithCode} />);
    expect(screen.getByText('python')).toBeInTheDocument();
  });

  it('handles empty content', () => {
    render(<FileContentViewer content="" />);
    expect(screen.getByText('暂无内容')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm run test:run -- FileContentViewer.test.tsx
```
Expected: FAIL - FileContentViewer not defined

- [ ] **Step 3: Write minimal implementation**

```tsx
// frontend/src/components/knowledge/FileContentViewer/FileContentViewer.tsx
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { Badge } from '../../ui';
import './FileContentViewer.css';

export interface FileContentViewerProps {
  content: string;
  fileName?: string;
}

export function FileContentViewer({ content, fileName }: FileContentViewerProps) {
  if (!content) {
    return <div className="file-content-empty">暂无内容</div>;
  }

  return (
    <div className="file-content-viewer">
      <div className="file-content-header">
        {fileName && <span className="file-content-name">{fileName}</span>}
        <Badge variant="info" size="sm">只读</Badge>
      </div>
      <div className="file-content-body">
        <ReactMarkdown
          components={{
            code({ node, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              const inline = !match;
              return !inline ? (
                <SyntaxHighlighter
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    margin: '1em 0',
                    borderRadius: 'var(--radius-md, 8px)',
                    fontSize: 'var(--text-sm, 0.875rem)',
                  }}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
```

```css
/* frontend/src/components/knowledge/FileContentViewer/FileContentViewer.css */
.file-content-viewer {
  background: var(--bg-card, #FCFAF5);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--border, rgba(83, 125, 150, 0.22));
  overflow: hidden;
}

.file-content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3, 0.75rem) var(--space-4, 1rem);
  background: var(--bg-inset, #E8E5DD);
  border-bottom: 1px solid var(--border, rgba(83, 125, 150, 0.22));
}

.file-content-name {
  font-weight: 500;
  color: var(--text, #3B3D3F);
}

.file-content-body {
  padding: var(--space-6, 1.5rem);
  overflow-y: auto;
  max-height: calc(100vh - 200px);
}

/* Markdown styles */
.file-content-body h1,
.file-content-body h2,
.file-content-body h3,
.file-content-body h4 {
  color: var(--text, #3B3D3F);
  margin-top: 1.5em;
  margin-bottom: 0.75em;
  line-height: 1.4;
}

.file-content-body h1 { font-size: var(--text-2xl, 1.5rem); }
.file-content-body h2 { font-size: var(--text-xl, 1.25rem); }
.file-content-body h3 { font-size: var(--text-lg, 1.125rem); }

.file-content-body p {
  margin: 0 0 1em 0;
  line-height: 1.7;
  color: var(--text, #3B3D3F);
}

.file-content-body code {
  background: var(--bg-inset, #E8E5DD);
  padding: 0.2em 0.4em;
  border-radius: var(--radius-sm, 4px);
  font-size: 0.9em;
  font-family: ui-monospace, monospace;
}

.file-content-body pre {
  margin: 1em 0;
}

.file-content-body pre code {
  background: none;
  padding: 0;
}

.file-content-body ul,
.file-content-body ol {
  margin: 1em 0;
  padding-left: 1.5em;
}

.file-content-body li {
  margin: 0.5em 0;
  line-height: 1.6;
}

.file-content-body blockquote {
  border-left: 3px solid var(--accent, #537D96);
  margin: 1em 0;
  padding-left: 1em;
  color: var(--text-light, #6B6F73);
}

.file-content-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}

.file-content-body th,
.file-content-body td {
  border: 1px solid var(--border, rgba(83, 125, 150, 0.22));
  padding: var(--space-2, 0.5rem) var(--space-3, 0.75rem);
  text-align: left;
}

.file-content-body th {
  background: var(--bg-inset, #E8E5DD);
  font-weight: 500;
}

.file-content-body a {
  color: var(--accent, #537D96);
  text-decoration: none;
}

.file-content-body a:hover {
  text-decoration: underline;
}

.file-content-empty {
  text-align: center;
  padding: var(--space-12, 3rem);
  color: var(--text-muted, #8E9196);
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm run test:run -- FileContentViewer.test.tsx
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/knowledge/FileContentViewer/
git commit -m "feat(knowledge): add FileContentViewer with markdown and syntax highlighting"
```

---

## Chunk 4: Page Components

### Task 6: Create KnowledgeListPage

**Files:**
- Create: `frontend/src/features/knowledge/KnowledgeListPage.tsx`
- Create: `frontend/src/features/knowledge/KnowledgeListPage.css`
- Create: `frontend/src/features/knowledge/KnowledgeListPage.test.tsx`

- [ ] **Step 1: Write failing test**

```tsx
// frontend/src/features/knowledge/KnowledgeListPage.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KnowledgeListPage } from './KnowledgeListPage';
import { MemoryRouter } from 'react-router-dom';
import { knowledgeListStore } from './knowledgeListStore';

vi.mock('./knowledgeListStore');

describe('KnowledgeListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders page title', () => {
    vi.mocked(knowledgeListStore.getState).mockReturnValue({
      fetchKnowledgeBases: vi.fn(),
      knowledgeBases: [],
      currentKB: null,
      files: [],
      currentFile: null,
      currentFileContent: '',
      isLoadingKBs: false,
      isLoadingFiles: false,
      isLoadingContent: false,
      error: null,
      setCurrentKB: vi.fn(),
      clearError: vi.fn(),
      fetchFiles: vi.fn(),
      fetchFileContent: vi.fn(),
    } as any);

    render(<MemoryRouter><KnowledgeListPage /></MemoryRouter>);
    expect(screen.getByText('知识库')).toBeInTheDocument();
  });

  it('shows loading spinner when loading', () => {
    vi.mocked(knowledgeListStore.getState).mockReturnValue({
      fetchKnowledgeBases: vi.fn(),
      knowledgeBases: [],
      currentKB: null,
      files: [],
      currentFile: null,
      currentFileContent: '',
      isLoadingKBs: true,
      isLoadingFiles: false,
      isLoadingContent: false,
      error: null,
      setCurrentKB: vi.fn(),
      clearError: vi.fn(),
      fetchFiles: vi.fn(),
      fetchFileContent: vi.fn(),
    } as any);

    render(<MemoryRouter><KnowledgeListPage /></MemoryRouter>);
    expect(document.querySelector('.spinner')).toBeInTheDocument();
  });

  it('renders knowledge cards when loaded', () => {
    const mockKBs = [
      { id: 'kb1', name: 'KB 1', description: 'Desc 1', user_id: 'u1', create_time: '', update_time: '' }
    ];
    vi.mocked(knowledgeListStore.getState).mockReturnValue({
      fetchKnowledgeBases: vi.fn(),
      knowledgeBases: mockKBs,
      currentKB: null,
      files: [],
      currentFile: null,
      currentFileContent: '',
      isLoadingKBs: false,
      isLoadingFiles: false,
      isLoadingContent: false,
      error: null,
      setCurrentKB: vi.fn(),
      clearError: vi.fn(),
      fetchFiles: vi.fn(),
      fetchFileContent: vi.fn(),
    } as any);

    render(<MemoryRouter><KnowledgeListPage /></MemoryRouter>);
    expect(screen.getByText('KB 1')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm run test:run -- KnowledgeListPage.test.tsx
```
Expected: FAIL - KnowledgeListPage not defined

- [ ] **Step 3: Write minimal implementation**

```tsx
// frontend/src/features/knowledge/KnowledgeListPage.tsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Spinner } from '../../components/ui';
import { KnowledgeCard } from '../../components/knowledge/KnowledgeCard/KnowledgeCard';
import { knowledgeListStore } from './knowledgeListStore';
import './KnowledgeListPage.css';

export function KnowledgeListPage() {
  const navigate = useNavigate();
  const { knowledgeBases, isLoadingKBs, error, fetchKnowledgeBases } = knowledgeListStore();

  useEffect(() => {
    fetchKnowledgeBases();
  }, [fetchKnowledgeBases]);

  const handleKBClick = (kbId: string) => {
    navigate(`/knowledge/${kbId}`);
  };

  if (isLoadingKBs) {
    return (
      <div className="knowledge-list-page">
        <div className="knowledge-list-loading">
          <Spinner />
        </div>
      </div>
    );
  }

  return (
    <div className="knowledge-list-page">
      <header className="knowledge-list-header">
        <h1 className="knowledge-list-title">知识库</h1>
      </header>

      {error && (
        <div className="knowledge-list-error">
          <p>{error}</p>
          <button onClick={fetchKnowledgeBases}>重试</button>
        </div>
      )}

      {knowledgeBases.length === 0 && !error ? (
        <div className="knowledge-list-empty">
          <p>暂无知识库</p>
        </div>
      ) : (
        <div className="knowledge-list-grid">
          {knowledgeBases.map((kb) => (
            <KnowledgeCard
              key={kb.id}
              knowledge={kb}
              fileCount={0}
              onClick={() => handleKBClick(kb.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

```css
/* frontend/src/features/knowledge/KnowledgeListPage.css */
.knowledge-list-page {
  padding: var(--space-6, 1.5rem);
  max-width: var(--container-max-lg, 1024px);
  margin: 0 auto;
}

.knowledge-list-header {
  margin-bottom: var(--space-6, 1.5rem);
}

.knowledge-list-title {
  font-size: var(--text-2xl, 1.5rem);
  font-weight: 600;
  color: var(--text, #3B3D3F);
  margin: 0;
}

.knowledge-list-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.knowledge-list-error {
  text-align: center;
  padding: var(--space-6, 1.5rem);
  color: var(--color-error, #cf222e);
}

.knowledge-list-error button {
  margin-top: var(--space-3, 0.75rem);
  padding: var(--space-2, 0.5rem) var(--space-4, 1rem);
  background: var(--accent, #537D96);
  color: white;
  border: none;
  border-radius: var(--radius-md, 8px);
  cursor: pointer;
}

.knowledge-list-empty {
  text-align: center;
  padding: var(--space-12, 3rem);
  color: var(--text-muted, #8E9196);
}

.knowledge-list-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--space-4, 1rem);
}

@media (min-width: 640px) {
  .knowledge-list-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .knowledge-list-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm run test:run -- KnowledgeListPage.test.tsx
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/knowledge/KnowledgeListPage.tsx frontend/src/features/knowledge/KnowledgeListPage.css frontend/src/features/knowledge/KnowledgeListPage.test.tsx
git commit -m "feat(knowledge): add KnowledgeListPage with grid layout"
```

---

### Task 7: Create KnowledgeFileListPage

**Files:**
- Create: `frontend/src/features/knowledge/KnowledgeFileListPage.tsx`
- Create: `frontend/src/features/knowledge/KnowledgeFileListPage.css`

- [ ] **Step 1: Write failing test**

```tsx
// frontend/src/features/knowledge/KnowledgeFileListPage.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KnowledgeFileListPage } from './KnowledgeFileListPage';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { knowledgeListStore } from './knowledgeListStore';

vi.mock('./knowledgeListStore');

describe('KnowledgeFileListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders back button and KB name', () => {
    vi.mocked(knowledgeListStore.getState).mockReturnValue({
      currentKB: { id: 'kb1', name: 'Test KB', description: '', user_id: 'u1', create_time: '', update_time: '' },
      files: [],
      isLoadingFiles: false,
      fetchFiles: vi.fn(),
      fetchKnowledgeBases: vi.fn(),
      knowledgeBases: [],
      currentFile: null,
      currentFileContent: '',
      isLoadingKBs: false,
      isLoadingContent: false,
      error: null,
      setCurrentKB: vi.fn(),
      clearError: vi.fn(),
      fetchFileContent: vi.fn(),
    } as any);

    render(
      <MemoryRouter initialEntries={['/knowledge/kb1']}>
        <Routes>
          <Route path="/knowledge/:kbId" element={<KnowledgeFileListPage />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText('Test KB')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm run test:run -- KnowledgeFileListPage.test.tsx
```
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```tsx
// frontend/src/features/knowledge/KnowledgeFileListPage.tsx
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Spinner } from '../../components/ui';
import { FileTable } from '../../components/knowledge/FileTable/FileTable';
import { knowledgeListStore } from './knowledgeListStore';
import './KnowledgeFileListPage.css';

export function KnowledgeFileListPage() {
  const { kbId } = useParams<{ kbId: string }>();
  const navigate = useNavigate();
  const { currentKB, files, isLoadingFiles, error, fetchFiles, knowledgeBases } = knowledgeListStore();

  useEffect(() => {
    if (kbId) {
      // Set current KB from knowledgeBases list
      const kb = knowledgeBases.find(k => k.id === kbId);
      if (kb) {
        knowledgeListStore.getState().setCurrentKB(kb);
      }
      fetchFiles(kbId);
    }
  }, [kbId, fetchFiles, knowledgeBases]);

  const handleFileClick = (file: { id: string }) => {
    navigate(`/knowledge/${kbId}/files/${file.id}`);
  };

  if (isLoadingFiles) {
    return (
      <div className="knowledge-file-list-page">
        <div className="knowledge-file-list-loading">
          <Spinner />
        </div>
      </div>
    );
  }

  return (
    <div className="knowledge-file-list-page">
      <header className="knowledge-file-list-header">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/knowledge')}
          className="knowledge-file-list-back"
        >
          ← 返回
        </Button>
        <h1 className="knowledge-file-list-title">{currentKB?.name || '知识库'}</h1>
      </header>

      {error && (
        <div className="knowledge-file-list-error">
          <p>{error}</p>
        </div>
      )}

      <div className="knowledge-file-list-content">
        <FileTable files={files} onFileClick={handleFileClick} />
      </div>
    </div>
  );
}
```

```css
/* frontend/src/features/knowledge/KnowledgeFileListPage.css */
.knowledge-file-list-page {
  padding: var(--space-6, 1.5rem);
  max-width: var(--container-max-lg, 1024px);
  margin: 0 auto;
}

.knowledge-file-list-header {
  margin-bottom: var(--space-6, 1.5rem);
}

.knowledge-file-list-back {
  margin-bottom: var(--space-3, 0.75rem);
}

.knowledge-file-list-title {
  font-size: var(--text-2xl, 1.5rem);
  font-weight: 600;
  color: var(--text, #3B3D3F);
  margin: 0;
}

.knowledge-file-list-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.knowledge-file-list-error {
  text-align: center;
  padding: var(--space-4, 1rem);
  color: var(--color-error, #cf222e);
  margin-bottom: var(--space-4, 1rem);
}

.knowledge-file-list-content {
  margin-top: var(--space-4, 1rem);
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm run test:run -- KnowledgeFileListPage.test.tsx
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/knowledge/KnowledgeFileListPage.tsx frontend/src/features/knowledge/KnowledgeFileListPage.css
git commit -m "feat(knowledge): add KnowledgeFileListPage with file table"
```

---

### Task 8: Create KnowledgeFileDetailPage

**Files:**
- Create: `frontend/src/features/knowledge/KnowledgeFileDetailPage.tsx`
- Create: `frontend/src/features/knowledge/KnowledgeFileDetailPage.css`

- [ ] **Step 1: Write failing test**

```tsx
// frontend/src/features/knowledge/KnowledgeFileDetailPage.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KnowledgeFileDetailPage } from './KnowledgeFileDetailPage';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { knowledgeListStore } from './knowledgeListStore';

vi.mock('./knowledgeListStore');

describe('KnowledgeFileDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders back button and file name', () => {
    vi.mocked(knowledgeListStore.getState).mockReturnValue({
      currentFile: { id: 'f1', file_name: 'test.md', knowledge_id: 'kb1', user_id: 'u1', status: 'success', oss_url: '', file_size: 1024, create_time: '', update_time: '' },
      currentFileContent: '# Hello',
      isLoadingContent: false,
      files: [],
      fetchFileContent: vi.fn(),
      fetchFiles: vi.fn(),
      fetchKnowledgeBases: vi.fn(),
      knowledgeBases: [],
      currentKB: null,
      isLoadingKBs: false,
      isLoadingFiles: false,
      error: null,
      setCurrentKB: vi.fn(),
      clearError: vi.fn(),
    } as any);

    render(
      <MemoryRouter initialEntries={['/knowledge/kb1/files/f1']}>
        <Routes>
          <Route path="/knowledge/:kbId/files/:fileId" element={<KnowledgeFileDetailPage />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText('test.md')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm run test:run -- KnowledgeFileDetailPage.test.tsx
```
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```tsx
// frontend/src/features/knowledge/KnowledgeFileDetailPage.tsx
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Spinner } from '../../components/ui';
import { FileContentViewer } from '../../components/knowledge/FileContentViewer/FileContentViewer';
import { knowledgeListStore } from './knowledgeListStore';
import './KnowledgeFileDetailPage.css';

export function KnowledgeFileDetailPage() {
  const { kbId, fileId } = useParams<{ kbId: string; fileId: string }>();
  const navigate = useNavigate();
  const { currentFile, currentFileContent, isLoadingContent, error, fetchFileContent, files } = knowledgeListStore();

  useEffect(() => {
    if (fileId) {
      fetchFileContent(fileId);
    }
  }, [fileId, fetchFileContent]);

  if (isLoadingContent) {
    return (
      <div className="knowledge-file-detail-page">
        <div className="knowledge-file-detail-loading">
          <Spinner />
        </div>
      </div>
    );
  }

  return (
    <div className="knowledge-file-detail-page">
      <header className="knowledge-file-detail-header">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(`/knowledge/${kbId}`)}
          className="knowledge-file-detail-back"
        >
          ← 返回
        </Button>
        <h1 className="knowledge-file-detail-title">{currentFile?.file_name || '文件'}</h1>
      </header>

      {error && (
        <div className="knowledge-file-detail-error">
          <p>{error}</p>
        </div>
      )}

      <div className="knowledge-file-detail-content">
        <FileContentViewer content={currentFileContent} fileName={currentFile?.file_name} />
      </div>
    </div>
  );
}
```

```css
/* frontend/src/features/knowledge/KnowledgeFileDetailPage.css */
.knowledge-file-detail-page {
  padding: var(--space-6, 1.5rem);
  max-width: var(--container-max-lg, 1024px);
  margin: 0 auto;
}

.knowledge-file-detail-header {
  margin-bottom: var(--space-6, 1.5rem);
}

.knowledge-file-detail-back {
  margin-bottom: var(--space-3, 0.75rem);
}

.knowledge-file-detail-title {
  font-size: var(--text-2xl, 1.5rem);
  font-weight: 600;
  color: var(--text, #3B3D3F);
  margin: 0;
  word-break: break-all;
}

.knowledge-file-detail-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.knowledge-file-detail-error {
  text-align: center;
  padding: var(--space-4, 1rem);
  color: var(--color-error, #cf222e);
  margin-bottom: var(--space-4, 1rem);
}

.knowledge-file-detail-content {
  margin-top: var(--space-4, 1rem);
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm run test:run -- KnowledgeFileDetailPage.test.tsx
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/knowledge/KnowledgeFileDetailPage.tsx frontend/src/features/knowledge/KnowledgeFileDetailPage.css
git commit -m "feat(knowledge): add KnowledgeFileDetailPage with markdown viewer"
```

---

## Chunk 5: Routing & Integration

### Task 9: Update routes

**Files:**
- Modify: `frontend/src/routes.tsx`

- [ ] **Step 1: Read current routes.tsx**

```bash
cat frontend/src/routes.tsx
```

- [ ] **Step 2: Update routes to include new pages**

```tsx
import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { App } from './App';

// Lazy load knowledge pages
const KnowledgeListPage = React.lazy(() => import('./features/knowledge/KnowledgeListPage').then(m => ({ default: m.KnowledgeListPage })));
const KnowledgeFileListPage = React.lazy(() => import('./features/knowledge/KnowledgeFileListPage').then(m => ({ default: m.KnowledgeFileListPage })));
const KnowledgeFileDetailPage = React.lazy(() => import('./features/knowledge/KnowledgeFileDetailPage').then(m => ({ default: m.KnowledgeFileDetailPage })));

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: React.createElement(React.Suspense, { fallback: <div>Loading...</div> }, React.createElement(KnowledgeListPage)),
      },
      {
        path: 'knowledge',
        element: React.createElement(React.Suspense, { fallback: <div>Loading...</div> }, React.createElement(KnowledgeListPage)),
      },
      {
        path: 'knowledge/:kbId',
        element: React.createElement(React.Suspense, { fallback: <div>Loading...</div> }, React.createElement(KnowledgeFileListPage)),
      },
      {
        path: 'knowledge/:kbId/files/:fileId',
        element: React.createElement(React.Suspense, { fallback: <div>Loading...</div> }, React.createElement(KnowledgeFileDetailPage)),
      },
      // ... other routes
    ],
  },
]);
```

- [ ] **Step 3: Verify routes work**

Run dev server and check routes work

- [ ] **Step 4: Commit**

```bash
git add frontend/src/routes.tsx
git commit -m "feat(knowledge): add routes for KB list, file list, and file detail pages"
```

---

## Chunk 6: Build & Verify

### Task 10: Install dependencies and build

- [ ] **Step 1: Install react-syntax-highlighter**

```bash
cd frontend && npm install react-syntax-highlighter && npm install -D @types/react-syntax-highlighter
```

- [ ] **Step 2: Run build**

```bash
cd frontend && npm run build
```

Expected: Build succeeds without errors

- [ ] **Step 3: Commit dependencies**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore(dependencies): add react-syntax-highlighter for syntax highlighting"
```

---

### Task 11: Run all tests

- [ ] **Step 1: Run all tests**

```bash
cd frontend && npm run test:run
```

Expected: All tests pass

- [ ] **Step 2: Final commit if needed**

---

## Summary

| Task | File | Status |
|------|------|--------|
| 1 | `api/knowledge.ts` | ⬜ |
| 2 | `knowledgeListStore.ts` | ⬜ |
| 3 | `KnowledgeCard` | ⬜ |
| 4 | `FileTable` | ⬜ |
| 5 | `FileContentViewer` | ⬜ |
| 6 | `KnowledgeListPage` | ⬜ |
| 7 | `KnowledgeFileListPage` | ⬜ |
| 8 | `KnowledgeFileDetailPage` | ⬜ |
| 9 | `routes.tsx` | ⬜ |
| 10 | Build & dependencies | ⬜ |
| 11 | Run all tests | ⬜ |
