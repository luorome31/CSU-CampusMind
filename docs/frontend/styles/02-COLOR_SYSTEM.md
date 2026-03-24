# 颜色系统文档

> 本文档详细说明 CampusMind Design System 的颜色系统，包括色彩理论、使用规范、搭配建议以及无障碍要求。

---

## 1. 设计理念

### 1.1 色彩哲学

CampusMind 采用 **Warm Paper + Blue-Grey Accent**（暖纸蓝灰）色彩哲学：

- **暖奶油底**：避免冷色调和纯白，采用暖奶油色 `#F8F5ED` 作为基调
- **低对比度和谐**：告别刺眼的纯白（`#FFFFFF`）和死黑（`#000000`），采用柔和的纸张底色和灰阶文字
- **蓝灰 accent**：强调色使用低饱和度的蓝灰色 `#537D96`，而非高饱和度的鲜艳色彩
- **触感深度**：使用高透明度的弥散阴影，以及低对比度的极细边框，界面层级清晰又不生硬

### 1.2 色彩关键词

```
温暖 (Warm) + 克制 (Restrained) + 自然 (Natural) + 专业 (Professional)
```

### 1.3 灵感来源

- Claude Desktop 的精致温暖配色
- 高端学术期刊排版的温润色调
- 传统造纸工艺的质感

---

## 2. 色彩结构

### 2.1 色彩层级图

```
┌─────────────────────────────────────────────────────────┐
│                    背景层 (Background)                   │
│  ┌─────────────────────────────────────────────────┐    │
│  │  #F8F5ED (bg) - 页面主背景 暖奶油               │    │
│  │  ┌─────────────────────────────────────────┐  │    │
│  │  │ #FCFAF5 (bg-card) - 卡片背景            │  │    │
│  │  │ rgba(250,248,242,0.92) (bg-glass)      │  │    │
│  │  │  - 玻璃态效果                           │  │    │
│  │  │  ┌─────────────────────────────────┐  │  │    │
│  │  │  │ #E8E5DD (bg-inset)              │  │  │    │
│  │  │  │  - 输入框、凹陷元素               │  │  │    │
│  │  │  └─────────────────────────────────┘  │  │    │
│  │  └─────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│                    文本层 (Text)                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  #3B3D3F (text) - 主要文本        ✓ AAA        │    │
│  │  #6B6F73 (text-light) - 次要文本  ✓ AA         │    │
│  │  #8E9196 (text-muted) - 辅助文本              │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│                    强调层 (Accent)                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │  #537D96 (accent) - 蓝灰色                     │    │
│  │  #456A80 (accent-hover) - hover 状态           │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 色彩角色

| 角色 | 色值 | 用途 | 使用频率 |
|------|------|------|----------|
| **Background** | `#F8F5ED` | 页面背景 | 高 |
| **Card** | `#FCFAF5` | 卡片表面 | 高 |
| **Text Primary** | `#3B3D3F` | 标题、主要文字 | 高 |
| **Text Secondary** | `#6B6F73` | 正文、说明文字 | 高 |
| **Text Muted** | `#8E9196` | 占位符、提示 | 中 |
| **Accent** | `#537D96` | 链接、选中态、图标 | 中 |
| **Accent Hover** | `#456A80` | 交互 hover 状态 | 中 |

---

## 3. 功能色定义

### 3.1 语义色彩

| 语义 | 色值 | 使用场景 | 对比度 |
|------|------|----------|--------|
| **Success** | `#1a7f37` | 成功提示、操作完成 | ✓ AA |
| **Error** | `#cf222e` | 错误提示、危险操作 | ✓ AA |
| **Warning** | `#d29922` | 警告提示、注意事项 | ✓ AA |
| **Info** | `#0969da` | 信息提示、引导操作 | ✓ AA |

### 3.2 语义色使用规范

```css
/* ✓ 正确示例 */
.success-message {
  color: var(--color-success);
  background-color: var(--color-success-bg);
  border: 1px solid var(--color-success-border);
}

.error-message {
  color: var(--color-error);
  background-color: var(--color-error-bg);
  border: 1px solid var(--color-error-border);
}

/* ✗ 错误示例：不应使用语义色进行纯装饰 */
.decorative-border {
  border-color: var(--color-success); /* 语义色不应滥用 */
}
```

