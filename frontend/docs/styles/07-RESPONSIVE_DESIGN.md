# 响应式设计指南

> 本文档定义 CampusMind Design System 的响应式设计策略，包括断点系统、移动优先原则、布局模式以及跨端适配规范。

---

## 1. 设计理念

### 1.1 核心原则

CampusMind 采用 **Mobile-First**（移动优先）响应式设计策略：

- **内容优先**：内容决定布局，而非布局限制内容
- **渐进增强**：从最小屏幕开始，逐步为更大屏幕添加特性
- **触摸友好**：移动端优先考虑触摸交互，大屏兼顾鼠标
- **表现一致**：核心体验在各端保持一致

### 1.2 设计目标

| 设备类型 | 目标视口 | 主要交互 |
|----------|----------|----------|
| 手机 | 375px | 触摸优先，拇指操作 |
| 平板 | 768px | 触摸 + 键盘 |
| 笔记本 | 1024px | 触控板 + 键盘 |
| 桌面 | 1280px+ | 鼠标 + 键盘 |

---

## 2. 断点系统

### 2.1 断点定义

| 断点 | 宽度 | 别名 | 典型设备 |
|------|------|------|----------|
| `sm` | `640px+` | 小屏 | 大屏手机、竖屏平板 |
| `md` | `768px+` | 中屏 | 横屏平板、小笔记本 |
| `lg` | `1024px+` | 大屏 | 笔记本、标准桌面 |
| `xl` | `1280px+` | 特大屏 | 大桌面显示器 |

### 2.2 断点使用规范

```css
/* 基础样式（移动端） */
.element {
  display: block;
  padding: var(--space-4);
}

/* 平板及以上 (md) */
@media (min-width: 768px) {
  .element {
    display: flex;
    padding: var(--space-6);
  }
}

/* 桌面及以上 (lg) */
@media (min-width: 1024px) {
  .element {
    padding: var(--space-8);
  }
}
```

---

## 3. 移动优先实现

### 3.1 CSS 编写顺序

```css
/* 1. 基础样式（移动端默认） */
.component {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

/* 2. sm 断点 */
@media (min-width: 640px) {
  .component {
    flex-direction: row;
    gap: var(--space-6);
  }
}

/* 3. md 断点 */
@media (min-width: 768px) {
  .component {
    padding: var(--space-6);
  }
}

/* 4. lg 断点 */
@media (min-width: 1024px) {
  .component {
    gap: var(--space-8);
  }
}
```

### 3.2 常见布局转换

```css
/* 单列 → 双列 */
.stack-to-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}

@media (min-width: 768px) {
  .stack-to-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 隐藏 → 显示 */
.hide-on-mobile {
  display: none;
}

@media (min-width: 768px) {
  .hide-on-mobile {
    display: block;
  }
}

/* 紧凑 → 宽松 */
.compact-spacing {
  padding: var(--space-3);
}

@media (min-width: 768px) {
  .compact-spacing {
    padding: var(--space-6);
  }
}
```

---

## 4. 布局模式

### 4.1 单列布局（移动端默认）

```css
.page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}
```

### 4.2 两列布局（平板+）

```css
.two-column-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}

@media (min-width: 768px) {
  .two-column-layout {
    grid-template-columns: 250px 1fr;
    gap: var(--space-6);
  }
}
```

### 4.3 三列布局（桌面）

```css
.three-column-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}

@media (min-width: 768px) {
  .three-column-layout {
    grid-template-columns: 200px 1fr;
  }
}

@media (min-width: 1024px) {
  .three-column-layout {
    grid-template-columns: 200px 1fr 200px;
  }
}
```

### 4.4 网格自适应

```css
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}
```

---

## 5. 组件响应式

### 5.1 导航组件

```css
/* 移动端：底部导航或汉堡菜单 */
.nav-mobile {
  display: flex;
  flex-direction: column;
}

/* 桌面端：顶部水平导航 */
@media (min-width: 768px) {
  .nav-mobile {
    flex-direction: row;
  }
}
```

### 5.2 卡片组件

```css
.card {
  display: flex;
  flex-direction: column;
}

@media (min-width: 640px) {
  .card {
    flex-direction: row;
  }

  .card-image {
    width: 200px;
  }
}
```

