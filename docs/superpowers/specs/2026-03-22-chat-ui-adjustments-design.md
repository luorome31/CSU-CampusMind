# Chat UI Adjustments Design

## Date: 2026-03-22

## Overview

对 Chat 界面进行 7 项 UI 调整，涉及对话页面、侧边栏和消息气泡的样式优化。

---

## 1. 移除知识库选择组件

**File**: `frontend/src/features/chat/ChatPage.tsx`

**Change**:
- 移除 `<KnowledgeSelector knowledgeBases={MOCK_KNOWLEDGE_BASES} />` 组件的渲染
- 保留 `KnowledgeSelector` 组件文件，便于后期在知识库页面复用

---

## 2. 侧边栏宽度和字体调整

**File**: `frontend/src/components/layout/Sidebar/Sidebar.css`

**Changes**:
| Property | Before | After |
|----------|--------|-------|
| `--sidebar-width` | 260px | 300px |
| `.sidebar-nav-item font-size` | `var(--text-sm)` (14px) | `var(--text-base)` (16px) |
| `.sidebar-nav-item font-weight` | `var(--font-medium)` (500) | `var(--font-semibold)` (600) |

---

## 3. Assistant 消息气泡宽度调整

**File**: `frontend/src/components/chat/MessageBubble/MessageBubble.css`

**Change**:
- `.message-assistant .message-content`: `width: 100%` → `width: fit-content`
- 保持 `max-width: 70ch` 限制

---

## 4. 输入框长度调整

**File**: `frontend/src/components/chat/ChatInput/ChatInput.css`

**Change**:
- `.chat-input-form` 添加左右 padding 或设置 `.chat-input-wrapper` 的 `max-width: 66.67%`

---

## 5. 输入框移除填充色

**File**: `frontend/src/components/chat/ChatInput/ChatInput.css`

**Change**:
- `.chat-input`: `background: var(--color-bg-inset)` → `background: transparent`

---

## 6. Assistant 消息气泡背景透明

**File**: `frontend/src/components/chat/MessageBubble/MessageBubble.css`

**Change**:
- `.message-assistant .message-content`: `background: var(--color-bg-surface)` → `background: transparent`

---

## 7. Assistant 消息气泡添加圆形 Icon

**File**: `frontend/src/components/chat/MessageBubble/index.tsx` & `MessageBubble.css`

**Change**:
- 为 assistant 消息添加 avatar 区域（圆形容器 + icon）
- 支持可扩展性：通过配置或 props 便于后期替换为图片
- 使用 lucide-react 的 Bot icon 或类似的通用图标

---

## Testing

验证清单：
- [ ] ChatPage 不再显示 KnowledgeSelector
- [ ] 侧边栏宽度增加，字体变大变粗
- [ ] Assistant 消息气泡不再撑满宽度
- [ ] 输入框长度约为屏幕的 2/3
- [ ] 输入框无填充色背景
- [ ] Assistant 消息气泡背景透明
- [ ] Assistant 消息气泡左侧有圆形 icon
