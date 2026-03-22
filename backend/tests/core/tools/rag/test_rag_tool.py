"""
RagTool 单元测试
"""
import pytest
from unittest.mock import patch, AsyncMock


class TestRagTool:
    """RagTool 业务逻辑测试"""

    @pytest.fixture
    def mock_rag_handler(self):
        """Mock rag_handler for RagTool tests"""
        with patch("app.core.tools.rag_tool.rag_handler") as mock:
            mock.retrieve_with_sources = AsyncMock(return_value={
                "context": "Test context about Python programming.",
                "sources": [
                    {"content": "Source 1", "score": 0.95, "file_name": "test1.txt"},
                    {"content": "Source 2", "score": 0.85, "file_name": "test2.txt"}
                ]
            })
            yield mock

    def test_create_rag_tool(self):
        """测试创建 RAG 工具工厂函数"""
        from app.core.tools.rag_tool import create_rag_tool, RagTool

        tool = create_rag_tool()

        assert isinstance(tool, RagTool)
        assert tool.name == "rag_search"

    def test_rag_tool_name(self):
        """测试 RAG 工具名称"""
        from app.core.tools.rag_tool import RagTool

        tool = RagTool()
        assert tool.name == "rag_search"

    def test_rag_tool_description(self):
        """测试 RAG 工具描述"""
        from app.core.tools.rag_tool import RagTool

        tool = RagTool()
        assert "knowledge bases" in tool.description
        assert "query" in tool.description

    def test_rag_tool_args_schema(self):
        """测试 RAG 工具参数模式"""
        from app.core.tools.rag_tool import RagTool, RagToolInput

        tool = RagTool()
        assert tool.args_schema == RagToolInput

    @pytest.mark.asyncio
    async def test_arun_with_results(self, mock_rag_handler):
        """测试异步执行-有结果"""
        from app.core.tools.rag_tool import RagTool

        tool = RagTool()

        result = await tool._arun(
            query="What is Python?",
            knowledge_ids=["kb_1", "kb_2"],
            top_k=5,
            min_score=0.0
        )

        assert "=== 相关上下文 ===" in result
        assert "Test context" in result
        assert "=== 来源 ===" in result

    @pytest.mark.asyncio
    async def test_arun_empty_context(self, mock_rag_handler):
        """测试异步执行-空结果"""
        from app.core.tools.rag_tool import RagTool

        mock_rag_handler.retrieve_with_sources = AsyncMock(return_value={
            "context": "",
            "sources": []
        })

        tool = RagTool()

        result = await tool._arun(
            query="Unknown topic?",
            knowledge_ids=["kb_1"]
        )

        assert result == "未找到相关信息。"

    @pytest.mark.asyncio
    async def test_arun_with_error(self, mock_rag_handler):
        """测试异步执行-错误处理"""
        from app.core.tools.rag_tool import RagTool

        mock_rag_handler.retrieve_with_sources = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        tool = RagTool()

        result = await tool._arun(
            query="test",
            knowledge_ids=["kb_1"]
        )

        assert "错误" in result
        assert "Database connection failed" in result

    @pytest.mark.asyncio
    async def test_arun_with_sources(self, mock_rag_handler):
        """测试异步执行-带来源信息"""
        from app.core.tools.rag_tool import RagTool

        tool = RagTool()

        result = await tool._arun(
            query="test query",
            knowledge_ids=["kb_1"],
            top_k=3
        )

        # Check source formatting
        assert "test1.txt" in result
        assert "test2.txt" in result

    def test_rag_tool_input_schema(self):
        """测试输入参数模式"""
        from app.core.tools.rag_tool import RagToolInput

        # Valid input
        valid_input = RagToolInput(
            query="test query",
            knowledge_ids=["kb_1", "kb_2"],
            top_k=5,
            min_score=0.0
        )
        assert valid_input.query == "test query"
        assert len(valid_input.knowledge_ids) == 2

        # Test defaults
        default_input = RagToolInput(
            query="test",
            knowledge_ids=["kb_1"]
        )
        assert default_input.top_k == 5
        assert default_input.min_score == 0.0

    def test_rag_tool_result_schema(self):
        """测试结果参数模式"""
        from app.core.tools.rag_tool import RagToolResult

        result = RagToolResult(
            context="Test context",
            sources=[{"content": "Source 1", "score": 0.9}]
        )

        assert result.context == "Test context"
        assert len(result.sources) == 1


class TestRagToolEdgeCases:
    """RagTool 边界情况测试"""

    @pytest.fixture
    def mock_rag_handler(self):
        """Mock rag_handler"""
        with patch("app.core.tools.rag_tool.rag_handler") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_arun_single_knowledge_id(self, mock_rag_handler):
        """测试单个知识库ID"""
        from app.core.tools.rag_tool import RagTool

        mock_rag_handler.retrieve_with_sources = AsyncMock(return_value={
            "context": "Context",
            "sources": []
        })

        tool = RagTool()

        _ = await tool._arun(
            query="test",
            knowledge_ids=["kb_1"]
        )

        # Verify handler was called with single ID
        call_args = mock_rag_handler.retrieve_with_sources.call_args
        assert call_args.kwargs["knowledge_ids"] == ["kb_1"]

    @pytest.mark.asyncio
    async def test_arun_custom_top_k(self, mock_rag_handler):
        """测试自定义 top_k"""
        from app.core.tools.rag_tool import RagTool

        mock_rag_handler.retrieve_with_sources = AsyncMock(return_value={
            "context": "Context",
            "sources": []
        })

        tool = RagTool()

        _ = await tool._arun(
            query="test",
            knowledge_ids=["kb_1"],
            top_k=10
        )

        call_args = mock_rag_handler.retrieve_with_sources.call_args
        assert call_args.kwargs["top_k"] == 10

    @pytest.mark.asyncio
    async def test_arun_custom_min_score(self, mock_rag_handler):
        """测试自定义 min_score"""
        from app.core.tools.rag_tool import RagTool

        mock_rag_handler.retrieve_with_sources = AsyncMock(return_value={
            "context": "Context",
            "sources": []
        })

        tool = RagTool()

        _ = await tool._arun(
            query="test",
            knowledge_ids=["kb_1"],
            min_score=0.5
        )

        call_args = mock_rag_handler.retrieve_with_sources.call_args
        assert call_args.kwargs["min_score"] == 0.5


class TestRagToolSync:
    """RagTool 同步执行测试"""

    def test_run_sync_fallback(self):
        """测试同步执行降级"""
        with patch("app.core.tools.rag_tool.rag_handler") as mock:
            mock.retrieve_with_sources = AsyncMock(return_value={
                "context": "Sync context",
                "sources": []
            })

            from app.core.tools.rag_tool import RagTool

            tool = RagTool()

            # Run sync method
            result = tool._run(
                query="test",
                knowledge_ids=["kb_1"]
            )

            assert "Sync context" in result
