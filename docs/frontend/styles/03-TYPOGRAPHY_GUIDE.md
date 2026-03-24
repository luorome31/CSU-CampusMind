# 排版设计指南

> 本文档定义 CampusMind Design System 的排版规范，包括字体选择、字号层级、行高设置、字间距使用以及响应式排版策略。

---

## 1. 排版理念

### 1.1 设计原则

CampusMind 排版遵循 **Editorial Precision**（编辑级精确）原则：

- **清晰层次**：通过字号、粗细、颜色建立明确的视觉层级
- **舒适阅读**：适当的行高和字间距确保长时间阅读不疲劳
- **克制装饰**：字体作为信息载体，而非主要视觉元素
- **流动适应**：排版随视口自动调整，实现最佳阅读体验

### 1.2 字体选择理念

| 字体角色 | 选择理由 |
|----------|----------|
| **DS-Project** | 品牌定制字体，表达学术严谨感 |
| **System UI Fallback** | 确保跨平台可读性和性能 |
| **IBM Plex Mono** | 代码展示，等宽特性确保对齐 |

### 1.3 排版节奏

排版间距遵循 **4px 基础网格**：

```
0px ─┬─ 4px ─┬─ 8px ─┬─ 12px ─┬─ 16px ─┬─ 24px ─┬─ 32px
     │        │        │         │         │
     └── 4px 基础单位 ────────────────────────┘
```

---

## 2. 字体规范

### 2.1 字体栈 (Font Stack)

```css
--font-sans: "DS-Project", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
--font-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
```

### 2.2 字体使用场景

| 字体 | 用途 | 示例 |
|------|------|------|
| `--font-sans` | 正文、标题、UI 元素 | 按钮文本、标签、导航 |
| `--font-mono` | 代码、技术内容 | 代码块、日志展示、版本号 |

### 2.3 Web Font 加载建议

```html
<!-- 在 index.html 中预加载关键字体 -->
<link rel="preconnect" href="https://fonts.example.com" crossorigin>
```

```css
/* 字体显示策略：确保文本可见 */
font-display: swap;
```

---

## 3. 字号系统

### 3.1 完整字号刻度

| Token | 字号 | 用途 | 使用频率 |
|-------|------|------|----------|
| `--text-xs` | 12px (0.75rem) | 徽章、标签、版权信息 | 中 |
| `--text-sm` | 14px (0.875rem) | 次要文本、表格、辅助说明 | 高 |
| `--text-base` | 16px (1rem) | 正文、默认文本 | 极高 |
| `--text-lg` | 18px (1.125rem) | 小标题、强调文本 | 中 |
| `--text-xl` | 20px (1.25rem) | 副标题、卡片标题 | 高 |
| `--text-2xl` | 24px (1.5rem) | 区块标题 | 中 |
| `--text-3xl` | 30px (1.875rem) | 页面副标题 | 中 |
| `--text-4xl` | 36-40px (2.25-2.5rem) | 区块主标题 | 中 |
| `--text-5xl` | 48-56px (3-3.5rem) | Hero 标题 | 低 |

### 3.2 字号使用规范

```css
/* 文章正文 - 使用基准字号 */
.article-body {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
}

/* 侧边栏文本 - 略小 */
.sidebar-text {
  font-size: var(--text-sm);
}

/* 标题层级 */
h1 { font-size: var(--text-4xl); }
h2 { font-size: var(--text-3xl); }
h3 { font-size: var(--text-2xl); }
h4 { font-size: var(--text-xl); }
h5 { font-size: var(--text-lg); }
h6 { font-size: var(--text-base); }
```

### 3.3 字号选择流程

```
┌─────────────────┐
│  文本类型判断   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
 Hero    页面标题
  │        │
  │   ┌────┴────┐
  │   │         │
  │  区块   次级区块
  │  标题    标题
  │   │       │
  └───┘   ┌───┴───┐
       卡片   表格
       标题   标题
           │
        ┌───┴───┐
       正文   辅助
       文本   说明
        │       │
        └───┬───┘
            │
         脚注/标签
           (text-xs)
```

---

## 4. 行高设置

### 4.1 行高刻度

| Token | 值 | 用途 |
|-------|-----|------|
| `--leading-none` | 1 | 紧凑列表、徽章文字 |
| `--leading-tight` | 1.25 | 标题 |
| `--leading-snug` | 1.375 | 卡片标题 |
| `--leading-normal` | 1.5 | 正文、默认 |
| `--leading-relaxed` | 1.625 | 长文本阅读 |

### 4.2 行高选择指南

| 场景 | 推荐行高 | 原因 |
|------|----------|------|
| 短标题 | `1.25` | 紧凑美观 |
| 长文章 | `1.625` | 提升阅读舒适度 |
| 界面文本 | `1.5` | 平衡可读性与密度 |
| 列表项 | `1.375` | 适中密度 |

### 4.3 行高与字号关系

```css
/* 标题：较小行高 */
h1, h2, h3 {
  line-height: var(--leading-tight);
}

/* 正文：宽松行高 */
p {
  line-height: var(--leading-relaxed);
}

/* 短文本：紧凑 */
.badge-text {
  line-height: var(--leading-none);
}
```

---

## 5. 字间距

### 5.1 字间距刻度

