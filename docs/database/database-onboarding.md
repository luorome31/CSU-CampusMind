# CampusMind 开发指南

> 本文档为新 AI 会话提供指导，确保开发方向正确、问题不被遗漏。

---

## 1. 项目概述

CampusMind 是一个基于 AI Agent 的校园智能助手系统，支持 RAG 检索、工具调用、多轮对话。

### 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | FastAPI + SQLModel |
| 数据库 | PostgreSQL (生产) / SQLite (测试) |
| 向量存储 | ChromaDB |
| 全文检索 | Elasticsearch 8.18 |
| LLM 集成 | LangChain / LangGraph |
| 认证 | JWT (CAS 统一认证) |

### 项目结构

```
backend/
├── app/
│   ├── api/v1/           # API 路由
│   │   ├── completion.py  # 对话接口 (核心)
│   │   ├── auth.py        # 认证
│   │   ├── knowledge*.py  # 知识库
│   │   └── ...
│   ├── core/
│   │   ├── session/       # 会话管理
│   │   └── security/      # JWT
│   ├── database/
│   │   ├── models/        # SQLModel 模型
│   │   └── session.py     # 数据库会话
│   ├── services/         # 业务逻辑服务
│   │   ├── dialog/
│   │   ├── history/
│   │   └── knowledge/
│   └── main.py            # 应用入口
├── tests/
│   ├── e2e/              # 端到端测试
│   └── services/         # 单元测试
└── docs/
    ├── database/schema.sql
    └── database-design.md
```

---

## 2. 数据库模型现状

### 2.1 已正常接入数据库的模型

| 模型 | 服务 | 状态 |
|------|------|------|
| `Dialog` | completion.py 直接使用 | ✅ 正常 |
| `ChatHistory` | completion.py 直接使用 | ✅ 正常 |
| `KnowledgeBase` | KnowledgeService | ✅ 正常 |
| `KnowledgeFile` | KnowledgeFileService | ✅ 正常 |

### 2.2 模型定义位置

| 模型 | 文件 |
|------|------|
| Dialog | `app/database/models/dialog.py` |
| ChatHistory | `app/database/models/chat_history.py` |
| KnowledgeBase | `app/database/models/knowledge.py` |
| KnowledgeFile | `app/database/models/knowledge_file.py` |
| User | `app/database/models/user.py` (未接入) |
| ToolCallLog | `app/database/models/tool_call_log.py` (未接入) |

### 2.3 字段命名规范

**重要：** 数据库字段使用下划线命名，Python 模型使用相同命名。

| 表 | 时间戳字段 |
|------|-----------|
| users | `created_at`, `updated_at` |
| dialogs | `updated_at` |
| chat_history | `created_at` |
| knowledge_bases | `created_at`, `updated_at` |
| knowledge_files | `created_at`, `updated_at` |

---

## 3. 当前已知问题

### 3.1 高优先级

**问题 1: 历史消息未被利用**

- **现状:** 保存了消息到 `chat_history`，但**从未读取历史消息**给 LLM
- **影响:** 每次对话都是独立的，LLM 看不到之前的上下文
- **位置:** `app/api/v1/completion.py`
- **修复方向:** 在调用 LLM 前，使用 `HistoryService.get_history_by_dialog()` 加载历史消息

**问题 2: user_id 安全问题**

- **现状:** JWT 已正确解析，但 `get_or_create_dialog()` 使用 `request.user_id`
- **影响:** 任何可以伪造任意 user_id
- **位置:** `app/api/v1/completion.py` 各接口
- **修复方向:**
  - 认证接口改用 `get_current_user` (必填认证)
  - 移除 request 中的 `user_id` 字段，统一用 JWT 的

### 3.2 中优先级

**问题 3: `create_db_and_tables()` 不完整** ✅ 已修复

- **修复:** 在 `app/main.py` 的 lifespan 中调用 `create_db_and_tables()`，
  所有模型 (User, ToolDefinition, ToolCallLog) 均已导入
