# 配置指南

CampusMind 后端配置说明。

## 环境变量

所有配置通过环境变量加载，参考 `.env.example`。

---

## 存储配置

### 存储模式

```bash
STORAGE_MODE=minio  # minio 或 oss
```

### MinIO 配置

| 变量 | 默认值 | 描述 |
|------|--------|------|
| MINIO_ENDPOINT | localhost:9000 | MinIO 服务地址 |
| MINIO_ACCESS_KEY | minioadmin | 访问密钥 |
| MINIO_SECRET_KEY | minioadmin | 秘密密钥 |
| MINIO_BUCKET | campusmind | 存储桶名 |

### 阿里云 OSS 配置

| 变量 | 描述 |
|------|------|
| OSS_ENDPOINT | OSS 端点 |
| OSS_ACCESS_KEY_ID | Access Key ID |
| OSS_ACCESS_KEY_SECRET | Access Key Secret |
| OSS_BUCKET | 存储桶名 |

---

## 数据库配置

```bash
DATABASE_URL=sqlite:///./campusmind.db
```

支持 SQLite、PostgreSQL、MySQL 等 SQLAlchemy 支持的数据库。

---

## Redis 配置

```bash
REDIS_URL=redis://localhost:6379/0
```

用于：
- CASTGC 存储
- Session 缓存
- 聊天历史缓存
- 登录频率限制

---

## JWT 配置

| 变量 | 默认值 | 描述 |
|------|--------|------|
| JWT_SECRET_KEY | your-secret-key-change-in-production | 密钥（生产环境必须修改） |
| JWT_ALGORITHM | HS256 | 算法 |
| JWT_EXPIRE_HOURS | 24 | Token 有效期（小时） |

---

## LLM 配置

```bash
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1
```

---

## Embedding 配置

```bash
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=sk-xxx
```

---

## 向量数据库配置

### ChromaDB

```bash
CHROMA_PERSIST_PATH=./data/chroma
```

### Elasticsearch

```bash
ELASTICSEARCH_HOSTS=http://localhost:9200
```

---

## Session 配置

```bash
SESSION_STORAGE_PATH=./data/csu_sessions.json
SESSION_TTL_SECONDS=1800
```

---

## CAS 配置

```bash
CAS_USERNAME=your_cas_username
CAS_PASSWORD=your_cas_password
```

---

## 完整示例 (.env)

```bash
# Storage
STORAGE_MODE=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=campusmind

# Database
DATABASE_URL=sqlite:///./campusmind.db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_EXPIRE_HOURS=24

# LLM
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-3.5-turbo

# Embedding
EMBEDDING_API_KEY=sk-xxx

# ChromaDB
CHROMA_PERSIST_PATH=./data/chroma

# Elasticsearch
ELASTICSEARCH_HOSTS=http://localhost:9200

# Session
SESSION_TTL_SECONDS=1800
```
