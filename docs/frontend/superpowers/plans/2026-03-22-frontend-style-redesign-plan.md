# Frontend Style Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将前端样式从 Warm Cream + Terracotta 升级为 Warm Paper 蓝灰色调主题

**Architecture:** 分三个 Phase 安全替换：1) 色彩系统 2) 动画与圆角 3) 组件样式。遵循 TDD 流程，每个 Phase 完成后验证无视觉回归。

**Tech Stack:** CSS Variables, CSS Transitions

---

## File Structure

```
frontend/src/
├── styles/tokens/
│   ├── colors.css      # Phase 1: 核心色板替换
│   └── elevation.css   # Phase 2: 圆角与动画曲线
├── components/
│   ├── layout/Sidebar/Sidebar.css  # Phase 3: Sidebar 样式
│   ├── chat/
│   │   ├── ChatInput/ChatInput.css    # Phase 3: 输入框样式
│   │   ├── MessageBubble/MessageBubble.css  # Phase 3: 消息气泡
│   │   └── ThinkingBlock/            # Phase 3: 新增 Thinking Block
│   │       ├── ThinkingBlock.css
│   │       └── index.tsx
│   └── chat/ToolGroup/               # Phase 3: 新增 Tool Group
│       ├── ToolGroup.css
│       └── index.tsx
└── index.css  # 全局样式入口
```

---

## Chunk 1: Phase 1 - 核心色彩系统

**Files:**
- Modify: `frontend/src/styles/tokens/colors.css`

- [ ] **Step 1: 备份当前 colors.css**

```bash
cp frontend/src/styles/tokens/colors.css frontend/src/styles/tokens/colors.css.bak
```

- [ ] **Step 2: 更新 colors.css 核心色板**

按照下表替换 `--bg` 到 `--coral` 的值：

```css
/* 将以下值替换为新值 */
--bg:           #F8F5ED;  /* 原 #F4F3EE */
--bg-card:      #FCFAF5;  /* 原 #FAF9F5 */
--bg-glass:     rgba(250, 248, 242, 0.92);  /* 原 rgba(244,243,238,0.92) */
--accent:       #537D96;  /* 原 #B5846E */
--accent-hover: #456A80;  /* 原 #A27460 */
--accent-light: rgba(83, 125, 150, 0.08);  /* 原 rgba(181,132,110,0.08) */
--text:         #3B3D3F;  /* 原 #2D2B28 */
--text-light:   #6B6F73;  /* 原 #6B6864 */
--text-muted:   #8E9196;  /* 原 #9B9793 */
--border:       rgba(83, 125, 150, 0.22);  /* 原 rgba(177,173,161,0.28) */
--shadow:       rgba(59, 61, 63, 0.09);  /* 原 rgba(45,43,40,0.07) */
--sidebar-bg:   #F4F2EA;  /* 原 #EDEAE2 */
--coral:        #EC8F8D;  /* 原 #C4917E */
```

- [ ] **Step 3: 验证颜色替换正确性**

Run: `grep -E "^[[:space:]]*--[a-z-]+:.*#" frontend/src/styles/tokens/colors.css`
Expected: 列出所有颜色变量，确认新值已生效

- [ ] **Step 4: 提交 Phase 1**

```bash
git add frontend/src/styles/tokens/colors.css
git commit -m "style(colors): 应用 Warm Paper 蓝灰色调主题 Phase 1"
```

---

## Chunk 2: Phase 2 - 动画曲线与圆角体系

**Files:**
- Modify: `frontend/src/styles/tokens/elevation.css`

- [ ] **Step 1: 备份当前 elevation.css**

```bash
cp frontend/src/styles/tokens/elevation.css frontend/src/styles/tokens/elevation.css.bak
```

- [ ] **Step 2: 更新 elevation.css**

替换现有值：

```css
/* 替换 --ease-default */
--ease-default: cubic-bezier(0.16, 1, 0.3, 1);

/* 添加 --ease-spring */
--ease-spring: cubic-bezier(0.16, 1, 0.3, 1);

/* 更新圆角 */
--radius-md: 10px;  /* 原 8px */
--radius-lg: 16px;  /* 原 12px */
--radius-xl: 18px;  /* 原 16px */
```

