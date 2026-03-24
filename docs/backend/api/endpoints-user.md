# 用户资料接口

用户个人资料管理 API，包括查看和更新个人资料、获取使用统计。

## 认证

所有接口需要认证（JWT Token）。

---

## 获取当前用户资料

获取登录用户的个人资料信息。

### 请求

```
GET /api/v1/users/me
```

### 响应

```json
{
  "id": "2020123456",
  "username": "2020123456",
  "display_name": "张三",
  "avatar_url": null,
  "email": "zhangsan@csu.edu.cn",
  "phone": "13800138000",
  "is_active": true,
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-20T15:30:00"
}
```

| 字段 | 类型 | 描述 |
|------|------|------|
| id | string | 用户 ID（学号） |
| username | string | 用户名 |
| display_name | string | 显示名称（可编辑） |
| avatar_url | string | 头像 URL（暂未支持上传） |
| email | string | 邮箱（可编辑） |
| phone | string | 手机号（可编辑） |
| is_active | bool | 账户状态 |
| created_at | string | 注册时间 |
| updated_at | string | 最后更新时间 |

---

## 更新个人资料

更新当前用户的个人资料（显示名称、邮箱、手机号）。

### 请求

```
PATCH /api/v1/users/me
```

```json
{
  "display_name": "新名称",
  "email": "newemail@csu.edu.cn",
  "phone": "13900139000"
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| display_name | string | 否 | 新的显示名称 |
| email | string | 否 | 新的邮箱 |
| phone | string | 否 | 新的手机号 |

### 响应

返回更新后的用户资料（同获取接口格式）。

### 错误

- **404**: 用户不存在

---

## 获取使用统计

获取当前用户的使用统计数据。

### 请求

```
GET /api/v1/users/me/stats
```

### 响应

```json
{
  "conversation_count": 42,
  "message_count": 156,
  "knowledge_base_count": 3,
  "join_date": "2026-03"
}
```

| 字段 | 类型 | 描述 |
|------|------|------|
| conversation_count | int | 对话总数 |
| message_count | int | 消息总数 |
| knowledge_base_count | int | 知识库总数 |
| join_date | string | 注册月份（YYYY-MM） |

### 错误

- **404**: 用户不存在
