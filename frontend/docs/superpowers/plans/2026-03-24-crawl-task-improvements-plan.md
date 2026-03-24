# 爬取任务 Tab 改进实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 改进爬取任务 Tab，实现滚动列表、任务删除、部分成功状态、重试失败链接功能

**Architecture:** 后端扩展 CrawlTask 模型添加 failed_urls 字段，前端增强 TaskCard/TaskList 组件，添加 ConfirmDialog 对话框组件

**Tech Stack:** FastAPI + SQLModel, React + Zustand + TypeScript

---

## 文件结构

### Backend
- Modify: `backend/app/database/models/crawl_task.py` - 添加 failed_urls 字段
- Modify: `backend/app/services/crawl/task_service.py` - 更新 update_task_progress 签名和逻辑
- Modify: `backend/app/services/crawl/task_worker.py` - 传递 url 和 error 参数
- Modify: `backend/app/api/v1/crawl.py` - 添加 DELETE 和 retry-failed 端点

### Frontend
- Modify: `frontend/src/features/build/api/crawl.ts` - 添加类型和 API 方法
- Modify: `frontend/src/features/build/buildStore.ts` - 添加 removeTask, retryFailedUrls
- Create: `frontend/src/features/build/components/ui/ConfirmDialog.tsx` - 确认对话框
- Modify: `frontend/src/features/build/components/CrawlTab/TaskCard.tsx` - 增强状态显示/删除/重试
- Modify: `frontend/src/features/build/components/CrawlTab/TaskCard.module.css` - 添加新样式
- Modify: `frontend/src/features/build/components/CrawlTab/TaskList.tsx` - 滚动容器/批量删除
- Modify: `frontend/src/features/build/components/CrawlTab/TaskList.module.css` - 添加滚动样式

---

## Chunk 0: 澄清状态值约定

**重要**: 后端和前端使用不同的状态值风格：

| 后端常量 | 值 | 说明 |
|----------|-----|------|
| `CrawlTaskStatus.PROCESSING` | `"processing"` | 小写 |
| `CrawlTaskStatus.COMPLETED` | `"completed"` | 小写 |
| `CrawlTaskStatus.FAILED` | `"failed"` | 小写 |

前端 `CrawlTask.status` 类型定义:
```typescript
status: 'pending' | 'processing' | 'SUCCESS' | 'FAILED' | 'completed' | 'failed';
```

**Partial Success 判断逻辑**（前端）:
```typescript
// 部分成功: completed + 有成功 + 有失败
if (task.status === 'completed' && task.fail_count > 0 && task.success_count > 0)
```

---

## Chunk 1: Backend - CrawlTask 模型扩展

### Task 1.1: 修改 CrawlTask 模型

**Files:**
- Modify: `backend/app/database/models/crawl_task.py:1-44`

- [ ] **Step 1: 添加 failed_urls 字段到模型**

编辑 `backend/app/database/models/crawl_task.py`，在 `CrawlTask` 类中添加 `failed_urls` 字段：

```python
from typing import Optional, List, Dict, Any

class CrawlTask(SQLModel, table=True):
    """Crawl task table - stores the progress and status of batch crawling jobs"""
    __tablename__ = "crawl_task"

    id: str = Field(default=None, primary_key=True, description="Task ID")
    knowledge_id: Optional[str] = Field(default=None, description="Optional associated knowledge base ID")
    user_id: str = Field(index=True, description="User who initiated the task")
    total_urls: int = Field(default=0, description="Total number of URLs to crawl")
    completed_urls: int = Field(default=0, description="Number of completed URLs (both success and fail)")
    success_count: int = Field(default=0, description="Number of successfully crawled URLs")
    fail_count: int = Field(default=0, description="Number of failed URLs")
    status: str = Field(default=CrawlTaskStatus.PROCESSING, description="Status: processing/completed/failed")
    failed_urls: List[Dict[str, Any]] = Field(
        default=[],
        description="List of failed URLs with error details: [{url, error, timestamp}]"
    )
    create_time: datetime = Field(default_factory=datetime.now, description="Task creation time")
    update_time: datetime = Field(default_factory=datetime.now, description="Task last update time")

    def to_dict(self):
        return {
            "id": self.id,
            "knowledge_id": self.knowledge_id,
            "user_id": self.user_id,
            "total_urls": self.total_urls,
            "completed_urls": self.completed_urls,
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "status": self.status,
            "failed_urls": self.failed_urls,  # <-- IMPORTANT: include failed_urls in API response
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }
```

- [ ] **Step 2: 验证模型更新**

运行: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.database.models.crawl_task import CrawlTask; print('Model OK')"`
Expected: `Model OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/database/models/crawl_task.py
git commit -m "feat(crawl): add failed_urls field to CrawlTask model"
```

---

### Task 1.2: 更新 task_service 的 update_task_progress 方法

**Files:**
- Modify: `backend/app/services/crawl/task_service.py:44-68`

- [ ] **Step 1: 更新 update_task_progress 方法签名和逻辑**

编辑 `backend/app/services/crawl/task_service.py`，替换 `update_task_progress` 方法：

