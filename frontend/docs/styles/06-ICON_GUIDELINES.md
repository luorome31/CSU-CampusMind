# 图标使用指南

> 本文档定义 CampusMind Design System 中图标的使用规范，包括图标库选择、尺寸规范、颜色处理以及无障碍要求。

---

## 1. 图标库

### 1.1 选用标准

CampusMind 使用 **Lucide React** 作为图标库：

| 特性 | 说明 |
|------|------|
| **风格** | 极简线性图标，与 Warm Minimal 美学契合 |
| **权重** | 2px 一致的描边权重 |
| **圆角** | 24px 圆角端点 |
| **尺寸** | 24px 作为基准尺寸 |
| **可访问性** | 内置 aria-hidden 支持 |

### 1.2 安装

```bash
npm install lucide-react
```

### 1.3 导入

```typescript
import { Mail, User, Lock, Plus, Search } from 'lucide-react';
```

---

## 2. 尺寸系统

### 2.1 图标尺寸刻度

| 尺寸 Token | 像素值 | 使用场景 |
|-----------|--------|----------|
| `xs` | 12px | 徽章内图标、紧凑列表 |
| `sm` | 14px | 按钮内图标、小标签 |
| `md` | 16px | **默认**，输入框、按钮 |
| `lg` | 20px | 导航、侧边栏 |
| `xl` | 24px | 大按钮、强调图标 |
| `2xl` | 32px | 空状态、特殊展示 |

### 2.2 尺寸使用规范

```typescript
// 徽章内图标 - 12px
<Badge>
  <CheckIcon size={12} />
  已完成
</Badge>

// 按钮内图标 - 根据按钮尺寸
<Button size="sm">
  <PlusIcon size={14} />
  添加
</Button>

<Button size="md">
  <PlusIcon size={16} />
  添加
</Button>

// 导航图标 - 20px
<NavItem>
  <HomeIcon size={20} />
  首页
</NavItem>

// 空状态图标 - 32px
<EmptyState>
  <InboxIcon size={32} />
  暂无消息
</EmptyState>
```

---

## 3. 图标颜色

### 3.1 颜色继承规则

图标颜色应继承父元素文字颜色：

```css
/* 图标继承父元素文字颜色 */
.icon {
  color: currentColor;
}

/* 在 Lucide React 中默认 inherit */
.icon {
  stroke: currentColor;
  fill: none; /* Lucide 默认无填充 */
}
```

### 3.2 常见颜色场景

```typescript
// 主要操作图标 - 使用 accent 颜色
.primary-icon {
  color: var(--color-accent);
}

// 次要/辅助图标 - 使用 tertiary 颜色
.secondary-icon {
  color: var(--color-text-tertiary);
}

// 交互反馈图标
.success-icon {
  color: var(--color-success);
}

.error-icon {
  color: var(--color-error);
}
```

### 3.3 禁止做法

```tsx
// ✗ 错误：硬编码图标颜色
<Icon color="#2d2a26" />

// ✗ 错误：使用 fill 改变颜色
<Icon fill="currentColor" />

// ✓ 正确：依赖 currentColor
<Icon color="var(--color-accent)" />
// 或
<Icon style={{ color: 'var(--color-accent)' }} />
```

---

## 4. 图标与文字

### 4.1 布局模式

```css
/* 水平排列 - 图标在左 */
.icon-left {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

/* 水平排列 - 图标在右 */
.icon-right {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  flex-direction: row-reverse;
}

/* 垂直排列 - 图标在上 */
.icon-top {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
}
```

### 4.2 图标与文字对齐

```css
/* 确保图标与文字基线对齐 */
.icon-wrapper {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.icon-wrapper svg {
  flex-shrink: 0; /* 防止图标被压缩 */
}
```

---

## 5. 无障碍规范

### 5.1 独立图标按钮

当图标作为独立按钮使用时，必须提供 `aria-label`：

```tsx
// ✓ 正确：提供 aria-label
<button aria-label="关闭对话框">
  <XIcon size={20} />
</button>

<button aria-label="删除项目">
  <TrashIcon size={20} />
</button>

// ✗ 错误：缺少无障碍标签
<button>
  <XIcon size={20} />
</button>
```

### 5.2 装饰性图标

当图标仅为装饰目的时，使用 `aria-hidden="true"`：

```tsx
// ✓ 正确：装饰性图标隐藏
<span aria-hidden="true">
  <MailIcon size={16} />
</span>

// ✓ 正确：与文字结合时隐藏
<button>
  <span aria-hidden="true"><MailIcon /></span>
  <span>发送邮件</span>
</button>
```

### 5.3 加载状态图标

```tsx
// 加载中图标
<SpinnerIcon
  size={20}
  aria-label="加载中"
  role="status"
/>
```

---

## 6. 图标使用清单

### 6.1 常用图标映射

| 语义 | 图标 | 使用场景 |
|------|------|----------|
| 添加 | `Plus` | 新建、添加按钮 |
| 编辑 | `Pencil` | 编辑操作 |
| 删除 | `Trash2` | 删除操作 |
| 保存 | `Save` | 保存按钮 |
| 关闭 | `X` | 关闭、取消 |
| 返回 | `ArrowLeft` | 返回按钮 |
| 下一个 | `ArrowRight` | 前进 |
| 搜索 | `Search` | 搜索框 |
| 筛选 | `Filter` | 筛选按钮 |
| 用户 | `User` | 用户相关 |
| 邮箱 | `Mail` | 邮箱相关 |
| 锁定 | `Lock` | 安全、密码 |
| 可见 | `Eye` | 显示密码 |
| 隐藏 | `EyeOff` | 隐藏密码 |
| 加载 | `Loader2` | 加载状态 |
| 成功 | `Check` | 成功状态 |
| 错误 | `AlertCircle` | 错误提示 |
| 警告 | `AlertTriangle` | 警告提示 |
| 信息 | `Info` | 信息提示 |

### 6.2 图标选择原则

1. **语义匹配**：图标含义与操作意图一致
2. **简洁优先**：选择最简单的图标表达含义
3. **避免歧义**：确保目标用户能理解图标含义
4. **保持一致**：相同操作使用相同图标

---

## 7. 图标最佳实践

### 7.1 代码规范

```tsx
// ✓ 推荐：命名导入 + 解构
import { Plus, Search, User } from 'lucide-react';

// ✓ 推荐：内联图标尺寸
<Button leftIcon={<Plus size={16} />}>添加</Button>

// ✓ 推荐：装饰性图标
<span aria-hidden="true"><Icon /></span>

// ✓ 推荐：图标按钮
<button aria-label="添加新项目">
  <PlusIcon size={20} />
</button>
```

### 7.2 样式规范

```css
/* 图标样式 */
.icon {
  display: inline-flex;
  flex-shrink: 0; /* 防止压缩 */
  vertical-align: middle; /* 与文字对齐 */
}

/* 按钮内图标 */
.button-icon {
  flex-shrink: 0;
}
```

### 7.3 审查清单

- [ ] 图标颜色使用 `currentColor` 或 CSS 变量
- [ ] 图标尺寸符合 12/14/16/20/24/32 规范
- [ ] 独立图标按钮有 `aria-label`
- [ ] 装饰性图标有 `aria-hidden`
- [ ] 图标与文字使用 `gap` 而非 `margin`
- [ ] 图标不会被 flex 压缩