### 3.3 状态色变化

| 状态 | Success | Error | Warning | Info |
|------|---------|--------|---------|------|
| **Default** | `#1a7f37` | `#cf222e` | `#d29922` | `#0969da` |
| **Hover** | `#16832d` | `#b81e2a` | `#bc8b1e` | `#0856b8` |
| **Active** | `#116227` | `#a11a24` | `#a87a1a` | `#074da6` |
| **Disabled** | `#1a7f37` @ 50% | `#cf222e` @ 50% | `#d29922` @ 50% | `#0969da` @ 50% |
| **Background** | `rgba(26,127,55,0.1)` | `rgba(207,34,46,0.1)` | `rgba(210,153,34,0.1)` | `rgba(9,105,218,0.1)` |

---

## 4. 透明度系统

### 4.1 透明度刻度

CampusMind 使用一致的透明度级别：

| 级别 | 值 | 用途 |
|------|-----|------|
| **High** | `0.9+` | 不透明元素 |
| **Medium** | `0.7 - 0.85` | 表面、覆盖层 |
| **Low** | `0.5 - 0.7` | 边框、次要元素 |
| **Subtle** | `0.2 - 0.4` | 背景装饰 |
| **Ghost** | `0.1 - 0.2` | 悬停效果 |

### 4.2 透明度使用场景

```css
/* 高透明度 - 固体表面 */
.solid-surface {
  background-color: rgba(255, 255, 255, 0.92);
}

/* 中透明度 - 玻璃态卡片 */
.glass-card {
  background-color: rgba(244, 243, 238, 0.75);
  backdrop-filter: blur(24px);
}

/* 低透明度 - 边框 */
.subtle-border {
  border-color: rgba(177, 173, 161, 0.28);
}

/* 微妙透明度 - 悬停背景 */
.hover-effect {
  background-color: rgba(0, 0, 0, 0.035);
}
```

---

## 5. 色彩搭配规范

### 5.1 推荐搭配

| 背景色 | 适用文本色 | 对比度 | 评级 |
|--------|------------|--------|------|
| `#F8F5ED` | `#3B3D3F` | 14.2:1 | ✓✓ AAA |
| `#F8F5ED` | `#6B6F73` | 7.5:1 | ✓✓ AAA |
| `#F8F5ED` | `#8E9196` | 4.8:1 | ✓ AA |
| `#FCFAF5` | `#3B3D3F` | 16.5:1 | ✓✓ AAA |
| `#E8E5DD` | `#3B3D3F` | 13.0:1 | ✓✓ AAA |

### 5.2 禁止搭配

| 搭配 | 原因 |
|------|------|
| `#F8F5ED` + `#000000` | 过于强烈，违反温暖设计理念 |
| `#FCFAF5` + `#6B6F73` | 对比度不足 (3.0:1) |
| 任何背景 + `#537D96` | 仅适用于非正文文本 |

### 5.3 搭配示例

```css
/* ✓ 推荐：温暖自然 */
.page {
  background-color: var(--bg);
  color: var(--text);
}

/* ✓ 推荐：层次分明 */
.sidebar {
  background-color: var(--sidebar-bg);
  border-right: 1px solid var(--border);
}

/* ✓ 推荐：玻璃态效果 */
.modal-overlay {
  background-color: var(--bg-glass);
  backdrop-filter: var(--glass-blur);
}

/* ✗ 禁止：过强对比 */
.loud-contrast {
  background-color: var(--bg);
  color: #000000; /* 过于刺眼 */
}

/* ✗ 禁止：对比度不足 */
.poor-contrast {
  background-color: var(--bg);
  color: #B5846E; /* 对比度仅 2.1:1 */
}
```

---

## 6. 无障碍要求

### 6.1 WCAG 合规性