```python
@staticmethod
def update_task_progress(
    task_id: str,
    success: bool,
    url: Optional[str] = None,
    error: Optional[str] = None,
) -> Optional[CrawlTask]:
    """Atomically increment completed_urls and success/fail counts"""
    from datetime import datetime

    with Session(engine) as session:
        statement = select(CrawlTask).where(CrawlTask.id == task_id)
        task = session.exec(statement).first()
        if not task:
            return None

        task.completed_urls += 1
        if success:
            task.success_count += 1
        else:
            task.fail_count += 1
            # Record failed URL details
            if url:
                task.failed_urls = task.failed_urls + [{
                    "url": url,
                    "error": error or "Unknown error",
                    "timestamp": datetime.now().isoformat()
                }]

        if task.completed_urls >= task.total_urls:
            # Set terminal status based on results
            if task.success_count == 0:
                task.status = CrawlTaskStatus.FAILED
            elif task.fail_count == 0:
                task.status = CrawlTaskStatus.COMPLETED
            else:
                # Partial success - keep as completed but with failures
                task.status = CrawlTaskStatus.COMPLETED

        task.update_time = datetime.now()
        session.commit()
        session.refresh(task)
        return task
```

- [ ] **Step 2: 验证更新**

运行: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.services.crawl.task_service import CrawlTaskService; import inspect; sig = inspect.signature(CrawlTaskService.update_task_progress); print('Params:', list(sig.parameters.keys()))"`
Expected: `Params: ['task_id', 'success', 'url', 'error']`

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/crawl/task_service.py
git commit -m "feat(crawl): update update_task_progress to record failed URL details"
```

---

### Task 1.3: 更新 task_worker 传递 url 和 error

**Files:**
- Modify: `backend/app/services/crawl/task_worker.py:36-52` 和 `87-113`

- [ ] **Step 1: 更新 task_worker 中的 _crawl_one 函数**

编辑 `backend/app/services/crawl/task_worker.py`，更新两个 `_crawl_one` 函数以传递 url 和 error：

在 `process_batch_crawl` 中 (约 line 37-52):
```python
async def _crawl_one(url: str):
    try:
        result = await crawler.arun(url=url, config=run_config, session_id="batch")
        if not result.success:
            CrawlTaskService.update_task_progress(task_id, success=False, url=url, error=result.error_message)
            return

        if store_to_oss:
            storage_key = crawl_service.generate_storage_key(url)
            content = result.markdown.raw_markdown.encode("utf-8")
            storage_client.upload_content(storage_key, content)

        CrawlTaskService.update_task_progress(task_id, success=True, url=url)
    except Exception as e:
        logger.error(f"Error crawling {url}: {e}")
        CrawlTaskService.update_task_progress(task_id, success=False, url=url, error=str(e))
```

在 `process_batch_crawl_with_knowledge` 中 (约 line 87-113):
```python
async def _crawl_one(url: str):
    try:
        result = await crawler.arun(url=url, config=run_config, session_id="batch_k")
        if not result.success:
            CrawlTaskService.update_task_progress(task_id, success=False, url=url, error=result.error_message)
            return

        storage_key = crawl_service.generate_storage_key(url)
        content = result.markdown.raw_markdown.encode("utf-8")
        oss_url = storage_client.upload_content(storage_key, content)

        file_name = storage_key.split("/")[-1]
        knowledge_file = KnowledgeFileService.create_knowledge_file(
            file_name=file_name,
            knowledge_id=knowledge_id,
            user_id=user_id,
            oss_url=oss_url,
            object_name=storage_key,
            file_size=len(content),
        )

        # Update status to PENDING_VERIFY instead of indexing right away
        KnowledgeFileService.update_file_status(knowledge_file.id, FileStatus.PENDING_VERIFY)
        CrawlTaskService.update_task_progress(task_id, success=True, url=url)
    except Exception as e:
        logger.error(f"Error crawling {url}: {e}")
        CrawlTaskService.update_task_progress(task_id, success=False, url=url, error=str(e))
```

- [ ] **Step 2: 验证语法**

运行: `cd /home/luorome/software/CampusMind/backend && uv run python -m py_compile app/services/crawl/task_worker.py`
Expected: 无输出（成功）

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/crawl/task_worker.py
git commit -m "feat(crawl): pass url and error to update_task_progress"
```

---

## Chunk 2: Backend - API 端点

### Task 2.1: 添加删除任务 API

**Files:**
- Modify: `backend/app/api/v1/crawl.py`
- Modify: `backend/app/services/crawl/task_service.py`

- [ ] **Step 1: 添加 delete_task 到 task_service**

编辑 `backend/app/services/crawl/task_service.py`，在类末尾添加 `delete_task` 方法：

```python
@staticmethod
def delete_task(task_id: str) -> bool:
    """Delete a crawl task by ID (does not cascade to KnowledgeFile records)"""
    with Session(engine) as session:
        statement = select(CrawlTask).where(CrawlTask.id == task_id)
        task = session.exec(statement).first()
        if not task:
            return False

        session.delete(task)
        session.commit()
        return True
```

- [ ] **Step 2: 添加 DELETE 端点**

在 `backend/app/api/v1/crawl.py` 末尾添加：

```python
@router.delete("/crawl/tasks/{task_id}")
async def delete_crawl_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a crawl task (only deletes task record, not KnowledgeFile records)"""
    task = CrawlTaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Ownership check
    if task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No permission to delete this task")

    CrawlTaskService.delete_task(task_id)
    return {"success": True, "message": "Task deleted"}
```

- [ ] **Step 3: 验证 task_service 有 delete_task 方法**

运行: `cd /home/luorome/software/CampusMind/backend && uv run python -m py_compile app/api/v1/crawl.py`
Expected: 无输出

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/crawl.py backend/app/services/crawl/task_service.py
git commit -m "feat(crawl): add DELETE endpoint and delete_task service method"
```

---

### Task 2.2: 添加重试失败 URL API

**Files:**
- Modify: `backend/app/api/v1/crawl.py`

- [ ] **Step 1: 添加 retry-failed 端点**

在 `backend/app/api/v1/crawl.py` 末尾添加：

```python
class RetryFailedResponse(BaseModel):
    """Response model for retry failed URLs"""
    task_id: str
    status: str
    message: str
    retry_count: int


