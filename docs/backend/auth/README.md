# 认证与授权

CampusMind 使用 **JWT + CAS** 的双层认证体系。

## 概述

```
┌─────────┐     ┌─────────┐     ┌─────────────┐
│  用户   │────▶│  CAS    │────▶│  JWT Token  │
│         │     │  统一认证│     │  应用访问   │
└─────────┘     └─────────┘     └─────────────┘
```

### 认证层级

1. **CAS 认证层**: 统一身份认证，获取跨子系统共享的 CASTGC
2. **JWT 应用层**: 应用内接口访问控制

---

## 目录结构

- [会话管理](./session-management.md) - Session 架构与 Redis 存储
- [认证流程](./auth-flow.md) - 详细认证流程图

---

## CAS 统一认证

CAS (Central Authentication Service) 是中南大学信息门户的统一身份认证系统。

### 支持的子系统

| 子系统 | Service URL | 用途 |
|--------|-------------|------|
| JWC | http://csujwc.its.csu.edu.cn | 教务系统 |
| Library | https://lib.csu.edu.cn | 图书馆 |
| ECARD | https://ecard.csu.edu.cn | 校园卡 |
| OA | https://oa.csu.edu.cn | 办公网 |

### CASTGC

CAS 登录成功后返回的 TGC (Ticket Granting Cookie)，有效期约 4 小时。

---

## JWT Token

### 特点

- **算法**: HS256
- **有效期**: 24 小时（可配置）
- **Payload**: `{"user_id": "学号", "exp": 过期时间}`

### 使用方式

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/knowledge
```

---

## 登录频率控制

使用滑动窗口算法限制登录尝试频率：

- **时间窗口**: 15 分钟
- **最大尝试次数**: 5 次
- **锁定时间**: 15 分钟

超过限制后返回 HTTP 429 状态码。
