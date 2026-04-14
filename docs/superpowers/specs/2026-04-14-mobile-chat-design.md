# Mobile Chat 模块设计方案

## 概述

本文档定义 CampusMind 移动端 Chat 模块的设计方案，基于 Web 端 chat 实现进行移动端适配。

## 核心技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| Markdown 渲染 | `react-native-markdown-display` + `react-native-syntax-highlighter` | 与 Web 端一致的用户体验 |
| ThinkingBlock | **方案 A: 默认全部折叠，仅显示步骤数** | 节省屏幕空间，用户主动触发查看 |
| ToolGroup | **方案 B: 内联折叠卡片** | 平衡空间与工具调用透明度 |
| ChatInput | **多行 TextInput + 发送按钮** | 符合移动端习惯 |
| 技术策略 | **Web 逻辑复用 + RN UI 重写** | 开发效率优先 |
| 助手头像 | `mobile/src/assets/csu-xiaotuanzi-answer.png` | 提供视觉引导和品牌一致性 |

---

## 组件架构

```
ChatScreen
├── EmptyState (无消息时)
│   └── 品牌展示 + 功能引导
│
└── (有消息时)
    ├── MessageList (FlatList + 自动滚动)
    │   └── MessageBubble (per message)
    │       ├── [头像] (仅助手消息显示)
    │       ├── ThinkingBlock (默认折叠，可展开全部)
    │       ├── [Markdown 内容]
    │       └── ToolGroup (内联折叠卡片)
    │
    └── ChatInput (fixed bottom, 多行 TextInput)
```

---

## 组件详细设计

### 1. ChatScreen

**位置**: `mobile/src/screens/ChatsScreen.tsx`

**职责**:
- 组合 MessageList + ChatInput
- 管理屏幕布局（SafeAreaView + KeyboardAvoidingView）
- 处理键盘弹出时的布局调整

### 2. ChatStore

**位置**: `mobile/src/features/chat/chatStore.ts`

**策略**: 直接复用 Web 端实现

```typescript
// 核心状态
interface ChatState {
  currentDialogId: string | null;
  currentKnowledgeIds: string[];
  enableRag: boolean;
  messages: ChatMessage[];
  isStreaming: boolean;
  toolEvents: ToolEvent[];
  dialogs: Dialog[];
}
```

### 3. useChatStream

**位置**: `mobile/src/features/chat/useChatStream.ts`

**策略**: 直接复用 Web 端实现，需适配 RN 的 SSE 处理

### 4. MessageBubble

**位置**: `mobile/src/components/chat/MessageBubble/MessageBubble.tsx`

**Props**:
```typescript
interface MessageBubbleProps {
  message: ChatMessage;
}
```

**样式**:
- 用户消息: 右对齐，背景 `colors.userBg`，圆角 16px
- 助手消息: 左对齐，背景 `colors.backgroundCard`，包含头像
- 助手头像: `csu-xiaotuanzi-answer.png`，尺寸 36x36，圆角 18px

### 5. ThinkingBlock

**位置**: `mobile/src/components/chat/ThinkingBlock/ThinkingBlock.tsx`

**策略**: **方案 A - 默认全部折叠**

- 初始状态: 仅显示 "🧠 AI 思考过程 (N步)" 单行提示
- 用户点击: 展开全部思考步骤列表
- 再次点击: 收起全部

### 6. ToolGroup

**位置**: `mobile/src/components/chat/ToolGroup/ToolGroup.tsx`

**策略**: **方案 B - 内联折叠卡片**

- 初始状态: 显示 "✓ 调用了 N 个工具" 或 "正在调用工具 (X/Y)..."
- 点击展开: 显示每个工具的状态、输入输出
- 状态图标: ✓ 成功，✗ 失败，○ 进行中

### 7. ChatInput

**位置**: `mobile/src/components/chat/ChatInput/ChatInput.tsx`

**样式**:
- 多行 TextInput，支持自动增长
- 右侧发送按钮（有内容时显示）
- placeholder: "输入消息..." / "等待回复中..." (流式中)

### 8. MessageList

**位置**: `mobile/src/components/chat/MessageList/MessageList.tsx`

**职责**:
- FlatList 渲染消息
- 自动滚动到底部（新消息或流式更新）
- `onContentSizeChange` + `scrollToEnd` 实现

### 9. EmptyState

**位置**: `mobile/src/components/chat/EmptyState/EmptyState.tsx`

**内容**:
- 助手头像 (csu-xiaotuanzi-answer.png)
- 标题: "CampusMind"
- 副标题: "你的智能校园助手"
- 功能引导列表

---

## API 层设计

### chat.ts (RN 专用)

由于 RN 不支持 `ReadableStream`，需要使用 `fetch` + `EventSource` 或原生流处理:

```typescript
// mobile/src/api/chat.ts
export interface ChatStreamOptions {
  dialogId?: string;
  knowledgeIds: string[];
  enableRag?: boolean;
}

export function createChatStream(
  message: string,
  options: ChatStreamOptions,
  onChunk: (event: SSEEvent) => void,
  onNewDialog?: (dialogId: string) => void
): { abort: () => void }
```

---

## 文件结构

```
mobile/src/
├── features/chat/
│   ├── chatStore.ts          # 直接复用 Web 端
│   ├── useChatStream.ts      # 直接复用 Web 端
│   └── api/
│       └── chat.ts           # RN 专用 SSE 处理
│
├── components/chat/
│   ├── MessageBubble/
│   │   ├── MessageBubble.tsx
│   │   ├── MessageBubble.test.tsx
│   │   └── index.ts
│   ├── MessageList/
│   │   ├── MessageList.tsx
│   │   ├── MessageList.test.tsx
│   │   └── index.ts
│   ├── ChatInput/
│   │   ├── ChatInput.tsx
│   │   ├── ChatInput.test.tsx
│   │   └── index.ts
│   ├── ThinkingBlock/
│   │   ├── ThinkingBlock.tsx
│   │   ├── ThinkingBlock.test.tsx
│   │   └── index.ts
│   ├── ToolGroup/
│   │   ├── ToolGroup.tsx
│   │   ├── ToolGroup.test.tsx
│   │   └── index.ts
│   └── EmptyState/
│       ├── EmptyState.tsx
│       ├── EmptyState.test.tsx
│       └── index.ts
│
└── screens/
    └── ChatsScreen.tsx
```

---

## 依赖安装

```bash
cd mobile
npm install react-native-markdown-display react-native-syntax-highlighter
```

---

## 实现顺序

1. **ChatStore** - 核心状态管理
2. **useChatStream** - 流式处理 Hook
3. **MessageBubble** - 消息气泡组件
4. **ThinkingBlock** - 思考过程组件
5. **ToolGroup** - 工具调用组件
6. **EmptyState** - 空状态组件
7. **MessageList** - 消息列表容器
8. **ChatInput** - 输入框组件
9. **ChatsScreen** - 完整页面组合
10. **TabNavigator 集成** - 替换占位组件

---

## 设计原则

1. **移动优先**: 优先考虑小屏空间利用，采用折叠/展开策略
2. **品牌一致**: 助手头像使用项目品牌素材
3. **交互直观**: 点击区域足够大，状态反馈清晰
4. **性能优先**: 使用 FlatList 避免大列表性能问题
