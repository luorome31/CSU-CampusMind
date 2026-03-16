# Session Demo 项目总结

> 用于复盘和复用的完整文档

## 目录结构

```
session-demo/
├── .env                        # 环境变量（账号密码）
├── pyproject.toml              # 项目配置（uv）
├── uv.lock                     # 依赖锁定
├── unified_session_v2.py        # 最终版本（含持久化）
├── session_persistence.py       # Session 持久化模块
├── test_cache.py               # 缓存测试脚本
├── jwc_client.py               # 教务系统业务客户端
├── cache_test_sessions.json    # 测试保存的 Cookie 文件
```

## 核心功能模块

### 1. unified_session_v2.py（核心）

统一会话管理器，包含以下特性：

| 特性 | 说明 |
|------|------|
| 用户+子系统粒度缓存 | `Map<UserId, Map<Subsystem, Session>>` |
| 登录频率控制 | 防止账号被封（5分钟最多5次） |
| 请求头模拟 | 防止被识别为机器人 |
| Session 持久化 | 保存到 JSON 文件 |

**核心类：**

```python
# 常量定义
Subsystem.JWC       # 教务系统
Subsystem.LIBRARY   # 图书馆
Subsystem.ECARD     # 校园卡

# 会话缓存
SubsystemSessionCache  # 用户+子系统双层缓存

# 登录频率控制
LoginRateLimiter(max_attempts=5, window_seconds=300)

# 统一会话管理
UnifiedSessionManager(
    ttl_seconds=30*60,        # 缓存有效期
    storage_path="./xxx.json", # 存储文件
    enable_persistence=True    # 启用持久化
)
```

**使用示例：**

```python
manager = UnifiedSessionManager(
    ttl_seconds=30*60,
    storage_path="./sessions.json",
    enable_persistence=True
)

# 获取教务系统会话（自动登录+缓存+持久化）
session = manager.access_jwc("8209220131", "password")

# 后续请求自动使用缓存
session = manager.access_jwc("8209220131", "password")
```

### 2. session_persistence.py

Session 持久化模块，将 Cookie 保存到 JSON 文件：

```python
persistence = SessionPersistence("./sessions.json")

# 保存
persistence.save(user_id, subsystem, session, ttl_seconds)

# 加载
session = persistence.load(user_id, subsystem)

# 失效
persistence.invalidate(user_id, subsystem)

# 清理过期
persistence.cleanup_expired()
```

**保存的文件格式：**

```json
{
  "8209220131": {
    "jwc": {
      "cookies": {
        "JSESSIONID": {
          "value": "xxx",
          "domain": "csujwc.its.csu.edu.cn",
          "path": "/"
        }
      },
      "saved_at": 1234567890,
      "expires_at": 1234567890 + 1800
    }
  }
}
```

### 3. jwc_client.py

教务系统业务客户端（高内聚低耦合）：

```
设计原则：
- Cookie 加载与业务逻辑分离
- 每个业务函数独立，只做一件事
- 统一的错误处理和数据解析
```

**模块结构：**

```python
# Cookie 加载器
CookieLoader.load(user_id, subsystem) -> Session

# 业务客户端
JwcClient.get_grades(term)        # 成绩查询
JwcClient.get_rank()              # 专业排名
JwcClient.get_class_schedule()    # 课表查询
JwcClient.get_level_exams()       # 等级考试

# 统一入口
JwcService.connect(user_id)       # 连接教务系统
JwcService.grades                 # 成绩查询
JwcService.rank                   # 排名查询
JwcService.classes                # 课表查询
```

**使用示例：**

```python
service = JwcService("./sessions.json")
service.connect("8209220131")

# 查询成绩
grades = service.grades.get_grades("2024-2025-1")

# 查询课表
classes = service.classes.get_class_schedule("2024-2025-1", "1")
```

## 关键实践发现

### 1. CAS 登录关键点

| 发现 | 说明 |
|------|------|
| 跳转地址必须访问 | 只有访问重定向地址后才能获取子系统 Cookie |
| 请求头必须设置 | 防止被识别为机器人 |
| 登录频率控制 | 几分钟内多次登录会封号 |
| 多 JSESSIONID 问题 | 需要清理重复的 Cookie |

### 2. Session 有效期

```
┌─────────────────────────────────────────┐
│  层级1: CAS Cookie (服务端控制)          │
│         - 取决于服务器设置               │
│         - 通常是会话 Cookie              │
│                                          │
│  层级2: 子系统 Cookie (服务端控制)      │
│         - 各系统独立                    │
│                                          │
│  层级3: 本地缓存 TTL (客户端控制)        │
│         - 当前设置为 30 分钟             │
└─────────────────────────────────────────┘
```

### 3. 持久化意义

| 对比项 | 无持久化 | 有持久化 |
|--------|----------|----------|
| 进程退出 | Cookie 丢失 | Cookie 保留 |
| 重新运行 | 需要重新登录 | 自动加载 |
| 登录频率 | 高（每次都登录） | 低（复用） |

## 依赖

```toml
# pyproject.toml
dependencies = [
    "requests>=2.32.0",
    "beautifulsoup4>=4.12.0",
    "pycryptodome>=3.20.0",
    "python-dotenv>=1.0.0",
]
```

## 运行命令

```bash
# 安装依赖
uv sync

# 运行演示
uv run python demo.py

# 运行缓存测试
uv run python test_cache.py

# 运行教务系统客户端
uv run python jwc_client.py
```

## 环境变量

```bash
# .env 文件
CSU_TEST_ID=82092201xx
CSU_TEST_PWD=你的密码
```

## 待解决问题

1. ~~JSESSIONID 重复问题~~ - 已修复
<!-- 2. Session 保存后文件未更新 - 需要验证 -->
2. 实际业务调用测试 - 需要完整流程测试

## 复用指南

### 复用统一会话管理

```python
from unified_session_v2 import UnifiedSessionManager, Subsystem

manager = UnifiedSessionManager(
    ttl_seconds=30*60,
    storage_path="./my_sessions.json",
    enable_persistence=True
)

# 教务系统
jwc_session = manager.access_jwc(user_id, password)

# 图书馆
lib_session = manager.access_library(user_id, password)

# 校园卡
ecard_session = manager.access_ecard(user_id, password)
```

### 复用教务系统客户端

```python
from jwc_client import JwcService

service = JwcService("./my_sessions.json")
service.connect(user_id)

# 使用业务功能
grades = service.grades.get_grades("")
exams = service.level_exams.get_level_exams()
classes = service.classes.get_class_schedule("2024-2025-1", "1")
```

### 添加新子系统

1. 在 `SUBSYSTEM_SERVICE_URLS` 添加 URL
2. 参考 `JwcClient` 实现业务逻辑
3. 在 `JwcService` 添加入口

---

**更新时间**: 2026-03-16
