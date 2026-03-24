# Frontend Style Redesign Design

**Date:** 2026-03-22
**Status:** Approved
**Theme:** Warm Paper (蓝灰色调)

---

## Overview

将前端样式从 Warm Cream + Terracotta 主题全面升级为 Warm Paper 蓝灰色调，遵循 AI Agent 跨端设计系统模板的最佳实践。

---

## Phase 1: 核心色彩系统

**File:** `src/styles/tokens/colors.css`

### 色板变更

| Token | 当前值 | 新值 |
|-------|--------|------|
| `--bg` | `#F4F3EE` | `#F8F5ED` |
| `--bg-card` | `#FAF9F5` | `#FCFAF5` |
| `--bg-glass` | `rgba(244,243,238,0.92)` | `rgba(250,248,242,0.92)` |
| `--accent` | `#B5846E` | `#537D96` |
| `--accent-hover` | `#A27460` | `#456A80` |
| `--accent-light` | `rgba(181,132,110,0.08)` | `rgba(83,125,150,0.08)` |
| `--text` | `#2D2B28` | `#3B3D3F` |
| `--text-light` | `#6B6864` | `#6B6F73` |
| `--text-muted` | `#9B9793` | `#8E9196` |
| `--border` | `rgba(177,173,161,0.28)` | `rgba(83,125,150,0.22)` |
| `--shadow` | `rgba(45,43,40,0.07)` | `rgba(59,61,63,0.09)` |
| `--sidebar-bg` | `#EDEAE2` | `#F4F2EA` |
| `--coral` | `#C4917E` | `#EC8F8D` |

### 语义色别名

保持现有 `--color-*` 别名体系不变，只更新底层变量值。

---

## Phase 2: 动画曲线与圆角体系

**File:** `src/styles/tokens/elevation.css`

### 过渡动画

| Token | 当前值 | 新值 |
|-------|--------|------|
| `--ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | `cubic-bezier(0.16, 1, 0.3, 1)` |
| `--ease-spring` | (无) | `cubic-bezier(0.16, 1, 0.3, 1)` |

### 圆角体系

| Token | 当前值 | 新值 |
|-------|--------|------|
| `--radius-sm` | `6px` | `6px` (不变) |
| `--radius-md` | `8px` | `10px` |
| `--radius-lg` | `12px` | `16px` |
| `--radius-xl` | `16px` | `18px` |

### 阴影系统

- 弃用硬阴影，改用弥散阴影 `box-shadow: 0 4px 24px var(--shadow)`
- 新增 `--shadow-glass: 0 8px 32px var(--shadow)`

---

## Phase 3: 核心组件样式

### 3.1 Sidebar 会话条目

**File:** `src/components/layout/Sidebar/Sidebar.css`

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
```

### 3.2 ChatInput 输入框

**File:** `src/components/chat/ChatInput/ChatInput.css`

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

### 3.3 MessageBubble

**File:** `src/components/chat/MessageBubble/MessageBubble.css`

- **User**: `--user-bg: rgba(83,125,150,0.08)` + 深色文字，无边框
- **Assistant**: 白底（`--bg-card`）或透明底

### 3.4 Thinking Block（新增）

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

### 3.5 Tool Group（新增）

```css
.tool-group {
  background: var(--tool-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
}
```

---

## Implementation Order

1. **Phase 1:** 更新 `colors.css` 核心色板
2. **Phase 2:** 更新 `elevation.css` 圆角和动画曲线
3. **Phase 3:** 逐个升级组件样式 + 新增 Thinking Block / Tool Group 组件

---

## Success Criteria

- [ ] 所有 CSS Variables 正确引用新色板
- [ ] 动画过渡平滑，使用弹簧曲线
- [ ] 组件圆角统一协调
- [ ] 移动端适配保持一致
- [ ] 无视觉回归问题
