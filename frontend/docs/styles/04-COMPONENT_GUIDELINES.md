# 组件开发规范

> 本文档定义 CampusMind Design System 组件的开发标准，包括组件结构、API 设计、样式规范、状态处理和无障碍要求。

---

## 1. 组件架构

### 1.1 目录结构

```
components/ui/[ComponentName]/
├── index.tsx      # 组件主入口
├── types.ts       # TypeScript 类型定义
└── styles.css     # 组件样式
```

### 1.2 组件模板

**types.ts** - 类型定义
```typescript
import { LucideIcon } from 'lucide-react';

export type ComponentVariant = 'primary' | 'secondary' | 'ghost';
export type ComponentSize = 'sm' | 'md' | 'lg';

export interface ComponentProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ComponentVariant;
  size?: ComponentSize;
  isLoading?: boolean;
  leftIcon?: LucideIcon;
  rightIcon?: LucideIcon;
  children: React.ReactNode;
}
```

**index.tsx** - 组件实现
```typescript
import React from 'react';
import type { ComponentProps } from './types';
import './styles.css';

/**
 * Component Component
 *
 * 组件描述，说明组件用途和行为。
 *
 * @example
 * <Component variant="primary" size="md">
 *   Button Text
 * </Component>
 */
export const Component = React.forwardRef<HTMLButtonElement, ComponentProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon: LeftIcon,
      rightIcon: RightIcon,
      children,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    const classes = [
      'component',
      `component-${variant}`,
      size !== 'md' && `component-${size}`,
      isLoading && 'component-loading',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || isLoading}
        {...props}
      >
        {LeftIcon && <LeftIcon size={size === 'sm' ? 14 : 16} />}
        {children}
        {RightIcon && <RightIcon size={size === 'sm' ? 14 : 16} />}
      </button>
    );
  }
);

Component.displayName = 'Component';

export default Component;
```

---

## 2. API 设计规范

### 2.1 Props 命名规范

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 布尔值 | `is` 或 `has` 前缀 | `isLoading`, `hasError` |
| 回调函数 | `on` 前缀 | `onClick`, `onChange` |
| 组件变体 | `variant` | `variant="primary"` |
| 尺寸 | `size` | `size="md"` |
| 子元素 | `children` | `<Button>Text</Button>` |

### 2.2 Props 默认值

```typescript
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost'; // 默认值在实现中设置
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  disabled?: boolean;
}
```

### 2.3 变体 (Variant) 规范

组件应支持 2-4 个变体，通常包括：

| 变体 | 用途 | 使用场景 |
|------|------|----------|
| `primary` | 主操作 | 主要提交按钮 |
| `secondary` | 次要操作 | 取消、返回 |
| `ghost` | 极简操作 | 辅助操作、工具栏 |
| `link` | 内联操作 | 编辑、查看更多 |

### 2.4 尺寸 (Size) 规范

| 尺寸 | 高度 | 字号 | 使用场景 |
|------|------|------|----------|
| `sm` | 32-36px | 12px | 紧凑场景、表格内 |
| `md` | 40-44px | 14px | 默认场景 |
| `lg` | 48px | 16px | 主要操作、Hero |

---

## 3. 样式规范

### 3.1 CSS 类命名

采用 **BEM + 语义化命名**：

```css
/* Block */
.component { }

/* Element */
.component_header { }
.component_body { }
.component_footer { }

/* Modifier */
.component--primary { }
.component--loading { }
.component--disabled { }

/* 尺寸变体 */
.component-sm { }
.component-md { }
.component-lg { }
```

### 3.2 样式优先级

```css
/* 1. 基础样式 */
.component {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-family: var(--font-sans);
  border-radius: var(--radius-md);
  transition: all var(--duration-normal) var(--ease-default);
}

/* 2. 变体样式 */
.component-primary { }
.component-secondary { }
.component-ghost { }

/* 3. 尺寸样式 */
.component-sm { }
.component-lg { }

/* 4. 状态样式 */
.component-loading { }
.component-disabled { }

/* 5. 悬停/聚焦样式 */
.component:hover { }
.component:focus-visible { }
```

### 3.3 必避免区域

```css
/* ✗ 禁止：硬编码宽度 */
.component {
  width: 200px; /* 使用 min-width 或让内容决定宽度 */
}

/* ✗ 禁止：硬编码颜色 */
.component {
  color: #2d2a26; /* 使用 CSS 变量 */
  background: #f7f2ea;
}

/* ✗ 禁止：!important */
.component {
  color: var(--color-text-primary) !important;
}

/* ✓ 正确：使用 CSS 变量 */
.component {
  color: var(--color-text-primary);
  background-color: var(--color-bg-surface);
}

/* ✓ 正确：响应式宽度 */
.component {
  width: 100%;
  max-width: 320px;
}
```

---

## 4. 状态处理

### 4.1 必需状态

每个交互组件必须处理以下状态：

| 状态 | 处理方式 |
|------|----------|
| **Default** | 默认外观 |
| **Hover** | 悬停反馈 |
| **Active/Pressed** | 按下状态 |
| **Focus** | 键盘聚焦 (`:focus-visible`) |
| **Disabled** | 禁用状态 |
| **Loading** | 加载状态（如适用） |

