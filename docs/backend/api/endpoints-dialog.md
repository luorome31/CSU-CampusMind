# 对话会话管理接口

对话（Dialog）会话管理 API，支持列表、详情、删除和标题更新。

## 认证

可选。已登录用户返回自己的对话列表，未登录用户返回匿名对话。

---

## 获取对话列表

获取当前用户的对话会话列表。

### 请求

```
GET /api/v1/dialogs
```

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| limit | int | 否 | 返回数量，默认 50 |

### 响应

```json
[
  {
    "id": "dialog_001",
    "user_id": "user_123",
    "agent_id": null,
    "title": "成绩查询",
    "updated_at": "2026-03-23T10:30:00"
  }
]
```

| 字段 | 类型 | 描述 |
|------|------|------|
| id | string | 对话 ID |
| user_id | string | 用户 ID（未登录为 null） |
| agent_id | string | Agent 模板 ID |
| title | string | 对话标题 |
| updated_at | string | ISO 格式更新时间 |

---

## 获取对话消息

获取指定对话的完整消息历史。

### 请求

```
GET /api/v1/dialogs/{dialog_id}/messages
```

### 响应

```json
[
  {
    "id": "1742723400000_user",
    "role": "user",
    "content": "帮我查询一下我的成绩",
    "file_url": null,
    "events": null,
    "created_at": "2026-03-23T10:30:00"
  },
  {
    "id": "1742723401000_assistant",
    "role": "assistant",
    "content": "正在为您查询成绩...",
    "file_url": null,
    "events": "[{\"id\": \"tool_1\", \"status\": \"END\"}]",
    "created_at": "2026-03-23T10:30:01"
  }
]
```

| 字段 | 类型 | 描述 |
|------|------|------|
| id | string | 消息 ID |
| role | string | 角色 (user/assistant) |
| content | string | 消息内容 |
| file_url | string | 文件 URL（可选） |
| events | string | JSON 序列化的工具事件数组（可选），格式见下方 |
| created_at | string | ISO 格式创建时间 |

### events 字段格式

`events` 是一个 JSON 字符串，解析后为工具事件数组。每个工具调用会产生多个事件（START → END 或 START → ERROR），它们共享相同的 `id`（tool_call_id）：

```json
[
  {"id": "call_function_xxx", "status": "START", "title": "rag_search", "message": "{'query': '...'}"},
  {"id": "call_function_xxx", "status": "END", "title": "rag_search", "message": "执行完成"}
]
```

| 字段 | 类型 | 描述 |
|------|------|------|
| id | string | 工具调用 ID（START 和 END 事件共享） |
| status | string | 状态：START / END / ERROR |
| title | string | 工具名称 |
| message | string | 状态消息（START 时为参数，END 时为"执行完成"，ERROR 时为错误信息） |

---

## 更新对话标题

更新指定对话的标题。

### 请求

```
PATCH /api/v1/dialogs/{dialog_id}
```

```json
{
  "title": "新的对话标题"
}
```

### 响应

```json
{
  "id": "dialog_001",
  "user_id": "user_123",
  "agent_id": null,
  "title": "新的对话标题",
  "updated_at": "2026-03-23T10:35:00"
}
```

---

## 删除对话

删除指定对话及其所有消息历史。

### 请求

```
DELETE /api/v1/dialogs/{dialog_id}
```

### 响应

```json
{
  "success": true,
  "message": "Conversation deleted"
}
```

### 错误

- `404`: 对话不存在或无权限访问
