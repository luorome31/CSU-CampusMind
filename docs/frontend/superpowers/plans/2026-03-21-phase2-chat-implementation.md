# Phase 2 聊天模块实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现完整的流式聊天功能，包括 SSE 流式输出、工具事件卡片、消息历史加载、知识库选择。

**Architecture:**
- `chatStore` (Zustand) 管理对话状态，`useChatStream` Hook 封装 SSE 逻辑
- 组件树：`ChatPage` → `EmptyState | (KnowledgeSelector + MessageList + ChatInput)`
- SSE 使用 `ReadableStream` API 消费 `/completion/stream`，`accumulated` 字段直接覆盖消息内容
- Markdown 使用 `react-markdown` + `remark-gfm` 渲染

**Tech Stack:** React 18, TypeScript, Zustand 5, react-markdown, remark-gfm, lucide-react

---

## Chunk 1: 基础架构（Store + SSE Hook + API）

建立聊天功能的基础设施：Zustand Store、SSE 解析工具、SSE Hook、API 层。

### 文件结构

```
src/
├── utils/
│   └── parseSSELines.ts      # SSE 行解析
├── api/
│   ├── chat.ts               # SSE stream API
│   └── dialog.ts             # Dialog history API
├── features/chat/
│   ├── chatStore.ts          # Zustand store（重写）
│   └── useChatStream.ts      # SSE hook（新增）
```

### Task 1: 安装依赖

- [ ] **Step 1: 安装 react-markdown 和 remark-gfm**

```bash
cd /home/luorome/software/CampusMind/frontend
npm install react-markdown remark-gfm
```

---

### Task 2: 创建 SSE 解析工具

- [ ] **Step 1: 创建 `src/utils/parseSSELines.ts`**

```typescript
// src/utils/parseSSELines.ts

export type SSEEventType = 'event' | 'response_chunk';

export interface SSEEvent {
  type: SSEEventType;
  data: Record<string, unknown>;
  timestamp?: number;
}

export interface SSEToolEventData {
  status: 'START' | 'END' | 'ERROR';
  title: string;
  message: string;
}

export interface SSEResponseChunkData {
  chunk: string;
  accumulated: string;
}

/**
 * Parse SSE lines from chunk text.
 * Yields individual SSE events.
 */
export function* parseSSELines(text: string): Generator<SSEEvent> {
  const lines = text.split('\n');

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || !trimmed.startsWith('data: ')) continue;

    try {
      const data = JSON.parse(trimmed.slice(6));
      yield {
        type: data.type,
        data: data.data,
        timestamp: data.timestamp,
      };
    } catch {
      // Skip malformed JSON
    }
  }
}
```

- [ ] **Step 2: 提交**

```bash
cd /home/luorome/software/CampusMind
git add src/utils/parseSSELines.ts
git commit -m "feat(chat): 添加 SSE 行解析工具"
```

---

### Task 3: 创建 Chat Store

- [ ] **Step 1: 重写 `src/features/chat/chatStore.ts`**

