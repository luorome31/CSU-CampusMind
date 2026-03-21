# 颜色系统文档

> 本文档详细说明 CampusMind Design System 的颜色系统，包括色彩理论、使用规范、搭配建议以及无障碍要求。

---

## 1. 设计理念

### 1.1 色彩哲学

CampusMind 采用 **Warm Minimal**（温暖极简）色彩哲学：

- **温暖导向**：避免冷色调和纯白，采用米色、暖灰作为基调
- **克制强调**：强调色使用低饱和度的蓝灰色，而非高饱和度的鲜艳色彩
- **自然过渡**：色彩之间通过微妙的透明度变化实现层级区分

### 1.2 色彩关键词

```
可信赖 (Trustworthy) + 精致 (Refined) + 温和 (Approachable)
```

### 1.3 灵感来源

- 高端学术期刊排版
- 传统造纸工艺的质感
- 古典实验室器皿的温润色调

---

## 2. 色彩结构

### 2.1 色彩层级图

```
┌─────────────────────────────────────────────────────────┐
│                    背景层 (Background)                   │
│  ┌─────────────────────────────────────────────────┐    │
│  │  #f7f2ea (bg-base) - 页面主背景                  │    │
│  │  ┌─────────────────────────────────────────┐  │    │
│  │  │ rgba(255,255,255,0.82) (bg-surface)   │  │    │
│  │  │  - 卡片、面板                              │  │    │
│  │  │  ┌─────────────────────────────────┐  │  │    │
│  │  │  │ #eee6dc (bg-inset)              │  │  │    │
│  │  │  │  - 输入框、凹陷元素                 │  │  │    │
│  │  │  └─────────────────────────────────┘  │  │    │
│  │  └─────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│                    文本层 (Text)                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  #2d2a26 (text-primary) - 主要文本  ✓ AA       │    │
│  │  #5d5a55 (text-secondary) - 次要文本  ✓ AA      │    │
│  │  #7e8b97 (text-tertiary) - 辅助文本            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│                    强调层 (Accent)                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │  #9fb1c2 (accent) - 主强调色                   │    │
│  │  #c7ad96 (accent-light) - 暖色强调              │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 色彩角色

| 角色 | 色值 | 用途 | 使用频率 |
|------|------|------|----------|
| **Primary** | `#2d2a26` | 标题、主要文字 | 高 |
| **Secondary** | `#5d5a55` | 正文、说明文字 | 高 |
| **Tertiary** | `#7e8b97` | 占位符、提示 | 中 |
| **Accent** | `#9fb1c2` | 链接、选中态、图标 | 中 |
| **Warm Accent** | `#c7ad96` | 装饰性强调 | 低 |
| **Background** | `#f7f2ea` | 页面背景 | 高 |

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
  background-color: rgba(26, 127, 55, 0.1);
  border: 1px solid rgba(26, 127, 55, 0.2);
}

.error-message {
  color: var(--color-error);
  background-color: rgba(207, 34, 46, 0.1);
  border: 1px solid rgba(207, 34, 46, 0.2);
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
  background-color: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(24px);
}

/* 低透明度 - 边框 */
.subtle-border {
  border-color: rgba(45, 42, 38, 0.12);
}

/* 微妙透明度 - 悬停背景 */
.hover-effect {
  background-color: rgba(0, 0, 0, 0.04);
}
```

---

## 5. 色彩搭配规范

### 5.1 推荐搭配

| 背景色 | 适用文本色 | 对比度 | 评级 |
|--------|------------|--------|------|
| `#f7f2ea` | `#2d2a26` | 13.8:1 | ✓✓ AAA |
| `#f7f2ea` | `#5d5a55` | 7.2:1 | ✓✓ AAA |
| `#f7f2ea` | `#7e8b97` | 4.5:1 | ✓ AA |
| `#ffffff` | `#2d2a26` | 16.1:1 | ✓✓ AAA |
| `#eee6dc` | `#2d2a26` | 12.4:1 | ✓✓ AAA |