@router.post("/crawl/tasks/{task_id}/retry-failed", response_model=RetryFailedResponse)
async def retry_failed_urls(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Retry failed URLs from an existing task"""
    task = CrawlTaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Ownership check
    if task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No permission to retry this task")

    # Check if task has failed_urls
    if not task.failed_urls:
        raise HTTPException(status_code=400, detail="No failed URLs to retry")

    # Extract URLs from failed_urls
    failed_url_list = [f["url"] for f in task.failed_urls if "url" in f]
    if not failed_url_list:
        raise HTTPException(status_code=400, detail="No valid URLs to retry")

    # Create new task with failed URLs
    new_task = CrawlTaskService.create_task(
        user_id=current_user["user_id"],
        total_urls=len(failed_url_list),
        knowledge_id=task.knowledge_id,
    )

    # Start background processing
    from app.services.crawl.task_worker import process_batch_crawl_with_knowledge

    # Note: This will use the original knowledge_id if available
    background_tasks = BackgroundTasks()
    background_tasks.add_task(
        process_batch_crawl_with_knowledge,
        task_id=new_task.id,
        urls=failed_url_list,
        knowledge_id=task.knowledge_id or "",
        user_id=current_user["user_id"],
    )

    # The background task needs to be added to the app's background tasks
    # For now, return the task_id and let the client poll
    return RetryFailedResponse(
        task_id=new_task.id,
        status=new_task.status,
        message=f"Retry task created for {len(failed_url_list)} URLs",
        retry_count=len(failed_url_list),
    )
```

**注意**: 上述 BackgroundTasks 方案需要修改。实际上需要通过 app 级别的 background_tasks 队列。更好的方案是在返回响应后立即触发处理。修改为：

```python
@router.post("/crawl/tasks/{task_id}/retry-failed", response_model=RetryFailedResponse)
async def retry_failed_urls(
    task_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Retry failed URLs from an existing task"""
    task = CrawlTaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Ownership check
    if task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No permission to retry this task")

    # Check if task has failed_urls
    if not task.failed_urls:
        raise HTTPException(status_code=400, detail="No failed URLs to retry")

    # Extract URLs from failed_urls
    failed_url_list = [f["url"] for f in task.failed_urls if "url" in f]
    if not failed_url_list:
        raise HTTPException(status_code=400, detail="No valid URLs to retry")

    # Create new task with failed URLs
    new_task = CrawlTaskService.create_task(
        user_id=current_user["user_id"],
        total_urls=len(failed_url_list),
        knowledge_id=task.knowledge_id,
    )

    # Schedule background processing
    from app.services.crawl.task_worker import process_batch_crawl_with_knowledge
    background_tasks.add_task(
        process_batch_crawl_with_knowledge,
        task_id=new_task.id,
        urls=failed_url_list,
        knowledge_id=task.knowledge_id or "",
        user_id=current_user["user_id"],
    )

    return RetryFailedResponse(
        task_id=new_task.id,
        status=new_task.status,
        message=f"Retry task created for {len(failed_url_list)} URLs",
        retry_count=len(failed_url_list),
    )
```

- [ ] **Step 2: 测试 API 语法**

运行: `cd /home/luorome/software/CampusMind/backend && uv run python -m py_compile app/api/v1/crawl.py`
Expected: 无输出

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/crawl.py
git commit -m "feat(crawl): add retry-failed endpoint for re-crawling failed URLs"
```

### Task 2.3: 后端验证

- [ ] **Step 1: 运行后端测试验证现有功能不受影响**

运行: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/ -v --tb=short -x 2>&1 | tail -30`
Expected: 所有测试通过（跳过 e2e）

- [ ] **Step 2: 验证 API 可以启动**

运行: `cd /home/luorome/software/CampusMind/backend && timeout 10 uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 2>&1 || true`
Expected: 无导入错误

---

## Chunk 3: Frontend - API 类型和 Methods

### Task 3.1: 扩展前端 API 类型

**Files:**
- Modify: `frontend/src/features/build/api/crawl.ts`

- [ ] **Step 1: 添加 FailedUrl 类型和更新 CrawlTask 接口**

编辑 `frontend/src/features/build/api/crawl.ts`:

```typescript
import { apiClient } from '../../../api/client';

export interface FailedUrl {
  url: string;
  error: string;
  timestamp: string;
}

export interface CrawlTask {
  id: string;
  knowledge_id: string;
  user_id: string;
  total_urls: number;
  completed_urls: number;
  success_count: number;
  fail_count: number;
  status: 'pending' | 'processing' | 'SUCCESS' | 'FAILED' | 'completed' | 'failed';
  failed_urls?: FailedUrl[];
  create_time: string;
  update_time: string;
}

interface BatchCrawlResponse {
  task_id: string;
  status: string;
  message: string;
}

class CrawlApi {
  async submitBatchCrawl(urls: string[], knowledgeId: string): Promise<string> {
    const response = await apiClient.post<BatchCrawlResponse>('/crawl/batch-with-knowledge', {
      urls,
      knowledge_id: knowledgeId,
    });
    return response.task_id;
  }

  async fetchTasks(): Promise<CrawlTask[]> {
    return apiClient.get<CrawlTask[]>('/crawl/tasks');
  }

  async fetchTaskProgress(taskId: string): Promise<CrawlTask> {
    return apiClient.get<CrawlTask>(`/crawl/tasks/${taskId}`);
  }

  async deleteTask(taskId: string): Promise<void> {
    await apiClient.delete(`/crawl/tasks/${taskId}`);
  }

  async retryFailed(taskId: string): Promise<{ task_id: string; retry_count: number }> {
    return apiClient.post(`/crawl/tasks/${taskId}/retry-failed`, {});
  }
}

export const crawlApi = new CrawlApi();
```

- [ ] **Step 2: 验证 TypeScript 类型**

运行: `cd /home/luorome/software/CampusMind/frontend && npx tsc --noEmit --skipLibCheck src/features/build/api/crawl.ts 2>&1 || true`
Expected: 无错误

**注意**: 如果单独文件检查失败，运行完整类型检查：
```bash
cd /home/luorome/software/CampusMind/frontend && npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/build/api/crawl.ts
git commit -m "feat(build): add FailedUrl type and deleteTask/retryFailed API methods"
```

---

## Chunk 4: Frontend - ConfirmDialog 组件

### Task 4.1: 创建 ConfirmDialog 组件

**Files:**
- Create: `frontend/src/features/build/components/ui/ConfirmDialog.tsx`

- [ ] **Step 1: 创建 ConfirmDialog 组件**

创建 `frontend/src/features/build/components/ui/ConfirmDialog.tsx`:

```typescript
import React from 'react';
import styles from './ConfirmDialog.module.css';

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  danger?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  title,
  message,
  confirmText = '确认',
  cancelText = '取消',
  onConfirm,
  onCancel,
  danger = false,
}) => {
  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onCancel}>
      <div className={styles.dialog} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h3 className={styles.title}>{title}</h3>
        </div>
        <div className={styles.content}>
          <p>{message}</p>
        </div>
        <div className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onCancel}>
            {cancelText}
          </button>
          <button
            className={`${styles.confirmBtn} ${danger ? styles.danger : ''}`}
            onClick={onConfirm}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};