```typescript
// src/features/chat/chatStore.ts
import { create } from 'zustand';

export interface ToolEvent {
  id: string;
  status: 'START' | 'END' | 'ERROR';
  title: string;
  message: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  events: ToolEvent[];
  createdAt: Date;
}

interface ChatState {
  currentDialogId: string | null;
  currentKnowledgeIds: string[];
  messages: ChatMessage[];
  isStreaming: boolean;
  toolEvents: ToolEvent[];
}

interface ChatActions {
  setCurrentDialogId: (id: string | null) => void;
  setCurrentKnowledgeIds: (ids: string[]) => void;
  addMessage: (msg: ChatMessage) => void;
  updateStreamingMessage: (content: string) => void;
  addToolEvent: (event: ToolEvent) => void;
  finishStreaming: () => void;
  clearMessages: () => void;
  setToolEvents: (events: ToolEvent[]) => void;
}

type ChatStore = ChatState & ChatActions;

let messageIdCounter = 0;
function generateId(): string {
  return `msg_${Date.now()}_${++messageIdCounter}`;
}

export const chatStore = create<ChatStore>((set, get) => ({
  currentDialogId: null,
  currentKnowledgeIds: [],
  messages: [],
  isStreaming: false,
  toolEvents: [],

  setCurrentDialogId: (id) => set({ currentDialogId: id }),

  setCurrentKnowledgeIds: (ids) => set({ currentKnowledgeIds: ids }),

  addMessage: (msg) =>
    set((state) => ({
      messages: [...state.messages, msg],
    })),

  updateStreamingMessage: (content) =>
    set((state) => {
      const messages = [...state.messages];
      if (messages.length === 0) return state;

      const lastMsg = messages[messages.length - 1];
      if (lastMsg.role !== 'assistant') return state;

      messages[messages.length - 1] = {
        ...lastMsg,
        content,
      };
      return { messages };
    }),

  addToolEvent: (event) =>
    set((state) => ({
      toolEvents: [...state.toolEvents, event],
    })),

  finishStreaming: () => set({ isStreaming: false }),

  clearMessages: () => set({ messages: [], toolEvents: [], currentDialogId: null }),

  setToolEvents: (events) => set({ toolEvents: events }),
}));
```

- [ ] **Step 2: 提交**

```bash
git add src/features/chat/chatStore.ts
git commit -m "feat(chat): 重写 chatStore，包含完整状态管理"
```

---

### Task 4: 创建 Chat API 层

- [ ] **Step 1: 创建 `src/api/chat.ts`**

```typescript
// src/api/chat.ts
import { apiClient } from './client';
import { parseSSELines, type SSEEvent } from '../utils/parseSSELines';

export interface ChatStreamOptions {
  dialogId?: string;
  knowledgeIds: string[];
  enableRag?: boolean;
  topK?: number;
  minScore?: number;
}

export interface ChatStreamResult {
  event: SSEEvent;
  newDialogId?: string;
}

/**
 * Create a chat SSE stream.
 * Returns a ReadableStream that yields SSE events.
 */
export function createChatStream(
  message: string,
  options: ChatStreamOptions
): ReadableStream<ChatStreamResult> {
  const {
    dialogId,
    knowledgeIds,
    enableRag = knowledgeIds.length > 0,
    topK = 5,
    minScore = 0.0,
  } = options;

  return new ReadableStream<ChatStreamResult>({
    async start(controller) {
      try {
        const response = await fetch('/api/v1/completion/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(sessionStorage.getItem('token')
              ? { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
              : {}),
          },
          body: JSON.stringify({
            message,
            dialog_id: dialogId ?? undefined,
            knowledge_ids: knowledgeIds,
            enable_rag: enableRag,
            top_k: topK,
            min_score: minScore,
          }),
        });

        // Handle new dialog ID from response headers
        const newDialogId = response.headers.get('X-Dialog-ID');

        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          controller.error(new Error(error.detail || 'Stream request failed'));
          return;
        }

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });

          for (const event of parseSSELines(chunk)) {
            controller.enqueue({ event, newDialogId: newDialogId ?? undefined });
          }
        }

        controller.close();
      } catch (err) {
        controller.error(err);
      }
    },
  });
}
```

- [ ] **Step 2: 创建 `src/api/dialog.ts`**

```typescript
// src/api/dialog.ts
import { apiClient } from './client';
import type { ChatMessage, ToolEvent } from '../features/chat/chatStore';

export interface Dialog {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface ChatHistoryResponse {
  id: string;
  dialog_id: string;
  role: string;
  content: string;
  events: ToolEvent[];
  created_at: string;
}

/**
 * Get dialog history messages.
 */
export async function getDialogHistory(dialogId: string): Promise<ChatMessage[]> {
  const history = await apiClient.get<ChatHistoryResponse[]>(
    `/dialogs/${dialogId}/history`
  );

  return history.map((item) => ({
    id: item.id,
    role: item.role as 'user' | 'assistant',
    content: item.content,
    events: item.events || [],
    createdAt: new Date(item.created_at),
  }));
}

/**
 * Get all user dialogs.
 */
export async function getUserDialogs(userId: string): Promise<Dialog[]> {
  return apiClient.get<Dialog[]>(`/users/${userId}/dialogs`);
}
```

