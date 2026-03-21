# CampusMind Frontend Architecture Design

## 1. Overview

### 1.1 Project Scope

A React-based intelligent dialogue and knowledge management system for university campus services, integrating CAS authentication, RAG-powered chat, and knowledge base construction.

### 1.2 Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Framework | React + Vite | React 18+ |
| Language | TypeScript | 5.x |
| Routing | React Router | 6.x |
| State Management | Zustand | 4.x |
| HTTP Client | ky (or fetch wrapper) | 1.x |
| UI Components | Custom Design System | - |
| Styling | CSS Variables (Design Tokens) + Global CSS | - |
| SSE Handling | Native EventSource | - |
| Unit Testing | Vitest | latest |
| Component Testing | @testing-library/react | 18.x |
| E2E Testing | Playwright | - |

### 1.3 Backend API Surface

```
Base URL: /api/v1
Auth:     JWT Bearer Token

Endpoints:
├── POST   /auth/login           → { token, user_id, expires_in }
├── POST   /auth/logout          → { message }
├── POST   /auth/refresh         → { token, user_id, expires_in }
├── POST   /completion/stream    → SSE stream (dialogue)
├── POST   /completion          → JSON (non-streaming dialogue)
├── GET    /users/{user_id}/dialogs          → Dialog[]
├── GET    /dialogs/{dialog_id}/history      → ChatHistory[]
├── GET    /knowledge/{knowledge_id}        → KnowledgeBase
├── GET    /users/{user_id}/knowledge        → KnowledgeBase[]
├── POST   /knowledge/create                 → KnowledgeBase
├── DELETE /knowledge/{knowledge_id}          → { success }
├── GET    /knowledge/{knowledge_id}/files   → KnowledgeFile[]
├── POST   /knowledge_file/create            → KnowledgeFile
├── DELETE /knowledge_file/{file_id}        → { success }
├── POST   /crawl/create                     → CrawlResult
├── POST   /crawl/batch                     → CrawlResult[]
├── POST   /crawl/create-and-index           → CrawlResult
├── POST   /crawl/batch-with-knowledge      → CrawlResult[]
├── POST   /index/create                     → { success, chunk_count }
├── POST   /index/create-from-oss            → { success, chunk_count }
├── POST   /retrieve                         → { success, context, sources }
```

---

## 2. Application Layout

### 2.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│                          Root                               │
│  ┌──────────┐  ┌────────────────────────────────────────┐ │
│  │          │  │              MainViewport               │ │
│  │          │  │  ┌────────────────────────────────────┐ │ │
│  │ Sidebar  │  │  │         Context Header             │ │ │
│  │ (drawer) │  │  ├────────────────────────────────────┤ │ │
│  │          │  │  │                                    │ │ │
│  │  侧边栏   │  │  │         Page Content               │ │ │
│  │          │  │  │         (动态渲染)                  │ │ │
│  │          │  │  │                                    │ │ │
│  │          │  │  │                                    │ │ │
│  └──────────┘  │  └────────────────────────────────────┘ │ │
│                └────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Responsive Strategy

| Breakpoint | Layout Behavior |
|------------|-----------------|
| < 768px (mobile) | Sidebar hidden, hamburger menu trigger |
| 768px - 1024px (tablet) | Sidebar collapsed to icon-only rail |
| > 1024px (desktop) | Sidebar expanded, content full-width |

---

## 3. Module Design

### 3.1 Route Architecture

```
/                           → ChatPage (default)
/knowledge                  → KnowledgeListPage (readonly browse)
/knowledge/build            → KnowledgeBuildPage (crawl & index)
/profile                    → ProfilePage (auth-gated)
```

### 3.2 Page Components

| Route | Component | Auth Required | Description |
|-------|-----------|--------------|-------------|
| `/` | `ChatPage` | No | AI dialogue interface |
| `/knowledge` | `KnowledgeListPage` | No | Browse knowledge bases |
| `/knowledge/build` | `KnowledgeBuildPage` | Yes | Crawl, upload, index |
| `/profile` | `ProfilePage` | Yes | User profile & settings |

