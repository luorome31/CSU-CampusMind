# 间距系统文档

> 本文档定义 CampusMind Design System 的间距规范，包括空间刻度、布局模式、响应式策略和使用指南。

---

## 1. 间距理念

### 1.1 设计原则

CampusMind 间距系统遵循 **4px 基础网格**原则：

- **统一基准**：所有间距基于 4px 网格
- **语义化**：间距大小表达关系的紧密程度
- **克制使用**：避免过多间距级别，保持简洁
- **响应式**：间距随屏幕尺寸适度调整

### 1.2 空间节奏

```
┌────────────────────────────────────────────────────────────────┐
│                        空间层级示意                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  micro    tight    default    medium    loose    section   page  │
│    │        │         │         │        │        │        │    │
│   4px     8px      16px      24px     32px     48px    64px  │
│                                                                │
│  图标旁   内联    组件内   组件间   区块间   大区块   页面级  │
│   间距    元素    padding   gap     gap     gap     margin   │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. 间距刻度

### 2.1 基础刻度

| Token | 值 | 像素 | 用途 | 使用频率 |
|-------|-----|------|------|----------|
| `--space-0` | `0` | 0px | 移除间距 | 高 |
| `--space-1` | `0.25rem` | 4px | 微间距、图标旁 | 中 |
| `--space-2` | `0.5rem` | 8px | 紧凑间距、内联元素 | 高 |
| `--space-3` | `0.75rem` | 12px | 默认间距、表单项 | 高 |
| `--space-4` | `1rem` | 16px | 组件内边距、段落 | 极高 |
| `--space-5` | `1.25rem` | 20px | 中等间距 | 中 |
| `--space-6` | `1.5rem` | 24px | 组件间间距 | 高 |
| `--space-8` | `2rem` | 32px | 大间距、区域分割 | 中 |
| `--space-10` | `2.5rem` | 40px | 区块间距 | 中 |
| `--space-12` | `3rem` | 48px | 大区块间距 | 中 |
| `--space-16` | `4rem` | 64px | 页面级间距 | 低 |
| `--space-20` | `5rem` | 80px | 超大间距 | 低 |
| `--space-24` | `6rem` | 96px | 最大间距 | 低 |

### 2.2 转换速查

```
4px   = --space-1  = micro
8px   = --space-2  = tight
12px  = --space-3  = default
16px  = --space-4  = default
24px  = --space-6  = medium
32px  = --space-8  = loose
48px  = --space-12 = section
64px  = --space-16 = page
```

---

## 3. 组件专用间距

### 3.1 触摸目标

| Token | 值 | 说明 | WCAG 要求 |
|-------|-----|------|-----------|
| `--hit-target-min` | `2.75rem` (44px) | 最小点击区域 | ≥ 44x44px |

### 3.2 输入框

| Token | 值 | 用途 |
|-------|-----|------|
| `--input-height` | `2.75rem` (44px) | 输入框标准高度 |

### 3.3 按钮

| Token | 值 | 尺寸 |
|-------|-----|------|
| `--button-height-sm` | `2.25rem` (36px) | 小按钮 |
| `--button-height-md` | `2.75rem` (44px) | 中按钮 |
| `--button-height-lg` | `3rem` (48px) | 大按钮 |

### 3.4 容器

| Token | 值 | 说明 |
|-------|-----|------|
| `--container-max` | `90vw` | 最大容器宽度（移动端） |
| `--container-max-sm` | `440px` | 小容器（单列表单） |
| `--container-max-md` | `720px` | 中容器（博客文章） |
| `--container-max-lg` | `1024px` | 大容器（仪表盘） |
| `--container-max-xl` | `1280px` | 超大容器（全宽布局） |

---

## 4. 间距使用规范

### 4.1 组件内间距

```css
/* 紧凑按钮 */
.button {
  padding: var(--space-2) var(--space-4);
  gap: var(--space-2);
}

/* 默认按钮 */
.button {
  padding: var(--space-3) var(--space-4);
  gap: var(--space-2);
}

/* 宽松按钮 */
.button {
  padding: var(--space-4) var(--space-6);
  gap: var(--space-3);
}
```

### 4.2 卡片间距

```css
.card {
  padding: var(--space-4);
  gap: var(--space-3);
}

.card-header {
  margin-bottom: var(--space-3);
}

.card-body {
  gap: var(--space-4);
}
```

### 4.3 区块间距

```css
.section {
  padding: var(--space-8) 0;
  margin-bottom: var(--space-8);
}

.subsection {
  margin-bottom: var(--space-6);
}

.element-group {
  gap: var(--space-4);
}
```

### 4.4 页面级间距

```css
.page {
  padding: var(--space-6);
}

@media (min-width: 768px) {
  .page {
    padding: var(--space-8);
  }
}

