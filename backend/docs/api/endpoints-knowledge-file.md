# 知识文件管理接口

## 创建知识文件记录

创建知识文件的元数据记录。

### 请求

```
POST /api/v1/knowledge_file/create
```

```json
{
  "file_name": "document.md",
  "knowledge_id": "t_abc123",
  "user_id": "system",
  "oss_url": "https://oss.example.com/bucket/path/document.md",
  "file_size": 1024
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| file_name | string | 是 | 文件名 |
| knowledge_id | string | 是 | 所属知识库 ID |
| user_id | string | 否 | 上传用户 ID |
| oss_url | string | 是 | OSS/MinIO 存储 URL |
| file_size | int | 否 | 文件大小（字节） |

### 响应

```json
{
  "id": "file_xyz789",
  "file_name": "document.md",
  "knowledge_id": "t_abc123",
  "user_id": "system",
  "status": "process",
  "oss_url": "https://oss.example.com/bucket/path/document.md",
  "file_size": 1024,
  "create_time": "2024-01-01T00:00:00",
  "update_time": "2024-01-01T00:00:00"
}
```

---

## 获取知识文件

根据 ID 获取文件详情。

### 请求

```
GET /api/v1/knowledge_file/{file_id}
```

### 响应

```json
{
  "id": "file_xyz789",
  "file_name": "document.md",
  "knowledge_id": "t_abc123",
  "user_id": "system",
  "status": "success",
  "oss_url": "https://oss.example.com/bucket/path/document.md",
  "file_size": 1024,
  "create_time": "2024-01-01T00:00:00",
  "update_time": "2024-01-01T00:00:00"
}
```

### 错误

- **404**: 文件不存在

---

## 列出知识库文件

获取指定知识库下的所有文件。

### 请求

```
GET /api/v1/knowledge/{knowledge_id}/files
```

### 响应

```json
[
  {
    "id": "file_xyz789",
    "file_name": "document.md",
    "knowledge_id": "t_abc123",
    "user_id": "system",
    "status": "success",
    "oss_url": "https://oss.example.com/bucket/path/document.md",
    "file_size": 1024,
    "create_time": "2024-01-01T00:00:00",
    "update_time": "2024-01-01T00:00:00"
  }
]
```

---

## 更新文件状态

更新文件的处理状态。

### 请求

```
PATCH /api/v1/knowledge_file/{file_id}
```

```json
{
  "status": "success"
}
```

| 状态值 | 含义 |
|--------|------|
| process | 处理中 |
| success | 处理成功 |
| fail | 处理失败 |

### 响应

```json
{
  "success": true
}
```

---

## 删除知识文件

删除指定的文件记录。

### 请求

```
DELETE /api/v1/knowledge_file/{file_id}
```

### 响应

```json
{
  "success": true
}
```

### 错误

- **404**: 文件不存在

---

## 获取文件原始内容

获取储存在 OSS 上的 Markdown 纯文本。

### 请求

```
GET /api/v1/knowledge_file/{file_id}/content
```

### 响应

```markdown
# 标题
这是从 OSS 返回的纯文本 Markdown 内容。
```

---

## 更新文件原始内容

修改文件的 Markdown 内容（并保存至 OSS）。

### 请求

```
PUT /api/v1/knowledge_file/{file_id}/content
```

```json
{
  "content": "# 修改后的标题\n\n新内容..."
}
```

### 响应

```json
{
  "success": true,
  "message": "Content updated and file verified"
}
```

---

## 触发手动索引

用户完成文件内容的校验之后，主动触发 RAG 构建索引过程。

### 请求

```
POST /api/v1/knowledge_file/{file_id}/trigger_index
```

```json
{
  "enable_vector": true,
  "enable_keyword": true
}
```

### 响应

```json
{
  "success": true,
  "message": "File indexed successfully"
}
```