### 5.3 表单组件

```css
.form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

@media (min-width: 768px) {
  .form-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }
}
```

---

## 6. 触摸优化

### 6.1 触摸目标

```css
/* 确保所有可交互元素满足 44x44px */
.touch-target {
  min-width: var(--hit-target-min);  /* 44px */
  min-height: var(--hit-target-min); /* 44px */
  padding: var(--space-2);
}

/* 紧凑列表中的触摸优化 */
.list-item {
  padding: var(--space-3) var(--space-2);
  min-height: 44px;
}
```

### 6.2 悬停状态处理

移动端没有悬停状态，但 hover 在触摸设备上会产生"粘滞"效果：

```css
/* 桌面端悬停效果 */
@media (hover: hover) and (pointer: fine) {
  .interactive:hover {
    background-color: var(--color-bg-hover);
    transform: translateY(-2px);
  }
}

/* 移动端不需要悬停效果 */
/* hover: hover 媒体查询确保只在支持悬停的设备上生效 */
```

### 6.3 点击延迟

```css
/* 移除 iOS 点击延迟 */
.no-delay {
  touch-action: manipulation;
}
```

---

## 7. 响应式内容

### 7.1 图片

```css
/* 响应式图片 */
.responsive-image {
  max-width: 100%;
  height: auto;
  display: block;
}
```

### 7.2 视频

```css
/* 视频容器保持 16:9 比例 */
.video-container {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 */
}

.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
```

### 7.3 表格

```css
/* 移动端表格转为卡片 */
@media (max-width: 640px) {
  .table-responsive {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .table-row {
    display: flex;
    flex-direction: column;
    padding: var(--space-3);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
  }

  .table-cell {
    display: flex;
    justify-content: space-between;
    padding: var(--space-1) 0;
  }
}
```

---

## 8. 断点速查

### 8.1 断点使用场景

| 场景 | 断点 | 调整内容 |
|------|------|----------|
| 单列→双列 | `md: 768px` | 侧边栏+主内容 |
| 隐藏→显示 | `md: 768px` | 桌面导航 |
| 紧凑→宽松 | `md: 768px` | 间距、内边距 |
| 小图→大图 | `lg: 1024px` | Hero 图片 |
| 2列→3列 | `lg: 1024px` | 特性网格 |

### 8.2 常见断点组合

```css
/* 手机优先 - 最大 639px */
/* sm+ - 640px+ */
/* md+ - 768px+ */
/* lg+ - 1024px+ */
/* xl+ - 1280px+ */
```

---

## 9. 响应式最佳实践

### 9.1 应该做

```css
/* ✓ 使用相对单位 */
.thing {
  width: 100%;
  max-width: 1280px;
  padding: var(--space-4);
}

/* ✓ 使用 min-width 媒体查询 */
@media (min-width: 768px) { }

/* ✓ 渐进增强 */
.element {
  /* 基础：单列 */
}
@media (min-width: 768px) {
  /* 增强：双列 */
}
@media (min-width: 1024px) {
  /* 进一步增强：三列 */
}

/* ✓ 触摸友好的点击区域 */
.touchable {
  min-height: var(--hit-target-min);
  min-width: var(--hit-target-min);
}
```

### 9.2 不应该做

```css
/* ✗ 使用 max-width 媒体查询 */
@media (max-width: 768px) { }

/* ✗ 固定宽度 */
.fixed {
  width: 1024px;
}

/* ✗ 硬编码像素值 */
.pixel {
  margin: 20px;
  padding: 15px;
}

/* ✗ 为所有元素设置响应式 */
.simple-element {
  font-size: 14px; /* 无需响应式 */
}
```

---

## 10. 设备模拟测试

### 10.1 推荐测试分辨率

| 设备 | 宽度 | 高度 | 断点 |
|------|------|------|------|
| iPhone SE | 375px | 667px | - |
| iPhone 14 | 390px | 844px | - |
| iPad Mini | 768px | 1024px | md |
| iPad Pro | 1024px | 1366px | lg |
| MacBook Air | 1440px | 900px | xl |

### 10.2 Chrome DevTools 设备模式

1. 打开 DevTools (F12)
2. 点击左上角设备切换图标
3. 选择预设设备或自定义尺寸
4. 旋转方向测试横屏布局
