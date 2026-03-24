# 爬取任务 Tab 改进设计规格

## 概述

改进知识库构建页面的爬取任务 Tab，解决以下问题：
1. 任务列表不支持滚动，新任务会挤出旧任务
2. 完成的任务无法删除，用户体验不佳
3. 任务状态显示不准确，需要支持"部分成功"等状态，并展示失败 URL 及原因

## 需求详细说明

### Issue 1: 任务列表滚动

**问题**: TaskList 组件没有滚动容器，任务数量增加时超出视口。

**解决方案**: 将 TaskList 包裹在 max-height 的滚动容器中。

```css
.taskListContainer {
  max-height: 500px;
  overflow-y: auto;
}
```

### Issue 2: 任务删除功能

**问题**: 已完成任务无法删除。

**解决方案**:
- 在 TaskCard 右侧添加删除按钮
- 仅在任务处于终态（completed/SUCCESS/FAILED）时启用删除
- 提供批量清除功能，带用户确认对话框

**删除语义（重要）**:
> 删除 CrawlTask 记录**仅删除任务历史本身**，不会级联删除已解析的 KnowledgeFile 记录。
> 成功爬取的 KnowledgeFile 记录保留在审核队列中。

**终态定义**:
```typescript
const TERMINAL_STATES = ['SUCCESS', 'FAILED', 'completed', 'failed'];
```

### Issue 3: 任务状态精细化

**问题**: 即使有失败的 URL，状态仍显示"成功"。

**解决方案**:
- 扩展后端 CrawlTask 模型，添加 `failed_urls` 字段存储失败详情
- 前端根据 success_count 和 fail_count 计算并显示精细化状态

**状态显示逻辑**:

| 条件 | 显示 | 样式 |
|------|------|------|
| `status == 'processing'` | "处理中" | spinning + processing |
| `status == 'pending'` | "等待中" | spinning + pending |
| `status == 'completed' && fail_count == 0` | "成功" | success |
| `status == 'completed' && fail_count > 0 && success_count > 0` | "部分成功" | warning (orange) |
| `status == 'completed' && success_count == 0` | "失败" | failed |
| `status == 'failed'` | "失败" | failed |

**失败详情展示**:
- 任务卡片底部添加"查看失败详情"折叠按钮
- 展开后列出所有失败 URL 及错误原因
- 使用 warning 颜色区分

### Issue 4: 重试失败链接 (UX Bonus)

**功能**: 对"部分成功"或"失败"状态的任务，提供"重试失败链接"按钮。

**行为**:
1. 用户点击"重试失败链接"
2. 弹出确认对话框，显示将重试的 URL 数量
3. 用户确认后，提取 `failed_urls` 中的 URL，提交到原有知识库
4. 创建新的 CrawlTask，开始爬取

**前置条件**: 任务必须有 `knowledge_id`（即通过 `batch-with-knowledge` 创建的任务）

---

## 后端变更

### 1. CrawlTask 模型扩展

**文件**: `backend/app/database/models/crawl_task.py`

```python
from typing import Optional, List, Dict, Any

class CrawlTask(SQLModel, table=True):
    # ... existing fields ...
    failed_urls: List[Dict[str, Any]] = Field(
        default=[],
        description="List of failed URLs with error details: [{url, error, timestamp}]"
    )
```

### 2. 更新 `update_task_progress` 方法

**签名变更**:
```python
def update_task_progress(
    task_id: str,
    success: bool,
    url: Optional[str] = None,
    error: Optional[str] = None,
) -> Optional[CrawlTask]:
```

**逻辑**:
- 当 `success=False` 时，将 `{url, error, timestamp}` 添加到 `failed_urls` 列表
- 当所有 URL 完成时，根据 success_count 和 fail_count 设置 status

### 3. 新增删除任务 API

**端点**: `DELETE /crawl/tasks/{task_id}`

**行为**:
- 仅删除 CrawlTask 记录
- 不影响 KnowledgeFile 记录
- 校验任务归属权

### 4. 新增重试失败 URL API

**端点**: `POST /crawl/tasks/{task_id}/retry-failed`