---

## 4. Core Module Specifications

### 4.1 Sidebar (Global Navigation)

**File Location**: `src/components/layout/Sidebar/`

```
Sidebar/
├── Sidebar.tsx          # Container with toggle logic
├── Sidebar.module.css   # Styles
├── NewChatButton.tsx    # "新建对话" button
├── NavSection.tsx       # Fixed function area
├── NavItem.tsx          # Individual nav tile
├── Divider.tsx          # Visual separator
├── SessionHistory.tsx   # Historical dialogue list
└── SessionItem.tsx      # Individual history entry
```

**State**:

```typescript
// Zustand store
interface LayoutStore {
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;  // for tablet rail mode
  toggleSidebar: () => void;
  collapseSidebar: () => void;
  expandSidebar: () => void;
}
```

**Interactions**:

- `NewChatButton` → clears current dialog, resets to logo state
- `NavSection` items → navigate + close sidebar (mobile)
- `SessionHistory` → click loads dialog, sidebar auto-hides on mobile
- Divider → static visual, no interaction

### 4.2 Chat Module

**File Location**: `src/pages/Chat/`

```
Chat/
├── ChatPage.tsx         # Main chat container
├── ChatHeader.tsx       # Optional: current dialog title
├── MessageList.tsx      # Scrollable message container
├── MessageBubble.tsx    # Individual message (user/assistant)
├── StreamingText.tsx    # Animated text reveal for SSE
├── ToolEventCard.tsx    # Renders tool call events (成绩查询等)
├── ChatInput.tsx        # Input area with send logic
├── DynamicActions.tsx   # Dynamic buttons from tool-calling response
├── EmptyState.tsx       # Logo + system intro when no messages
└── types.ts
```

**State**:

```typescript
interface ChatStore {
  currentDialogId: string | null;
  currentKnowledgeIds: string[];  // ← Active knowledge bases for RAG
  messages: ChatMessage[];
  isStreaming: boolean;
  toolEvents: ToolEvent[];

  // Actions
  setCurrentDialogId: (id: string) => void;
  setCurrentKnowledgeIds: (ids: string[]) => void;  // ← User selects KBs before chatting
  sendMessage: (content: string) => Promise<void>;
  loadDialog: (dialogId: string) => Promise<void>;
  clearCurrentDialog: () => void;
  appendChunk: (chunk: string) => void;
  addToolEvent: (event: ToolEvent) => void;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  events?: ToolEvent[];
  createdAt: Date;
}
```

**SSE Handling** (per `async-parallel` rule — start promise early):

```typescript
// Avoid waterfall: start SSE connection immediately on mount or dialog switch
async function* streamChat(
  message: string,
  options: {
    dialogId?: string;
    knowledgeIds: string[];   // ← Required when enableRag=true
    enableRag?: boolean;       // ← Defaults to true in backend
    topK?: number;
    minScore?: number;
  }
) {
  const { dialogId, knowledgeIds, enableRag = true, topK = 5, minScore = 0.0 } = options;

  // ⚠️ CRITICAL: enable_rag=true requires knowledge_ids (backend enforces 400 if missing)
  const response = await fetch('/api/v1/completion/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
    },
    body: JSON.stringify({
      message,
      dialog_id: dialogId ?? undefined,
      knowledge_ids: knowledgeIds,      // ← Required when enableRag=true
      enable_rag: enableRag,             // ← Defaults to true
      top_k: topK,
      min_score: minScore,
    }),
  });

  // ⚠️ CRITICAL: Extract X-Dialog-ID header for NEW dialogs (dialogId was null)
  // Backend returns the newly created dialog_id in this header
  const newDialogId = response.headers.get('X-Dialog-ID');
  if (newDialogId && !dialogId) {
    chatStore.getState().setCurrentDialogId(newDialogId);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(response.status, error.detail || 'Stream request failed');
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    yield* parseSSELines(chunk); // { type, data }
  }
}
```

**SSE Event Types**:

