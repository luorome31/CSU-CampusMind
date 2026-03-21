# 知识库 CRUD 接口

## 创建知识库

创建新的知识库。

### 请求

```
POST /api/v1/knowledge/create
```

```json
{
  "name": "我的知识库",
  "description": "知识库描述",
  "user_id": "system"
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| name | string | 是 | 知识库名称 |
| description | string | 否 | 知识库描述 |
| user_id | string | 否 | 创建者用户 ID，默认为 "system" |

### 响应

```json
{
  "id": "t_abc123",
  "name": "我的知识库",
  "description": "知识库描述",
  "user_id": "system",
  "create_time": "2024-01-01T00:00:00",
  "update_time": "2024-01-01T00:00:00"
}
```

---

## 获取知识库

根据 ID 获取知识库详情。

### 请求

```
GET /api/v1/knowledge/{knowledge_id}
```

### 响应

```json
{
  "id": "t_abc123",
  "name": "我的知识库",
  "description": "知识库描述",
  "user_id": "system",
  "create_time": "2024-01-01T00:00:00",
  "update_time": "2024-01-01T00:00:00"
}
```

### 错误

- **404**: 知识库不存在

---

## 列出用户知识库

获取指定用户的所有知识库。

### 请求

```
GET /api/v1/users/{user_id}/knowledge
```

### 响应

```json
[
  {
    "id": "t_abc123",
    "name": "我的知识库",
    "description": "知识库描述",
    "user_id": "system",
    "create_time": "2024-01-01T00:00:00",
    "update_time": "2024-01-01T00:00:00"
  }
]
```

---

## 删除知识库

删除指定的知识库。

### 请求

```
DELETE /api/v1/knowledge/{knowledge_id}
```

### 响应

```json
{
  "success": true
}
```

### 错误

- **404**: 知识库不存在
