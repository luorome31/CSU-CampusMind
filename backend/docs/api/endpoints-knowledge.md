# 知识库 CRUD 接口

所有接口均需要在 Header 中携带 `Authorization: Bearer <token>`。

## 创建知识库

创建新的知识库。

### 请求

```
POST /api/v1/knowledge/create
```

```json
{
  "name": "我的知识库",
  "description": "知识库描述"
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| name | string | 是 | 知识库名称 |
| description | string | 否 | 知识库描述 |

### 响应

```json
{
  "id": "t_abc123",
  "name": "我的知识库",
  "description": "知识库描述",
  "user_id": "20210001",
  "create_time": "2024-01-01T00:00:00",
  "update_time": "2024-01-01T00:00:00",
  "file_count": 0
}
```

---

## 获取知识库

根据 ID 获取知识库详情。只能获取属于自己的知识库。

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
  "user_id": "20210001",
  "create_time": "2024-01-01T00:00:00",
  "update_time": "2024-01-01T00:00:00",
  "file_count": 0
}
```

### 错误

- **401**: 未提供认证凭证或 Token 无效
- **403**: 无权访问该知识库
- **404**: 知识库不存在

---

## 列出当前用户知识库

获取当前登录用户的所有知识库。

### 请求

```
GET /api/v1/knowledge
```

### 响应

```json
[
  {
    "id": "t_abc123",
    "name": "我的知识库",
    "description": "知识库描述",
    "user_id": "20210001",
    "create_time": "2024-01-01T00:00:00",
    "update_time": "2024-01-01T00:00:00",
    "file_count": 4
  }
]
```

| 字段 | 类型 | 描述 |
|------|------|------|
| file_count | int | 知识库中的文件数量 |

---

## 删除知识库

删除指定的知识库。只能删除属于自己的知识库。

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

- **401**: 未提供认证凭证或 Token 无效
- **403**: 无权删除该知识库
- **404**: 知识库不存在