| 内容类型 | 最小对比度 | CampusMind 达标 |
|----------|------------|-----------------|
| 普通文本 | 4.5:1 (AA) | ✓ 所有主要文本均达标 |
| 大文本 (≥18px 或 14px bold) | 3:1 (AA) | ✓ |
| UI 组件和图形对象 | 3:1 (AA) | ✓ |
| 增强对比度 (AAA) | 7:1 | ✓ 主要文本达标 |

### 6.2 聚焦状态

所有交互元素必须具有明显的聚焦状态：

```css
/* ✓ 正确：具有清晰的聚焦指示 */
.button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

/* ✓ 输入框聚焦状态 */
.input:focus {
  border-color: var(--accent);
  box-shadow: var(--shadow-inset-focus);
}

/* ✗ 错误：移除默认聚焦环 */
.button:focus {
  outline: none; /* 无障碍违规 */
}
```

### 6.3 色彩盲友好

CampusMind 不依赖颜色作为唯一信息载体：

```css
/* ✓ 正确：颜色 + 图案/文字 */
.validation-success {
  color: var(--color-success);
  /* 添加图标而非仅依赖颜色 */
}

.validation-success::before {
  content: "✓ ";
}

/* ✗ 错误：仅用颜色区分 */
.status-success { background: green; }
.status-error { background: red; }
/* 色盲用户无法区分 */
```

---

## 7. 聊天专用色彩

### 7.1 心情/Mood 色彩

| 变量 | 色值 | 用途 |
|------|------|------|
| `--assistant-text` | `#2D2B28` | AI 助手文字 |
| `--mood-bg` | `rgba(83, 125, 150, 0.05)` | 心情背景 |
| `--mood-text` | `#537D96` | 心情文字 |
| `--mood-border` | `rgba(83, 125, 150, 0.16)` | 心情边框 |

### 7.2 工具调用卡片

| 变量 | 色值 | 用途 |
|------|------|------|
| `--tool-bg` | `rgba(83, 125, 150, 0.06)` | 工具卡片背景 |
| `--tool-text` | `#6B6F73` | 工具卡片文字 |

### 7.3 用户消息

| 变量 | 色值 | 用途 |
|------|------|------|
| `--user-bg` | `rgba(83, 125, 150, 0.08)` | 用户消息背景 |

---

## 8. 色彩在代码中的使用

### 8.1 CSS 变量使用规范

```css
/* ✓ 始终使用 CSS 变量 */
.component {
  color: var(--text);
  background-color: var(--bg-card);
  border-color: var(--border);
}

/* ✗ 禁止硬编码颜色 */
.component {
  color: #2D2B28; /* 硬编码 */
  background-color: #FAF9F5; /* 硬编码 */
}
```

### 8.2 JavaScript 中使用

```typescript
// ✓ 正确：从设计系统获取颜色
const styles = {
  backgroundColor: 'var(--bg-card)',
  color: 'var(--text)',
};

// ✗ 错误：硬编码
const styles = {
  backgroundColor: '#FAF9F5',
  color: '#2D2B28',
};
```

---

## 9. 调色板快速参考

```
┌─────────────────────────────────────────────────────────────────┐
│                    CampusMind Color Palette                      │
│                   Warm Cream + Blue-Grey Accent                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Background          Text               Accent                   │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐             │
│  │ #F8F5ED │       │ #3B3D3F │       │ #537D96 │             │
│  │   bg    │       │  text   │       │ accent  │             │
│  └─────────┘       └─────────┘       └─────────┘             │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐             │
│  │ #FCFAF5 │       │ #6B6F73 │       │ #456A80 │             │
│  │ bg-card │       │text-light│       │accent-hov│            │
│  └─────────┘       └─────────┘       └─────────┘             │
│  ┌─────────┐       ┌─────────┐                               │
│  │ #E8E5DD │       │ #8E9196 │                               │
│  │ bg-inset│       │text-muted│                              │
│  └─────────┘       └─────────┘                               │
│                                                                 │
│  Sidebar              Status                                  │
│  ┌─────────┐       ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │ #F4F2EA │       │ #1a7f37 │ │ #cf222e │ │ #d29922 │      │
│  │sidebar-bg│      │ success │ │  error  │ │ warning │      │
│  └─────────┘       └─────────┘ └─────────┘ └─────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
