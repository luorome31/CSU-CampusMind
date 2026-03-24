# 认证流程

## 登录流程

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant CAS
    participant Redis
    participant DB

    Client->>API: POST /auth/login {username, password}
    API->>API: 检查登录频率限制
    API->>CAS: CAS登录请求
    CAS-->>API: CASTGC Cookie
    API->>Redis: 保存CASTGC (TTL 4h)
    API->>DB: 确保用户存在 (UPSERT)
    API->>API: 生成JWT Token
    API-->>Client: {token, user_id, expires_in}
```

### 详细步骤

1. **频率检查**: `LoginRateLimiter.can_login(username)`
2. **CAS 认证**: `cas_login_only_castgc(username, password)`
3. **CASTGC 存储**: Redis SETEX `castgc:{user_id}`
4. **用户创建**: `INSERT ... ON CONFLICT DO NOTHING`
5. **JWT 生成**: `jwt_manager.create_token({"user_id": username})`

---

## 登出流程

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Redis

    Client->>API: POST /auth/logout {user_id}
    API->>API: 验证当前用户权限
    API->>Redis: DELETE castgc:{user_id}
    API->>Redis: INVALIDATE all subsystem sessions
    API-->>Client: {message: "登出成功"}
```

---

## Token 刷新流程

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Redis

    Client->>API: POST /auth/refresh (with JWT)
    API->>API: 验证JWT有效性
    API->>Redis: 检查CASTGC是否有效
    alt CASTGC 有效
        API->>API: 生成新JWT
        API-->>Client: {token, user_id, expires_in}
    else CASTGC 过期
        API-->>Client: 401 Unauthorized (需重新登录)
    end
```

---

## 工具调用时的 Session 获取

```mermaid
sequenceDiagram
    participant Agent
    participant SessionMgr
    participant Redis
    participant Provider
    participant Subsystem

    Agent->>SessionMgr: get_session(user_id, subsystem)
    SessionMgr->>Redis: 查找缓存Session
    alt Session 存在且有效
        Redis-->>SessionMgr: 返回Session
        SessionMgr-->>Agent: 返回Session
    else Session 不存在/过期
        SessionMgr->>Redis: 获取CASTGC
        alt CASTGC 存在
            SessionMgr->>Provider: 使用CASTGC获取Session
            Provider->>Subsystem: 验证CASTGC
            Subsystem-->>Provider: 返回Session
            SessionMgr->>Redis: 缓存新Session
            SessionMgr-->>Agent: 返回Session
        else CASTGC 不存在
            SessionMgr-->>Agent: NeedReLoginError
            Agent-->>Client: 请重新登录
        end
    end
```

---

## 错误处理

| 错误类型 | 原因 | 处理方式 |
|----------|------|----------|
| `CASLoginError` | 用户名/密码错误 | 提示重新输入 |
| `AccountLockedError` | 账号被锁定 | 返回 423，提示联系管理员 |
| `NeedReLoginError` | CASTGC 过期 | 引导用户重新登录 |
| `LoginRateLimitError` | 登录过于频繁 | 等待后重试 |

---

## 前端集成建议

### 登录状态维护

```javascript
// 存储 Token
localStorage.setItem('token', response.token)

// 请求拦截器
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 401 处理
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token 过期，引导重新登录
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

### 登录频率限制提示

```javascript
try {
  await login(username, password)
} catch (error) {
  if (error.response?.status === 429) {
    const waitTime = extractWaitTime(error.response.data.detail)
    showMessage(`登录过于频繁，请等待 ${waitTime} 秒`)
  }
}
```