- [ ] **Step 3: 验证修改**

Run: `grep -E "^[[:space:]]*--(radius|ease)" frontend/src/styles/tokens/elevation.css`
Expected: 显示新的圆角和动画曲线值

- [ ] **Step 4: 提交 Phase 2**

```bash
git add frontend/src/styles/tokens/elevation.css
git commit -m "style(elevation): 应用弹簧曲线和圆角升级 Phase 2"
```

---

## Chunk 3: Phase 3.1 - Sidebar 组件样式

**Files:**
- Modify: `frontend/src/components/layout/Sidebar/Sidebar.css`

- [ ] **Step 1: 读取当前 Sidebar.css**

- [ ] **Step 2: 更新 .session-item 样式**

替换现有的 `.session-item` 相关样式为：

```css
.session-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  transition: background-color var(--ease-spring) 0.2s;
  cursor: pointer;
  border: none;
  background: transparent;
}
.session-item:hover {
  background-color: var(--overlay-light, rgba(0,0,0,0.05));
}
.session-item:active {
  background-color: var(--overlay-medium, rgba(0,0,0,0.08));
}
.session-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}
.session-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.session-item-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.session-item-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

- [ ] **Step 3: 验证 Sidebar 渲染**

Run dev server and visually verify sidebar styling.

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/layout/Sidebar/Sidebar.css
git commit -m "style(sidebar): 应用 session-item 样式升级 Phase 3.1"
```

---

## Chunk 4: Phase 3.2 - ChatInput 输入框样式

**Files:**
- Modify: `frontend/src/components/chat/ChatInput/ChatInput.css`

- [ ] **Step 1: 读取当前 ChatInput.css**

- [ ] **Step 2: 更新样式**

将 `.input-wrapper` 样式替换为：

```css
.input-wrapper {
  background: var(--bg-card);
  border: 1px solid var(--border);
  box-shadow: 0 4px 16px var(--shadow);
  border-radius: 16px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all var(--ease-spring) 0.3s;
}
```

- [ ] **Step 3: 验证输入框渲染**

Run dev server and verify input field styling.

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/chat/ChatInput/ChatInput.css
git commit -m "style(chatinput): 应用输入框样式升级 Phase 3.2"
```

---

## Chunk 5: Phase 3.3 - MessageBubble 消息气泡

**Files:**
- Modify: `frontend/src/components/chat/MessageBubble/MessageBubble.css`

- [ ] **Step 1: 读取当前 MessageBubble.css**

- [ ] **Step 2: 更新用户消息样式**

将 `.message-user .message-content` 样式更新为：

```css
.message-user .message-content {
  background: rgba(83, 125, 150, 0.08);
  color: var(--text);
  border-bottom-right-radius: var(--radius-sm);
}
```

- [ ] **Step 3: 验证消息气泡渲染**

Run dev server and verify message bubble styling.

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/chat/MessageBubble/MessageBubble.css
git commit -m "style(messagebubble): 应用消息气泡样式升级 Phase 3.3"
```

---

## Chunk 6: Phase 3.4 - 新增 Thinking Block 组件

**Files:**
- Create: `frontend/src/components/chat/ThinkingBlock/ThinkingBlock.css`
- Create: `frontend/src/components/chat/ThinkingBlock/index.tsx`

- [ ] **Step 1: 创建 ThinkingBlock 目录和样式文件**

```bash
mkdir -p frontend/src/components/chat/ThinkingBlock
```

- [ ] **Step 2: 创建 ThinkingBlock.css**

```css
.thinking-block {
  margin: 8px 0;
  border-left: 2px solid var(--border);
  padding-left: 12px;
}

.thinking-block-summary {
  cursor: pointer;
  color: var(--text-muted);
  font-size: 0.85rem;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s;
}

.thinking-block-summary:hover {
  color: var(--text);
}

.thinking-block-body {
  color: var(--text-light);
  font-size: 0.9rem;
  margin-top: 6px;
}
```

- [ ] **Step 3: 创建 index.tsx**