### 5.2 禁止搭配

| 搭配 | 原因 |
|------|------|
| `#f7f2ea` + `#000000` | 过于强烈，违反温暖设计理念 |
| `#ffffff` + `#5d5a55` | 对比度不足 (2.8:1) |
| 任何背景 + `#9fb1c2` | 仅适用于非正文文本 |

### 5.3 搭配示例

```css
/* ✓ 推荐：温暖自然 */
.page {
  background-color: var(--color-bg-base);
  color: var(--color-text-primary);
}

/* ✓ 推荐：层次分明 */
.sidebar {
  background-color: var(--color-bg-surface);
  border-right: 1px solid var(--color-border);
}

/* ✓ 推荐：玻璃态效果 */
.modal-overlay {
  background-color: var(--color-bg-overlay);
  backdrop-filter: var(--glass-blur);
}

/* ✗ 禁止：过强对比 */
.loud-contrast {
  background-color: #f7f2ea;
  color: #000000; /* 过于刺眼 */
}

/* ✗ 禁止：对比度不足 */
.poor-contrast {
  background-color: #f7f2ea;
  color: #9fb1c2; /* 对比度仅 2.1:1 */
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
| 增强对比度 (AAA) | 7:1 | ⚠️ 部分次要文本略低 |

### 6.2 聚焦状态

所有交互元素必须具有明显的聚焦状态：

```css
/* ✓ 正确：具有清晰的聚焦指示 */
.button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* ✓ 输入框聚焦状态 */
.input:focus {
  border-color: var(--color-accent);
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

## 7. 暗色模式准备

> 当前版本主要面向亮色模式，暗色模式预留接口。

### 7.2 暗色模式变量（预留）

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* 预留变量 - 待后续实现 */
    /* --color-bg-base-dark: #1a1915; */
    /* --color-text-primary-dark: #e8e6e3; */
  }
}
```

---

## 8. 色彩在代码中的使用

### 8.1 CSS 变量使用规范

```css
/* ✓ 始终使用 CSS 变量 */
.component {
  color: var(--color-text-primary);
  background-color: var(--color-bg-surface);
  border-color: var(--color-border);
}

/* ✗ 禁止硬编码颜色 */
.component {
  color: #2d2a26; /* 硬编码 */
  background-color: #f7f2ea; /* 硬编码 */
}
```

### 8.2 JavaScript 中使用

```typescript
// ✓ 正确：从设计系统获取颜色
const styles = {
  backgroundColor: 'var(--color-bg-surface)',
  color: 'var(--color-text-primary)',
};

// ✗ 错误：硬编码
const styles = {
  backgroundColor: 'rgba(255, 255, 255, 0.82)',
  color: '#2d2a26',
};
```

---

## 9. 调色板快速参考

```
┌─────────────────────────────────────────────────────────────────┐
│                      CampusMind Color Palette                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Background          Text               Accent                   │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐             │
│  │ #f7f2ea │       │ #2d2a26 │       │ #9fb1c2 │             │
│  │  base   │       │ primary  │       │ accent   │             │
│  └─────────┘       └─────────┘       └─────────┘             │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐             │
│  │ rgba()  │       │ #5d5a55 │       │ #c7ad96 │             │
│  │ surface  │       │secondary │       │ warm    │             │
│  └─────────┘       └─────────┘       └─────────┘             │
│  ┌─────────┐       ┌─────────┐                               │
│  │ #eee6dc │       │ #7e8b97 │                               │
│  │ inset   │       │tertiary │                               │
│  └─────────┘       └─────────┘                               │
│                                                                 │
│  Semantic                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│  │ #1a7f37 │ │ #cf222e │ │ #d29922 │ │ #0969da │            │
│  │ success │ │  error  │ │ warning │ │  info   │            │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
