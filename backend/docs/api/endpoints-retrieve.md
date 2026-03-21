# RAG 检索接口

混合检索接口，结合 ChromaDB 向量搜索和 Elasticsearch 关键词搜索。

## 检索

执行混合检索，返回相关上下文和来源。

### 请求

```
POST /api/v1/retrieve
```

```json
{
  "query": "校园有哪些招聘活动？",
  "knowledge_ids": ["t_abc123"],
  "enable_vector": true,
  "enable_keyword": true,
  "top_k": 5,
  "min_score": 0.0
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| query | string | 是 | 用户查询 |
| knowledge_ids | array[string] | 是 | 知识库 ID 列表 |
| enable_vector | bool | 否 | 启用向量搜索，默认 true |
| enable_keyword | bool | 否 | 启用关键词搜索，默认 true |
| top_k | int | 否 | 返回结果数量，默认 5 |
| min_score | float | 否 | 最低分数阈值，默认 0.0 |

### 响应

```json
{
  "success": true,
  "context": "检索到的上下文内容...",
  "sources": [
    {
      "chunk_id": "chunk_001",
      "content": "学校将于10月举办秋季招聘会...",
      "score": 0.95,
      "source": "recruitment.md"
    }
  ]
}
```

---

## 检索流程

```
┌─────────┐     ┌───────────────┐     ┌─────────┐
│  Query  │────▶│  Embedding    │────▶│ ChromaDB│
│  输入   │     │  向量化       │     │ 向量检索 │
└─────────┘     └───────────────┘     └─────────┘
                     │
                     ▼
┌─────────┐     ┌───────────────┐     ┌─────────────┐
│ BM25    │────▶│ Elasticsearch │────▶│  结果融合   │
│ 查询    │     │  关键词检索   │     │  去重排序   │
└─────────┘     └───────────────┘     └─────────────┘
                                            │
                                            ▼
                                     ┌─────────────┐
                                     │  返回结果   │
                                     └─────────────┘
```

## 混合检索策略

1. **向量检索 (ChromaDB)**: 基于语义相似度
2. **关键词检索 (Elasticsearch)**: 基于 BM25 算法
3. **结果融合**: 按分数排序，去重，返 top_k