| Token | 值 | 效果 | 用途 |
|-------|-----|------|------|
| `--tracking-tighter` | -0.025em | 字间距紧凑 | 大标题 (28px+) |
| `--tracking-tight` | -0.015em | 略微紧凑 | 中等标题 (20-27px) |
| `--tracking-normal` | 0 | 标准 | 正文 |
| `--tracking-wide` | 0.025em | 略微宽松 | 重要标签 |
| `--tracking-wider` | 0.05em | 宽松 | 大写标签 |
| `--tracking-widest` | 0.1em | 极宽松 | 品牌标语 |
| `--tracking-label` | 0.16em | 标签专用 | 徽章、分类标签 |
| `--tracking-brand` | 0.2em | 品牌专用 | Logo、副品牌 |

### 5.2 字间距使用原则

```css
/* 大标题收紧字间距，增强紧凑感 */
.hero-title {
  font-size: var(--text-5xl);
  letter-spacing: var(--tracking-tight);
}

/* 标签使用宽松字间距，便于识别 */
.badge {
  font-size: var(--text-xs);
  letter-spacing: var(--tracking-label);
  text-transform: uppercase;
}

/* 正文保持标准字间距 */
.body-text {
  letter-spacing: var(--tracking-normal);
}
```

### 5.3 字号与字间距关系

```
字号        推荐字间距
──────────────────────
≥ 32px    tracking-tight 或 tighter
24-31px   tracking-normal 或 tight
18-23px   tracking-normal
12-17px   可适当宽松，如 tracking-wide
< 12px    tracking-wider 或 wider
```

---

## 6. 字体粗细

### 6.1 粗细刻度

| Token | 值 | 用途 |
|-------|-----|------|
| `--font-normal` | 400 | 正文 |
| `--font-medium` | 500 | 强调文本、按钮 |
| `--font-semibold` | 600 | 标题、标签 |
| `--font-bold` | 700 | 重点强调（慎用） |

### 6.2 粗细使用规范

```css
/* 标题：使用 semibold */
h1, h2, h3, h4 {
  font-weight: var(--font-semibold);
}

/* 正文：使用 normal */
p, span, div {
  font-weight: var(--font-normal);
}

/* 强调：使用 medium */
.emphasis {
  font-weight: var(--font-medium);
}

/* 按钮：使用 medium */
.button {
  font-weight: var(--font-medium);
}
```

### 6.3 粗细与字号的搭配

```css
/* 大标题可用较轻重量的对比效果 */
.page-title {
  font-size: var(--text-4xl);
  font-weight: var(--font-semibold); /* 大字可用较轻重量 */
}

.section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
}

/* 小文本建议使用较重重量确保可读性 */
.small-emphasis {
  font-size: var(--text-sm);
  font-weight: var(--font-medium); /* 小字用较重重量 */
}
```

---

## 7. 响应式排版

### 7.1 流动字号 (Fluid Typography)

使用 `clamp()` 实现视口自适应字号：

```css
/* 流动标题 */
.fluid-title {
  font-size: clamp(1.5rem, 2.5vw + 1rem, 2.5rem);
}

/* 流动正文 */
.fluid-body {
  font-size: clamp(0.875rem, 1vw + 0.75rem, 1rem);
}
```

### 7.2 响应式断点字号

| 元素 | < 640px | 640-1024px | > 1024px |
|------|---------|------------|-----------|
| Hero 标题 | 36px | 48px | 56px |
| 页面标题 | 28px | 36px | 40px |
| 区块标题 | 24px | 28px | 32px |
| 正文 | 14px | 15px | 16px |

### 7.3 响应式行高

```css
/* 移动端行高略小，节省空间 */
p {
  line-height: 1.5;
}

@media (min-width: 768px) {
  p {
    line-height: 1.625; /* 桌面端稍宽松 */
  }
}
```

---

## 8. 特殊文本样式

### 8.1 链接

```css
a {
  color: var(--color-accent);
  text-decoration: none;
  transition: color var(--duration-fast) var(--ease-default);
}

a:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}
```

### 8.2 代码

```css
code {
  font-family: var(--font-mono);
  font-size: 0.875em; /* 相对父元素 87.5% */
  background-color: var(--color-bg-inset);
  padding: 0.125em 0.375em;
  border-radius: var(--radius-sm);
}

pre {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.6;
  background-color: var(--color-bg-inset);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  overflow-x: auto;
}
```

### 8.3 引用

```css
blockquote {
  font-size: var(--text-lg);
  font-style: italic;
  color: var(--color-text-secondary);
  border-left: 4px solid var(--color-accent);
  padding-left: var(--space-4);
  margin: var(--space-4) 0;
}
```

---

## 9. 排版组件模板

### 9.1 标题组件

```css
.heading-1 {
  font-family: var(--font-sans);
  font-size: var(--text-4xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-4);
}

.heading-2 {
  font-family: var(--font-sans);
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-3);
}

/* ... 以此类推 */
```

### 9.2 段落组件

```css
.paragraph {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  line-height: var(--leading-relaxed);
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-4);
}

.paragraph-small {
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  color: var(--color-text-tertiary);
}
```

### 9.3 标签组件

```css
.label {
  font-family: var(--font-sans);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  letter-spacing: var(--tracking-label);
  text-transform: uppercase;
  color: var(--color-text-secondary);
}
```

---

## 10. 排版最佳实践清单

- [ ] 始终使用 CSS 变量而非硬编码字号
- [ ] 标题使用 `--font-semibold`，正文使用 `--font-normal`
- [ ] 长文本使用 `--leading-relaxed` (1.625)
- [ ] 大标题收紧字间距，小标签放宽字间距
- [ ] 确保正文与背景对比度 ≥ 4.5:1
- [ ] 代码使用 `--font-mono`
- [ ] 支持 `prefers-reduced-motion` 用户的动效需求
- [ ] 移动端字号不小于 12px
- [ ] 触摸目标文字不小 14px
