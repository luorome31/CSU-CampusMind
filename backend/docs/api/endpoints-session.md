# 会话管理接口

多设备登录管理 API，支持查看活跃会话和登出指定设备。

## 认证

所有接口需要认证（JWT Token）。

---

## 获取活跃会话列表

获取当前用户所有活跃的登录会话。

### 请求

```
GET /api/v1/auth/sessions
```

**需要认证**

### 响应

```json
[
  {
    "session_id": "sess_abc123",
    "device": "Chrome on Windows",
    "location": "Localhost",
    "created_at": 1742789012.5,
    "is_current": true
  },
  {
    "session_id": "sess_def456",
    "device": "Safari on iPhone",
    "location": "Mobile",
    "created_at": 1742788000.0,
    "is_current": false
  }
]
```

| 字段 | 类型 | 描述 |
|------|------|------|
| session_id | string | 会话 ID |
| device | string | 设备描述（从 User-Agent 解析） |
| location | string | 位置（当前为 "Localhost" 或 "Mobile"） |
| created_at | float | 创建时间戳 |
| is_current | bool | 是否为当前会话 |

**识别当前会话**：
1. 优先使用 `X-Session-ID` 请求头
2. 若无，则通过 User-Agent 匹配

---

## 获取当前会话信息

获取当前会话的详细信息。

### 请求

```
GET /api/v1/auth/sessions/current
```

**需要认证**

### 响应

```json
{
  "session_id": "sess_abc123",
  "device": "Chrome on Windows",
  "location": "Localhost",
  "created_at": 1742789012.5
}
```

| 字段 | 类型 | 描述 |
|------|------|------|
| session_id | string | 会话 ID |
| device | string | 设备描述 |
| location | string | 位置 |
| created_at | float | 创建时间戳 |

---

## 登出指定会话

使指定设备上的会话失效（不会影响当前会话）。

### 请求

```
DELETE /api/v1/auth/sessions/{session_id}
```

| 参数 | 类型 | 描述 |
|------|------|------|
| session_id | string | 要删除的会话 ID |

### 响应

```json
{
  "success": true,
  "message": "Session revoked"
}
```

### 错误

- **404**: 会话不存在

---

## 登出所有其他会话

使当前会话以外的所有会话失效。

### 请求

```
DELETE /api/v1/auth/sessions
```

### 响应

```json
{
  "success": true,
  "message": "3 sessions revoked"
}
```

---

## 设备识别逻辑

会话追踪器（SessionTracker）从 User-Agent 解析设备类型：

| User-Agent 关键词 | device 值 |
|-------------------|-----------|
| Mobile/iPhone | Safari on iPhone |
| Mobile/Android | Chrome on Android |
| Windows | Chrome on Windows |
| Mac | Safari on Mac |
| Linux | Chrome on Linux |
| 其他 | Chrome on Unknown |

位置（location）根据设备类型判断：
- 移动设备：`"Mobile"`
- 桌面设备：`"Localhost"`
