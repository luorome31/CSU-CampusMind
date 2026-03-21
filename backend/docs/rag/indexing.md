# 内容索引

将文本内容分块、嵌入并存储到向量数据库和关键词数据库。

## 索引流程

```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────┐
│  内容   │────▶│ 分块    │────▶│  向量嵌入   │────▶│ ChromaDB│
│  输入   │     │ Chunker │     │ Embedding   │     │  存储   │
└─────────┘     └─────────┘     └─────────────┘     └─────────┘
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │ Elasticsearch│
                                    │  关键词存储  │
                                    └─────────────┘
```

## 分块策略

### TextChunker

```python
class TextChunker:
    def __init__(self, chunk_size: int = 500, overlap_size: int = 100):
        self.chunk_size = chunk_size        # 每块字符数
        self.overlap_size = overlap_size    # 重叠字符数
```

### 分块算法

使用滑动窗口分块：

```
文本: "这是第一段内容。这是第二段内容。这是第三段内容。"

chunk_size=10, overlap_size=5

Chunk 1: "这是第一段内容"
Chunk 2: "段内容。这是第二段"  (重叠 5 字符)
Chunk 3: "段内容。这是第三段"
```

### 优点

- 保持上下文连贯性
- 避免句子/段落被切断
- 重叠部分提供连续上下文

## 嵌入模型

### Embedding Service

```python
class EmbeddingService:
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        base_url: str = "https://api.openai.com/v1",
        api_key: Optional[str] = None
    ):
        ...

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量获取嵌入向量"""
        ...
```

### 配置

| 参数 | 默认值 | 描述 |
|------|--------|------|
| embedding_model | text-embedding-3-small | 嵌入模型 |
| embedding_base_url | https://api.openai.com/v1 | API 地址 |
| embedding_api_key | - | API 密钥 |

## 存储

### ChromaDB (向量存储)

```python
class VectorDB:
    async def insert_chunks(
        self,
        collection_name: str,
        chunks: List[ChunkModel],
        embeddings: List[List[float]]
    ) -> bool:
        """插入分块到向量数据库"""
        ...

    async def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5
    ) -> List[SearchModel]:
        """相似度搜索"""
        ...
```

### Elasticsearch (关键词存储)

```python
class ESClient:
    def insert_chunks(
        self,
        index_name: str,
        chunks: List[ChunkModel]
    ) -> bool:
        """插入分块到关键词索引"""
        ...

    def search(
        self,
        index_name: str,
        query: str,
        top_k: int = 5
    ) -> List[dict]:
        """BM25 搜索"""
        ...
```

## ChunkModel

```python
class ChunkModel(BaseModel):
    chunk_id: str           # 分块唯一 ID
    content: str           # 文本内容
    file_id: str           # 来源文件 ID
    file_name: str         # 来源文件名
    knowledge_id: str      # 所属知识库
    chunk_index: int       # 分块序号
```

## 索引 API

### 直接索引

```python
result = await indexer.index_content(
    content="要索引的文本内容",
    knowledge_id="t_abc123",
    source_name="document.md",
    metadata={"enable_vector": True, "enable_keyword": True}
)
```

### 从 OSS 索引

```python
result = await indexer.index_from_oss(
    oss_url="https://oss.example.com/bucket/path/doc.md",
    knowledge_id="t_abc123",
    storage_client=storage_client
)
```

## 索引响应

```json
{
  "success": true,
  "chunk_count": 10,
  "file_id": "file_xyz789",
  "knowledge_id": "t_abc123"
}
```
