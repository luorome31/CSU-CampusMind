# CampusMind 后端文档

CampusMind 智能问答助手后端 API 文档。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend                                   │
│                    (Streamlit / Web App)                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CampusMind Backend                            │
│                                                                     │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │   Auth    │  │  Knowledge │  │   Crawl   │  │ Completion │       │
│  │  API      │  │   API     │  │   API     │  │   API      │       │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘       │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    UnifiedSessionManager                       │ │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │ │
│  │   │   JWC   │  │ Library │  │ Career  │  │   OA    │        │ │
│  │   │ Provider│  │ Provider│  │ Provider│  │ Provider│        │ │
│  │   └─────────┘  └─────────┘  └─────────┘  └─────────┘        │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                       ReactAgent + Tools                       │ │
│  │   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  │ │
│  │   │  JWC   │  │Library │  │Career │  │   OA   │  │  RAG   │  │ │
│  │   │ Tools  │  │ Tools  │  │ Tools │  │ Tools  │  │ Tools  │  │ │
│  │   └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
   ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
   │    Redis    │       │  ChromaDB   │       │Elasticsearch│
   │   (Cache)   │       │  (Vector)   │       │ (Keyword)   │
   └─────────────┘       └─────────────┘       └─────────────┘
```

## 核心概念

### 认证体系

CampusMind 使用 **JWT + CAS** 双层认证：

1. **CAS 认证**: 统一身份认证，获取跨子系统 CASTGC
2. **JWT Token**: 应用内接口访问控制

### 工具系统

基于 LangChain 的工具系统，支持：

| 工具 | 来源 | 需要登录 |
|------|------|----------|
| 成绩/课表查询 | 教务系统 | 是 |
| 图书搜索 | 图书馆 | 否 |
| 宣讲会/招聘信息 | 就业中心 | 否 |
| 校内通知 | 办公网 | 是 |
| 知识库检索 | RAG | 否 |

### RAG 管道

混合检索结合向量搜索 (ChromaDB) 和关键词搜索 (Elasticsearch)。

## 技术栈

| 类别 | 技术 |
|------|------|
| Python 管理 | uv |
| Web 框架 | FastAPI |
| 数据库 | SQLModel (SQLAlchemy) |
| 缓存/Session | Redis |
| 向量数据库 | ChromaDB |
| 关键词索引 | Elasticsearch |
| LLM 框架 | LangChain |
| 爬取 | Crawl4AI |
| 存储 | MinIO / 阿里云 OSS |

## 快速开始

```bash
cd backend

# 使用 uv 安装依赖
uv sync

# 配置环境变量
cp .env.example .env

# 启动服务（使用 uv 运行）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

## 文档导航

### API 参考

- [API 概览](./api/README.md)
- [认证接口](./api/endpoints-auth.md)
- [知识库 CRUD](./api/endpoints-knowledge.md)
- [知识文件管理](./api/endpoints-knowledge-file.md)
- [网页爬取](./api/endpoints-crawl.md)
- [内容索引](./api/endpoints-index.md)
- [RAG 检索](./api/endpoints-retrieve.md)
- [LLM 对话](./api/endpoints-completion.md)

### 认证与授权

- [认证概述](./auth/README.md)
- [会话管理](./auth/session-management.md)
- [认证流程](./auth/auth-flow.md)

### 数据模型

- [模型概览](./models/README.md)
- [用户模型](./models/user.md)
- [知识库模型](./models/knowledge.md)
- [对话模型](./models/dialog.md)

### 工具系统

- [工具架构](./tools/README.md)
- [教务系统工具](./tools/jwc.md)
- [图书馆工具](./tools/library.md)
- [就业中心工具](./tools/career.md)
- [办公网工具](./tools/oa.md)
- [RAG 检索工具](./tools/rag.md)

### RAG 管道

- [RAG 概述](./rag/README.md)
- [混合检索](./rag/retrieval.md)
- [内容索引](./rag/indexing.md)

### 配置指南

- [环境变量](./config/README.md)
- [生产环境部署](./config/deployment.md)

### 测试指南

- [测试概览](./testing/README.md)
- [测试 Fixtures](./testing/fixtures.md)

### 开发指南

- [本地开发](./deploy/development.md)
- [项目结构](./deploy/project-structure.md)

## 环境变量

关键环境变量：

| 变量 | 描述 | 必需 |
|------|------|------|
| DATABASE_URL | 数据库连接 | 是 |
| REDIS_URL | Redis 连接 | 是 |
| JWT_SECRET_KEY | JWT 密钥 | 是 |
| OPENAI_API_KEY | OpenAI API Key | 是 |
| ELASTICSEARCH_HOSTS | ES 集群地址 | 推荐 |
| CHROMA_PERSIST_PATH | ChromaDB 路径 | 推荐 |

详见 [配置指南](./config/README.md)

## 测试

```bash
# 运行所有测试
uv run pytest

# 收集测试（不运行）
uv run pytest --collect-only
```

## 最佳实践

### API 调用

1. 先调用 `/auth/login` 获取 Token
2. 在请求头中携带 `Authorization: Bearer <token>`
3. Token 过期后调用 `/auth/refresh` 刷新

### 错误处理

```python
try:
    response = await client.post("/auth/login", json=data)
except HTTPStatusError as e:
    if e.response.status_code == 401:
        # 处理登录失败
    elif e.response.status_code == 429:
        # 处理频率限制
```

### 并发控制

- 爬取使用 SemaphoreDispatcher 限制并发数
- Session 获取使用分布式锁避免竞态
- 聊天历史使用双写策略保证一致性