@media (min-width: 1024px) {
  .page {
    padding: var(--space-12);
  }
}
```

---

## 5. Flexbox 间距模式

### 5.1 gap 替代 margin

> **最佳实践**：使用 `gap` 而非 `margin` 处理元素间距

```css
/* ✓ 推荐：使用 gap */
.flex-group {
  display: flex;
  gap: var(--space-3);
}

/* ✗ 避免：使用 margin */
/* 这种方式需要在每个子元素上处理首尾间距 */
.flex-group > * + * {
  margin-left: var(--space-3);
}
```

### 5.2 常见 Flex 间距场景

```css
/* 图标与文字 */
.icon-with-text {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: var(--space-3);
}

/* 标签组 */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

/* 列表项 */
.list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
```

### 5.3 Grid 间距

```css
/* 卡片网格 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
}

/* 双列布局 */
.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-8);
}

@media (max-width: 768px) {
  .two-column {
    grid-template-columns: 1fr;
    gap: var(--space-6);
  }
}
```

---

## 6. 响应式间距

### 6.1 断点缩放

| 元素类型 | < 640px | 640-1024px | > 1024px |
|----------|----------|-------------|----------|
| 页面边距 | 16px | 24px | 32px |
| 区块间距 | 32px | 48px | 64px |
| 组件内距 | 12px | 16px | 16px |
| 元素 gap | 8px | 12px | 16px |

### 6.2 响应式间距实现

```css
/* 基础间距 */
.container {
  padding: var(--space-4);
  gap: var(--space-4);
}

/* 平板及以上 */
@media (min-width: 768px) {
  .container {
    padding: var(--space-6);
    gap: var(--space-6);
  }
}

/* 桌面及以上 */
@media (min-width: 1024px) {
  .container {
    padding: var(--space-8);
    gap: var(--space-8);
  }
}
```

### 6.3 移动端优先 vs 桌面端优先

```css
/* 移动端优先（默认） */
.element {
  padding: var(--space-4);
  gap: var(--space-3);
}

/* 桌面端增强 */
@media (min-width: 1024px) {
  .element {
    padding: var(--space-6);
    gap: var(--space-4);
  }
}
```

---

## 7. 间距速查表

### 7.1 快速参考

| 场景 | 推荐 Token | 像素值 |
|------|------------|--------|
| 内联图标间距 | `--space-2` | 8px |
| 按钮内边距 | `--space-3` / `--space-4` | 12px / 16px |
| 卡片内边距 | `--space-4` | 16px |
| 表单项间距 | `--space-4` | 16px |
| 区块间间距 | `--space-8` | 32px |
| 页面边距 | `--space-4` ~ `--space-8` | 16px ~ 32px |
| 网格 gap | `--space-4` ~ `--space-6` | 16px ~ 24px |

### 7.2 常见模式

```css
/* 极简间距（紧凑界面） */
.compact {
  gap: var(--space-2);
  padding: var(--space-2);
}

/* 默认间距（标准界面） */
.standard {
  gap: var(--space-4);
  padding: var(--space-4);
}

/* 宽松间距（阅读界面） */
.spacious {
  gap: var(--space-6);
  padding: var(--space-6);
}
```

---

## 8. 常见错误

### 8.1 错误示例

```css
/* ✗ 错误：使用任意数值 */
.thing {
  margin: 13px; /* 13px 不在网格系统内 */
  padding: 7px;
}

/* ✗ 错误：间距过小 */
.tiny-gap {
  gap: 2px; /* 小于最小间距 */
}

/* ✗ 错误：间距过大 */
.huge-gap {
  margin: 100px; /* 过于宽松 */
}

/* ✗ 错误：混合使用 gap 和 margin */
.mixed {
  display: flex;
  gap: var(--space-4);
  margin-left: var(--space-2); /* 不一致 */
}
```

### 8.2 正确示例

```css
/* ✓ 正确：使用网格值 */
.correct {
  margin: var(--space-4);
  padding: var(--space-3);
}

/* ✓ 正确：一致的 gap */
.uniform {
  display: flex;
  gap: var(--space-4);
}

/* ✓ 正确：响应式调整 */
.responsive {
  padding: var(--space-4);
}

@media (min-width: 768px) {
  .responsive {
    padding: var(--space-6);
  }
}
```

---

## 9. 最佳实践清单

- [ ] 所有间距使用 4px 倍数
- [ ] 优先使用 `gap` 而非 `margin`
- [ ] 触摸目标最小 44x44px
- [ ] 组件内间距使用 `--space-2` ~ `--space-4`
- [ ] 区块间距使用 `--space-6` ~ `--space-8`
- [ ] 页面级间距使用 `--space-8` 及以上
- [ ] 响应式调整间距而非固定值
- [ ] 避免过小（< 4px）或过大（> 64px）间距
