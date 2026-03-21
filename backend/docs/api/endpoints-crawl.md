# 网页爬取接口

使用 Crawl4AI 进行网页内容爬取，支持单 URL 和批量爬取。

## 爬取单个 URL

爬取网页内容并可选存储到 OSS。

### 请求

```
POST /api/v1/crawl/create
```

```json
{
  "url": "https://example.com/article",
  "store_to_oss": true
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| url | string | 是 | 待爬取 URL |
| store_to_oss | bool | 否 | 是否存储到 OSS，默认 true |

### 响应

```json
{
  "success": true,
  "url": "https://example.com/article",
  "oss_url": "https://oss.example.com/crawl/xxx.md",
  "title": "页面标题"
}
```

---

## 爬取并索引

爬取网页、存储到 OSS、创建文件记录，并索引到向量/关键词数据库。

### 请求

```
POST /api/v1/crawl/create-and-index
```

```json
{
  "url": "https://example.com/article",
  "knowledge_id": "t_abc123",
  "user_id": "system",
  "enable_vector": true,
  "enable_keyword": true
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| url | string | 是 | 待爬取 URL |
| knowledge_id | string | 是 | 目标知识库 ID |
| user_id | string | 否 | 用户 ID |
| enable_vector | bool | 否 | 启用向量索引，默认 true |
| enable_keyword | bool | 否 | 启用关键词索引，默认 true |

### 响应

```json
{
  "success": true,
  "url": "https://example.com/article",
  "oss_url": "https://oss.example.com/crawl/xxx.md",
  "title": "页面标题",
  "file_id": "file_xyz789"
}
```

---

## 批量爬取

并发爬取多个 URL。

### 请求

```
POST /api/v1/crawl/batch
```

```json
{
  "urls": [
    "https://example.com/article1",
    "https://example.com/article2"
  ],
  "store_to_oss": true
}
```

### 响应

```json
[
  {
    "success": true,
    "url": "https://example.com/article1",
    "oss_url": "https://oss.example.com/crawl/xxx1.md",
    "title": "文章1"
  },
  {
    "success": false,
    "url": "https://example.com/article2",
    "error": "Connection timeout"
  }
]
```

---

## 批量爬取并索引

批量爬取并为每个 URL 创建文件记录和索引。

### 请求

```
POST /api/v1/crawl/batch-with-knowledge
```

```json
{
  "urls": [
    "https://example.com/article1",
    "https://example.com/article2"
  ],
  "knowledge_id": "t_abc123",
  "user_id": "system",
  "enable_vector": true,
  "enable_keyword": true
}
```

### 响应

```json
[
  {
    "success": true,
    "url": "https://example.com/article1",
    "oss_url": "https://oss.example.com/crawl/xxx1.md",
    "title": "文章1",
    "file_id": "file_001"
  },
  {
    "success": true,
    "url": "https://example.com/article2",
    "oss_url": "https://oss.example.com/crawl/xxx2.md",
    "title": "文章2",
    "file_id": "file_002"
  }
]
```

---

## 爬取流程

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  URL    │────▶│ Crawl4AI│────▶│  OSS    │────▶│  Index  │
│  输入   │     │  爬取   │     │  存储   │     │  索引   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                                            │
                                            ▼
                                    ┌─────────────┐
                                    │ KnowledgeFile│
                                    │   记录创建   │
                                    └─────────────┘
```
