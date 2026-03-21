# 测试 Fixtures

## conftest.py Fixtures

### mock_knowledge_service

模拟 KnowledgeService 用于测试。

```python
@pytest.fixture
def mock_knowledge_service():
    mock = MagicMock()
    mock.create_knowledge = MagicMock(return_value=MagicMock(
        id="test_kb_1",
        name="Test Knowledge",
        to_dict=lambda: {...}
    ))
    return mock
```

**用途**: API 测试中避免依赖真实数据库

---

### mock_rag_handler

模拟 RAG 处理器用于测试。

```python
@pytest.fixture
def mock_rag_handler():
    mock = MagicMock()
    mock.retrieve_with_sources = AsyncMock(return_value={
        "context": "Test context from retrieval",
        "sources": [
            {"content": "Source 1", "score": 0.9}
        ]
    })
    return mock
```

**用途**: Completion API 测试

---

### mock_crawl_service

模拟爬取服务用于测试。

```python
@pytest.fixture
def mock_crawl_service():
    mock = MagicMock()
    mock.crawl_url = AsyncMock(return_value={
        "success": True,
        "task_id": "crawl_task_123",
        "status": "pending"
    })
    return mock
```

**用途**: Crawl API 测试

---

### mock_langchain_model

模拟 LangChain 聊天模型。

```python
@pytest.fixture
def mock_langchain_model():
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.tool_calls = [
        {"name": "test_tool", "args": {"query": "test"}, "id": "call_123"}
    ]
    mock_response.content = "Test response"
    mock_model.bind_tools = MagicMock(return_value=MagicMock(
        ainvoke=AsyncMock(return_value=mock_response)
    ))
    return mock_model
```

**用途**: ReactAgent 测试

---

### mock_base_tool

模拟 LangChain BaseTool。

```python
@pytest.fixture
def mock_base_tool():
    tool = MagicMock()
    tool.name = "test_tool"
    tool.description = "A test tool"
    tool.coroutine = True
    tool.ainvoke = AsyncMock(return_value="Tool execution result")
    return tool
```

---

### mock_stream_writer

模拟流式响应写入器。

```python
@pytest.fixture
def mock_stream_writer():
    writer = MagicMock()
    writer_calls = []

    def capture_call(data):
        writer_calls.append(data)

    writer.side_effect = capture_call
    writer.calls = writer_calls
    return writer
```

---

## 示例数据 Fixtures

### sample_knowledge_request

```python
@pytest.fixture
def sample_knowledge_request():
    return {
        "name": "Test Knowledge Base",
        "description": "A test knowledge base",
        "user_id": "test_user"
    }
```

### sample_retrieve_request

```python
@pytest.fixture
def sample_retrieve_request():
    return {
        "query": "What is CampusMind?",
        "knowledge_ids": ["test_kb_1"],
        "enable_vector": True,
        "enable_keyword": True,
        "top_k": 5,
        "min_score": 0.0
    }
```

### sample_crawl_request

```python
@pytest.fixture
def sample_crawl_request():
    return {
        "url": "https://example.com",
        "knowledge_id": "test_kb_1"
    }
```

---

## 使用示例

```python
def test_create_knowledge(mock_knowledge_service, sample_knowledge_request):
    # 使用 mock service
    result = mock_knowledge_service.create_knowledge(
        name=sample_knowledge_request["name"],
        user_id=sample_knowledge_request["user_id"]
    )
    assert result.id == "test_kb_1"

@pytest.mark.asyncio
async def test_retrieve(mock_rag_handler, sample_retrieve_request):
    # 使用 mock RAG handler
    result = await mock_rag_handler.retrieve_with_sources(
        query=sample_retrieve_request["query"],
        knowledge_ids=sample_retrieve_request["knowledge_ids"]
    )
    assert result["context"] == "Test context from retrieval"
```
