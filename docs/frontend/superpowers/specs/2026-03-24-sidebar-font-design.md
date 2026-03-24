# Design: Sidebar Collapse + LXGW WenKai Screen Font

**Date**: 2026-03-24
**Status**: Approved

---

## Feature 1: Sidebar Collapse/Expand

### Design Direction

- **Aesthetic**: Warm Paper 风格下的极简抽屉交互
- **Behavior**: 侧边栏完全滑出主内容区左侧，主内容区无缝扩展
- **Trigger**: 主内容区左侧边缘悬浮圆角按钮（PanelLeft icon），点击展开

### Implementation

| File | Change |
|------|--------|
| `src/routes.tsx` | `LayoutWithSidebar` 添加 `sidebarCollapsed` state，传递 `className` 给 layout container |
| `src/index.css` | `.layout-main` 根据 collapsed 状态动态调整 `margin-left: var(--sidebar-width)` → `0` |
| `src/components/layout/Sidebar/Sidebar.css` | 添加 `.sidebar.collapsed { transform: translateX(-100%) }` + 过渡动画 |
| `src/components/layout/Sidebar/Sidebar.tsx` | 添加 collapse toggle button，接收 `isCollapsed` 和 `onToggle` props |

### CSS Animation

```css
.sidebar {
  transition: transform 0.3s var(--ease-spring, cubic-bezier(0.16, 1, 0.3, 1));
}
.sidebar.collapsed {
  transform: translateX(-100%);
}
```

### Floating Expand Button

- 位于主内容区左侧边缘，居中于视口高度
- 使用 glassmorphism 风格（与 sidebar 一致）
- PanelLeft icon from lucide-react
- 悬浮时 scale 微微放大

---

## Feature 2: LXGW WenKai Screen Font

### Design Direction

- **Font**: LXGW WenKai Screen (屏幕阅读版) — 针对屏幕显示优化，字形清晰锐利
- **Style**: 霞鹜文楷风格，中文字体优先

### Implementation

| File | Change |
|------|--------|
| `src/main.tsx` | 添加 `import 'lxgwwenkai-screen-webfont/style.css'` |
| `src/styles/tokens/typography.css` | 更新 `--font-sans: "LXGW WenKai Screen", "DS-Project", sans-serif` |
| `vite.config.ts` | 添加 alias 指向包目录（Vite 6 需要，无 exports 字段的包需要此配置） |

### NPM Package

```
npm install --save lxgw-wenkai-screen-webfont
```

### Vite 配置说明

该包没有 `exports` 字段，Vite 6 使用严格的新模块解析算法无法直接通过包名解析。在 `vite.config.ts` 中添加 alias 指向包目录：

```ts
resolve: {
  alias: {
    'lxgwwenkai-screen-webfont': path.resolve(
      __dirname,
      'node_modules/lxgw-wenkai-screen-webfont'
    ),
  },
},
```

这样 Vite 通过 alias 解析到包目录后，会读取 `package.json` 的 `main`/`style` 字段找到 `style.css`，再正确解析其中 `@import url(...)` 的相对路径。

---

## Acceptance Criteria

1. Sidebar 点击按钮可收起/展开，动画流畅（0.3s spring curve）
2. 收起后主内容区无缝扩展，占据全宽
3. LXGW WenKai Screen 字体正确加载，中文显示正常
4. `npm run build` 打包通过
5. `npm run test:run` 所有单元测试通过
6. 更新 `frontend-progress-log.md`