```

- [ ] **Step 2: 创建 ConfirmDialog CSS 模块**

创建 `frontend/src/features/build/components/ui/ConfirmDialog.module.css`:

```css
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: var(--color-bg-surface, #fff);
  border-radius: var(--radius-md, 8px);
  min-width: 320px;
  max-width: 480px;
  box-shadow: var(--shadow-lg, 0 10px 25px rgba(0, 0, 0, 0.15));
}

.header {
  padding: var(--space-4, 16px) var(--space-6, 24px);
  border-bottom: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
}

.title {
  margin: 0;
  font-size: var(--text-lg, 18px);
  font-weight: 600;
  color: var(--color-text-primary, #3b3d3f);
}

.content {
  padding: var(--space-6, 24px);
}

.content p {
  margin: 0;
  font-size: var(--text-base, 16px);
  color: var(--color-text-secondary, #666);
  line-height: 1.5;
}

.footer {
  padding: var(--space-4, 16px) var(--space-6, 24px);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3, 12px);
  border-top: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
}

.cancelBtn,
.confirmBtn {
  padding: var(--space-2, 8px) var(--space-4, 16px);
  border-radius: var(--radius-sm, 4px);
  font-size: var(--text-sm, 14px);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancelBtn {
  background: none;
  border: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  color: var(--color-text-secondary, #666);
}

.cancelBtn:hover {
  background: var(--color-bg-hover, rgba(83, 125, 150, 0.05));
}

.confirmBtn {
  background: var(--color-accent, #537d96);
  border: none;
  color: #fff;
}

.confirmBtn:hover {
  opacity: 0.9;
}

.confirmBtn.danger {
  background: var(--color-error, #ef4444);
}
```

- [ ] **Step 3: 验证组件**

运行: `cd /home/luorome/software/CampusMind/frontend && npx tsc --noEmit --skipLibCheck src/features/build/components/ui/ConfirmDialog.tsx 2>&1 || true`
Expected: 无错误

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/build/components/ui/ConfirmDialog.tsx frontend/src/features/build/components/ui/ConfirmDialog.module.css
git commit -m "feat(build): add ConfirmDialog component"
```

---

## Chunk 5: Frontend - buildStore Actions

### Task 5.1: 添加 removeTask 和 retryFailedUrls 到 buildStore

**Files:**
- Modify: `frontend/src/features/build/buildStore.ts`

- [ ] **Step 1: 添加 removeTask 和 retryFailedUrls actions**

编辑 `frontend/src/features/build/buildStore.ts`，在 `BuildState` 接口中添加：

```typescript
interface BuildState {
  // ... existing fields ...

  // Actions
  removeTask: (taskId: string) => Promise<void>;
  retryFailedUrls: (taskId: string) => Promise<string | null>;
  clearCompletedTasks: () => Promise<void>;
}
```

在 `buildStore` 创建的 `actions` 对象中添加实现：

```typescript
removeTask: async (taskId) => {
  try {
    await crawlApi.deleteTask(taskId);
    set((state) => ({
      tasks: state.tasks.filter((t) => t.id !== taskId),
    }));
  } catch (error) {
    console.error('Failed to remove task:', error);
  }
},

retryFailedUrls: async (taskId) => {
  const task = get().tasks.find((t) => t.id === taskId);
  if (!task?.knowledge_id || !task.failed_urls?.length) return null;

  try {
    const failedUrls = task.failed_urls.map((f) => f.url);
    const newTaskId = await get().submitBatchCrawl(failedUrls);
    return newTaskId;
  } catch (error) {
    console.error('Failed to retry failed URLs:', error);
    return null;
  }
},

clearCompletedTasks: async () => {
  const { tasks, removeTask } = get();
  const terminalTasks = tasks.filter((t) =>
    ['SUCCESS', 'FAILED', 'completed', 'failed'].includes(t.status)
  );

  for (const task of terminalTasks) {
    await removeTask(task.id);
  }
},
```

- [ ] **Step 2: 验证 TypeScript**

运行: `cd /home/luorome/software/CampusMind/frontend && npx tsc --noEmit --skipLibCheck src/features/build/buildStore.ts 2>&1 || true`
Expected: 无错误

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/build/buildStore.ts
git commit -m "feat(build): add removeTask, retryFailedUrls, clearCompletedTasks to buildStore"
```

---

## Chunk 6: Frontend - TaskCard 增强

### Task 6.1: 增强 TaskCard 组件

**Files:**
- Modify: `frontend/src/features/build/components/CrawlTab/TaskCard.tsx`
- Modify: `frontend/src/features/build/components/CrawlTab/TaskCard.module.css`

- [ ] **Step 1: 编写 TaskCard 增强测试**

创建 `frontend/src/features/build/components/CrawlTab/TaskCard.test.tsx`:

```typescript
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskCard } from './TaskCard';

const mockTask = {
  id: 'task-123',
  knowledge_id: 'kb-1',
  user_id: 'user-1',
  total_urls: 5,
  completed_urls: 5,
  success_count: 3,
  fail_count: 2,
  status: 'completed' as const,
  failed_urls: [
    { url: 'http://failed1.com', error: 'Connection timeout', timestamp: '2026-03-24T10:00:00' },
    { url: 'http://failed2.com', error: '404 Not Found', timestamp: '2026-03-24T10:00:01' },
  ],
  create_time: '2026-03-24T09:00:00',
  update_time: '2026-03-24T10:00:00',
};

describe('TaskCard', () => {
  it('shows "部分成功" when task is completed with some failures', () => {
    render(<TaskCard task={mockTask} />);
    expect(screen.getByText('部分成功')).toBeInTheDocument();
  });

  it('shows "成功" when task is completed with no failures', () => {
    const successTask = { ...mockTask, success_count: 5, fail_count: 0 };
    render(<TaskCard task={successTask} />);
    expect(screen.getByText('成功')).toBeInTheDocument();
  });

  it('shows "失败" when all URLs failed', () => {
    const failedTask = { ...mockTask, success_count: 0, fail_count: 5 };
    render(<TaskCard task={failedTask} />);
    expect(screen.getByText('失败')).toBeInTheDocument();
  });

  it('does not show failed details by default', () => {
    render(<TaskCard task={mockTask} />);
    expect(screen.queryByText('http://failed1.com')).not.toBeInTheDocument();
  });

  it('expands failed details when clicking toggle', () => {
    render(<TaskCard task={mockTask} />);
    const toggleBtn = screen.getByText('查看失败详情');
    fireEvent.click(toggleBtn);
    expect(screen.getByText('http://failed1.com')).toBeInTheDocument();
    expect(screen.getByText('Connection timeout')).toBeInTheDocument();
  });

  it('calls onDelete when delete button is clicked', () => {
    const onDelete = vi.fn();
    render(<TaskCard task={mockTask} onDelete={onDelete} />);
    const deleteBtn = screen.getByLabelText('删除任务');
    fireEvent.click(deleteBtn);
    expect(onDelete).toHaveBeenCalledWith('task-123');
  });

  it('calls onRetry when retry button is clicked', () => {
    const onRetry = vi.fn();
    render(<TaskCard task={mockTask} onRetry={onRetry} />);
    const retryBtn = screen.getByText('重试失败链接');
    fireEvent.click(retryBtn);
    expect(onRetry).toHaveBeenCalledWith('task-123');
  });

  it('disables delete button for non-terminal tasks', () => {
    const processingTask = { ...mockTask, status: 'processing' as const };
    const onDelete = vi.fn();
    render(<TaskCard task={processingTask} onDelete={onDelete} />);
    const deleteBtn = screen.getByLabelText('删除任务');
    expect(deleteBtn).toBeDisabled();
  });
});
```

- [ ] **Step 2: 运行测试验证失败**

运行: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/TaskCard.test.tsx 2>&1 | head -50`
Expected: 测试失败（因为 TaskCard 尚未更新）

- [ ] **Step 3: 更新 TaskCard 组件**

编辑 `frontend/src/features/build/components/CrawlTab/TaskCard.tsx`:

```typescript
import React, { useState } from 'react';
import { Check, X, Loader2, Trash2, RotateCw, ChevronDown, ChevronUp } from 'lucide-react';
import { CrawlTask } from '../../api/crawl';
import styles from './TaskCard.module.css';

interface TaskCardProps {
  task: CrawlTask;
  onDelete?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
}

const TERMINAL_STATES = ['SUCCESS', 'FAILED', 'completed', 'failed'];

export const TaskCard: React.FC<TaskCardProps> = ({ task, onDelete, onRetry }) => {
  const [showFailedDetails, setShowFailedDetails] = useState(false);

  const progress = task.total_urls > 0
    ? Math.round((task.completed_urls / task.total_urls) * 100)
    : 0;

  const isTerminal = TERMINAL_STATES.includes(task.status);
  const hasFailedUrls = (task.failed_urls?.length ?? 0) > 0;
  const canRetry = isTerminal && hasFailedUrls && task.knowledge_id;

  const getStatusDisplay = () => {
    // For completed status, determine exact state
    if (task.status === 'completed' || task.status === 'SUCCESS') {
      if (task.fail_count === 0) {
        return { icon: <Check size={16} />, text: '成功', className: styles.success };
      } else if (task.success_count === 0) {
        return { icon: <X size={16} />, text: '失败', className: styles.failed };
      } else {
        return { icon: <X size={16} />, text: '部分成功', className: styles.partial };
      }
    }
    switch (task.status) {
      case 'FAILED':
        return { icon: <X size={16} />, text: '失败', className: styles.failed };
      case 'processing':
        return { icon: <Loader2 size={16} className={styles.spinning} />, text: '处理中', className: styles.processing };
      case 'pending':
      default:
        return { icon: <Loader2 size={16} className={styles.spinning} />, text: '等待中', className: styles.pending };
    }
  };

  const status = getStatusDisplay();

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleDelete = () => {
    if (isTerminal && onDelete) {
      onDelete(task.id);
    }
  };

  const handleRetry = () => {
    if (canRetry && onRetry) {
      onRetry(task.id);
    }
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.taskId}>Task ID: {task.id.slice(0, 8)}</span>
        <div className={styles.actions}>
          {canRetry && onRetry && (
            <button
              className={styles.actionBtn}
              onClick={handleRetry}
              title="重试失败链接"
            >
              <RotateCw size={16} />
              <span>重试</span>
            </button>
          )}
          {isTerminal && onDelete && (
            <button
              className={`${styles.actionBtn} ${styles.deleteBtn}`}
              onClick={handleDelete}
              disabled={!isTerminal}
              aria-label="删除任务"
              title="删除任务"
            >
              <Trash2 size={16} />
            </button>
          )}
          <span className={`${styles.status} ${status.className}`}>
            {status.icon}
            {status.text}
          </span>
        </div>
      </div>

      <div className={styles.progress}>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className={styles.progressText}>
          {task.completed_urls}/{task.total_urls}
        </span>
      </div>

      <div className={styles.stats}>
        <span className={styles.successStat}>成功: {task.success_count}</span>
        <span className={task.fail_count > 0 ? styles.failStat : ''}>失败: {task.fail_count}</span>
        <span className={styles.date}>{formatDate(task.create_time)}</span>
      </div>

      {hasFailedUrls && (
        <div className={styles.failedSection}>
          <button
            className={styles.failedToggle}
            onClick={() => setShowFailedDetails(!showFailedDetails)}
          >
            {showFailedDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            <span>查看失败详情 ({task.failed_urls.length})</span>
          </button>
          {showFailedDetails && (
            <ul className={styles.failedList}>
              {task.failed_urls.map((failed, idx) => (
                <li key={idx} className={styles.failedItem}>
                  <span className={styles.failedUrl}>{failed.url}</span>
                  <span className={styles.failedError}>{failed.error}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};
```

- [ ] **Step 4: 更新 TaskCard CSS**

编辑 `frontend/src/features/build/components/CrawlTab/TaskCard.module.css`，添加新样式：

```css
/* 在现有样式后添加 */

.actions {
  display: flex;
  align-items: center;
  gap: var(--space-2, 8px);
}

.actionBtn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1, 4px);
  padding: var(--space-1, 4px) var(--space-2, 8px);
  border: none;
  background: rgba(83, 125, 150, 0.1);
  color: var(--color-accent, #537d96);
  border-radius: var(--radius-sm, 4px);
  font-size: var(--text-xs, 12px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.actionBtn:hover:not(:disabled) {
  background: rgba(83, 125, 150, 0.2);
}

.actionBtn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.deleteBtn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error, #ef4444);
}

.partial {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.successStat {
  color: var(--color-success, #22c55e);
}

.failStat {
  color: var(--color-error, #ef4444);
}

.failedSection {
  margin-top: var(--space-3, 12px);
  padding-top: var(--space-3, 12px);
  border-top: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
}

.failedToggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1, 4px);
  padding: var(--space-1, 4px) var(--space-2, 8px);
  border: none;
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error, #ef4444);
  border-radius: var(--radius-sm, 4px);
  font-size: var(--text-xs, 12px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.failedToggle:hover {
  background: rgba(239, 68, 68, 0.2);
}

.failedList {
  list-style: none;
  margin: var(--space-2, 8px) 0 0 0;
  padding: 0;
}

.failedItem {
  display: flex;
  flex-direction: column;
  gap: var(--space-1, 4px);
  padding: var(--space-2, 8px);
  background: rgba(239, 68, 68, 0.05);
  border-radius: var(--radius-sm, 4px);
  margin-bottom: var(--space-2, 8px);
}

.failedUrl {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-primary, #3b3d3f);
  word-break: break-all;
}

.failedError {
  font-size: var(--text-xs, 12px);
  color: var(--color-error, #ef4444);
}
```

- [ ] **Step 5: 运行测试验证通过**

运行: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/TaskCard.test.tsx 2>&1`
Expected: 所有测试通过

- [ ] **Step 6: Commit**

```bash
git add frontend/src/features/build/components/CrawlTab/TaskCard.tsx frontend/src/features/build/components/CrawlTab/TaskCard.module.css frontend/src/features/build/components/CrawlTab/TaskCard.test.tsx
git commit -m "feat(build): enhance TaskCard with partial success status, failed details, delete and retry"
```

---

## Chunk 7: Frontend - TaskList 增强

### Task 7.1: 增强 TaskList 组件（滚动 + 批量删除）

**Files:**
- Modify: `frontend/src/features/build/components/CrawlTab/TaskList.tsx`
- Modify: `frontend/src/features/build/components/CrawlTab/TaskList.module.css`

- [ ] **Step 1: 编写 TaskList 增强测试**

创建 `frontend/src/features/build/components/CrawlTab/TaskList.test.tsx`:

```typescript
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskList } from './TaskList';
import { CrawlTask } from '../../api/crawl';

const mockTasks: CrawlTask[] = [
  {
    id: 'task-1',
    knowledge_id: 'kb-1',
    user_id: 'user-1',
    total_urls: 5,
    completed_urls: 5,
    success_count: 5,
    fail_count: 0,
    status: 'completed',
    create_time: '2026-03-24T09:00:00',
    update_time: '2026-03-24T10:00:00',
  },
  {
    id: 'task-2',
    knowledge_id: 'kb-1',
    user_id: 'user-1',
    total_urls: 3,
    completed_urls: 3,
    success_count: 1,
    fail_count: 2,
    status: 'completed',
    failed_urls: [
      { url: 'http://fail.com', error: 'timeout', timestamp: '2026-03-24T10:00:00' },
    ],
    create_time: '2026-03-24T08:00:00',
    update_time: '2026-03-24T09:00:00',
  },
  {
    id: 'task-3',
    knowledge_id: 'kb-1',
    user_id: 'user-1',
    total_urls: 2,
    completed_urls: 1,
    success_count: 0,
    fail_count: 0,
    status: 'processing',
    create_time: '2026-03-24T07:00:00',
    update_time: '2026-03-24T08:00:00',
  },
];

describe('TaskList', () => {
  it('renders task list in scrollable container', () => {
    render(<TaskList tasks={mockTasks} />);
    const container = screen.getByTestId('task-list-container');
    expect(container).toBeInTheDocument();
  });

  it('shows clear completed button', () => {
    render(<TaskList tasks={mockTasks} />);
    expect(screen.getByText('清空已完成')).toBeInTheDocument();
  });

  it('shows confirm dialog when clicking clear completed', () => {
    const onClearCompleted = vi.fn();
    render(<TaskList tasks={mockTasks} onClearCompleted={onClearCompleted} />);
    fireEvent.click(screen.getByText('清空已完成'));
    expect(screen.getByText('确定要清空所有已完成的任务吗？')).toBeInTheDocument();
  });

  it('calls onClearCompleted when confirming dialog', () => {
    const onClearCompleted = vi.fn();
    render(<TaskList tasks={mockTasks} onClearCompleted={onClearCompleted} />);
    fireEvent.click(screen.getByText('清空已完成'));
    fireEvent.click(screen.getByText('确认'));
    expect(onClearCompleted).toHaveBeenCalled();
  });

  it('does not show clear button when no completed tasks', () => {
    const activeTasks = [mockTasks[2]]; // only processing task
    render(<TaskList tasks={activeTasks} />);
    expect(screen.queryByText('清空已完成')).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2: 运行测试验证失败**

运行: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/TaskList.test.tsx 2>&1 | head -30`
Expected: 测试失败（TaskList 尚未更新）

- [ ] **Step 3: 更新 TaskList 组件**

编辑 `frontend/src/features/build/components/CrawlTab/TaskList.tsx`:

```typescript
import React, { useState } from 'react';
import { TaskCard } from './TaskCard';
import { ConfirmDialog } from '../ui/ConfirmDialog';
import { CrawlTask } from '../../api/crawl';
import styles from './TaskList.module.css';

interface TaskListProps {
  tasks: CrawlTask[];
  onDelete?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
  onClearCompleted?: () => void;
}

const TERMINAL_STATES = ['SUCCESS', 'FAILED', 'completed', 'failed'];

export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onDelete,
  onRetry,
  onClearCompleted,
}) => {
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  if (tasks.length === 0) {
    return (
      <div style={{
        textAlign: 'center',
        padding: 'var(--space-8, 32px)',
        color: 'var(--color-text-secondary, #666)',
      }}>
        暂无爬取任务
      </div>
    );
  }

  // Sort by create_time descending (newest first)
  const sortedTasks = [...tasks].sort(
    (a, b) => new Date(b.create_time).getTime() - new Date(a.create_time).getTime()
  );

  const completedCount = tasks.filter((t) => TERMINAL_STATES.includes(t.status)).length;
  const hasCompletedTasks = completedCount > 0;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.count}>共 {tasks.length} 个任务</span>
        {hasCompletedTasks && onClearCompleted && (
          <button
            className={styles.clearBtn}
            onClick={() => setShowClearConfirm(true)}
          >
            清空已完成
          </button>
        )}
      </div>
      <div className={styles.list} data-testid="task-list-container">
        {sortedTasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onDelete={onDelete}
            onRetry={onRetry}
          />
        ))}
      </div>

      <ConfirmDialog
        isOpen={showClearConfirm}
        title="清空确认"
        message="确定要清空所有已完成的任务吗？此操作不会删除已爬取的文件。"
        confirmText="确认"
        cancelText="取消"
        onConfirm={() => {
          setShowClearConfirm(false);
          onClearCompleted?.();
        }}
        onCancel={() => setShowClearConfirm(false)}
      />
    </div>
  );
};
```

- [ ] **Step 4: 更新 TaskList CSS**

编辑 `frontend/src/features/build/components/CrawlTab/TaskList.module.css`:

```css
.container {
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3, 12px);
}

