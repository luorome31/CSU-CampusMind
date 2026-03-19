"""
JWC Career tools unit tests
"""
import pytest

from app.core.tools.jwc_career.tools import (
    JWC_CAREER_TOOLS,
    JwcTeachinTool,
    JwcCampusRecruitTool,
    JwcCampusInternTool,
    JwcJobfairTool,
    TeachinInput,
    CampusRecruitInput,
    CampusInternInput,
    JobfairInput,
)


class TestToolsCount:
    """Test that JWC_CAREER_TOOLS has correct number of tools."""

    def test_has_four_tools(self):
        assert len(JWC_CAREER_TOOLS) == 4


class TestToolNames:
    """Test tool names are correct."""

    def test_teachin_tool_name(self):
        assert JwcTeachinTool.name == "jwc_teachin"

    def test_campus_recruit_tool_name(self):
        assert JwcCampusRecruitTool.name == "jwc_campus_recruit"

    def test_campus_intern_tool_name(self):
        assert JwcCampusInternTool.name == "jwc_campus_intern"

    def test_jobfair_tool_name(self):
        assert JwcJobfairTool.name == "jwc_jobfair"


class TestToolDescriptions:
    """Test tool descriptions contain expected keywords."""

    def test_teachin_description_contains_keywords(self):
        desc = JwcTeachinTool.description
        assert "宣讲会" in desc
        assert "中南大学" in desc
        assert "公司名称" in desc
        assert "宣讲地点" in desc
        assert "宣讲时间" in desc

    def test_campus_recruit_description_contains_keywords(self):
        desc = JwcCampusRecruitTool.description
        assert "校园招聘" in desc
        assert "中南大学" in desc
        assert "招聘公告" in desc
        assert "工作城市" in desc
        assert "发布时间" in desc

    def test_campus_intern_description_contains_keywords(self):
        desc = JwcCampusInternTool.description
        assert "实习" in desc
        assert "中南大学" in desc
        assert "实习公告" in desc
        assert "工作城市" in desc
        assert "发布时间" in desc

    def test_jobfair_description_contains_keywords(self):
        desc = JwcJobfairTool.description
        assert "招聘会" in desc
        assert "中南大学" in desc
        assert "招聘会名称" in desc
        assert "举办城市" in desc
        assert "举办地址" in desc
        assert "招聘会类型" in desc
        assert "举办时间" in desc


class TestToolInputSchemas:
    """Test tool input schemas."""

    def test_teachin_input_schema(self):
        assert hasattr(TeachinInput, "model_fields")

    def test_campus_recruit_input_schema(self):
        assert hasattr(CampusRecruitInput, "model_fields")

    def test_campus_intern_input_schema(self):
        assert hasattr(CampusInternInput, "model_fields")

    def test_jobfair_input_schema(self):
        assert hasattr(JobfairInput, "model_fields")


class TestToolInvocation:
    """Test tool invocation works."""

    def test_teachin_tool_is_callable(self):
        assert callable(JwcTeachinTool.func)

    def test_campus_recruit_tool_is_callable(self):
        assert callable(JwcCampusRecruitTool.func)

    def test_campus_intern_tool_is_callable(self):
        assert callable(JwcCampusInternTool.func)

    def test_jobfair_tool_is_callable(self):
        assert callable(JwcJobfairTool.func)