- [ ] **Step 3: 提交**

```bash
git add src/api/chat.ts src/api/dialog.ts
git commit -m "feat(chat): 添加 chat API 层（SSE stream + dialog history）"
```

---

### Task 5: 创建 useChatStream Hook

- [ ] **Step 1: 创建 `src/features/chat/useChatStream.ts`**

```typescript
// src/features/chat/useChatStream.ts
import { useCallback, useRef } from 'react';
import { chatStore, type ChatMessage, type ToolEvent } from './chatStore';
import { createChatStream, type ChatStreamResult } from '../api/chat';

let toolEventIdCounter = 0;
function generateToolEventId(): string {
  return `tool_${Date.now()}_${++toolEventIdCounter}`;
}

export function useChatStream() {
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (content: string, knowledgeIds: string[]) => {
      // Cancel any existing stream
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      const store = chatStore.getState();

      // Add user message
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'user',
        content,
        events: [],
        createdAt: new Date(),
      };
      store.addMessage(userMessage);

      // Create assistant placeholder
      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: '',
        events: [],
        createdAt: new Date(),
      };
      store.addMessage(assistantMessage);

      // Start streaming
      store.setToolEvents([]);
      chatStore.setState({ isStreaming: true });

      try {
        const stream = createChatStream(content, {
          dialogId: store.currentDialogId ?? undefined,
          knowledgeIds,
          enableRag: knowledgeIds.length > 0,
        });

        const reader = stream.getReader();

        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;

          const { event, newDialogId } = value as ChatStreamResult;

          // Set new dialog ID if this is a new dialog
          if (newDialogId && !store.currentDialogId) {
            chatStore.getState().setCurrentDialogId(newDialogId);
          }

          if (event.type === 'response_chunk') {
            const data = event.data as { accumulated: string };
            chatStore.getState().updateStreamingMessage(data.accumulated);
          } else if (event.type === 'event') {
            const data = event.data as ToolEvent;
            const toolEvent: ToolEvent = {
              id: generateToolEventId(),
              status: data.status,
              title: data.title,
              message: data.message,
            };
            chatStore.getState().addToolEvent(toolEvent);
          }
        }
      } catch (err) {
        console.error('Stream error:', err);
      } finally {
        chatStore.setState({ isStreaming: false });
        abortControllerRef.current = null;
      }
    },
    []
  );

  const cancelStream = useCallback(() => {
    abortControllerRef.current?.abort();
    chatStore.setState({ isStreaming: false });
  }, []);

  return {
    sendMessage,
    cancelStream,
    isStreaming: chatStore((s) => s.isStreaming),
    messages: chatStore((s) => s.messages),
    toolEvents: chatStore((s) => s.toolEvents),
  };
}
```

- [ ] **Step 2: 提交**

```bash
git add src/features/chat/useChatStream.ts
git commit -m "feat(chat): 添加 useChatStream Hook"
```

---

## Chunk 2: UI 组件

实现聊天界面的所有 UI 组件。

### 文件结构

```
src/components/chat/
├── EmptyState/
│   ├── index.tsx
│   └── EmptyState.css
├── KnowledgeSelector/
│   ├── index.tsx
│   └── KnowledgeSelector.css
├── MessageList/
│   ├── index.tsx
│   └── MessageList.css
├── MessageBubble/
│   ├── index.tsx
│   └── MessageBubble.css
├── StreamingText/
│   ├── index.tsx
│   └── StreamingText.css
├── ToolEventCard/
│   ├── index.tsx
│   └── ToolEventCard.css
└── ChatInput/
    ├── index.tsx
    └── ChatInput.css
```

