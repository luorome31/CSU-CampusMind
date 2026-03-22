# Chat UI Adjustments Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 对 Chat 界面进行 7 项 UI 调整（移除知识库选择、侧边栏调整、气泡样式、输入框样式）

**Architecture:** 主要涉及 CSS 样式调整和一处 JSX 组件移除。修改分散在 5 个文件中，均为样式相关改动。

**Tech Stack:** React, CSS Variables, lucide-react (Bot icon)

---

## Chunk 1: 移除知识库选择组件

### Task 1: 从 ChatPage 移除 KnowledgeSelector

**Files:**
- Modify: `frontend/src/features/chat/ChatPage.tsx:35-43`

- [ ] **Step 1: 修改 ChatPage.tsx**

移除第 39 行的 `<KnowledgeSelector knowledgeBases={MOCK_KNOWLEDGE_BASES} />` 组件渲染

```tsx
// 修改前 (第 36-44 行)
{hasMessages ? (
  <>
    <KnowledgeSelector knowledgeBases={MOCK_KNOWLEDGE_BASES} />
    <MessageList messages={messages} isStreaming={isStreaming} />
    <div className="chat-page-input-fixed">
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  </>
) : (

// 修改后
{hasMessages ? (
  <>
    <MessageList messages={messages} isStreaming={isStreaming} />
    <div className="chat-page-input-fixed">
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  </>
) : (
```

---

## Chunk 2: 侧边栏样式调整

### Task 2: 调整侧边栏宽度和字体

**Files:**
- Modify: `frontend/src/components/layout/Sidebar/Sidebar.css:1-150`

- [ ] **Step 1: 修改侧边栏宽度**

在 `.sidebar` 中将 `--sidebar-width` 从 260px 改为 300px（通过 CSS 变量覆盖）

- [ ] **Step 2: 修改字体大小**

`.sidebar-nav-item` 的 `font-size` 从 `var(--text-sm)` 改为 `var(--text-base)`

- [ ] **Step 3: 修改字体粗细**

`.sidebar-nav-item` 的 `font-weight` 从 `var(--font-medium)` 改为 `var(--font-semibold)`

---

## Chunk 3: 消息气泡样式调整

### Task 3: 调整 Assistant 气泡宽度和背景

**Files:**
- Modify: `frontend/src/components/chat/MessageBubble/MessageBubble.css:1-120`

- [ ] **Step 1: 修改 Assistant 气泡宽度**

`.message-assistant .message-content` 的 `width: 100%` 改为 `width: fit-content`

- [ ] **Step 2: 修改 Assistant 气泡背景为透明**

`.message-assistant .message-content` 的 `background: var(--color-bg-surface)` 改为 `background: transparent`

### Task 4: 为 Assistant 气泡添加圆形 Icon

**Files:**
- Modify: `frontend/src/components/chat/MessageBubble/index.tsx:1-43`
- Modify: `frontend/src/components/chat/MessageBubble/MessageBubble.css:1-120`

- [ ] **Step 1: 在 MessageBubble 中添加 Bot icon 导入**

```tsx
import { Bot } from 'lucide-react';
```

- [ ] **Step 2: 在 assistant 消息中添加 avatar 区域**

```tsx
<div className={`message-bubble message-${isUser ? 'user' : 'assistant'}`}>
  {!isUser && (
    <div className="message-avatar">
      <Bot size={20} />
    </div>
  )}
  <div className="message-content">
    ...
  </div>
</div>
```

- [ ] **Step 3: 添加 avatar 样式**

```css
.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-accent-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: var(--space-2);
}

.message-avatar svg {
  color: var(--color-accent);
}
```

---

## Chunk 4: 输入框样式调整

### Task 5: 调整输入框长度和背景

**Files:**
- Modify: `frontend/src/components/chat/ChatInput/ChatInput.css:1-51`

- [ ] **Step 1: 限制输入框长度为屏幕的 2/3**

在 `.chat-input-form` 中添加 `display: flex; justify-content: center;`

在 `.chat-input-wrapper` 中添加 `max-width: 66.67%;` 并移除原有的 `width: 100%` 相关设置

- [ ] **Step 2: 移除输入框填充色**

`.chat-input` 的 `background: var(--color-bg-inset)` 改为 `background: transparent`

---

## Verification

所有修改完成后，运行以下验证：

```bash
# 1. 启动前端开发服务器
cd /home/luorome/software/CampusMind/frontend && npm run dev

# 2. 访问 http://localhost:5173 验证：
#    - 对话页面不再显示知识库选择器
#    - 侧边栏宽度增加，字体变大变粗
#    - Assistant 消息气泡不再撑满宽度
#    - Assistant 消息气泡左侧有圆形 Bot icon
#    - Assistant 消息气泡背景透明
#    - 输入框长度约为屏幕的 2/3
#    - 输入框无填充色背景
```
