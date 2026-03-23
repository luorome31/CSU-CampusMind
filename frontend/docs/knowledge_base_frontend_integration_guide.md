# 知识库管理系统 Frontend 交互集成指南

本文档依据后端的最新更新，为前端开发提供交互场景和 API 调用的总结参考，特别是涉及“异步任务监控”与“人工校验及触发重建”数据流向。

**重要提示**: 所有请求必须在 Header 中携带 `Authorization: Bearer <token>`。后端将自动从 JWT 中提取请求者的 Identity。

## 场景一：知识库展示页（只读模式）

**要求**：浏览知识库目录及其详细内容。不提供修改或后置操作。

1. **获取知识库列表** (已更新)
   `GET /api/v1/knowledge`

2. **获取某一知识库的文件目录**
   `GET /api/v1/knowledge/{knowledge_id}/files`

3. **获取单个文件的详细文本内容 (Markdown)**
   为了在页面中直接渲染 Markdown 文本，并保持权限可控，引入了安全拉取内容的接口。
   ```http
   GET /api/v1/knowledge_file/{file_id}/content
   ```
   **响应**: 返回 `text/plain` 或纯字符串类型的 Markdown 内容。

---

## 场景二：构建与爬取页 (异步工作流设计)

支持单链接/批量链接提交后，界面实时显示总体爬取进度。

1. **提交批量爬取任务**
   ```http
   POST /api/v1/crawl/batch-with-knowledge
   Body:
   {
       "urls": ["http://link1", "http://link2", ...],
       "knowledge_id": "t_abc123"
   }
   ```
   **响应**: 不再阻塞数百秒等待完成，而是立即返回 Task 信息。
   ```json
   {
       "task_id": "d04a2...98b",
       "status": "processing",
       "message": "Batch crawl with knowledge task started"
   }
   ```

2. **任务监控轮询 (Task Progress)**
   前端拿到 `task_id` 后，启动一个 Timer（比如每 1~2 秒），轮询以下接口刷新进度条：
   ```http
   GET /api/v1/crawl/tasks/{task_id}
   ```
   **响应**:
   ```json
   {
       "id": "d04a2...98b",
       "total_urls": 10,
       "completed_urls": 4,      <-- 进度 = completed_urls / total_urls
       "success_count": 3,
       "fail_count": 1,
       "status": "processing",   <-- 当变为 "completed" 或 "failed" 时停止轮询
       ...
   }
   ```

---

## 场景三：人工校验流

爬取成功的条目需要经过详情页进行人工修改校验，保存后再触发 RAG 向量/关键词索引。

1. **查阅待校验文件**
   当后台 URL 爬取存入 OSS 后，数据库里对应的 `KnowledgeFile.status` 会被设置为 `pending_verify` (待校验)。您可以通过知识库文件列表 API 过滤出这些状态的文件。

2. **请求文件的原始内容 (Markdown)**
   进入修改详情页时，调用该接口获取文本填充进 Editor：
   ```http
   GET /api/v1/knowledge_file/{file_id}/content
   ```

3. **保存修改并打上校验标签**
   在前端 Markdown Editor 完成修改后，保存最新的有效性内容。这会覆盖更新 OSS 内容，并将状态改变为 `verified`。
   ```http
   PUT /api/v1/knowledge_file/{file_id}/content
   Body:
   {
       "content": "# 修改后的标题\n\n校对后的正文..."
   }
   ```
   **响应**: `{"success": true, "message": "Content updated and file verified"}`

4. **主动触发后续索引 (RAG 索引构建)**
   用户校验满意并保存后，前端发起最终动作：
   ```http
   POST /api/v1/knowledge_file/{file_id}/trigger_index
   Body:
   {
       "enable_vector": true,
       "enable_keyword": true
   }
   ```
   *注意*: 这个过程会将文件状态变为 `indexing`，如果完成会变为 `indexed` 或 `success`。如果报错，则变为 `fail`。
