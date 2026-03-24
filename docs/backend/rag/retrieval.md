# 混合检索

结合 ChromaDB 向量检索和 Elasticsearch 关键词检索的混合检索策略。

## 检索架构

```
┌─────────┐
│  Query  │
└────┬────┘
     │
     ├──────────────────┐
     ▼                  ▼
┌─────────────┐  ┌─────────────┐
│  ChromaDB   │  │Elasticsearch│
│  向量检索   │  │  关键词检索 │
└──────┬──────┘  └──────┬──────┘
       │                 │
       └────────┬────────┘
                ▼
        ┌─────────────┐
        │ 结果融合   │
        │ 去重+排序  │
        └──────┬─────┘
               ▼
        ┌─────────────┐
        │  Top-K     │
        │   结果     │
        └─────────────┘
```

## 检索流程

### 1. 向量检索 (ChromaDB)

```python
# 伪代码
async def retrieve_vector_documents(query, knowledge_ids, top_k):
    documents = []
    for knowledge_id in knowledge_ids:
        # 在对应 collection 中搜索
        docs = await vector_db.search(
            collection_name=knowledge_id,
            query=query,
            top_k=top_k
        )
        documents.extend(docs)
    return documents
```

- **相似度度量**: 余弦相似度
- **返回字段**: chunk_id, content, score, metadata

### 2. 关键词检索 (Elasticsearch)

```python
# 伪代码
def retrieve_keyword_documents(query, knowledge_ids, top_k):
    documents = []
    for knowledge_id in knowledge_ids:
        # 在对应 index 中搜索
        docs = es_client.search(
            index_name=knowledge_id,
            query=query,
            top_k=top_k
        )
        documents.extend(docs)
    return documents
```

- **算法**: BM25
- **返回字段**: chunk_id, content, score, metadata

### 3. 结果融合

```python
async def mix_retrieve(query, knowledge_ids, enable_vector, enable_keyword, top_k):
    all_documents = []

    # 向量检索
    if enable_vector:
        vector_docs = await retrieve_vector_documents(query, knowledge_ids, top_k)
        all_documents.extend(vector_docs)

    # 关键词检索
    if enable_keyword:
        keyword_docs = await retrieve_keyword_documents(query, knowledge_ids, top_k)
        all_documents.extend(keyword_docs)

    # 去重（按 chunk_id）
    seen = set()
    deduplicated = []
    for doc in sorted(all_documents, key=lambda x: x.score, reverse=True):
        if doc.chunk_id not in seen:
            seen.add(doc.chunk_id)
            deduplicated.append(doc)

    # 返回 Top-K
    return deduplicated[:top_k]
```

## 搜索模型

```python
class SearchModel(BaseModel):
    chunk_id: str           # 分块 ID
    content: str           # 内容
    score: float           # 相似度分数
    source: Optional[str]  # 来源文件名
    knowledge_id: str       # 所属知识库
```

## 配置参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| enable_vector | bool | true | 是否启用向量检索 |
| enable_keyword | bool | true | 是否启用关键词检索 |
| top_k | int | 5 | 返回结果数量 |
| min_score | float | 0.0 | 最低分数阈值 |

## 分数归一化

向量检索和关键词检索的分数范围不同：
- **ChromaDB**: 余弦相似度，范围 [-1, 1]，通常为正
- **Elasticsearch**: BM25 分数，通常为正

检索结果按分数降序排列，分数越高相关性越强。
