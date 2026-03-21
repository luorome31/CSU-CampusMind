# CampusMind 前端样式文档索引

> 本文档为 CampusMind Design System 样式文档的导航索引。

---

## 文档列表

| 编号 | 文档 | 说明 |
|------|------|------|
| 01 | [Design Tokens 参考文档](./01-DESIGN_TOKENS_REFERENCE.md) | 所有 CSS 变量的完整参考 |
| 02 | [颜色系统](./02-COLOR_SYSTEM.md) | 色彩理念、搭配规范、无障碍要求 |
| 03 | [排版设计指南](./03-TYPOGRAPHY_GUIDE.md) | 字体、字号、行高、字间距规范 |
| 04 | [组件开发规范](./04-COMPONENT_GUIDELINES.md) | 组件开发标准、API 设计、无障碍 |
| 05 | [间距系统](./05-SPACING_SYSTEM.md) | 4px 网格系统、布局间距规范 |
| 06 | [图标使用指南](./06-ICON_GUIDELINES.md) | Lucide React 使用规范 |
| 07 | [响应式设计指南](./07-RESPONSIVE_DESIGN.md) | 移动优先、断点系统、布局模式 |

---

## 文档关系图

```
Design Tokens Reference (01)
    │
    ├──▶ Color System (02)
    │       └── Typography Guide (03)
    │
    ├──▶ Spacing System (05)
    │       └── Responsive Design (07)
    │
    └──▶ Component Guidelines (04)
            └── Icon Guidelines (06)
```

---

## 快速入门

### 新开发者

1. 先阅读 **Design Tokens Reference** 了解所有可用变量
2. 阅读 **Component Guidelines** 了解组件开发标准
3. 参考 **Playground** (`npm run playground`) 查看组件实际效果

### 添加新组件

1. 参考 **Component Guidelines** 的组件模板
2. 使用 **Design Tokens** 中的 CSS 变量
3. 确保响应式支持（参考 **Responsive Design**）
4. 添加无障碍支持（参考 **Component Guidelines**）

### 样式开发

1. 颜色：参考 **Color System**
2. 排版：参考 **Typography Guide**
3. 间距：参考 **Spacing System**
4. 图标：参考 **Icon Guidelines**

---

## 相关资源

- ** Playground**: `npm run playground` → http://localhost:5174/playground.html
- ** 设计系统 Manifest**: [DESIGN_SYSTEM_MANIFEST.md](./DESIGN_SYSTEM_MANIFEST.md)
- ** GitHub 仓库**: CampusMind/frontend

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-03-21 | 1.0.0 | 初始文档创建 |
