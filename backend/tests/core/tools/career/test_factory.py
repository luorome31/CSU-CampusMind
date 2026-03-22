"""
Tests for career tools factory function.
"""
from unittest.mock import patch, MagicMock

from app.core.tools.career import create_career_tools
from app.core.context import ToolContext


class TestCreateCareerTools:
    """Test create_career_tools factory function."""

    def test_returns_list_of_tools(self):
        """Test that create_career_tools returns a list."""
        ctx = ToolContext()
        tools = create_career_tools(ctx)
        assert isinstance(tools, list)

    def test_returns_four_tools(self):
        """Test that create_career_tools returns exactly 4 tools."""
        ctx = ToolContext()
        tools = create_career_tools(ctx)
        assert len(tools) == 4

    def test_tool_names(self):
        """Test that all expected tool names are present."""
        ctx = ToolContext()
        tools = create_career_tools(ctx)
        tool_names = [t.name for t in tools]
        assert "career_teachin" in tool_names
        assert "career_campus_recruit" in tool_names
        assert "career_campus_intern" in tool_names
        assert "career_jobfair" in tool_names

    @patch("app.core.tools.career.tools.CareerService")
    def test_teachin_tool_call(self, mock_service_class):
        """Test career_teachin tool execution."""
        mock_service = MagicMock()
        mock_service.get_teachin.return_value = "宣讲会列表"
        mock_service_class.return_value = mock_service

        ctx = ToolContext()
        tools = create_career_tools(ctx)
        teachin_tool = next(t for t in tools if t.name == "career_teachin")

        result = teachin_tool.invoke({"zone": "岳麓山校区"})
        assert "宣讲会" in result
        mock_service.get_teachin.assert_called_once_with("岳麓山校区")

    @patch("app.core.tools.career.tools.CareerService")
    def test_campus_recruit_tool_call(self, mock_service_class):
        """Test career_campus_recruit tool execution."""
        mock_service = MagicMock()
        mock_service.get_campus_recruit.return_value = "招聘信息"
        mock_service_class.return_value = mock_service

        ctx = ToolContext()
        tools = create_career_tools(ctx)
        recruit_tool = next(t for t in tools if t.name == "career_campus_recruit")

        result = recruit_tool.invoke({"keyword": "软件"})
        assert "招聘" in result
        mock_service.get_campus_recruit.assert_called_once_with("软件")

    @patch("app.core.tools.career.tools.CareerService")
    def test_campus_intern_tool_call(self, mock_service_class):
        """Test career_campus_intern tool execution."""
        mock_service = MagicMock()
        mock_service.get_campus_intern.return_value = "实习信息"
        mock_service_class.return_value = mock_service

        ctx = ToolContext()
        tools = create_career_tools(ctx)
        intern_tool = next(t for t in tools if t.name == "career_campus_intern")

        result = intern_tool.invoke({"keyword": "字节"})
        assert "实习" in result
        mock_service.get_campus_intern.assert_called_once_with("字节")

    @patch("app.core.tools.career.tools.CareerService")
    def test_jobfair_tool_call(self, mock_service_class):
        """Test career_jobfair tool execution."""
        mock_service = MagicMock()
        mock_service.get_jobfair.return_value = "招聘会列表"
        mock_service_class.return_value = mock_service

        ctx = ToolContext()
        tools = create_career_tools(ctx)
        jobfair_tool = next(t for t in tools if t.name == "career_jobfair")

        result = jobfair_tool.invoke({})
        assert "招聘会" in result
        mock_service.get_jobfair.assert_called_once_with()

    @patch("app.core.tools.career.tools.CareerService")
    def test_tool_exception_handling(self, mock_service_class):
        """Test that tools handle exceptions gracefully."""
        mock_service = MagicMock()
        mock_service.get_teachin.side_effect = Exception("Network error")
        mock_service_class.return_value = mock_service

        ctx = ToolContext()
        tools = create_career_tools(ctx)
        teachin_tool = next(t for t in tools if t.name == "career_teachin")

        result = teachin_tool.invoke({"zone": ""})
        assert "失败" in result
        assert "Network error" not in result  # Error details should not be exposed