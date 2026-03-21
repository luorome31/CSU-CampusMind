# RAG 检索工具

在知识库中检索相关内容的工具。

## 工具列表

### rag_search - 知识库检索

在指定知识库中检索相关内容。

**参数:**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| query | string | 是 | 用户查询问题 |
| knowledge_ids | array[string] | 是 | 知识库 ID 列表 |
| top_k | int | 否 | 返回结果数量，默认 5 |
| min_score | float | 否 | 最低分数阈值，默认 0.0 |

**返回格式:**

```markdown
## 检索结果

根据查询 "校园有哪些图书馆资源" 找到以下相关内容：

---

### 来源：图书馆使用指南.md

相关内容：
中南大学图书馆提供丰富的纸质和电子资源，包括：
- 纸质图书：300 万册
- 电子图书：250 万种
- 数据库：80 余个

**相关度分数**: 0.92

---

### 来源：电子资源使用说明.md

相关内容：
图书馆电子资源可通过校园网访问，包括中国知网、万方数据...

**相关度分数**: 0.85
```

---

## 特性

### 混合检索

RAG 工具内部使用混合检索策略：

1. **向量检索 (ChromaDB)**: 基于语义相似度
2. **关键词检索 (Elasticsearch)**: 基于 BM25 算法
3. **结果融合**: 去重、排序

### 无认证要求

RAG 工具是公开的，所有用户都可以使用，不需要登录。

---

## 实现

```python
from app.core.tools.rag_tool import create_rag_tool

# 创建 RAG 工具
rag_tool = create_rag_tool(knowledge_ids=["t_abc123", "t_def456"])

# 工具定义
class RAGSearchInput(BaseModel):
    query: str = Field(..., description="用户查询问题")
    top_k: int = Field(default=5, description="返回结果数量")
    min_score: float = Field(default=0.0, description="最低分数阈值")
```

---

## 使用场景

RAG 工具主要用于：

1. **课程问答**: 检索课程资料、政策文件
2. **校园指南**: 检索校园生活指南
3. **规章制度**: 检索学校规章制度
4. **常见问题**: 检索 FAQ 文档
