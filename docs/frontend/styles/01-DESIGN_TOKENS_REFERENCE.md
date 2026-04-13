# Design Tokens 参考文档

> Design Tokens 是设计系统中原子级别的设计决策，是 CSS 变量的语义化封装。本文档详细记录 CampusMind Design System 中所有 Token 的用途、值和使用指南。

---

## 1. 概述

### 1.1 什么是 Design Tokens

Design Tokens 是设计决策的原子单元，以 CSS 变量的形式存储。它们将设计语言翻译成开发友好的格式，实现设计与代码的同步。

### 1.2 命名规范

```
--[category]-[variant]-[state]
```

| 部分 | 说明 | 示例 |
|------|------|------|
| `category` | 类别 | `color`, `space`, `font` |
| `variant` | 变体 | `primary`, `secondary`, `accent` |
| `state` | 状态（可选） | `hover`, `active`, `disabled` |

### 1.3 Token 文件结构

```
src/styles/tokens/
├── colors.css      # 颜色系统
├── spacing.css     # 间距系统
├── typography.css  # 排版系统
└── elevation.css   # 阴影、圆角、动画
```

---

## 2. 颜色系统 (Colors)

### 2.1 背景色 (Background)

| Token | 值 | 说明 |
|-------|-----|------|
| `--bg` | `#F8F5ED` | 页面主背景色，温暖的奶油色调 |
| `--bg-card` | `#FCFAF5` | 卡片、对话气泡、弹出层底色 |
| `--bg-glass` | `rgba(250, 248, 242, 0.92)` | 毛玻璃/头部遮罩底色 |
| `--sidebar-bg` | `#F4F2EA` | 侧边栏背景，比主背景稍暗以区分 |
| `--bg-inset` | `#E8E5DD` | 凹陷元素背景色，如输入框 |

**使用场景**：

```css
/* 页面背景 */
.page {
  background-color: var(--bg);
}

/* 卡片 */
.card {
  background-color: var(--bg-card);
}

/* 玻璃态效果 */
.glass-effect {
  background-color: var(--bg-glass);
  backdrop-filter: blur(24px);
}

/* 侧边栏 */
.sidebar {
  background-color: var(--sidebar-bg);
}
```

### 2.2 文本色 (Text)

| Token | 值 | 说明 |
|-------|-----|------|
| `--text` | `#3B3D3F` | 正文高对比度文字 |
| `--text-light` | `#6B6F73` | 辅助文字/副标题 |
| `--text-muted` | `#8E9196` | 提示文本、时间戳、禁用状态 |

**对比度要求**：
- 主要文本与背景对比度 ≥ 4.5:1 (WCAG AA)
- 次要文本与背景对比度 ≥ 3:1

```css
/* 标题 */
h1, h2, h3 {
  color: var(--text);
}

/* 正文 */
p {
  color: var(--text-light);
  line-height: 1.6;
}

/* 提示文字 */
.placeholder {
  color: var(--text-muted);
}
```

### 2.3 强调色 (Accent)

| Token | 值 | 说明 |
|-------|-----|------|
| `--accent` | `#537D96` | 主强调色，蓝灰色调 |
| `--accent-hover` | `#456A80` | 悬停状态强调色 |
| `--accent-light` | `rgba(83, 125, 150, 0.08)` | 浅色强调背景 |

**使用指南**：
- `--accent` 用于链接、重点强调、可点击元素
- `--accent-light` 用于标签背景、选中态背景

```css
/* 链接 */
a {
  color: var(--accent);
}

a:hover {
  color: var(--accent-hover);
}

/* 选中标签 */
.tag-selected {
  background-color: var(--accent-light);
  color: var(--accent);
}
```

### 2.4 边框色 (Border)

| Token | 值 | 说明 |
|-------|-----|------|
| `--border` | `rgba(83, 125, 150, 0.22)` | 全局统一细边框，基于 accent 色 |
| `--shadow` | `rgba(59, 61, 63, 0.09)` | 弥散阴影色 |

```css
/* 默认边框 */
.card {
  border: 1px solid var(--border);
}

/* 悬停边框 */
.interactive:hover {
  border-color: var(--accent);
}
```