---

### Task 6: 创建 EmptyState 组件

- [ ] **Step 1: 创建 `src/components/chat/EmptyState/index.tsx`**

```tsx
// src/components/chat/EmptyState/index.tsx
import React from 'react';
import './EmptyState.css';

/**
 * Empty state shown when there are no messages.
 * Shows CampusMind branding and system introduction.
 */
export const EmptyState: React.FC = () => {
  return (
    <div className="empty-state">
      <div className="empty-state-logo">
        <svg
          width="64"
          height="64"
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="32" cy="32" r="30" stroke="var(--color-accent)" strokeWidth="2" />
          <path
            d="M32 16C23.163 16 16 23.163 16 32s7.163 16 16 16 16-7.163 16-16-7.163-16-16-16zm0 4c6.627 0 12 5.373 12 12s-5.373 12-12 12-12-5.373-12-12 5.373-12 12-12z"
            fill="var(--color-accent)"
          />
          <circle cx="32" cy="32" r="4" fill="var(--color-accent)" />
        </svg>
      </div>
      <h1 className="empty-state-title">CampusMind</h1>
      <p className="empty-state-subtitle">你的智能校园助手</p>
      <ul className="empty-state-features">
        <li>查询成绩和课表</li>
        <li>了解校园通知和活动</li>
        <li>获取选课和教务信息</li>
      </ul>
    </div>
  );
};

export default EmptyState;
```

- [ ] **Step 2: 创建 `src/components/chat/EmptyState/EmptyState.css`**

```css
/* src/components/chat/EmptyState/EmptyState.css */

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: var(--space-8);
  text-align: center;
}

.empty-state-logo {
  margin-bottom: var(--space-6);
  opacity: 0.85;
}

.empty-state-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2);
  letter-spacing: var(--tracking-tight);
}

.empty-state-subtitle {
  font-size: var(--text-lg);
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-8);
}

.empty-state-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  color: var(--color-text-tertiary);
  font-size: var(--text-sm);
}

.empty-state-features li::before {
  content: '·';
  margin-right: var(--space-2);
  color: var(--color-accent);
}
```

- [ ] **Step 3: 提交**

```bash
git add src/components/chat/EmptyState/
git commit -m "feat(chat): 添加 EmptyState 组件"
```

---

### Task 7: 创建 KnowledgeSelector 组件

- [ ] **Step 1: 创建 `src/components/chat/KnowledgeSelector/index.tsx`**

```tsx
// src/components/chat/KnowledgeSelector/index.tsx
import React from 'react';
import { X } from 'lucide-react';
import { Chip } from '../../ui/Chip';
import { useChatStore } from '../../../features/chat/chatStore';
import './KnowledgeSelector.css';

interface KnowledgeBase {
  id: string;
  name: string;
}

interface KnowledgeSelectorProps {
  knowledgeBases: KnowledgeBase[];
}

/**
 * Knowledge base selector shown above the message list.
 * Users select which knowledge bases to include in RAG.
 */
export const KnowledgeSelector: React.FC<KnowledgeSelectorProps> = ({
  knowledgeBases,
}) => {
  const currentKnowledgeIds = useChatStore((s) => s.currentKnowledgeIds);
  const setCurrentKnowledgeIds = useChatStore((s) => s.setCurrentKnowledgeIds);

  const selectedKBs = knowledgeBases.filter((kb) =>
    currentKnowledgeIds.includes(kb.id)
  );

  const handleToggle = (kbId: string) => {
    if (currentKnowledgeIds.includes(kbId)) {
      setCurrentKnowledgeIds(currentKnowledgeIds.filter((id) => id !== kbId));
    } else {
      setCurrentKnowledgeIds([...currentKnowledgeIds, kbId]);
    }
  };

  const handleRemove = (kbId: string) => {
    setCurrentKnowledgeIds(currentKnowledgeIds.filter((id) => id !== kbId));
  };

  return (
    <div className="knowledge-selector">
      <span className="knowledge-selector-label">知识库</span>
      <div className="knowledge-selector-chips">
        {knowledgeBases.map((kb) => {
          const isSelected = currentKnowledgeIds.includes(kb.id);
          return (
            <Chip
              key={kb.id}
              variant={isSelected ? 'active' : 'default'}
              onClick={() => handleToggle(kb.id)}
            >
              {kb.name}
            </Chip>
          );
        })}
      </div>
      {selectedKBs.length > 0 && (
        <button
          className="knowledge-selector-clear"
          onClick={() => setCurrentKnowledgeIds([])}
          type="button"
        >
          <X size={14} />
          清除
        </button>
      )}
    </div>
  );
};

export default KnowledgeSelector;
```