```typescript
type SSEToolEvent = {
  type: 'event';
  data: { status: 'START' | 'END' | 'ERROR'; title: string; message: string };
};

type SSEChunkEvent = {
  type: 'response_chunk';
  data: { chunk: string; accumulated: string };
};
```

### 4.3 Knowledge Base Module

**File Location**: `src/pages/Knowledge/`

```
Knowledge/
├── KnowledgeListPage.tsx   # Readonly browse
├── KnowledgeDetail.tsx     # File listing within KB
├── FileCard.tsx           # Individual file display
├── types.ts
KnowledgeBuild/
├── KnowledgeBuildPage.tsx  # Crawl + upload + index
├── CrawlPanel.tsx         # URL input section
├── BatchUploadModal.tsx   # File-based batch import
├── TaskProgress.tsx       # Real-time crawl/index status
├── ContentReview.tsx      # Markdown editor for human review
└── types.ts
```

**KnowledgeListPage State**:

```typescript
interface KnowledgeListStore {
  knowledgeBases: KnowledgeBase[];
  selectedKB: KnowledgeBase | null;
  files: KnowledgeFile[];
  isLoading: boolean;

  fetchUserKnowledge: (userId: string) => Promise<void>;
  selectKnowledge: (kb: KnowledgeBase) => Promise<void>;
}
```

**KnowledgeBuildPage State**:

```typescript
interface BuildStore {
  // Crawl
  crawlUrl: string;
  crawlResults: CrawlResult[];
  isCrawling: boolean;

  // Batch
  batchUrls: string[];
  isBatchModalOpen: boolean;

  // Progress
  tasks: TaskProgress[];
  activeTaskId: string | null;

  // Review
  reviewContent: string | null;
  reviewFileId: string | null;

  // Actions
  crawlSingle: (url: string) => Promise<void>;
  crawlBatch: (urls: string[]) => Promise<void>;
  updateTaskProgress: (taskId: string, status: TaskStatus) => void;
  submitForIndexing: (content: string, fileId: string) => Promise<void>;
}
```

### 4.4 Authentication Module

**File Location**: `src/features/auth/`

```
auth/
├── AuthProvider.tsx      # Context provider wrapping app
├── useAuth.ts             # Hook for accessing auth state
├── authStore.ts           # Zustand store
├── LoginPage.tsx          # Login form (Guest mode)
├── ProfilePage.tsx         # User profile display
├── ProtectedRoute.tsx     # Route guard component
└── types.ts
```

**Auth State Machine**:

```
┌─────────┐   login    ┌─────────┐
│  Guest  │ ─────────▶ │  User   │
│ (未登录) │            │ (已登录) │
 └─────────┤            └─────────┘
            │ logout     │
            ◀────────────┘
```

```typescript
interface AuthStore {
  user: User | null;
  token: string | null;  // Stored in sessionStorage, NOT httpOnly cookie
  isAuthenticated: boolean;

  login: (username: string, password: string) => Promise<void>;  // Receives { token, user_id } from JSON body
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  initAuth: () => Promise<void>;  // Reads token from sessionStorage on app load
}
```

**Token Storage**: JWT returned in JSON body → stored in `sessionStorage` (not httpOnly cookie).

> ⚠️ **Security Note**: Since the backend returns `{ token }` in the JSON response (not a `Set-Cookie` header), the token is accessible to JavaScript. This means:
> - **XSS attacks can steal the token** — mitigated by sanitizing all user-generated content
> - Use `sessionStorage` (not `localStorage`) so token is cleared on tab close
> - Consider adding a short-lived token + refresh mechanism for sensitive operations

---

## 5. API Layer Design

### 5.1 API Client Structure

**File Location**: `src/api/`

```
api/
├── client.ts          # Base fetch wrapper with interceptors
├── auth.ts            # Auth endpoints
├── chat.ts            # Completion & dialog endpoints
├── knowledge.ts       # Knowledge base CRUD
├── crawl.ts           # Crawling endpoints
├── index.ts           # Indexing endpoints
└── types.ts           # Shared API types
```

### 5.2 Request/Response Pattern