### 2.5 语义色 (Semantic)

| Token | 值 | 用途 |
|-------|-----|------|
| `--green` | `#7BAE7F` | 成功状态 |
| `--coral` | `#EC8F8D` | 醒目/警告/红色系提示 |

---

## 3. 间距系统 (Spacing)

### 3.1 基础间距刻度

| Token | 值 | 像素 | 使用场景 |
|-------|-----|------|----------|
| `--space-0` | `0` | 0px | 重置间距 |
| `--space-1` | `0.25rem` | 4px | 微间距、内联元素间隙 |
| `--space-2` | `0.5rem` | 8px | 紧凑间距、图标与文字间隙 |
| `--space-3` | `0.75rem` | 12px | 默认间距、表单项间隙 |
| `--space-4` | `1rem` | 16px | 组件内边距、段落间距 |
| `--space-5` | `1.25rem` | 20px | 中等间距 |
| `--space-6` | `1.5rem` | 24px | 组件间间距 |
| `--space-8` | `2rem` | 32px | 大间距、区域分割 |
| `--space-10` | `2.5rem` | 40px | 区块间距 |
| `--space-12` | `3rem` | 48px | 大区块间距 |
| `--space-16` | `4rem` | 64px | 页面级间距 |
| `--space-20` | `5rem` | 80px | 超大间距 |
| `--space-24` | `6rem` | 96px | 最大间距 |

### 3.2 组件专用间距

| Token | 值 | 像素 | 说明 |
|-------|-----|------|------|
| `--hit-target-min` | `2.75rem` | 44px | WCAG 最小点击区域 |
| `--input-height` | `2.75rem` | 44px | 输入框高度 |
| `--button-height-sm` | `2.25rem` | 36px | 小按钮高度 |
| `--button-height-md` | `2.75rem` | 44px | 中按钮高度 |
| `--button-height-lg` | `3rem` | 48px | 大按钮高度 |

### 3.3 容器宽度

| Token | 值 | 说明 |
|-------|-----|------|
| `--container-max` | `90vw` | 最大容器宽度（移动端） |
| `--container-max-sm` | `440px` | 小容器 |
| `--container-max-md` | `720px` | 中容器 |
| `--container-max-lg` | `1024px` | 大容器 |
| `--container-max-xl` | `1280px` | 超大容器 |

### 3.4 使用示例

```css
/* 内联元素间距 */
.icon-with-text {
  gap: var(--space-2);
}

/* 卡片内边距 */
.card {
  padding: var(--space-4);
}

/* 区块间间距 */
.section {
  margin-bottom: var(--space-8);
}

/* 确保可点击区域 */
.button {
  min-height: var(--hit-target-min);
  min-width: var(--hit-target-min);
}
```

---

## 4. 排版系统 (Typography)

### 4.1 字体族

| Token | 值 | 用途 |
|-------|-----|------|
| `--font-sans` | `"DS-Project", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` | 主字体 |
| `--font-mono` | `"IBM Plex Mono", ui-monospace, SFMono-Regular, monospace` | 代码字体 |

### 4.2 字号刻度

| Token | 值 | 说明 |
|-------|-----|------|
| `--text-xs` | `0.75rem` (12px) | 标签、徽章、辅助说明 |
| `--text-sm` | `0.875rem` (14px) | 次要文本、表格内容 |
| `--text-base` | `1rem` (16px) | 正文、默认文本 |
| `--text-lg` | `1.125rem` (18px) | 小标题、强调文本 |
| `--text-xl` | `1.25rem` (20px) | 副标题 |
| `--text-2xl` | `1.5rem` (24px) | 中等标题 |
| `--text-3xl` | `1.875rem` (30px) | 大标题 |
| `--text-4xl` | `2.25rem` → `2.5rem` | 区块标题（流动字号） |
| `--text-5xl` | `3rem` → `3.5rem` | Hero 标题（流动字号） |

### 4.3 行高

