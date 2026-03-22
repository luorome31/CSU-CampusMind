"""
ReactAgent 单元测试
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from langchain_core.messages import HumanMessage


class TestReactAgent:
    """ReactAgent 业务逻辑测试"""

    @pytest.fixture
    def agent(self, mock_langchain_model, mock_base_tool):
        """Create ReactAgent instance"""
        from app.core.agents.react_agent import ReactAgent

        return ReactAgent(
            model=mock_langchain_model,
            system_prompt="You are a helpful assistant.",
            tools=[mock_base_tool]
        )

    def test_wrap_stream_output(self, agent):
        """测试流输出包装方法"""
        output = agent._wrap_stream_output("event", {"status": "START", "message": "test"})

        assert output["type"] == "event"
        assert "timestamp" in output
        assert output["data"]["status"] == "START"
        assert output["data"]["message"] == "test"

    def test_wrap_stream_output_response_chunk(self, agent):
        """测试响应块输出"""
        output = agent._wrap_stream_output(
            "response_chunk",
            {"chunk": "Hello", "accumulated": "Hello"}
        )

        assert output["type"] == "response_chunk"
        assert output["data"]["chunk"] == "Hello"
        assert output["data"]["accumulated"] == "Hello"

    def test_get_tool_by_name_found(self, agent, mock_base_tool):
        """测试获取存在的工具"""
        tool = agent.get_tool_by_name("test_tool")
        assert tool is not None
        assert tool.name == "test_tool"

    def test_get_tool_by_name_not_found(self, agent):
        """测试获取不存在的工具"""
        tool = agent.get_tool_by_name("nonexistent_tool")
        assert tool is None

    def test_get_tool_by_name_empty_tools(self):
        """测试空工具列表"""
        from app.core.agents.react_agent import ReactAgent
        from unittest.mock import MagicMock

        mock_model = MagicMock()
        agent = ReactAgent(model=mock_model, tools=[])

        tool = agent.get_tool_by_name("any_tool")
        assert tool is None

    @pytest.mark.asyncio
    async def test_should_continue_with_tool_calls(self, agent):
        """测试有工具调用时继续执行"""
        # Create mock state with tool_calls
        mock_message = MagicMock()
        mock_message.tool_calls = [{"name": "test_tool", "args": {}}]

        state = {
            "messages": [mock_message],
            "tool_call_count": 0
        }

        result = await agent._should_continue(state)
        assert result == "execute_tool"

    @pytest.mark.asyncio
    async def test_should_continue_without_tool_calls(self, agent):
        """测试无工具调用时结束"""
        mock_message = MagicMock()
        mock_message.tool_calls = []

        state = {
            "messages": [mock_message],
            "tool_call_count": 0
        }

        result = await agent._should_continue(state)
        # LangGraph uses END (or __end__) for termination
        assert result in ["END", "__end__"]

    @pytest.mark.asyncio
    async def test_call_model_node_without_tools(self, agent, mock_langchain_model, mock_stream_writer):
        """测试模型节点无工具调用"""
        # Setup mock model response without tool_calls
        mock_response = MagicMock()
        mock_response.tool_calls = []

        mock_langchain_model.bind_tools.return_value.ainvoke = AsyncMock(
            return_value=mock_response
        )

        mock_message = MagicMock()
        mock_message.tool_calls = []

        state = {
            "messages": [mock_message],
            "tool_call_count": 0
        }

        result = await agent._call_model_node(state, mock_stream_writer)

        # Should return messages
        assert "messages" in result
        # Should send events via stream writer
        assert len(mock_stream_writer.calls) > 0

    @pytest.mark.asyncio
    async def test_execute_tool_node(self, agent, mock_base_tool, mock_stream_writer):
        """测试工具执行节点"""
        mock_message = MagicMock()
        mock_message.tool_calls = [
            {
                "name": "test_tool",
                "args": {"query": "test query"},
                "id": "call_123"
            }
        ]

        state = {
            "messages": [mock_message],
            "tool_call_count": 0
        }

        result = await agent._execute_tool_node(state, mock_stream_writer)

        assert "messages" in result
        assert result["tool_call_count"] == 1

    @pytest.mark.asyncio
    async def test_execute_tool_node_tool_not_found(self, agent, mock_stream_writer):
        """测试工具执行节点-工具不存在"""
        mock_message = MagicMock()
        mock_message.tool_calls = [
            {
                "name": "nonexistent_tool",
                "args": {},
                "id": "call_123"
            }
        ]

        state = {
            "messages": [mock_message],
            "tool_call_count": 0
        }

        result = await agent._execute_tool_node(state, mock_stream_writer)

        # Should still return with error message in messages
        assert "messages" in result

    @pytest.mark.asyncio
    async def test_execute_tool_node_no_tool_calls(self, agent, mock_stream_writer):
        """测试工具执行节点-无工具调用"""
        mock_message = MagicMock()
        mock_message.tool_calls = []

        state = {
            "messages": [mock_message],
            "tool_call_count": 0
        }

        result = await agent._execute_tool_node(state, mock_stream_writer)

        assert result["tool_call_count"] == 0

    @pytest.mark.asyncio
    async def test_init_agent(self, agent):
        """测试 Agent 初始化"""
        assert agent.graph is None
        await agent._init_agent()
        assert agent.graph is not None

    def test_agent_initialization(self, mock_langchain_model, mock_base_tool):
        """测试 Agent 初始化参数"""
        from app.core.agents.react_agent import ReactAgent

        agent = ReactAgent(
            model=mock_langchain_model,
            system_prompt="Test prompt",
            tools=[mock_base_tool]
        )

        assert agent.model is mock_langchain_model
        assert agent.system_prompt == "Test prompt"
        assert len(agent.tools) == 1
        assert agent.tools[0] is mock_base_tool

    def test_agent_initialization_default_params(self, mock_langchain_model):
        """测试 Agent 默认参数"""
        from app.core.agents.react_agent import ReactAgent

        agent = ReactAgent(model=mock_langchain_model)

        assert agent.model is mock_langchain_model
        assert agent.system_prompt is None
        assert agent.tools == []


class TestStreamOutput:
    """StreamOutput 类型测试"""

    def test_stream_output_type_event(self):
        """测试事件类型输出"""
        from app.core.agents.react_agent import StreamOutput, StreamEventData

        event_data: StreamEventData = {
            "title": "Test",
            "status": "START",
            "message": "Test message"
        }

        output: StreamOutput = {
            "type": "event",
            "timestamp": 1234567890.0,
            "data": event_data
        }

        assert output["type"] == "event"
        assert output["data"]["status"] == "START"

    def test_stream_output_type_response_chunk(self):
        """测试响应块类型输出"""
        from app.core.agents.react_agent import StreamOutput

        output: StreamOutput = {
            "type": "response_chunk",
            "timestamp": 1234567890.0,
            "data": {
                "chunk": "Hello",
                "accumulated": "Hello"
            }
        }

        assert output["type"] == "response_chunk"
        assert output["data"]["chunk"] == "Hello"


class TestReactAgentState:
    """ReactAgentState 类型测试"""

    def test_state_with_messages(self):
        """测试状态包含消息"""
        from app.core.agents.react_agent import ReactAgentState

        state: ReactAgentState = {
            "messages": [HumanMessage(content="Hello")],
            "tool_call_count": 0,
            "model_call_count": 0
        }

        assert len(state["messages"]) == 1
        assert state["tool_call_count"] == 0

    def test_state_without_optional_fields(self):
        """测试可选字段"""
        from app.core.agents.react_agent import ReactAgentState

        state: ReactAgentState = {
            "messages": []
        }

        assert "messages" in state
        assert "tool_call_count" not in state