```typescript
// src/api/client.ts
class ApiClient {
  private baseUrl = '/api/v1';

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = authStore.getState().token;

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });

    if (response.status === 401) {
      // Auto-refresh or redirect to login
      authStore.getState().logout();
      throw new ApiError(401, 'Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(response.status, error.detail || 'Request failed');
    }

    return response.json();
  }

  get<T>(url: string) {
    return this.request<T>(url, { method: 'GET' });
  }

  post<T>(url: string, data?: unknown) {
    return this.request<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  delete<T>(url: string) {
    return this.request<T>(url, { method: 'DELETE' });
  }
}
```

### 5.3 SSE Stream Handler

```typescript
// src/api/chat.ts
export function createChatStream(
  message: string,
  options: {
    dialogId?: string;
    knowledgeIds: string[];
    enableRag?: boolean;
    topK?: number;
    minScore?: number;
  }
): ReadableStream<ChatStreamEvent> {
  const { dialogId, knowledgeIds, enableRag = true, topK = 5, minScore = 0.0 } = options;

  return new ReadableStream({
    async start(controller) {
      const response = await fetch('/api/v1/completion/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
        },
        body: JSON.stringify({
          message,
          dialog_id: dialogId ?? undefined,
          knowledge_ids: knowledgeIds,    // ← Required when enableRag=true
          enable_rag: enableRag,          // ← Defaults to true
          top_k: topK,
          min_score: minScore,
        }),
      });

      // ⚠️ CRITICAL: Extract X-Dialog-ID for new dialogs (dialogId was null/undefined)
      // This header contains the newly created dialog_id from the server
      const newDialogId = response.headers.get('X-Dialog-ID');
      if (newDialogId && !dialogId) {
        chatStore.getState().setCurrentDialogId(newDialogId);
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        controller.error(new ApiError(response.status, error.detail || 'Stream request failed'));
        return;
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        for (const line of text.split('\n')) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            controller.enqueue(data);
          }
        }
      }

      controller.close();
    },
  });
}
```

---

## 6. State Management

### 6.1 Store Architecture (Zustand)

| Store | Scope | Purpose |
|-------|-------|---------|
| `authStore` | Global | User authentication state |
| `layoutStore` | Global | Sidebar visibility, theme |
| `chatStore` | Chat module | Current dialog, messages, SSE state |
| `knowledgeListStore` | Knowledge module | KB list, selected KB, files |
| `buildStore` | Build module | Crawl tasks, progress, review state |

### 6.2 Cross-Cutting Concerns

- **Server State vs Client State**: Prefer server state (API data) in local stores; use Zustand for UI state only
- **Token Refresh**: `authStore` handles refresh on 401, queues failed requests
- **Optimistic Updates**: Apply to UI immediately, reconcile on server response

---

## 7. Component Design System

### 7.1 Existing Components (to extend)

| Component | Location | Purpose |
|-----------|----------|---------|
| `Button` | `src/components/ui/Button/` | Primary actions |
| `Input` | `src/components/ui/Input/` | Text entry |
| `Card` | `src/components/ui/Card/` | Container |
| `Chip` | `src/components/ui/Chip/` | Tags, status |
| `Badge` | `src/components/ui/Badge/` | Counters, labels |

### 7.2 New Components to Add

```
src/components/
├── layout/
│   ├── Sidebar/
│   ├── Header/
│   └── MainViewport/
├── chat/
│   ├── MessageBubble/
│   ├── ChatInput/
│   ├── StreamingText/
│   ├── ToolEventCard/
│   └── DynamicActions/
├── knowledge/
│   ├── KnowledgeCard/
│   ├── FileList/
│   └── KnowledgeDetail/
├── build/
│   ├── CrawlPanel/
│   ├── BatchUploadModal/
│   ├── TaskProgress/
│   └── ContentReview/
└── auth/
    ├── LoginForm/
    └── ProfileCard/
```

### 7.3 CSS Architecture

> 项目使用 **全局 CSS Custom Properties** 而非 CSS Modules。所有样式均通过 CSS 变量引用，遵循 `docs/styles/` 中的设计规范。

