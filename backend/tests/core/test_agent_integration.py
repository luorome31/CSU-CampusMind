"""
集成测试：Agent + Tools + Auth

测试场景：
1. 未登录用户只能使用 Library 和 RAG 工具
2. 登录用户可以使用 JWC + Library + RAG 工具
3. JWT token 解析正确
4. ToolContext 正确传递 user_id
"""
import pytest
from unittest.mock import Mock, MagicMock

from app.core.context import ToolContext
from app.core.agents.factory import AgentFactory
from app.core.tools.jwc import create_jwc_tools
from app.core.tools.library import create_library_tools


class TestToolContext:
    """测试 ToolContext"""

    def test_unauthenticated_context(self):
        """未登录上下文"""
        ctx = ToolContext()
        assert not ctx.is_authenticated
        assert ctx.user_id is None
        assert ctx.get_subsystem_session("jwc") is None

    def test_authenticated_context(self):
        """已登录上下文"""
        mock_manager = Mock()
        mock_session = Mock()
        mock_manager.get_session.return_value = mock_session

        ctx = ToolContext(user_id="123456", session_manager=mock_manager)
        assert ctx.is_authenticated
        assert ctx.user_id == "123456"

        session = ctx.get_subsystem_session("jwc")
        mock_manager.get_session.assert_called_once_with("123456", "jwc")
        assert session == mock_session


class TestJwcToolsFactory:
    """测试 JWC 工具工厂"""

    def test_tools_hide_user_id(self):
        """工具函数签名不包含 user_id"""
        mock_manager = Mock()
        ctx = ToolContext(user_id="123456", session_manager=mock_manager)

        tools = create_jwc_tools(ctx)

        # 检查工具名称
        tool_names = [t.name for t in tools]
        assert "jwc_grade" in tool_names
        assert "jwc_schedule" in tool_names
        assert "jwc_rank" in tool_names
        assert "jwc_level_exam" in tool_names

        # 检查参数签名 - 不应该包含 user_id
        grade_tool = next(t for t in tools if t.name == "jwc_grade")
        params = grade_tool.args_schema.model_fields
        assert "user_id" not in params
        assert "term" in params

    def test_unauthenticated_returns_message(self):
        """未登录时返回提示消息"""
        ctx = ToolContext()  # 未认证
        tools = create_jwc_tools(ctx)

        grade_tool = next(t for t in tools if t.name == "jwc_grade")
        result = grade_tool.func(term="")

        assert "请先登录" in result


class TestLibraryToolsFactory:
    """测试 Library 工具工厂"""

    def test_tools_available_without_auth(self):
        """图书馆工具无需认证"""
        ctx = ToolContext()  # 未认证
        tools = create_library_tools(ctx)

        tool_names = [t.name for t in tools]
        assert "library_search" in tool_names
        assert "library_get_book_location" in tool_names


class TestAgentFactory:
    """测试 AgentFactory"""

    def test_create_agent_for_anonymous(self):
        """为匿名用户创建 Agent"""
        mock_manager = Mock()
        factory = AgentFactory(mock_manager)

        agent = factory.create_agent(
            user_id=None,
            knowledge_ids=[]
        )

        # 检查 system prompt 包含游客模式
        assert "游客模式" in agent.system_prompt

    def test_create_agent_for_authenticated(self):
        """为登录用户创建 Agent"""
        mock_manager = Mock()
        factory = AgentFactory(mock_manager)

        agent = factory.create_agent(
            user_id="123456",
            knowledge_ids=[]
        )

        # 检查 system prompt 包含用户信息
        assert "123456" in agent.system_prompt
        assert "已登录" in agent.system_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