```tsx
import { useState } from 'react';
import './ThinkingBlock.css';

interface ThinkingBlockProps {
  content: string;
}

export function ThinkingBlock({ content }: ThinkingBlockProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="thinking-block">
      <div
        className="thinking-block-summary"
        onClick={() => setIsExpanded(!isExpanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setIsExpanded(!isExpanded)}
      >
        <span>{isExpanded ? '▼' : '▶'}</span>
        <span>AI 思考过程</span>
      </div>
      {isExpanded && <div className="thinking-block-body">{content}</div>}
    </div>
  );
}
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/chat/ThinkingBlock/
git commit -m "feat(thinkingblock): 新增 Thinking Block 组件 Phase 3.4"
```

---

## Chunk 7: Phase 3.5 - 新增 Tool Group 组件

**Files:**
- Create: `frontend/src/components/chat/ToolGroup/ToolGroup.css`
- Create: `frontend/src/components/chat/ToolGroup/index.tsx`

- [ ] **Step 1: 创建 ToolGroup 目录和样式文件**

```bash
mkdir -p frontend/src/components/chat/ToolGroup
```

- [ ] **Step 2: 创建 ToolGroup.css**

```css
.tool-group {
  background: var(--tool-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  margin: 8px 0;
}

.tool-group-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-light);
  font-size: 0.875rem;
}

.tool-group-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}
```

- [ ] **Step 3: 创建 index.tsx**

```tsx
import { useState } from 'react';
import './ToolGroup.css';

interface Tool {
  name: string;
  status: 'running' | 'done' | 'error';
  result?: string;
}

interface ToolGroupProps {
  tools: Tool[];
}

function LoadingDots() {
  return (
    <span style={{ display: 'inline-flex', gap: '4px' }}>
      <span style={{ animation: 'bounce 1.4s infinite', animationDelay: '0s' }}>.</span>
      <span style={{ animation: 'bounce 1.4s infinite', animationDelay: '0.2s' }}>.</span>
      <span style={{ animation: 'bounce 1.4s infinite', animationDelay: '0.4s' }}>.</span>
    </span>
  );
}

export function ToolGroup({ tools }: ToolGroupProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const allDone = tools.every((t) => t.status === 'done');
  const doneCount = tools.filter((t) => t.status === 'done').length;

  return (
    <div className="tool-group">
      <div
        className="tool-group-summary"
        onClick={() => setIsExpanded(!isExpanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setIsExpanded(!isExpanded)}
      >
        {allDone ? (
          <>
            <span>✓</span>
            <span>执行完成 {tools.length} 个工具</span>
          </>
        ) : (
          <>
            <LoadingDots />
            <span>运行中 {doneCount}/{tools.length} 个工具</span>
          </>
        )}
      </div>
      {isExpanded && (
        <div className="tool-group-details">
          {tools.map((tool, i) => (
            <div key={i} style={{ fontSize: '0.8rem', marginBottom: '4px' }}>
              <span style={{ color: tool.status === 'done' ? 'var(--green)' : 'var(--coral)' }}>
                {tool.status === 'done' ? '✓' : '○'}
              </span>
              <span style={{ marginLeft: '8px' }}>{tool.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/chat/ToolGroup/
git commit -m "feat(toolgroup): 新增 Tool Group 组件 Phase 3.5"
```

---

## Chunk 8: 全局验证

- [ ] **Step 1: 启动开发服务器验证**

```bash
tmux new-session -d -s campusmind-frontend 'cd /home/luorome/software/CampusMind/frontend && npm run dev'
```

- [ ] **Step 2: 使用 Playwright MCP 验证页面渲染**

```javascript
await browser_navigate({ url: "http://localhost:5173" })
await browser_snapshot({})
```

- [ ] **Step 3: 检查控制台错误**

```javascript
await browser_console_messages({ level: "error" })
```

- [ ] **Step 4: 提交最终验证**

```bash
git add -A
git commit -m "style: 完成 Warm Paper 主题全面升级"
```

---

## Success Criteria

- [ ] Phase 1-3 所有修改已提交
- [ ] 开发服务器正常运行
- [ ] 无控制台错误
- [ ] 页面样式符合 Warm Paper 设计规范