```
src/styles/
├── tokens/           # Design tokens (已有)
│   ├── colors.css
│   ├── typography.css
│   ├── spacing.css
│   └── elevation.css
├── global/           # Reset, base styles, component globals
│   └── global.css
└── utilities/        # Helper classes
    └── utilities.css
```

**使用方式**：组件直接引用 CSS 变量，如 `color: var(--color-bg-surface)`，无需 `.module.css` 后缀。

---

## 8. Performance Guidelines

### 8.1 Critical Rules (per react-best-practices)

| Rule | Application |
|------|-------------|
| `async-parallel` | Parallel fetch dialog history + user profile on navigation |
| `async-defer-await` | Defer non-critical: avatar loading, analytics |
| `bundle-dynamic-imports` | Lazy load `KnowledgeBuildPage` and `BatchUploadModal` |
| `rerender-defer-reads` | `SessionHistory` subscribes only to count, not full list |
| `rerender-memo` | `MessageBubble` memoized — avoid re-render on each keystroke |
| `bundle-preload` | Preload chat page on sidebar hover |
| `server-cache-react` | N/A (client-only app) |

### 8.2 Bundle Optimization

```typescript
// Lazy load non-critical routes (code splitting)
const KnowledgeBuildPage = lazy(() => import('./pages/KnowledgeBuild/'));

// Preload on hover via dynamic import()
function NavItem({ to, children }) {
  const handleMouseEnter = () => {
    import(/* @vite-ignore */ './pages/KnowledgeBuild/');
  };

  return (
    <Link to={to} onMouseEnter={handleMouseEnter}>
      {children}
    </Link>
  );
}
```

> Note: React Router 6 does not have a `router.preload()` method. Prefetching with Vite is done via `import()` with `/* @vite-ignore */` comment.

### 8.3 SSE Performance

- Single SSE connection per dialog; multiplex events through store
- Use `requestAnimationFrame` for streaming text animation (avoid layout thrashing)
- Abort controller to cancel stale streams on dialog switch

---

## 9. Security Considerations

| Concern | Mitigation |
|---------|------------|
| XSS | Sanitize markdown content before render; use `DOMPurify` |
| CSRF | No CSRF risk — backend reads token from `Authorization` header, not cookies |
| Token Storage | Use `sessionStorage` only; clear on tab close |
| XSS Protection | Sanitize all markdown/HTML content before render; CSP headers recommended |
| Auth Redirects | `ProtectedRoute` wraps auth-gated pages |
| API Errors | Never expose internal error details to UI |

---

## 10. File Structure Summary

```
frontend/src/
├── api/
│   ├── client.ts
│   ├── auth.ts
│   ├── chat.ts
│   ├── knowledge.ts
│   ├── crawl.ts
│   ├── index.ts
│   └── types.ts
├── components/
│   ├── ui/                 # Existing design system
│   ├── layout/
│   │   ├── Sidebar/
│   │   ├── Header/
│   │   └── MainViewport/
│   ├── chat/
│   ├── knowledge/
│   ├── build/
│   └── auth/
├── features/
│   ├── chat/
│   │   ├── ChatPage.tsx
│   │   └── chatStore.ts
│   ├── knowledge/
│   │   ├── KnowledgeListPage.tsx
│   │   └── knowledgeListStore.ts
│   ├── build/
│   │   ├── KnowledgeBuildPage.tsx
│   │   └── buildStore.ts
│   └── auth/
│       ├── LoginPage.tsx
│       ├── ProfilePage.tsx
│       └── authStore.ts
├── hooks/
│   ├── useAuth.ts
│   ├── useChatStream.ts
│   └── useKnowledge.ts
├── styles/
│   ├── tokens/
│   ├── global/
│   └── utilities/
├── App.tsx
├── main.tsx
└── routes.tsx
```

---

## 11. Implementation Priorities