.count {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary, #666);
}

.clearBtn {
  padding: var(--space-1, 4px) var(--space-3, 12px);
  border: 1px solid var(--color-border, rgba(83, 125, 150, 0.22));
  background: none;
  color: var(--color-text-secondary, #666);
  border-radius: var(--radius-sm, 4px);
  font-size: var(--text-sm, 14px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.clearBtn:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--color-error, #ef4444);
  color: var(--color-error, #ef4444);
}

.list {
  max-height: 500px;
  overflow-y: auto;
  padding-right: var(--space-2, 8px);
}

/* Custom scrollbar */
.list::-webkit-scrollbar {
  width: 6px;
}

.list::-webkit-scrollbar-track {
  background: var(--color-border, rgba(83, 125, 150, 0.1));
  border-radius: 3px;
}

.list::-webkit-scrollbar-thumb {
  background: var(--color-border, rgba(83, 125, 150, 0.3));
  border-radius: 3px;
}

.list::-webkit-scrollbar-thumb:hover {
  background: var(--color-border, rgba(83, 125, 150, 0.5));
}
```

- [ ] **Step 5: 运行测试验证通过**

运行: `cd /home/luorome/software/CampusMind/frontend && npm run test:run -- --reporter=verbose src/features/build/components/CrawlTab/TaskList.test.tsx 2>&1`
Expected: 所有测试通过

- [ ] **Step 6: Commit**

```bash
git add frontend/src/features/build/components/CrawlTab/TaskList.tsx frontend/src/features/build/components/CrawlTab/TaskList.module.css frontend/src/features/build/components/CrawlTab/TaskList.test.tsx
git commit -m "feat(build): enhance TaskList with scrollable container and clear completed"
```

---

## Chunk 8: Frontend - 集成到 KnowledgeBuildPage

### Task 8.1: 更新 KnowledgeBuildPage 集成新功能

**Files:**
- Modify: `frontend/src/features/build/KnowledgeBuildPage.tsx`

- [ ] **Step 1: 更新 KnowledgeBuildPage 传递 TaskList props**

编辑 `frontend/src/features/build/KnowledgeBuildPage.tsx`，更新 TaskList 使用：

```typescript
{activeTab === 'crawl' ? (
  <>
    <CrawlPanel />
    <TaskList
      tasks={tasks}
      onDelete={removeTask}
      onRetry={retryFailedUrls}
      onClearCompleted={clearCompletedTasks}
    />
  </>
) : ( ... )}
```

需要从 buildStore 获取这些 actions：
```typescript
const removeTask = buildStore((s) => s.removeTask);
const retryFailedUrls = buildStore((s) => s.retryFailedUrls);
const clearCompletedTasks = buildStore((s) => s.clearCompletedTasks);
```

- [ ] **Step 2: 验证 TypeScript**

运行: `cd /home/luorome/software/CampusMind/frontend && npx tsc --noEmit --skipLibCheck 2>&1 | head -30`
Expected: 无错误

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/build/KnowledgeBuildPage.tsx
git commit -m "feat(build): integrate TaskList with delete, retry, and clear actions"
```

---

## Chunk 9: 验证与测试

### Task 9.1: 运行完整测试套件

- [ ] **Step 1: 前端构建**

运行: `cd /home/luorome/software/CampusMind/frontend && npm run build 2>&1 | tail -20`
Expected: BUILD SUCCESSFUL

- [ ] **Step 2: 前端测试**

运行: `cd /home/luorome/software/CampusMind/frontend && npm run test:run 2>&1 | tail -30`
Expected: 所有测试通过

- [ ] **Step 3: 后端测试**

运行: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/ -v --tb=short 2>&1 | tail -50`
Expected: 所有测试通过（跳过 e2e）

### Task 9.2: 更新文档

- [ ] **Step 1: 更新前端进度日志**

编辑 `frontend/docs/frontend-progress-log.md`，添加新条目：

```markdown
| 2026-03-24 | v0.4.x | 爬取任务 Tab 改进 | 添加滚动列表、部分成功状态、删除/重试功能 |
```

- [ ] **Step 2: 更新前端问题日志（如有）**

如有问题，编辑 `frontend/docs/frontend-question-log.md`

- [ ] **Step 3: Commit 文档更新**

```bash
git add frontend/docs/frontend-progress-log.md
git commit -m "docs(frontend): update progress log for crawl task improvements"
```

---

## 执行摘要

完成以上所有任务后，实现将包括：

1. **后端**:
   - CrawlTask 模型新增 `failed_urls` 字段（包含在 `to_dict()` 中）
   - `update_task_progress` 记录失败 URL 详情（url, error, timestamp）
   - DELETE `/crawl/tasks/{task_id}` 端点
   - POST `/crawl/tasks/{task_id}/retry-failed` 端点

2. **前端**:
   - ConfirmDialog 通用确认对话框
   - TaskCard 增强：部分成功状态（fail_count > 0 且 success_count > 0）、失败详情折叠、删除/重试按钮
   - TaskList 增强：滚动容器（max-height: 500px）、清空已完成功能
   - buildStore 新增 `removeTask`, `retryFailedUrls`, `clearCompletedTasks` actions

3. **删除语义**: 删除 CrawlTask 仅删除任务记录，不影响 KnowledgeFile 记录

4. **重试逻辑**: 重试创建新的 CrawlTask 和 KnowledgeFile 记录（保留审计追踪）

**Plan complete and saved to `frontend/docs/superpowers/plans/2026-03-24-crawl-task-improvements-plan.md`. Ready to execute?**