- **位置:** `app/main.py`, `app/database/session.py`

**问题 4: 缺少模型导入**

```python
# 当前只导入了这些:
from app.database.models.knowledge import KnowledgeBase
from app.database.models.knowledge_file import KnowledgeFile
from app.database.models.dialog import Dialog
from app.database.models.chat_history import ChatHistory

# 缺少 (如果需要这些表):
from app.database.models.user import User
from app.database.models.tool_call_log import ToolCallLog
```

### 3.3 低优先级

| 问题 | 说明 |
|------|------|
| DialogService 未被使用 | completion.py 直接操作 Dialog，绕过 DialogService |
| ToolCallLog 未接入 | 工具调用日志从未写入数据库 |
| 会话管理使用文件存储 | 存储到 `./data/csu_sessions.json`，Redis 是 TODO |

---

## 4. 开发最佳实践

### 4.1 数据库操作

**使用 SQLModel 的异步会话:**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session

async def some_endpoint(db: AsyncSession = Depends(get_db_session)):
    # 查询
    statement = select(Model).where(Model.id == id)
    result = await db.execute(statement)
    item = result.scalar_one_or_none()

    # 插入
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
```

**JSON 字段序列化:**

如果模型字段是 `TEXT` 但存储 JSON:
```python
import json
# 写入时
events_json = json.dumps(events) if events else None

# 读取时
events = json.loads(events_json) if events_json else None
```

### 4.2 对话流程 (completion.py)

正确的对话流程应该是:

```
1. 解析 JWT 获取 user_id
2. 创建或获取 Dialog
3. 加载历史消息
4. 将历史消息格式化为上下文
5. 调用 LLM (携带历史上下文)
6. 保存用户消息到 chat_history
7. 保存助手回复到 chat_history
8. 更新 Dialog 的 updated_at
```

### 4.3 认证依赖

| 依赖 | 用途 | 返回值 |
|------|------|--------|
| `get_current_user` | 必填认证 | `dict` (JWT payload) |
| `get_optional_user` | 可选认证 | `dict` 或 `None` |

```python
# 需要登录的接口
async def endpoint(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")

# 匿名也可用的接口
async def endpoint(current_user: Optional[dict] = Depends(get_optional_user)):
    user_id = current_user.get("user_id") if current_user else None
```

### 4.4 新增模型流程

1. 在 `app/database/models/` 创建模型文件
2. 在 `app/database/models/__init__.py` 导出
3. 在 `app/database/session.py` 的 `create_db_and_tables()` 添加导入
4. 在服务层创建对应的 Service 类
5. 编写测试

### 4.5 Schema 与模型同步

**重要:** Schema (schema.sql) 必须与 Python 模型保持一致。

修改模型后，同步更新:
- `docs/database/schema.sql`
- `docs/database-design.md`

---

## 5. 测试

### 5.1 运行测试

```bash
cd backend
source .venv/bin/activate

# 单元测试
pytest tests/services/ -v

# E2E 测试
pytest tests/e2e/ -v

# 特定测试
pytest tests/services/test_history.py -v
```

### 5.2 E2E 测试配置

E2E 测试需要:
1. 启动后端服务
2. 调用 `create_db_and_tables()` 初始化数据库
3. 设置环境变量或 `.env` 文件

---

## 6. 环境变量

```bash
# 数据库
DATABASE_URL=sqlite:///./data/campusmind.db

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# CAS 认证 (可选)
CAS_BASE_URL=https://cas.csu.edu.cn
```

---

## 7. 常见检查清单

开始新会话时，确认以下问题:

- [ ] 数据库连接正常
- [ ] Schema 与模型字段一致
- [ ] 新功能是否需要数据库表/字段
- [ ] 是否需要用户认证
- [ ] 是否需要记录历史消息
- [ ] 敏感操作是否需要权限检查

---

## 8. 参考文档

- [数据库设计](./database-design.md)
- [Schema SQL](./database/schema.sql)
- [API 路由](./app/api/v1/)
- [现有测试](./backend/tests/)
