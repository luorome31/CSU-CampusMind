# Phase 4: Knowledge Build - Crawl Panel, Batch Upload, Task Progress, Content Review

## 1. Overview

**Goal**: Implement Phase 4 of CampusMind frontend - knowledge base build workflow including crawl panel, batch upload with file import, task progress monitoring, and content review.

**Route**: `/knowledge/build` (requires authentication via `ProtectedRoute`)

**Layout**: Tab-based with two tabs
- **Tab 1: 爬取任务** (Crawl Tasks) - URL submission + task monitoring
- **Tab 2: 审核队列** (Review Queue) - Pending verification files with notification badge

---

## 2. File Structure

```
src/features/build/
├── KnowledgeBuildPage.tsx      # Main page with tabs (replace placeholder)
├── buildStore.ts              # Zustand store for build state
├── api/
│   └── crawl.ts               # Crawl API client (new file)
├── components/
│   ├── CrawlTab/
│   │   ├── CrawlPanel.tsx     # Knowledge selector + URL input
│   │   ├── UrlImportModal.tsx # Batch URL import modal (new)
│   │   ├── TaskList.tsx       # Task list with progress
│   │   └── TaskCard.tsx       # Individual task card
│   └── ReviewTab/
│       ├── ReviewInbox.tsx     # Global pending verification list
│       └── ReviewEditor.tsx   # Content editor for verification
```

---

## 3. API Endpoints

### Crawl API (`api/crawl.ts`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/crawl/batch-with-knowledge` | Submit batch crawl task |
| GET | `/api/v1/crawl/tasks` | List all user tasks |
| GET | `/api/v1/crawl/tasks/{task_id}` | Get task progress |

### Knowledge File API (existing, extended usage)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/knowledge_file/pending_verify` | Get all pending verification files |
| GET | `/api/v1/knowledge_file/{file_id}/content` | Get file content for review |
| PUT | `/api/v1/knowledge_file/{file_id}/content` | Update file content |
| POST | `/api/v1/knowledge_file/{file_id}/trigger_index` | Trigger RAG indexing |

---

## 4. buildStore State

```typescript
interface BuildState {
  // UI State
  activeTab: 'crawl' | 'review';

  // Crawl Tab
  selectedKnowledgeId: string | null;
  crawlUrls: string;                    // Manual URL input (newline separated)
  tasks: CrawlTask[];
  activeTaskId: string | null;
  isPolling: boolean;
  pollingErrorCount: number;

  // Batch Import Modal
  isImportModalOpen: boolean;
  previewUrls: string[];               // Parsed URLs from file upload

  // Review Tab
  pendingFiles: KnowledgeFile[];
  pendingReviewCount: number;           // Badge count for tab notification
  selectedFile: KnowledgeFile | null;
  fileContent: string;
  isSaving: boolean;
  isIndexing: boolean;

  // Actions
  setActiveTab: (tab: 'crawl' | 'review') => void;
  setSelectedKnowledgeId: (id: string) => void;
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
```

### Type Definitions

```typescript
interface CrawlTask {
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

interface KnowledgeFile {
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
```

---

## 5. Crawl Tab - Components

### 5.1 CrawlPanel

**Purpose**: Knowledge selector + URL input interface

**Elements**:
- Knowledge selector dropdown (required, must select before crawl)
- Manual URL textarea (newline separated)
- Buttons: [开始爬取] [批量导入] [清空]

