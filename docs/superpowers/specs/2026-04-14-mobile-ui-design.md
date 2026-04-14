# Mobile UI 模块设计方案

## 概述

完成 `mobile/src/components/ui` 模块开发，包括基础 UI 组件、LoginScreen 图标替换、Tab Bar 毛玻璃效果、移动端特权工具函数。

## 设计原则

1. **Props API 与 Web 端对齐** - 保持跨端一致性
2. **复用已有设计系统** - `mobile/src/styles` 中的 colors, typography, spacing, elevation tokens
3. **Lucide React Native** - 图标库选型（PRD 已确定）

---

## 1. 基础 UI 组件

### Button

| Prop | Type | Default | 说明 |
|------|------|---------|------|
| `variant` | `'primary' \| 'secondary' \| 'ghost' \| 'danger'` | `'primary'` | 变体样式 |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | 尺寸 |
| `leftIcon` | `React.ComponentType<{size: number}>` | - | 左侧图标 |
| `rightIcon` | `React.ComponentType<{size: number}>` | - | 右侧图标 |
| `isLoading` | `boolean` | `false` | 加载状态 |
| `fullWidth` | `boolean` | `false` | 全宽 |
| `disabled` | `boolean` | `false` | 禁用 |
| `children` | `React.ReactNode` | - | 内容 |

**样式复用**:
- 高度: `spacing.buttonHeightSm/Md/Lg`
- 圆角: `elevation.radiusMd`
- 颜色: `colors.accent`, `colors.backgroundCard`
- 阴影: `elevation.shadowCard`

### Card

| Prop | Type | Default | 说明 |
|------|------|---------|------|
| `variant` | `'default' \| 'elevated' \| 'glass'` | `'default'` | 变体 |
| `padding` | `'sm' \| 'md' \| 'lg'` | `'md'` | 内边距 |
| `children` | `React.ReactNode` | - | 内容 |

### Input

| Prop | Type | Default | 说明 |
|------|------|---------|------|
| `label` | `string` | - | 标签 |
| `error` | `string` | - | 错误信息 |
| `hint` | `string` | - | 提示信息 |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | 尺寸 |
| `leftIcon` | `React.ComponentType<{size: number}>` | - | 左侧图标 |
| `rightIcon` | `React.ComponentType<{size: number}>` | - | 右侧图标 |
| `fullWidth` | `boolean` | `true` | 全宽 |

### Badge

| Prop | Type | Default | 说明 |
|------|------|---------|------|
| `variant` | `'success' \| 'error' \| 'warning' \| 'info'` | `'info'` | 变体 |
| `children` | `React.ReactNode` | - | 内容 |

### Modal

| Prop | Type | Default | 说明 |
|------|------|---------|------|
| `visible` | `boolean` | - | 显示状态 |
| `onClose` | `() => void` | - | 关闭回调 |
| `title` | `string` | - | 标题 |
| `children` | `React.ReactNode` | - | 内容 |

---

## 2. LoginScreen 图标替换

| 位置 | 原 Emoji | Lucide Icon | 颜色 |
|------|----------|-------------|------|
| 学号输入 | 👤 | `User` | `colors.textLight` |
| 密码输入 | 🔒 | `Lock` | `colors.textLight` |
| 密码切换 | 👁️/👁️‍🗨️ | `Eye`/`EyeOff` | `colors.textMuted` |
| Logo | 🎓 | `GraduationCap` | `colors.accent` |
| 装饰叶 | 🍃/🍂 | `Leaf` | `colors.green` (20% opacity) |
| 装饰罗盘 | 🧭 | `Compass` | `colors.accent` (20% opacity) |

---

## 3. Tab Bar 毛玻璃效果

**实现方式**: `@react-native-community/blur`

```tsx
import { BlurView } from '@react-native-community/blur';

<BlurView
  intensity={80}
  tint="light"
  style={StyleSheet.absoluteFill}
/>
```

**背景色**: `colors.backgroundGlass` (#FCFAF5, 92% opacity)

---

## 4. 移动端特权工具函数

### imagePicker.ts

```typescript
// pickImage(): 调起相册选择图片
// takePhoto(): 调起相机拍照
// 返回: Promise<{ uri: string; width: number; height: number } | null>
```

### documentPicker.ts

```typescript
// pickDocument(): 调起文件管理器选择文档
// 返回: Promise<{ uri: string; name: string; size: number } | null>
```

---

## 文件结构

```
mobile/src/
├── components/
│   └── ui/
│       ├── Button/
│       ├── Card/
│       ├── Input/
│       ├── Badge/
│       ├── Modal/
│       └── index.ts
├── features/auth/
│   └── LoginScreen.tsx        # 更新：替换 emoji 为 lucide
├── utils/
│   ├── imagePicker.ts         # 新增
│   └── documentPicker.ts      # 新增
└── navigation/
    └── TabNavigator.tsx       # 更新：添加毛玻璃 Tab Bar
```
