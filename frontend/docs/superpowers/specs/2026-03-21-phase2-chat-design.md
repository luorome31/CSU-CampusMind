# Phase 2 聊天模块设计方案

> 本文档记录 Phase 2 流式聊天功能的完整设计决策。

## 设计决策

| 编号 | 决策点 | 选择 | 理由 |
|------|--------|------|------|
| 1 | 对话气泡风格 | A. 双色对称气泡 | 区分度高，视觉清晰 |
| 2 | 知识库选择流程 | A. 聊前选择模式 | 显式可控，符合架构 |
| 3 | 流式中交互 | A. 禁止发送新消息 | 避免对话逻辑混乱 |
| 4 | 工具事件展示 | A. 可展开详情卡片 | 信息层次分明 |
| 5 | 空状态设计 | A. Logo + 系统介绍 | 第一印象好 |
| 6 | think 标签处理 | B. 基础实现 | Phase 2 scope 控制 |
| 7 | Markdown 渲染 | A. react-markdown | 功能与复杂度平衡 |

---

## 1. 组件架构

```
ChatPage (容器)
├── EmptyState           # 无消息时：Logo + 系统介绍
├── KnowledgeSelector    # 知识库多选芯片栏（聊前选择）
├── MessageList          # 滚动容器
│   └── MessageBubble   # 消息气泡（用户/助手）
│       └── ToolEventCard  # 可折叠工具事件卡片（助手消息内）
└── ChatInput           # 输入框 + 发送按钮
```

---

## 2. Store 设计 (chatStore)

```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  events?: ToolEvent[];
  createdAt: Date;
}

interface ToolEvent {
  id: string;
  status: 'START' | 'END' | 'ERROR';
  title: string;
  message: string;
}

interface ChatStore {
  currentDialogId: string | null;
  currentKnowledgeIds: string[];
  messages: ChatMessage[];
  isStreaming: boolean;
  toolEvents: ToolEvent[];

  // Actions
  setCurrentDialogId: (id: string) => void;
  setCurrentKnowledgeIds: (ids: string[]) => void;
  addMessage: (msg: ChatMessage) => void;
  updateStreamingMessage: (content: string) => void;  // 方案 A：用 accumulated 覆盖
  addToolEvent: (event: ToolEvent) => void;
  finishStreaming: () => void;
  clearMessages: () => void;
}
```

**流式消息更新策略（方案 A）**：
- SSE 后端每个 `response_chunk` 包含 `accumulated`（全量内容）
- 直接用 `accumulated` 覆盖最后一条消息的 `content`
- 无需客户端拼接 `previousChunk + newChunk`

---

## 3. SSE 处理 (useChatStream Hook)

```typescript
// useChatStream.ts
export function useChatStream() {
  const store = useChatStore();

  async function sendMessage(content: string, knowledgeIds: string[]) {
    // 1. 添加用户消息到 messages
    // 2. 创建 assistant 占位消息（content: ''）
    // 3. 建立 SSE 连接 POST /completion/stream
    // 4. 流式处理：
    //    - response_chunk: updateStreamingMessage(accumulated)
    //    - event START/END/ERROR: addToolEvent
    // 5. finishStreaming()
  }

  return { sendMessage, isStreaming: store.isStreaming };
}
```

**RAG 参数处理**：
```typescript
// knowledgeIds 为空时，必须设置 enable_rag: false
// 否则后端返回 400
const enableRag = knowledgeIds.length > 0;
```

**X-Dialog-ID 处理**：
```typescript
// 新建对话时（dialogId 为 null），从响应头提取 X-Dialog-ID
const newDialogId = response.headers.get('X-Dialog-ID');
if (newDialogId) {
  chatStore.getState().setCurrentDialogId(newDialogId);
}
```

---

## 4. 组件清单