- [ ] **Step 2: 创建 `src/components/chat/KnowledgeSelector/KnowledgeSelector.css`**

```css
/* src/components/chat/KnowledgeSelector/KnowledgeSelector.css */

.knowledge-selector {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-surface);
  border-bottom: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.knowledge-selector-label {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  white-space: nowrap;
}

.knowledge-selector-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  flex: 1;
}

.knowledge-selector-clear {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  background: none;
  border: none;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: color var(--duration-fast);
}

.knowledge-selector-clear:hover {
  color: var(--color-text-secondary);
}
```

- [ ] **Step 3: 提交**

```bash
git add src/components/chat/KnowledgeSelector/
git commit -m "feat(chat): 添加 KnowledgeSelector 组件"
```

---

### Task 8: 创建 StreamingText 组件

- [ ] **Step 1: 创建 `src/components/chat/StreamingText/index.tsx`**

```tsx
// src/components/chat/StreamingText/index.tsx
import React, { useEffect, useState } from 'react';
import './StreamingText.css';

interface StreamingTextProps {
  text: string;
  isStreaming: boolean;
}

/**
 * Animated text that reveals content as it streams in.
 * Uses cursor blinking during streaming.
 */
export const StreamingText: React.FC<StreamingTextProps> = ({
  text,
  isStreaming,
}) => {
  const [displayedText, setDisplayedText] = useState(text);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (text === displayedText) return;

    setIsAnimating(true);

    // For simplicity, we update immediately since backend sends accumulated text
    // This component mainly handles the streaming cursor
    setDisplayedText(text);
    setIsAnimating(false);
  }, [text]);

  return (
    <span className="streaming-text">
      {displayedText}
      {isStreaming && <span className="streaming-cursor" />}
    </span>
  );
};

export default StreamingText;
```

- [ ] **Step 2: 创建 `src/components/chat/StreamingText/StreamingText.css`**

```css
/* src/components/chat/StreamingText/StreamingText.css */

.streaming-text {
  position: relative;
}

.streaming-cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: var(--color-accent);
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
```

- [ ] **Step 3: 提交**

```bash
git add src/components/chat/StreamingText/
git commit -m "feat(chat): 添加 StreamingText 组件"
```

---

### Task 9: 创建 ToolEventCard 组件

- [ ] **Step 1: 创建 `src/components/chat/ToolEventCard/index.tsx`**

