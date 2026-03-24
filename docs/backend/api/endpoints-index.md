# 内容索引接口

将文本内容分块并索引到 ChromaDB（向量数据库）和 Elasticsearch（关键词索引）。

## 直接索引内容

将文本内容分块并索引。

### 请求

```
POST /api/v1/index/create
```

```json
{
  "content": "这是要索引的文本内容...",
  "knowledge_id": "t_abc123",
  "source_name": "my_document.md",
  "enable_vector": true,
  "enable_keyword": true
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| content | string | 是 | 待索引文本内容 |
| knowledge_id | string | 是 | 目标知识库 ID |
| source_name | string | 否 | 源文件名，默认 "text" |
| enable_vector | bool | 否 | 启用向量索引，默认 true |
| enable_keyword | bool | 否 | 启用关键词索引，默认 true |

### 响应

```json
{
  "success": true,
  "chunk_count": 5,
  "file_id": "file_xyz789",
  "knowledge_id": "t_abc123"
}
```

---

## 从 OSS 索引

从 OSS 下载文件内容并索引。

### 请求

```
POST /api/v1/index/create-from-oss
```

```json
{
  "oss_url": "https://oss.example.com/bucket/path/document.md",
  "knowledge_id": "t_abc123",
  "enable_vector": true,
  "enable_keyword": true
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| oss_url | string | 是 | OSS 文件 URL |
| knowledge_id | string | 是 | 目标知识库 ID |
| enable_vector | bool | 否 | 启用向量索引，默认 true |
| enable_keyword | bool | 否 | 启用关键词索引，默认 true |

### 响应

```json
{
  "success": true,
  "chunk_count": 10,
  "file_id": "file_xyz789",
  "knowledge_id": "t_abc123"
}
```

---

## 索引流程

```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────┐
│  内容   │────▶│ 分块    │────▶│  向量嵌入    │────▶│ ChromaDB│
│  输入   │     │ Chunker │     │ Embedding   │     │  存储   │
└─────────┘     └─────────┘     └─────────────┘     └─────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ Elasticsearch│
                                        │  关键词存储  │
                                        └─────────────┘
```

### 分块策略

- **chunk_size**: 500 字符（默认）
- **overlap_size**: 100 字符（默认）
- 使用滑动窗口保持上下文连贯性
