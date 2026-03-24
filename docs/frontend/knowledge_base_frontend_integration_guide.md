# 知识库管理系统 Frontend 交互集成指南

本文档依据后端的最新更新，为前端开发提供交互场景和 API 调用的总结参考，特别是涉及“异步任务监控”与“人工校验及触发重建”数据流向。

**重要提示**: 所有请求必须在 Header 中携带 `Authorization: Bearer <token>`。后端将自动从 JWT 中提取请求者的 Identity。

## 场景一：知识库展示页（只读模式）

**要求**：浏览知识库目录及其详细内容。不提供修改或后置操作。

1. **获取知识库列表** (已更新)
   `GET /api/v1/knowledge`

2. **获取某一知识库的文件目录**
   `GET /api/v1/knowledge/{knowledge_id}/files`
   *支持可选查询参数 `?status=indexed` 只看已生效文件。*

3. **获取单个文件的详细文本内容 (Markdown)**
   为了在页面中直接渲染 Markdown 文本，并保持权限可控，引入了安全拉取内容的接口。
   ```http
   GET /api/v1/knowledge_file/{file_id}/content
   ```
   **响应**: 返回 `text/plain` 或纯字符串类型的 Markdown 内容。

---

## 场景二：构建与爬取页 (异步工作流设计)

支持单链接/批量链接提交后，界面实时显示总体爬取进度。

1. **查看历史任务列表** (新增)
   如果用户刷新页面，可以拉取此前的任务继续监控：
   ```http
   GET /api/v1/crawl/tasks
   ```

2. **提交批量爬取任务**
   ```http
   POST /api/v1/crawl/batch-with-knowledge
   Body:
   {
       "urls": ["http://link1", "http://link2", ...],
       "knowledge_id": "t_abc123"
   }
   ```
   **响应**: 立即返回 Task ID。

3. **任务监控轮询 (Task Progress)**
   前端拿到 `task_id` 后，定时轮询刷新进度：
   ```http
   GET /api/v1/crawl/tasks/{task_id}
   ```
   **响应**:
   ```json
   {
       "id": "task_id",
       "total_urls": 10,
       "completed_urls": 4, 
       "success_count": 3,
       "fail_count": 1,
       "status": "processing"
   }
   ```

---

## 场景三：人工校验流

爬取成功的条目需要经过详情页进行人工修改校验，保存后再触发 RAG 索引构建。

1. **查阅待校验文件 (Verification Inbox)**
   *   **方案 A (推荐全局列表)**: 获取所有知识库下所有待处理文件：
       ```http
       GET /api/v1/knowledge_file/pending_verify
       ```
   *   **方案 B (特定知识库下)**: 
       ```http
       GET /api/v1/knowledge/{knowledge_id}/files?status=pending_verify
       ```

2. **请求文件原始内容并在 Editor 中校对**
   ```http
   GET /api/v1/knowledge_file/{file_id}/content
   ```

3. **保存修改并确认有效性**
   在前端 Markdown Editor 完成修改后，保存最新的有效性内容。这会覆盖更新 OSS 内容，并将状态改变为 `verified`。
   ```http
   PUT /api/v1/knowledge_file/{file_id}/content
   Body:
   {
       "content": "# 修改后的标题\n\n校对后的正文..."
   }
   ```

4. **主动触发最终索引 (RAG 索引构建)**
   用户校对满意后，前端发起最终动作：
   ```http
   POST /api/v1/knowledge_file/{file_id}/trigger_index
   Body:
   {
       "enable_vector": true,
       "enable_keyword": true
   }
   ```
   *注意*: 这个过程会将文件状态变为 `indexing`，如果完成会变为 `indexed` 或 `success`。