```tsx
// src/components/chat/ToolEventCard/index.tsx
import React, { useState } from 'react';
import { ChevronDown, Loader2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import type { ToolEvent } from '../../../features/chat/chatStore';
import './ToolEventCard.css';

interface ToolEventCardProps {
  event: ToolEvent;
}

/**
 * Expandable tool event card shown within assistant messages.
 * Shows status icon, title, and brief message.
 * Clicking expands to show full details.
 */
export const ToolEventCard: React.FC<ToolEventCardProps> = ({ event }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusIcon = {
    START: <Loader2 size={14} className="tool-icon tool-icon-loading" />,
    END: <CheckCircle size={14} className="tool-icon tool-icon-success" />,
    ERROR: <XCircle size={14} className="tool-icon tool-icon-error" />,
  }[event.status];

  const statusText = {
    START: '进行中',
    END: '完成',
    ERROR: '错误',
  }[event.status];

  return (
    <div
      className={`tool-event-card tool-event-${event.status.toLowerCase()}`}
    >
      <button
        className="tool-event-header"
        onClick={() => setIsExpanded(!isExpanded)}
        type="button"
      >
        <div className="tool-event-summary">
          {statusIcon}
          <span className="tool-event-title">{event.title}</span>
          <span className="tool-event-status">{statusText}</span>
        </div>
        <ChevronDown
          size={14}
          className={`tool-event-chevron ${isExpanded ? 'expanded' : ''}`}
        />
      </button>
      {isExpanded && (
        <div className="tool-event-details">
          <p className="tool-event-message">{event.message}</p>
        </div>
      )}
    </div>
  );
};

export default ToolEventCard;
```

- [ ] **Step 2: 创建 `src/components/chat/ToolEventCard/ToolEventCard.css`**

```css
/* src/components/chat/ToolEventCard/ToolEventCard.css */

.tool-event-card {
  border-left: 3px solid var(--color-accent);
  background: var(--color-bg-surface);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  margin-top: var(--space-2);
  overflow: hidden;
}

.tool-event-start {
  border-left-color: var(--color-info);
}

.tool-event-end {
  border-left-color: var(--color-success);
}

.tool-event-error {
  border-left-color: var(--color-error);
}

.tool-event-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
}

.tool-event-summary {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.tool-event-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.tool-event-status {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.tool-event-chevron {
  color: var(--color-text-tertiary);
  transition: transform var(--duration-fast);
}

.tool-event-chevron.expanded {
  transform: rotate(180deg);
}

.tool-event-details {
  padding: var(--space-2) var(--space-3);
  padding-top: 0;
}

.tool-event-message {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.tool-icon-loading {
  animation: spin 1s linear infinite;
  color: var(--color-info);
}

.tool-icon-success {
  color: var(--color-success);
}

.tool-icon-error {
  color: var(--color-error);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

- [ ] **Step 3: 提交**

```bash
git add src/components/chat/ToolEventCard/
git commit -m "feat(chat): 添加 ToolEventCard 组件"
```

---

### Task 10: 创建 MessageBubble 组件

- [ ] **Step 1: 创建 `src/components/chat/MessageBubble/index.tsx`**

```tsx
// src/components/chat/MessageBubble/index.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { StreamingText } from '../StreamingText';
import { ToolEventCard } from '../ToolEventCard';
import type { ChatMessage } from '../../../features/chat/chatStore';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

/**
 * Single message bubble.
 * - User: right-aligned, dark background
 * - Assistant: left-aligned, light background, supports Markdown + tool events
 */
export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isStreaming = false,
}) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-bubble message-${isUser ? 'user' : 'assistant'}`}>
      <div className="message-content">
        {isUser ? (
          <p className="message-text">{message.content}</p>
        ) : (
          <>
            <div className="message-markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
            {message.events.length > 0 && (
              <div className="message-events">
                {message.events.map((event) => (
                  <ToolEventCard key={event.id} event={event} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
```

- [ ] **Step 2: 创建 `src/components/chat/MessageBubble/MessageBubble.css`**

