# CampusMind Frontend Architecture

## 1. Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | React 18+ + Vite |
| Language | TypeScript 5.x |
| Routing | React Router 6.x |
| State | Zustand 4.x |
| Styling | CSS Variables + Global CSS (no CSS Modules) |
| Testing | Vitest + @testing-library/react |

## 2. Project Structure

```
frontend/src/
├── api/               # API clients (client.ts, auth.ts, chat.ts, dialog.ts, knowledge.ts, crawl.ts)
├── components/
│   ├── ui/            # Design system (Button, Input, Card, Chip, Badge)
│   ├── layout/        # Sidebar, Header, MainViewport
│   └── chat/          # MessageBubble, ChatInput, StreamingText, ToolEventCard
├── features/
│   ├── auth/          # LoginPage, ProfilePage, authStore
│   ├── chat/          # ChatPage, chatStore
│   ├── knowledge/     # KnowledgeListPage, knowledgeListStore
│   └── build/         # KnowledgeBuildPage, buildStore
├── styles/tokens/     # Design tokens (colors, typography, spacing, elevation)
└── utils/             # Utilities
```

## 3. Layout Structure

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
│  └──────────┘  │  └────────────────────────────────────┘ │ │
│                └────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| < 768px (mobile) | Sidebar hidden, hamburger menu trigger |
| 768px - 1024px (tablet) | Sidebar collapsed to icon-only rail |
| > 1024px (desktop) | Sidebar expanded, content full-width |

### Sidebar Components

```
Sidebar/
├── Sidebar.tsx          # Container with toggle + history list integration
├── HistoryItem.tsx      # Individual history entry (title, time, delete)
└── HistoryItem.css      # History item styles (hover, transition animation)
```

## 4. Routes

| Route | Component | Auth | Description |
|-------|-----------|------|-------------|
| `/` | `ChatPage` | No | AI dialogue interface |
| `/knowledge` | `KnowledgeListPage` | No | Browse knowledge bases |
| `/knowledge/build` | `KnowledgeBuildPage` | Yes | Crawl & index |
| `/profile` | `ProfilePage` | Yes | User profile |

## 5. State Management (Zustand)

| Store | Scope | Key State |
|-------|-------|-----------|
| `authStore` | Global | `user`, `token`, `isAuthenticated` |
| `layoutStore` | Global | `sidebarOpen`, `sidebarCollapsed` |
| `chatStore` | Chat | `currentDialogId`, `messages`, `isStreaming`, `toolEvents`, `dialogs` |
| `knowledgeListStore` | Knowledge | `knowledgeBases`, `selectedKB`, `files` |
| `buildStore` | Build | `crawlResults`, `tasks`, `reviewContent` |

## 6. Critical API Patterns

### 6.1 SSE Chat Stream
- Endpoint: `POST /api/v1/completion/stream`
- **Required**: `knowledge_ids` when `enable_rag=true`
- **Important**: Extract `X-Dialog-ID` header for new dialogs
- SSE events: `response_chunk`, `event` (START/END/ERROR), `new_dialog`, `title_update`

### 6.2 API Client
- Base URL: `/api/v1`
- Token: `Authorization: Bearer <token>` from sessionStorage
- 401 response → auto logout
- Methods: `get`, `post`, `delete`, `patch`

### 6.3 Dialog API (`api/dialog.ts`)
- `listDialogs(limit?)` → GET `/dialogs`
- `getDialogMessages(dialogId)` → GET `/dialogs/{id}/messages`
- `deleteDialog(dialogId)` → DELETE `/dialogs/{id}`
- `updateDialogTitle(dialogId, title)` → PATCH `/dialogs/{id}`

## 7. Component Styling

All components use CSS variables (e.g., `var(--color-bg-surface)`), **no CSS Modules**.

Token files: `src/styles/tokens/{colors,typography,spacing,elevation}.css`

## 8. Performance Rules

| Rule | Usage |
|------|-------|
| `async-parallel` | Parallel fetch dialog history + profile on navigation |
| `bundle-dynamic-imports` | Lazy load `KnowledgeBuildPage`, `BatchUploadModal` |
| `rerender-memo` | Memoize `MessageBubble` |
| `bundle-preload` | Preload chat page on sidebar hover |

## 9. Security

- Token stored in `sessionStorage` (cleared on tab close)
- Sanitize markdown/HTML content before render (XSS protection)
- `ProtectedRoute` wraps auth-gated pages
- CSRF not a risk (token in Authorization header, not cookies)

## 10. Implementation Priorities

| Phase | Tasks |
|-------|-------|
| **Phase 1** | Layout (Sidebar + routing), Auth flow, Basic chat |
| **Phase 2** | Streaming chat, Tool event rendering, Message history |
| **Phase 3** | Knowledge list, Knowledge detail view |
| **Phase 4** | Crawl panel, Batch upload, Task progress, Content review |
| **Phase 5** | RAG integration polish, Error handling, Loading states |

## 11. Testing Strategy

### Test Location
Test files alongside source files with `.test.ts`/`.test.tsx` suffix.

### What to Test (Priority Order)

| Priority | Area | What to Test |
|----------|------|-------------|
| **High** | `api/client.ts` | Token injection, 401 auto-logout, error parsing |
| **High** | `api/chat.ts` | SSE parsing, `X-Dialog-ID` extraction, `knowledge_ids` param |
| **High** | `chatStore` | SSE appending, `dialogId` management |
| **High** | `authStore` | Login/logout, token restoration |
| **Medium** | `knowledgeListStore`, `buildStore` | Fetch, error states |
| **Low** | Utility functions | `parseSSELines` |

### What NOT to Test
- Pure UI components (Button, Card, Input) - too simple
- CSS/styling - test behavior only
- Layout components - integration test only

### Run Tests
```bash
npm run test:run           # Run once
npm run test:coverage      # With coverage
NODE_OPTIONS="--max-old-space-size=4096" npm run test:run  # OOM fix
```