**Validation**:
- Knowledge must be selected
- At least one URL required
- URLs should be valid format (http:// or https://)

### 5.2 UrlImportModal

**Purpose**: Batch import URLs from .txt/.csv file with preview

**Trigger**: Click "批量导入" button

**Flow**:
1. Open modal with drag-and-drop zone
2. User uploads .txt or .csv file
3. Frontend parses file (one URL per line, or CSV first column)
4. Display parsed URLs in preview list with count
5. User can remove individual URLs from preview
6. Click "确认" → URLs added to submission
7. Click "取消" → discard and close

**Validation**:
- File types: .txt, .csv
- Max file size: 1MB
- Max URLs: 100

### 5.3 TaskList

**Purpose**: Display all tasks for current user

**Display**: List of TaskCard components, sorted by create_time desc

### 5.4 TaskCard

**Purpose**: Show individual task progress

**Display**:
```
┌─────────────────────────────────────────────────────────┐
│ Task ID: task_xyz123        Status: 处理中 / 成功 / 失败 │
├─────────────────────────────────────────────────────────┤
│ Progress: ████████████░░░░░░░░░░░  7/10                │
│ Success: 5  |  Failed: 2                               │
│ Created: 2024-01-01 12:00                             │
└─────────────────────────────────────────────────────────┘
```

**Status Icons**:
- pending/processing: Spinner
- SUCCESS/completed: Checkmark (green)
- FAILED: X mark (red)

---

## 6. Review Tab - Components

### 6.1 ReviewInbox

**Purpose**: Global list of pending verification files

**Display**: List of pending files with metadata
```
┌─────────────────────────────────────────────────────────┐
│ 📄 document1.md                    知识库A  |  2024-01-01│
│ 📄 document2.md                    知识库B  |  2024-01-02│
└─────────────────────────────────────────────────────────┘
```

**Badge**: Red notification badge showing `pendingReviewCount`

### 6.2 ReviewEditor

**Purpose**: Edit file content for verification

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ File: document.md                    [保存] [确认索引]  │
├─────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────────┐ │
│ │ Markdown content editor (textarea)                 │ │
│ │ ...                                               │ │
│ └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Buttons**:
- 保存: `PUT /api/v1/knowledge_file/{file_id}/content`
- 确认索引: `POST /api/v1/knowledge_file/{file_id}/trigger_index`

---

## 7. Polling Implementation

**Constants**:
```typescript
const POLL_INTERVAL = 3000;           // 3 seconds
const MAX_POLL_FAILURES = 3;           // Stop after 3 consecutive failures
const TERMINAL_STATES = ['SUCCESS', 'FAILED', 'completed', 'failed'];
```

**Polling Logic**:
```typescript
// 1. Submit batch crawl → get task_id
const taskId = await submitBatchCrawl(urls);

// 2. Start polling
startPolling(taskId);

// 3. On each interval tick:
//    - Call GET /api/v1/crawl/tasks/{task_id}
//    - Update task progress in store
//    - Check if status is terminal → stopPolling()

// 4. Error handling:
//    - On failure: increment pollingErrorCount
//    - If pollingErrorCount >= 3: stopPolling(), show error toast

// 5. On tab switch to Review:
//    - Fetch pending files
//    - Update pendingReviewCount badge
```

---

## 8. Workflows

### 8.1 Batch Crawl Workflow

```
1. User selects knowledge base
2. User enters URLs manually OR clicks "批量导入"
   2a. Modal opens
   2b. User uploads .txt/.csv
   2c. Preview URLs in modal
   2d. Click "确认" → URLs added to form
3. Click "开始爬取"
4. Show task in TaskList with progress
5. Poll every 3s for updates
6. On terminal state → stop polling, refresh pending count
7. If in Review tab → update badge
```

### 8.2 Content Review Workflow

```
1. Navigate to 审核队列 tab
2. Load pending files (pendingVerify API)
3. Update badge count
4. Click file → load content
5. Edit content in textarea
6. Click "保存" → update content API
7. Click "确认索引" → trigger indexing API
8. Remove from pending list, update badge
```

---

## 9. Error Handling

| Scenario | Handling |
|----------|----------|
| No knowledge base selected | Disable submit, show validation |
| Empty URL list | Disable submit |
| Invalid URL format | Filter out, show warning |
| Poll failure (1-2 times) | Show toast, continue polling |
| Poll failure (3+ times) | Stop polling, show "网络异常，停止自动刷新" |
| File save failure | Show error toast |
| Index trigger failure | Show error toast |
| No pending files | Show empty state message |

---

## 10. Design Tokens (CSS Variables)

Use existing design tokens from `src/styles/tokens/`:

```css
/* Colors */
--color-bg-base          /* Page background */
--color-bg-surface       /* Card/panel background */
--color-text-primary     /* Primary text */
--color-text-secondary   /* Secondary text */
--color-accent          /* Accent color */
--color-success         /* Success state */
--color-error           /* Error state */

/* Spacing */
--space-1 to --space-16  /* Spacing scale */

/* Radius */
--radius-sm, --radius-md, --radius-lg

/* Elevation */
--shadow-sm, --shadow-md, --shadow-lg
```

---

## 11. Testing Strategy

### Unit Tests (High Priority)

| Test File | Coverage |
|-----------|----------|
| `buildStore.test.ts` | All state transitions, actions, polling logic |
| `crawl.test.ts` | API client methods, URL parsing |

### Component Tests (Medium Priority)

| Test File | Coverage |
|-----------|----------|
| `CrawlPanel.test.tsx` | Knowledge selection, URL input, submit |
| `UrlImportModal.test.tsx` | File upload, parsing, preview |
| `TaskCard.test.tsx` | Progress display, status icons |
| `ReviewInbox.test.tsx` | File list, badge count |
| `ReviewEditor.test.tsx` | Content load, save, trigger index |

### Integration Tests (Lower Priority)

- Full polling lifecycle (start → progress → terminal)
- Tab switching with badge updates

---

## 12. Dependencies

**New dependencies**: None (using existing stack)

**Existing APIs used**:
- `apiClient` from `api/client.ts`
- Existing `knowledgeApi` from `api/knowledge.ts`

**UI Components** (from `src/components/ui/`):
- Button
- Input
- Card / CardBody
- Badge
- Modal (already exists)
- Chip

---

## 13. Acceptance Criteria

1. **Crawl Panel**: User can select knowledge base, enter URLs, submit batch crawl
2. **Batch Import**: Modal opens on button click, parses .txt/.csv, shows preview
3. **Task List**: Shows all tasks with progress bars and status icons
4. **Polling**: 3-second interval, stops on terminal state or 3 failures
5. **Review Inbox**: Shows all pending verification files with badge count
6. **Review Editor**: Loads content, allows edit, save, and trigger index
7. **Cross-Tab Notification**: Badge updates when pending count changes
8. **Error Handling**: Toast messages for errors, graceful degradation
9. **Unit Tests**: All new code has test coverage
10. **Build**: Project builds without errors

---

## 14. Implementation Order

1. Create `api/crawl.ts` - Crawl API client
2. Create `buildStore.ts` - Zustand store with all state and actions
3. Create `UrlImportModal.tsx` - Batch import modal
4. Create `CrawlPanel.tsx` - Knowledge selector + URL input
5. Create `TaskCard.tsx` - Individual task display
6. Create `TaskList.tsx` - Task list container
7. Create `ReviewInbox.tsx` - Pending files list with badge
8. Create `ReviewEditor.tsx` - Content editor
9. Replace `KnowledgeBuildPage.tsx` with tab-based layout
10. Write tests for all new code
11. Verify build passes