```css
/* src/components/chat/MessageBubble/MessageBubble.css */

.message-bubble {
  display: flex;
  margin-bottom: var(--space-3);
}

.message-user {
  justify-content: flex-end;
}

.message-assistant {
  justify-content: flex-start;
}

.message-content {
  max-width: 80%;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  line-height: var(--leading-normal);
}

.message-user .message-content {
  background: var(--color-text-primary);
  color: var(--color-bg-base);
  border-bottom-right-radius: var(--radius-sm);
}

.message-assistant .message-content {
  background: var(--color-bg-surface);
  color: var(--color-text-primary);
  border-bottom-left-radius: var(--radius-sm);
}

.message-text {
  margin: 0;
  font-size: var(--text-base);
}

.message-markdown {
  font-size: var(--text-base);
}

.message-markdown p {
  margin: 0 0 var(--space-2);
}

.message-markdown p:last-child {
  margin-bottom: 0;
}

.message-markdown code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  background: var(--color-bg-inset);
  padding: 0.1em 0.4em;
  border-radius: var(--radius-sm);
}

.message-markdown pre {
  background: var(--color-bg-inset);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: var(--space-2) 0;
}

.message-markdown pre code {
  background: none;
  padding: 0;
}

.message-markdown a {
  color: var(--color-accent);
}

.message-markdown ul,
.message-markdown ol {
  margin: var(--space-2) 0;
  padding-left: var(--space-6);
}

.message-markdown h1,
.message-markdown h2,
.message-markdown h3 {
  margin: var(--space-3) 0 var(--space-2);
  font-weight: var(--font-semibold);
}

.message-events {
  margin-top: var(--space-3);
}
```

- [ ] **Step 3: 提交**

```bash
git add src/components/chat/MessageBubble/
git commit -m "feat(chat): 添加 MessageBubble 组件"
```

---

### Task 11: 创建 MessageList 组件

- [ ] **Step 1: 创建 `src/components/chat/MessageList/index.tsx`**

```tsx
// src/components/chat/MessageList/index.tsx
import React, { useEffect, useRef } from 'react';
import { MessageBubble } from '../MessageBubble';
import type { ChatMessage } from '../../../features/chat/chatStore';
import './MessageList.css';

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming: boolean;
}

/**
 * Scrollable message list container.
 * Auto-scrolls to bottom when new messages arrive.
 */
export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isStreaming,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  if (messages.length === 0) return null;

  return (
    <div className="message-list">
      {messages.map((msg) => {
        const isLastAssistant =
          msg.role === 'assistant' &&
          messages[messages.length - 1].id === msg.id;
        return (
          <MessageBubble
            key={msg.id}
            message={msg}
            isStreaming={isLastAssistant && isStreaming}
          />
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
};

export default MessageList;
```

- [ ] **Step 2: 创建 `src/components/chat/MessageList/MessageList.css`**

```css
/* src/components/chat/MessageList/MessageList.css */

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
}
```

- [ ] **Step 3: 提交**

```bash
git add src/components/chat/MessageList/
git commit -m "feat(chat): 添加 MessageList 组件"
```

---

### Task 12: 创建 ChatInput 组件

- [ ] **Step 1: 创建 `src/components/chat/ChatInput/index.tsx`**

```tsx
// src/components/chat/ChatInput/index.tsx
import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { Button } from '../../ui/Button';
import './ChatInput.css';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

/**
 * Chat input with send button.
 * Disabled during streaming.
 */
export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [value, setValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <div className="chat-input-wrapper">
        <input
          type="text"
          className="chat-input"
          placeholder={disabled ? '等待回复中...' : '输入消息...'}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={disabled}
          autoComplete="off"
        />
        <Button
          type="submit"
          variant="primary"
          size="md"
          disabled={disabled || !value.trim()}
          className="chat-input-send"
        >
          <Send size={16} />
        </Button>
      </div>
    </form>
  );
};

export default ChatInput;
```

- [ ] **Step 2: 创建 `src/components/chat/ChatInput/ChatInput.css`**

