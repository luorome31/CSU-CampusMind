# 生产环境配置

## 安全检查清单

### 必需修改

- [ ] **JWT_SECRET_KEY**: 使用强随机密钥替换默认值
- [ ] **OPENAI_API_KEY**: 使用真实的 API 密钥
- [ ] **CAS_USERNAME/PASSWORD**: 配置真实的 CAS 凭证

### 推荐配置

- [ ] **数据库**: 使用 PostgreSQL 替代 SQLite
- [ ] **Redis**: 配置密码认证
- [ ] **HTTPS**: 使用 HTTPS 终结

---

## Docker 部署

### Dockerfile 示例

项目使用 uv 管理依赖，Dockerfile 示例：

```dockerfile
FROM python:3.11-slim

# 安装 uv
RUN pip install uv

WORKDIR /app

# 复制 pyproject.toml 和 lockfile
COPY pyproject.toml uv.lock ./

# 使用 uv 安装依赖
RUN uv sync --frozen

# 复制代码
COPY . .

# 运行服务
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml 示例

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/campusmind
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./data/chroma:/app/data/chroma  # 持久化 ChromaDB 数据

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=campusmind
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    command: redis-server --requirepass ${REDIS_PASSWORD}

volumes:
  postgres_data:
```

---

## 环境变量示例

### 生产环境 (.env.production)

```bash
# 安全相关（必须配置）
JWT_SECRET_KEY=super-secure-random-key-at-least-32-chars
OPENAI_API_KEY=sk-prod-xxxxxxxxxxxxx

# 数据库
DATABASE_URL=postgresql://user:pass@prod-db:5432/campusmind

# Redis
REDIS_URL=redis://:password@prod-redis:6379/0

# 存储
STORAGE_MODE=oss
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_ACCESS_KEY_ID=xxx
OSS_ACCESS_KEY_SECRET=xxx
OSS_BUCKET=campusmind-prod

# Elasticsearch
ELASTICSEARCH_HOSTS=http://es1:9200,http://es2:9200

# ChromaDB
CHROMA_PERSIST_PATH=/data/chroma
```

---

## 健康检查

```bash
curl http://localhost:8000/health
```

---

## 日志配置

使用 Loguru，默认日志输出到 stderr。

可通过 `LOGURU_SINK` 环境变量配置日志输出。