| Phase | Tasks | Deliverable |
|-------|-------|-------------|
| **Phase 1** | Layout (Sidebar + routing), Auth flow, Basic chat | Functional skeleton |
| **Phase 2** | Streaming chat, Tool event rendering, Message history | Chat as MVP |
| **Phase 3** | Knowledge list, Knowledge detail view | Browse functionality |
| **Phase 4** | Crawl panel, Batch upload, Task progress, Content review | Build workflow |
| **Phase 5** | RAG integration polish, Error handling, Loading states | Production hardening |

---

## 12. Testing Strategy

### 12.1 Test Dependencies

```bash
npm install -D vitest @testing-library/react @testing-library/user-event jsdom @vitest/coverage-v8
```

### 12.2 Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
```

```json
// package.json scripts
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

### 12.3 What to Test

| Priority | Area | What to Test |
|----------|------|-------------|
| **High** | `api/client.ts` | Token injection, 401 auto-logout, error parsing |
| **High** | `api/chat.ts` | SSE stream parsing, `X-Dialog-ID` extraction, `knowledge_ids` param, error handling |
| **High** | `chatStore` | SSE message appending, `dialogId` management, `currentKnowledgeIds` state |
| **High** | `authStore` | Login/logout state machine, token restoration from sessionStorage, 401 handling |
| **Medium** | `knowledgeListStore` | KB list fetch, file list fetch, error states |
| **Medium** | `buildStore` | Crawl task creation, batch URL handling, progress updates |
| **Low** | Utility functions | `parseSSELines`, error response parsers |

### 12.4 What NOT to Test

| Skip | Reason |
|------|--------|
| Pure UI components (Button, Card, Input) | Too simple, no business logic |
| CSS/styling | Only test behavior, not appearance |
| Layout components | Integration test only |

### 12.5 Test File Structure

```
src/
├── api/
│   ├── client.ts
│   └── client.test.ts         # API client unit tests
├── features/
│   ├── auth/
│   │   ├── authStore.ts
│   │   └── authStore.test.ts
│   ├── chat/
│   │   ├── chatStore.ts
│   │   ├── chatStore.test.ts
│   │   └── chat.test.ts       # SSE stream tests
│   ├── knowledge/
│   │   └── knowledgeListStore.test.ts
│   └── build/
│       └── buildStore.test.ts
└── utils/
    ├── parseSSELines.ts
    └── parseSSELines.test.ts
```

### 12.6 Example Tests

```typescript
// src/api/client.test.ts
import { describe, it, expect, vi } from 'vitest'
import { createApiClient } from './client'

describe('ApiClient', () => {
  it('injects Authorization header when token exists', async () => {
    authStore.setState({ token: 'test-token' });

    const client = createApiClient();
    const response = await client.post('/test', { data: 'test' });

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token',
        }),
      })
    );
  });

  it('calls logout on 401 response', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValueOnce(
      new Response(null, { status: 401 })
    );

    const client = createApiClient();
    await expect(client.get('/test')).rejects.toThrow('Unauthorized');
    expect(authStore.getState().logout).toHaveBeenCalled();
  });
});
```

```typescript
// src/features/chat/chat.test.ts
import { describe, it, expect, vi } from 'vitest'
import { parseSSELines } from './parseSSELines'

describe('parseSSELines', () => {
  it('parses response_chunk event', () => {
    const input = 'data: {"type":"response_chunk","data":{"chunk":"Hello","accumulated":"Hello"}}\n\n';
    const events = [...parseSSELines(input)];

    expect(events[0]).toMatchObject({
      type: 'response_chunk',
      data: { chunk: 'Hello', accumulated: 'Hello' },
    });
  });

  it('parses tool event', () => {
    const input = 'data: {"type":"event","data":{"status":"START","title":"RAG Search"}}\n\n';
    const events = [...parseSSELines(input)];

    expect(events[0]).toMatchObject({
      type: 'event',
      data: { status: 'START', title: 'RAG Search' },
    });
  });
});
```

### 12.7 Running Tests

```bash
npm test            # Run all tests in watch mode
npm run test:ui     # Run with Vitest UI browser
npm run test:coverage  # Generate coverage report
```
