# 项目结构

## 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py                # 配置加载
│   │
│   ├── api/                     # API 路由
│   │   ├── __init__.py
│   │   ├── dependencies.py       # 依赖注入
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py           # 认证接口
│   │       ├── knowledge.py      # 知识库接口
│   │       ├── knowledge_file.py # 知识文件接口
│   │       ├── crawl.py          # 爬取接口
│   │       ├── index.py          # 索引接口
│   │       ├── retrieve.py       # 检索接口
│   │       └── completion.py      # 对话接口
│   │
│   ├── core/                     # 核心模块
│   │   ├── __init__.py
│   │   ├── security.py           # JWT 管理
│   │   ├── context.py            # 工具上下文
│   │   ├── agents/               # Agent 实现
│   │   │   ├── __init__.py
│   │   │   ├── react_agent.py    # ReAct Agent
│   │   │   └── factory.py        # Agent 工厂
│   │   ├── session/              # Session 管理
│   │   │   ├── __init__.py
│   │   │   ├── manager.py        # 统一会话管理器
│   │   │   ├── factory.py        # Session 工厂
│   │   │   ├── cache.py          # Session 缓存
│   │   │   ├── persistence.py    # Session 持久化
│   │   │   ├── rate_limiter.py   # 登录限流
│   │   │   ├── cas_login.py      # CAS 登录
│   │   │   └── providers/        # 子系统 Provider
│   │   │       ├── base.py
│   │   │       ├── jwc.py
│   │   │       ├── oa.py
│   │   │       └── ...
│   │   └── tools/                # LangChain 工具
│   │       ├── __init__.py
│   │       ├── jwc/              # 教务系统工具
│   │       ├── library/          # 图书馆工具
│   │       ├── career/           # 就业中心工具
│   │       ├── oa/               # 办公网工具
│   │       └── rag_tool.py       # RAG 工具
│   │
│   ├── database/                 # 数据库
│   │   ├── __init__.py
│   │   ├── session.py            # 数据库会话
│   │   └── models/               # SQLModel 模型
│   │       ├── __init__.py
│   │       ├── user.py
│   │       ├── knowledge.py
│   │       ├── knowledge_file.py
│   │       ├── dialog.py
│   │       ├── chat_history.py
│   │       └── tool_call_log.py
│   │
│   ├── services/                 # 业务服务
│   │   ├── __init__.py
│   │   ├── knowledge.py
│   │   ├── knowledge_file.py
│   │   ├── crawl/                # 爬取服务
│   │   │   └── crawler.py
│   │   ├── storage/              # 存储服务
│   │   │   └── client.py
│   │   └── rag/                  # RAG 服务
│   │       ├── __init__.py
│   │       ├── handler.py        # RAG 处理器
│   │       ├── retrieval.py      # 混合检索
│   │       ├── indexer.py       # 索引器
│   │       ├── embedding.py     # 嵌入服务
│   │       ├── vector_db.py     # 向量数据库
│   │       ├── es_client.py     # ES 客户端
│   │       └── chunker.py       # 分块器
│   │
│   ├── repositories/             # 数据访问层
│   │   ├── __init__.py
│   │   └── dialog_repository.py
│   │
│   └── schema/                   # Pydantic 模型
│       ├── __init__.py
│       ├── chunk.py
│       └── search.py
│
├── tests/                        # 测试
│   ├── __init__.py
│   ├── conftest.py              # pytest 配置
│   ├── api/                     # API 测试
│   ├── core/                    # 核心模块测试
│   ├── services/               # 服务层测试
│   └── e2e/                    # 端到端测试
│
├── docs/                         # 文档
│   ├── api/
│   ├── auth/
│   ├── models/
│   ├── tools/
│   ├── rag/
│   ├── config/
│   ├── testing/
│   └── deploy/
│
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

---

## 核心模块说明

### app/main.py

FastAPI 应用入口，定义 API 路由和中间件。

### app/config.py

使用 Pydantic BaseModel 从环境变量加载配置。

### app/api/

API 路由层，处理 HTTP 请求/响应。

### app/core/

核心业务逻辑：
- `security.py`: JWT 令牌管理
- `session/`: 统一会话管理（CAS + 子系统）
- `agents/`: LangChain Agent 实现
- `tools/`: 各类工具定义

### app/database/models/

SQLModel ORM 模型，定义数据库表结构。

### app/services/

业务服务层，封装业务逻辑。

### app/repositories/

数据访问层，提供数据库操作接口。