### 4.2 状态样式模板

```css
/* 默认状态 */
.button {
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  cursor: pointer;
}

/* 悬停状态 */
.button:hover:not(:disabled) {
  background-color: var(--color-bg-overlay-strong);
  border-color: var(--color-border-hover);
  transform: translateY(-1px);
}

/* 聚焦状态 - 键盘可访问 */
.button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* 按下状态 */
.button:active:not(:disabled) {
  transform: translateY(0);
}

/* 禁用状态 */
.button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
  pointer-events: none;
}

/* 加载状态 */
.button-loading {
  position: relative;
  color: transparent;
  pointer-events: none;
}
```

### 4.3 状态组合处理

```css
/* 悬停 + 禁用（禁用时忽略悬停） */
.button:hover:disabled {
  /* 不应有悬停效果 */
  transform: none;
  background-color: inherit;
}

/* 聚焦 + 悬停 */
.button:focus-visible:hover {
  /* 保持聚焦样式或增强 */
  outline-width: 3px;
}
```

---

## 5. 无障碍规范 (Accessibility)

### 5.1 语义化 HTML

```tsx
// ✓ 正确：使用语义标签
<button onClick={handleClick}>Submit</button>
<a href="/about">About</a>
<input type="text" />

// ✗ 错误：使用 div 模拟按钮
<div onClick={handleClick}>Submit</div>
```

### 5.2 ARIA 属性

```tsx
// 图标按钮需要 aria-label
<button aria-label="Close dialog">
  <CloseIcon />
</button>

// 加载状态需要 aria-busy
<div aria-busy={isLoading}>
  {content}
</div>

// 错误提示需要 aria-describedby
<input
  aria-invalid={hasError}
  aria-describedby={hasError ? 'error-message' : undefined}
/>
<span id="error-message" role="alert">
  {errorMessage}
</span>
```

### 5.3 键盘导航

```css
/* 确保可聚焦元素有可见聚焦指示 */
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* Tab 索引 */
.interactive-component {
  tab-index: 0;
}

/* 按下回车/Space 激活 */
.interactive-component:active {
  transform: scale(0.98);
}
```

### 5.4 触摸目标

```css
/* 最小触摸区域 44x44px */
.touch-target {
  min-width: var(--hit-target-min);  /* 44px */
  min-height: var(--hit-target-min); /* 44px */
}
```

---

## 6. 组件清单

### 6.1 Button

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `variant` | `'primary' \| 'secondary' \| 'ghost' \| 'link'` | `'primary'` | 变体样式 |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | 尺寸 |
| `isLoading` | `boolean` | `false` | 加载状态 |
| `leftIcon` | `LucideIcon` | - | 左侧图标 |
| `rightIcon` | `LucideIcon` | - | 右侧图标 |
| `fullWidth` | `boolean` | `false` | 全宽按钮 |
| `disabled` | `boolean` | `false` | 禁用状态 |

### 6.2 Input

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `label` | `string` | - | 输入框标签 |
| `error` | `string` | - | 错误信息 |
| `hint` | `string` | - | 提示文字 |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | 尺寸 |
| `leftIcon` | `LucideIcon` | - | 左侧图标 |
| `rightIcon` | `LucideIcon` | - | 右侧图标 |
| `fullWidth` | `boolean` | `true` | 全宽显示 |

### 6.3 Card

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `variant` | `'default' \| 'elevated' \| 'glass' \| 'auth'` | `'default'` | 变体样式 |
| `padding` | `'none' \| 'sm' \| 'md' \| 'lg'` | `'md'` | 内边距 |

### 6.4 Badge

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `variant` | `'default' \| 'accent' \| 'warm' \| 'success' \| 'error'` | `'default'` | 变体样式 |
| `size` | `'sm' \| 'md'` | `'md'` | 尺寸 |

### 6.5 Chip

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `variant` | `'default' \| 'active' \| 'disabled'` | `'default'` | 变体样式 |
| `size` | `'sm' \| 'md'` | `'md'` | 尺寸 |
| `icon` | `LucideIcon` | - | 图标 |

---

## 7. 代码审查清单

### 7.1 功能性

- [ ] 组件在所有支持状态下正确渲染
- [ ] Props 传递正确，类型定义完整
- [ ] 默认值符合规范
- [ ] 变体和尺寸组合正常工作

### 7.2 样式

- [ ] 所有颜色使用 CSS 变量
- [ ] 无硬编码尺寸值
- [ ] 响应式设计正确实现
- [ ] 过渡动画设置合理

### 7.3 无障碍

- [ ] 使用语义化 HTML 标签
- [ ] 键盘导航正常工作
- [ ] 聚焦状态可见
- [ ] ARIA 属性正确使用
- [ ] 触摸目标 ≥ 44x44px

### 7.4 代码质量

- [ ] TypeScript 类型完整
- [ ] 组件名称符合规范
- [ ] JSDoc 注释完整
- [ ] 无 console.error/warning
