# 认证接口

## 登录

用户登录 CAS 统一身份认证平台，获取 JWT Token。

### 请求

```
POST /api/v1/auth/login
```

```json
{
  "username": "学号",
  "password": "密码"
}
```

### 响应

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": "2020123456",
  "session_id": "sess_abc123xyz",
  "expires_in": 86400
}
```

| 字段 | 类型 | 描述 |
|------|------|------|
| token | string | JWT 访问令牌 |
| user_id | string | 用户学号 |
| session_id | string | 会话 ID（用于多设备管理） |
| expires_in | int | 有效期（秒），默认 24 小时 |

### 错误响应

- **401**: 用户名或密码错误
- **423**: 账号已被锁定
- **429**: 登录过于频繁

---

## 登出

清除用户会话，使 CASTGC 和所有子系统 Session 失效。

### 请求

```
POST /api/v1/auth/logout
```

**需要认证**

```json
{
  "user_id": "2020123456"
}
```

### 响应

```json
{
  "message": "登出成功"
}
```

---

## 刷新 Token

刷新 JWT Token，无需重新登录 CAS。

### 请求

```
POST /api/v1/auth/refresh
```

**需要认证**

### 响应

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": "2020123456",
  "expires_in": 86400
}
```

---

## 登录流程

```
┌─────────┐     ┌─────────┐     ┌─────────────┐
│  用户   │────▶│  CAS    │────▶│  JWT Token  │
│  登录   │     │  认证   │     │  生成       │
└─────────┘     └─────────┘     └─────────────┘
                    │
                    ▼
              ┌─────────────┐
              │  CASTGC     │
              │  存储       │
              └─────────────┘
```

1. 用户提交学号/密码到 CAS 认证
2. CAS 返回 CASTGC Cookie（跨子系统共享）
3. CASTGC 存储到 Redis（TTL 4 小时）
4. 生成 JWT Token 返回给客户端（TTL 24 小时）