| 组件 | 文件位置 | 职责 |
|------|---------|------|
| `MessageList` | `components/chat/MessageList/` | 滚动容器，自动滚动到底部 |
| `MessageBubble` | `components/chat/MessageBubble/` | 单条消息，role 区分样式 |
| `StreamingText` | `components/chat/StreamingText/` | 流式文字动画（逐字/逐段显示） |
| `ToolEventCard` | `components/chat/ToolEventCard/` | 可展开工具事件卡片 |
| `KnowledgeSelector` | `components/chat/KnowledgeSelector/` | 知识库多选芯片栏 |
| `ChatInput` | `components/chat/ChatInput/` | 输入框，发送逻辑 |
| `EmptyState` | `components/chat/EmptyState/` | Logo + 系统介绍 |

---

## 5. 样式规范

### 消息气泡
- 用户气泡：`background: var(--color-text-primary)`，文字 `var(--color-bg-base)`，右对齐
- 助手气泡：`background: var(--color-bg-surface)`，文字 `var(--color-text-primary)`，左对齐
- 圆角：`var(--radius-lg)`，间距：`var(--space-3)`

### 工具卡片
- `border-left: 3px solid var(--color-accent)`
- 状态图标：加载中（旋转）/ 成功（勾）/ 错误（叉）
- 展开动画：`var(--duration-normal)`

### 知识选择栏
- Chip 组件复用 `components/ui/Chip/`
- 已选：`background: var(--color-accent-bg)`
- 未选：`placeholder text`

### 输入框
- `background: var(--color-bg-inset)`
- `var(--shadow-inset)`
- 发送中：`opacity: 0.6`，`cursor: not-allowed`

### Markdown 渲染
- 使用 `react-markdown` + `remark-gfm`
- 代码块：`background: var(--color-bg-inset)`，`font-family: var(--font-mono)`
- 链接：`color: var(--color-accent)`

### think 标签（Phase 2 基础实现）
- 直接渲染为 Markdown 代码块样式
- 解析作为后续优化项

---

## 6. API 层扩展

```typescript
// api/chat.ts
export function createChatStream(
  message: string,
  options: {
    dialogId?: string;
    knowledgeIds: string[];
    enableRag?: boolean;
    topK?: number;
    minScore?: number;
  }
): ReadableStream<SSEEvent>
```

```typescript
// api/dialog.ts
export async function getDialogHistory(dialogId: string): Promise<ChatMessage[]>
export async function getUserDialogs(userId: string): Promise<Dialog[]>
```

---

## 7. 文件结构

```
src/
├── api/
│   ├── chat.ts           # SSE stream + completion API
│   └── dialog.ts         # History API
├── components/
│   └── chat/
│       ├── MessageList/
│       │   ├── index.tsx
│       │   └── MessageList.css
│       ├── MessageBubble/
│       │   ├── index.tsx
│       │   └── MessageBubble.css
│       ├── StreamingText/
│       │   ├── index.tsx
│       │   └── StreamingText.css
│       ├── ToolEventCard/
│       │   ├── index.tsx
│       │   └── ToolEventCard.css
│       ├── KnowledgeSelector/
│       │   ├── index.tsx
│       │   └── KnowledgeSelector.css
│       ├── ChatInput/
│       │   ├── index.tsx
│       │   └── ChatInput.css
│       └── EmptyState/
│           ├── index.tsx
│           └── EmptyState.css
├── features/chat/
│   ├── ChatPage.tsx      # 容器（重构当前 placeholder）
│   ├── chatStore.ts      # Zustand store（重构当前空实现）
│   └── useChatStream.ts  # SSE hook（新增）
└── utils/
    └── parseSSELines.ts  # SSE 行解析（新增）
```

---

## 8. 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 网络错误 | Toast 提示"连接失败，点击重试"，可点击重发 |
| 401 | 触发登出流程 |
| SSE 错误事件 | 显示错误状态卡片，不中断已有消息 |
| 知识库未选且 enableRag=true | 客户端强制设置 enableRag: false |

---

## 9. 依赖清单

```json
{
  "react-markdown": "^9.x",
  "remark-gfm": "^4.x"
}
```

---

## 10. 待后续优化（Phase 5）

- [ ] think 标签解析和折叠渲染
- [ ] Markdown 表格、引用块等丰富样式
- [ ] 消息复制/编辑功能
- [ ] 流式中断和恢复
