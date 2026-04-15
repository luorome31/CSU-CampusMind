# Knowledge 模块设计方案

## 概述

Mobile 端 Knowledge 模块（F-023 ~ F-029）实现知识库浏览与 RAG 上下文控制功能。

## 架构设计

```
KnowledgeScreen (Tab 页面)
├── RAG 控制面板（可折叠）
│   ├── RAG 开关
│   └── KnowledgeSelector（勾选 KB 附加到对话）
├── KB 列表（KnowledgeCard 网格）
└── Stack Navigator（嵌套）
    ├── KnowledgeDetailScreen（KB → 文件列表）
    │   └── FileTable（文件列表）
    └── FileDetailScreen（文件内容）
        └── FileContentViewer（Markdown 查看器）

Build 入口按钮 → 跳转 BuildScreen
```

## 功能决策

| 决策项 | 选择 | 原因 |
|--------|------|------|
| 新建 KB | 不需要 | 复杂管理引导去 Web 端 |
| RAG 控制位置 | 折叠收起 | 节省空间，知识库浏览为主 |
| 文件列表展示 | 列表模式 | 与 Web 一致，信息完整 |
| 文件详情 | 仅查看 | 复杂编辑交给 BuildScreen |

## 组件清单

| 组件 | 职责 | 文件位置 |
|------|------|----------|
| `KnowledgeListStore` | KB列表、文件列表、文件内容状态管理 | `features/knowledge/knowledgeStore.ts` |
| `KnowledgeCard` | KB卡片展示（名称/描述/文件数） | `components/knowledge/KnowledgeCard/` |
| `FileTable` | 文件列表（名称/状态Badge/时间） | `components/knowledge/FileTable/` |
| `FileContentViewer` | Markdown 内容渲染 | `components/knowledge/FileContentViewer/` |
| `RAGSwitch` | RAG 开关 + 知识选择器 | `components/knowledge/RAGSwitch/` |
| `KnowledgeScreen` | KB列表页容器 | `screens/KnowledgeScreen.tsx` |
| `KnowledgeDetailScreen` | 文件列表页 | `screens/KnowledgeDetailScreen.tsx` |
| `FileDetailScreen` | 文件内容页 | `screens/FileDetailScreen.tsx` |

## 移动端适配要点

1. **RAG 控制折叠** - 默认收起，Header 按钮展开
2. **嵌套导航** - 与 BuildScreen 结构一致，使用 Stack Navigator
3. **返回按钮** - 统一使用 `ChevronLeft` 图标
4. **加载状态** - Spinner 居中展示
5. **空状态** - 友好提示文案
6. **Build 入口** - Header 右侧按钮，跳转 BuildScreen

## API 依赖

- `GET /knowledge` - 获取 KB 列表
- `GET /knowledge/{kb_id}/files` - 获取文件列表
- `GET /knowledge_file/{file_id}/content` - 获取文件内容

## 与 Web 端差异

| 方面 | Web 端 | Mobile 端 |
|------|--------|-----------|
| 新建 KB | 支持 | 不支持 |
| 编辑文件 | 支持 | 仅查看 |
| RAG 控制 | 内嵌 ChatInput | 折叠在 KnowledgeTab |
| 导航 | 路由跳转 | Stack Navigator |