```css
/* src/components/chat/ChatInput/ChatInput.css */

.chat-input-form {
  padding: var(--space-4);
  background: var(--color-bg-surface);
  border-top: 1px solid var(--color-border-subtle);
}

.chat-input-wrapper {
  display: flex;
  gap: var(--space-2);
  max-width: 800px;
  margin: 0 auto;
}

.chat-input {
  flex: 1;
  height: var(--input-height);
  padding: 0 var(--space-4);
  font-size: var(--text-base);
  font-family: var(--font-sans);
  color: var(--color-text-primary);
  background: var(--color-bg-inset);
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-inset);
  outline: none;
  transition: box-shadow var(--duration-fast);
}

.chat-input:focus {
  box-shadow: var(--shadow-inset-focus);
}

.chat-input::placeholder {
  color: var(--color-text-tertiary);
}

.chat-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chat-input-send {
  flex-shrink: 0;
}
```

- [ ] **Step 3: 提交**

```bash
git add src/components/chat/ChatInput/
git commit -m "feat(chat): 添加 ChatInput 组件"
```

---

## Chunk 3: 集成 ChatPage

将所有组件集成到 ChatPage，重构当前的 placeholder 实现。

### Task 13: 重构 ChatPage

- [ ] **Step 1: 重写 `src/features/chat/ChatPage.tsx`**

```tsx
// src/features/chat/ChatPage.tsx
import React, { useCallback } from 'react';
import { EmptyState } from '../../components/chat/EmptyState';
import { KnowledgeSelector } from '../../components/chat/KnowledgeSelector';
import { MessageList } from '../../components/chat/MessageList';
import { ChatInput } from '../../components/chat/ChatInput';
import { useChatStream } from './useChatStream';
import { useChatStore } from './chatStore';
import './ChatPage.css';

// Mock knowledge bases for demo - replace with API call
const MOCK_KNOWLEDGE_BASES = [
  { id: 'kb_1', name: '教务系统' },
  { id: 'kb_2', name: '图书馆' },
  { id: 'kb_3', name: '校园通知' },
];

/**
 * Main chat page component.
 * Shows EmptyState when no messages, otherwise shows chat UI.
 */
export function ChatPage() {
  const { sendMessage, isStreaming, messages } = useChatStream();
  const currentKnowledgeIds = useChatStore((s) => s.currentKnowledgeIds);

  const handleSend = useCallback(
    (content: string) => {
      sendMessage(content, currentKnowledgeIds);
    },
    [sendMessage, currentKnowledgeIds]
  );

  const hasMessages = messages.length > 0;

  return (
    <div className="chat-page">
      {hasMessages ? (
        <>
          <KnowledgeSelector knowledgeBases={MOCK_KNOWLEDGE_BASES} />
          <MessageList messages={messages} isStreaming={isStreaming} />
          <ChatInput onSend={handleSend} disabled={isStreaming} />
        </>
      ) : (
        <>
          <EmptyState />
          <div className="chat-page-input-fixed">
            <ChatInput onSend={handleSend} disabled={isStreaming} />
          </div>
        </>
      )}
    </div>
  );
}
```

- [ ] **Step 2: 创建 `src/features/chat/ChatPage.css`**

```css
/* src/features/chat/ChatPage.css */

.chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.chat-page-input-fixed {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-bg-base);
}
```

- [ ] **Step 3: 提交**

```bash
git add src/features/chat/ChatPage.tsx src/features/chat/ChatPage.css
git commit -m "feat(chat): 重构 ChatPage，集成所有聊天组件"
```

---

## Chunk 4: 收尾与测试

清理和更新进度文档。

### Task 14: 更新进度日志

- [ ] **Step 1: 更新 `frontend/docs/frontend-progress-log.md`**

在 Phase 1 完成后添加 Phase 2 的记录。

- [ ] **Step 2: 提交**

```bash
git add frontend/docs/frontend-progress-log.md
git commit -m "docs(frontend): 记录 Phase 2 完成状态"
```

---

## 最终检查

所有任务完成后，确认：

- [ ] `npm run dev` 启动无编译错误
- [ ] 聊天页面加载正常，显示 EmptyState
- [ ] 输入消息后出现用户气泡和助手气泡
- [ ] 流式输出时输入框被禁用
- [ ] 工具事件卡片可展开
- [ ] Markdown 内容正确渲染