| Token | 值 | 用途 |
|-------|-----|------|
| `--leading-none` | `1` | 紧凑行高 |
| `--leading-tight` | `1.25` | 标题行高 |
| `--leading-snug` | `1.375` | 卡片标题 |
| `--leading-normal` | `1.5` | 正文行高 |
| `--leading-relaxed` | `1.625` | 松散行高，阅读文本 |

### 4.4 字间距

| Token | 值 | 用途 |
|-------|-----|------|
| `--tracking-tighter` | `-0.025em` | 大标题 |
| `--tracking-tight` | `-0.015em` | 中等标题 |
| `--tracking-normal` | `0` | 正文 |
| `--tracking-wide` | `0.025em` | 宽字间距 |
| `--tracking-wider` | `0.05em` | 标签 |
| `--tracking-widest` | `0.1em` | 全大写标签 |
| `--tracking-label` | `0.16em` | 徽章、标签 |
| `--tracking-brand` | `0.2em` | 品牌文字 |

### 4.5 字体粗细

| Token | 值 | 用途 |
|-------|-----|------|
| `--font-normal` | `400` | 正文 |
| `--font-medium` | `500` | 强调文本 |
| `--font-semibold` | `600` | 标题 |
| `--font-bold` | `700` | 重点强调 |

### 4.6 使用示例

```css
/* 页面标题 */
.page-title {
  font-family: var(--font-sans);
  font-size: var(--text-4xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
}

/* 正文 */
.body-text {
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--text-light);
}

/* 标签徽章 */
.badge {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  letter-spacing: var(--tracking-label);
  text-transform: uppercase;
}
```

---

## 5. 阴影与高程 (Elevation)

### 5.1 阴影

| Token | 值 | 说明 |
|-------|-----|------|
| `--shadow-card` | `0 4px 24px var(--shadow)` | 默认卡片阴影，弥散投影 |
| `--shadow-card-hover` | `0 8px 32px var(--shadow)` | 卡片悬停阴影 |
| `--shadow-elevated` | `0 8px 32px var(--shadow)` | 浮动元素阴影（毛玻璃效果） |
| `--shadow-inset` | `inset 0 2px 4px rgba(59,61,63,0.08)` | 内凹阴影（输入框） |
| `--shadow-inset-focus` | `inset 0 2px 4px rgba(59,61,63,0.08), 0 0 0 2px var(--accent)` | 内凹聚焦阴影 |

**注意**：弃用生硬的重阴影，采用环境弥散投影。

### 5.2 圆角

| Token | 值 | 使用场景 |
|-------|-----|----------|
| `--radius-sm` | `6px` | 小按钮、标签 |
| `--radius-md` | `10px` | 输入框、默认按钮、卡片标题 |
| `--radius-lg` | `16px` | 卡片、面板、模态框 |
| `--radius-xl` | `18px` | Auth 卡片 |
| `--radius-full` | `9999px` | 药丸形徽章、头像 |

### 5.3 使用示例

```css
/* 卡片阴影 */
.card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--duration-base) var(--ease-spring);
}

.card:hover {
  box-shadow: var(--shadow-card-hover);
}

/* 输入框内凹效果 */
.input {
  background: var(--bg-inset);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-inset);
}

.input:focus {
  box-shadow: var(--shadow-inset-focus);
}
```

---

## 6. 动效系统 (Motion)

### 6.1 时长

| Token | 值 | 用途 |
|-------|-----|------|
| `--duration-fast` | `150ms` | 微交互、状态切换 |
| `--duration-base` | `300ms` | 默认过渡，所有交互动画基准 |
| `--duration-slow` | `400ms` | 大元素移动、页面过渡 |

### 6.2 缓动函数

| Token | 值 | 用途 |
|-------|-----|------|
| `--ease-spring` | `cubic-bezier(0.16, 1, 0.3, 1)` | 物理弹簧曲线，悬停/展开等交互动画 |
| `--ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | 标准缓动，大多数场景 |
| `--ease-soft` | `cubic-bezier(0.25, 0.1, 0.25, 1)` | 柔和过渡 |

### 6.3 使用原则

1. **功能性优先**：动效应服务于功能，而非装饰
2. **保持克制**：避免过度动画造成视觉疲劳
3. **尊重系统设置**：支持 `prefers-reduced-motion`

```css
/* 标准交互动画 */
.element {
  transition: all var(--duration-base) var(--ease-spring);
}

