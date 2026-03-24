# Phase 3 Design: Knowledge List & Knowledge Detail View

## 1. Overview

实现知识库的浏览功能（只读模式），包括：
- 知识库列表页面
- 知识库文件列表页面
- 文件详情查看页面

**参考文档：**
- `frontend/docs/knowledge_base_frontend_integration_guide.md` - 场景一
- `backend/docs/api/endpoints-knowledge.md` - 知识库 CRUD 接口
- `backend/docs/api/endpoints-knowledge-file.md` - 知识文件管理接口

## 2. Route Structure

```
/knowledge                              → KnowledgeListPage
/knowledge/:kb_id                       → KnowledgeFileListPage
/knowledge/:kb_id/files/:file_id        → KnowledgeFileDetailPage
```

## 3. API Endpoints

| 接口 | Method | 用途 |
|------|--------|------|
| `/api/v1/users/{user_id}/knowledge` | GET | 获取用户知识库列表 |
| `/api/v1/knowledge/{knowledge_id}/files` | GET | 获取知识库文件列表 |
| `/api/v1/knowledge_file/{file_id}/content` | GET | 获取文件 Markdown 内容 |

## 4. Data Models

### KnowledgeBase
```typescript
interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  user_id: string;
  create_time: string;
  update_time: string;
}
```

### KnowledgeFile
```typescript
interface KnowledgeFile {
  id: string;
  file_name: string;
  knowledge_id: string;
  user_id: string;
  status: 'process' | 'success' | 'fail' | 'pending_verify' | 'verified' | 'indexing' | 'indexed';
  oss_url: string;
  file_size: number;
  create_time: string;
  update_time: string;
}
```

## 5. Components

### 5.1 New Components

| 组件 | 路径 | 描述 |
|------|------|------|
| `KnowledgeCard` | `components/knowledge/KnowledgeCard/` | 知识库卡片，显示名称、描述、文件数、更新时间 |
| `FileTable` | `components/knowledge/FileTable/` | 文件列表表格，含状态 Badge |
| `FileContentViewer` | `components/knowledge/FileContentViewer/` | Markdown 内容查看器，含语法高亮 |
| `KnowledgeListPage` | `features/knowledge/KnowledgeListPage.tsx` | 知识库列表页 |
| `KnowledgeFileListPage` | `features/knowledge/KnowledgeFileListPage.tsx` | 知识库文件列表页 |
| `KnowledgeFileDetailPage` | `features/knowledge/KnowledgeFileDetailPage.tsx` | 文件详情页 |

### 5.2 Existing Components to Reuse

- `Badge` - 状态徽章
- `Button` - 返回按钮
- `Card` - 卡片容器
- `Spinner` - 加载状态

## 6. State Management

### knowledgeListStore (Zustand)

```typescript
interface KnowledgeListState {
  knowledgeBases: KnowledgeBase[];
  currentKB: KnowledgeBase | null;
  files: KnowledgeFile[];
  currentFile: KnowledgeFile | null;
  currentFileContent: string;
  isLoadingKBs: boolean;
  isLoadingFiles: boolean;
  isLoadingContent: boolean;
  error: string | null;
}

interface KnowledgeListActions {
  fetchKnowledgeBases: () => Promise<void>;
  fetchFiles: (kbId: string) => Promise<void>;
  fetchFileContent: (fileId: string) => Promise<void>;
  setCurrentKB: (kb: KnowledgeBase | null) => void;
  clearError: () => void;
}
```

## 7. Page Layouts

### 7.1 KnowledgeListPage (`/knowledge`)

```
┌─────────────────────────────────────────────────────┐
│  知识库                                            │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │ 知识库 A   │  │ 知识库 B   │  │ 知识库 C   ││
│  │            │  │            │  │            ││
│  │ 描述...    │  │ 描述...    │  │ 描述...    ││
│  │            │  │            │  │            ││
│  │ 3 个文件   │  │ 5 个文件   │  │ 2 个文件   ││
│  │ 2024-01-01│  │ 2024-01-02│  │ 2024-01-03││
│  └─────────────┘  └─────────────┘  └─────────────┘│
└─────────────────────────────────────────────────────┘
```

- 响应式网格：1列(mobile) / 2列(tablet) / 3列(desktop)
- 每个卡片：KB名称、描述、文件数 Badge、更新时间
- 点击卡片跳转 `/knowledge/:kb_id`

### 7.2 KnowledgeFileListPage (`/knowledge/:kb_id`)

```
┌─────────────────────────────────────────────────────┐
│  ← 返回  知识库 A                                    │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ 文件名           状态         大小    更新时间│  │
│  ├──────────────────────────────────────────────┤  │
│  │ document.md     ● 成功     1.2KB   2024-01-01│  │
│  │ notes.md        ◐ 处理中   0.5KB   2024-01-02│  │
│  │ guide.pdf       ✗ 失败     -       2024-01-03│  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

- 状态 Badge 颜色映射：
  - `process` / `indexing` → info (蓝)
  - `success` / `verified` / `indexed` → success (绿)
  - `fail` → error (红)
  - `pending_verify` → warning (黄)
- 点击行跳转 `/knowledge/:kb_id/files/:file_id`

### 7.3 KnowledgeFileDetailPage (`/knowledge/:kb_id/files/:file_id`)

```
┌─────────────────────────────────────────────────────┐
│  ← 返回  document.md                         只读   │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │                                              │  │
│  │  # Markdown Content                          │  │
│  │                                              │  │
│  │  ## Code Block                               │  │
│  │  ```python                                  │  │
│  │  def hello():                               │  │
│  │      print("world")                        │  │
│  │  ```                                        │  │
│  │                                              │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

- Markdown 使用 `react-markdown` 渲染
- 代码块使用 `react-syntax-highlighter` 语法高亮
- 只读模式，无编辑功能

## 8. Styling

- 使用现有 CSS 变量（`colors.css`）
- 复用 `Card`、`Badge`、`Button` 组件
- 自定义 CSS：
  - `KnowledgeListPage.css` - 网格布局
  - `KnowledgeFileListPage.css` - 表格样式
  - `FileContentViewer.css` - Markdown 渲染样式

## 9. Status Badge Mapping

| Status | Badge variant | 说明 |
|--------|---------------|------|
| `process` | info | 处理中 |
| `indexing` | info | 索引构建中 |
| `success` | success | 成功 |
| `verified` | success | 已验证 |
| `indexed` | success | 已索引 |
| `fail` | error | 失败 |
| `pending_verify` | warning | 待验证 |

## 10. Error Handling

- API 错误：显示错误消息到页面
- 空状态：显示"暂无知识库"或"暂无文件"
- 加载状态：显示 Spinner

## 11. Testing

- `knowledgeListStore.test.ts` - 状态管理测试
- `KnowledgeCard.test.tsx` - 卡片组件测试
- `FileTable.test.tsx` - 表格组件测试
- `FileContentViewer.test.tsx` - Markdown 查看器测试
- `KnowledgeListPage.test.tsx` - 页面组件测试

## 12. Dependencies

需安装：
- `react-syntax-highlighter` - 代码语法高亮