**行为**:
- 提取任务中的 `failed_urls`
- 创建新的 CrawlTask，total_urls = len(failed_urls)
- 返回新任务 ID

---

## 前端变更

### 1. API 类型扩展

**文件**: `frontend/src/features/build/api/crawl.ts`

```typescript
export interface FailedUrl {
  url: string;
  error: string;
  timestamp: string;
}

export interface CrawlTask {
  // ... existing fields ...
  failed_urls?: FailedUrl[];
}
```

### 2. buildStore 扩展

**新增**:

```typescript
interface BuildState {
  // ... existing fields ...

  // Actions
  removeTask: (taskId: string) => Promise<void>;
  retryFailedUrls: (taskId: string) => Promise<string | null>;
}
```

**removeTask 逻辑**:
```typescript
removeTask: async (taskId) => {
  await crawlApi.deleteTask(taskId);
  set((state) => ({
    tasks: state.tasks.filter((t) => t.id !== taskId),
  }));
},
```

**retryFailedUrls 逻辑**:
```typescript
retryFailedUrls: async (taskId) => {
  const task = get().tasks.find((t) => t.id === taskId);
  if (!task?.knowledge_id || !task.failed_urls?.length) return null;

  const failedUrls = task.failed_urls.map((f) => f.url);
  return get().submitBatchCrawl(failedUrls);
},
```

### 3. TaskCard 组件增强

**新增功能**:
- 状态显示逻辑更新（部分成功）
- 失败详情折叠/展开
- 删除按钮
- 重试按钮（仅部分成功/失败状态）

**Props 扩展**:
```typescript
interface TaskCardProps {
  task: CrawlTask;
  onDelete?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
}
```

### 4. TaskList 组件增强

**新增功能**:
- 滚动容器包裹
- 批量清除已完成任务按钮
- 确认对话框

### 5. 删除确认对话框

**使用项目已有的 UI 组件或创建确认对话框**:

```typescript
interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}
```

---

## 数据流

### 重试失败 URL 流程

```
User clicks "重试失败链接"
  → ConfirmDialog shows "将重试 N 个失败的链接"
  → User confirms
  → buildStore.retryFailedUrls(taskId)
    → crawlApi.retryFailed(taskId)
      → POST /crawl/tasks/{task_id}/retry-failed
        → Backend creates new CrawlTask with failed_urls
        → Returns new task_id
  → New task appears in list
  → Polling starts for new task
```

---

## 测试策略

### 后端测试
- `test_update_task_progress_records_failed_url`: 验证失败 URL 被正确记录
- `test_delete_task_preserves_knowledge_files`: 验证删除不级联
- `test_retry_failed_creates_new_task`: 验证重试创建新任务

### 前端测试
- `TaskCard.test.tsx`: 测试各种状态显示
- `buildStore.test.ts`: 测试 removeTask 和 retryFailedUrls
- `TaskList.test.tsx`: 测试滚动和批量删除

---

## 文件清单

### 后端
| 文件 | 变更 |
|------|------|
| `backend/app/database/models/crawl_task.py` | 添加 `failed_urls` 字段 |
| `backend/app/services/crawl/task_service.py` | 更新 `update_task_progress` 签名和逻辑 |
| `backend/app/api/v1/crawl.py` | 添加 DELETE 和 retry-failed 端点 |

### 前端
| 文件 | 变更 |
|------|------|
| `frontend/src/features/build/api/crawl.ts` | 添加类型和 API 方法 |
| `frontend/src/features/build/buildStore.ts` | 添加 removeTask, retryFailedUrls |
| `frontend/src/features/build/components/CrawlTab/TaskCard.tsx` | 增强显示和交互 |
| `frontend/src/features/build/components/CrawlTab/TaskCard.module.css` | 添加新样式 |
| `frontend/src/features/build/components/CrawlTab/TaskList.tsx` | 滚动容器和批量删除 |
| `frontend/src/features/build/components/CrawlTab/TaskList.module.css` | 添加滚动样式 |
| `frontend/src/features/build/components/ui/ConfirmDialog.tsx` | 新增确认对话框组件 |
