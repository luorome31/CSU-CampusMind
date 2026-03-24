# 本地开发环境

## 环境要求

- Python 3.10+ (通过 uv 管理)
- Redis
- ChromaDB (可选，用于向量检索)
- Elasticsearch (可选，用于关键词检索)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/luorome31/CampusMind.git
cd CampusMind/backend
```

### 2. 安装依赖

使用 uv 安装项目依赖：

```bash
uv sync
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入必要配置
```

### 4. 启动 Redis (Docker)

```bash
docker run -d -p 6379:6379 redis:7
```

### 5. 启动服务

使用 uv 运行开发服务器（自动重载）：

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或直接运行：

```bash
uv run python -m uvicorn app.main:app --reload
```

### 6. 验证

访问 http://localhost:8000/docs 查看 Swagger UI。

---

## 依赖服务

### Redis (必需)

用于 Session 存储和缓存。

```bash
docker run -d -p 6379:6379 redis:7
```

### ChromaDB (推荐)

用于向量检索。

```bash
# 嵌入式模式（开发用）
uv add chromadb

# 或 Docker 模式
docker run -d -p 8001:8000 ghcr.io/chroma-core/chroma:latest
```

### Elasticsearch (推荐)

用于关键词检索。

```bash
docker run -d -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.11.0
```

### MinIO (可选)

本地 S3 兼容存储。

```bash
docker run -d -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```

---

## 开发工具

### 代码格式化

```bash
uv run ruff format .
```

### 代码检查

```bash
uv run ruff check .
```

### 运行测试

```bash
uv run pytest tests/ -v
```

---

## 热重载

使用 `uv run uvicorn --reload` 实现代码修改自动重载。

注意：某些模块（如 ChromaDB 客户端）的初始化代码只在启动时执行，修改后需重启服务。

---

## uv 常用命令

| 命令 | 说明 |
|------|------|
| `uv sync` | 同步依赖到当前环境 |
| `uv run <cmd>` | 在项目环境中运行命令 |
| `uv add <package>` | 添加依赖 |
| `uv remove <package>` | 移除依赖 |
| `uv lock` | 更新 lockfile |
| `uv pip install` | 安装依赖（不修改 lockfile） |