/* 悬停提升效果 */
.interactive {
  transition: transform var(--duration-base) var(--ease-spring),
              box-shadow var(--duration-base) var(--ease-spring),
              background-color var(--duration-base) var(--ease-spring);
}

.interactive:hover {
  transform: translateY(-2px);
}

/* 尊重减少动效偏好 */
@media (prefers-reduced-motion: reduce) {
  .element {
    transition: none;
  }
}
```

---

## 7. Z-Index 层级

| Token | 值 | 用途 |
|-------|-----|------|
| `--z-base` | `0` | 基础层级 |
| `--z-dropdown` | `10` | 下拉菜单 |
| `--z-sticky` | `20` | 粘性定位元素 |
| `--z-overlay` | `30` | 遮罩层 |
| `--z-modal` | `40` | 模态框 |
| `--z-toast` | `50` | 吐司通知 |

---

## 8. 响应式适配

### 8.1 断点

| 名称 | 宽度 | 典型设备 |
|------|-------|----------|
| `sm` | `640px+` | 大屏手机、平板竖屏 |
| `md` | `768px+` | 平板横屏、小笔记本 |
| `lg` | `1024px+` | 笔记本 |
| `xl` | `1280px+` | 台式机 |

### 8.2 响应式间距调整

```css
/* 移动端间距 */
.container {
  padding: var(--space-4);
}

/* 平板及以上 */
@media (min-width: 768px) {
  .container {
    padding: var(--space-6);
  }
}

/* 桌面端 */
@media (min-width: 1024px) {
  .container {
    padding: var(--space-8);
  }
}
```

---

## 9. 附录：Token 完整列表

```css
:root {
  /* === Colors === */
  --bg: #F8F5ED;
  --bg-card: #FCFAF5;
  --bg-glass: rgba(250, 248, 242, 0.92);
  --sidebar-bg: #F4F2EA;
  --bg-inset: #E8E5DD;

  --text: #3B3D3F;
  --text-light: #6B6F73;
  --text-muted: #8E9196;

  --accent: #537D96;
  --accent-hover: #456A80;
  --accent-light: rgba(83, 125, 150, 0.08);

  --border: rgba(83, 125, 150, 0.22);
  --shadow: rgba(59, 61, 63, 0.09);

  --green: #7BAE7F;
  --coral: #EC8F8D;

  /* Chat-specific */
  --user-bg: rgba(83, 125, 150, 0.08);
  --tool-bg: rgba(83, 125, 150, 0.06);
  --tool-text: #6B6F73;

  /* === Spacing === */
  --space-0: 0;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  --space-24: 6rem;

  --hit-target-min: 2.75rem;
  --input-height: 2.75rem;
  --button-height-sm: 2.25rem;
  --button-height-md: 2.75rem;
  --button-height-lg: 3rem;

  /* === Typography === */
  --font-sans: "DS-Project", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;

  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;

  --tracking-tighter: -0.025em;
  --tracking-tight: -0.015em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
  --tracking-widest: 0.1em;
  --tracking-label: 0.16em;
  --tracking-brand: 0.2em;

  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* === Elevation === */
  --shadow-card: 0 4px 24px var(--shadow);
  --shadow-card-hover: 0 8px 32px var(--shadow);
  --shadow-elevated: 0 8px 32px var(--shadow);
  --shadow-inset: inset 0 2px 4px rgba(59,61,63,0.08);
  --shadow-inset-focus: inset 0 2px 4px rgba(59,61,63,0.08), 0 0 0 2px var(--accent);

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 18px;
  --radius-full: 9999px;

  --duration-fast: 150ms;
  --duration-base: 300ms;
  --duration-slow: 400ms;

  --ease-spring: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-soft: cubic-bezier(0.25, 0.1, 0.25, 1);

  --z-dropdown: 10;
  --z-sticky: 20;
  --z-overlay: 30;
  --z-modal: 40;
  --z-toast: 50;
}
```
