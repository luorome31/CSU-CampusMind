# Session 管理

## 架构概述

```
┌─────────────────────────────────────────────────────────────┐
│                    UnifiedSessionManager                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │   CASTGC    │  │  Subsystem  │  │   LoginRateLimiter   ││
│  │  (Redis)    │  │   Sessions  │  │   (滑动窗口限流)      ││
│  └─────────────┘  └─────────────┘  └─────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │   JWC    │   │  Library │   │    OA    │
    │  Provider│   │  Provider│   │  Provider│
    └──────────┘   └──────────┘   └──────────┘
```

## CASTGC 存储

### Redis Key 格式

```
castgc:{user_id}
```

### 存储结构

```json
{
  "castgc": "TGC-xxx",
  "created_at": 1234567890,
  "expires_at": 1234585890
}
```

- **TTL**: 4 小时
- **过期自动清除**

---

## 子系统 Session

### Session Provider

每个子系统有自己的 Session Provider：

| Provider | 用途 | 认证方式 |
|----------|------|----------|
| JwcProvider | 教务系统 | Cookie 转发 |
| LibraryProvider | 图书馆 | Cookie 转发 |
| EcardProvider | 校园卡 | Cookie 转发 |
| OaProvider | 办公网 | Cookie 转发 |

### 获取流程

1. 检查本地/Redis 缓存的 Session
2. 如无，使用 CASTGC 通过 Provider 获取新 Session
3. 缓存新 Session（TTL 30 分钟）

---

## 持久化

### 文件持久化 (开发环境)

```python
session_storage_path: "./data/csu_sessions.json"
```

### Redis 持久化 (生产环境)

```python
redis_url: "redis://localhost:6379/0"
```

### Session 数据结构

```json
{
  "user_id": "2020123456",
  "subsystem": "jwc",
  "session_data": {
    "cookies": {...},
    "headers": {...}
  },
  "created_at": "2024-01-01T00:00:00",
  "expires_at": "2024-01-01T00:30:00"
}
```

---

## 速率限制

### LoginRateLimiter

使用滑动窗口算法实现分布式限流。

```python
class LoginRateLimiter:
    window_seconds = 900      # 15分钟窗口
    max_attempts = 5          # 最大尝试次数
    lockout_duration = 900    # 锁定时长
```

### Redis 存储

```
ratelimit:login:{username} -> [timestamp1, timestamp2, ...]
```

### 超时处理

当用户 Session 过期或 CASTGC 失效时，抛出 `NeedReLoginError`，前端需引导用户重新登录。
