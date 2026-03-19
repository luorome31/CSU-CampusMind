"""
LangChain StructuredTool definitions for career center tools.
"""

from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool

from .service import CareerService


# Input schemas

class TeachinInput(BaseModel):
    """Input for career_teachin tool."""
    zone: str = Field(default="", description="校区筛选，如'岳麓山校区'、'天心校区'、'杏林校区'、'潇湘校区'，留空则显示全部")


class CampusRecruitInput(BaseModel):
    """Input for career_campus_recruit tool."""
    keyword: str = Field(default="", description="关键词搜索，留空则显示全部")


class CampusInternInput(BaseModel):
    """Input for career_campus_intern tool."""
    keyword: str = Field(default="", description="关键词搜索，留空则显示全部")


class JobfairInput(BaseModel):
    """Input for career_jobfair tool."""
    pass


# Tool functions

def _get_teachin(zone: str = "") -> str:
    """Get 宣讲会 list from career center."""
    service = CareerService()
    return service.get_teachin(zone)


def _get_campus_recruit(keyword: str = "") -> str:
    """Get 校园招聘 list from career center."""
    service = CareerService()
    return service.get_campus_recruit(keyword)


def _get_campus_intern(keyword: str = "") -> str:
    """Get 实习 list from career center."""
    service = CareerService()
    return service.get_campus_intern(keyword)


def _get_jobfair() -> str:
    """Get 招聘会 list from career center."""
    service = CareerService()
    return service.get_jobfair()


# Tools

CareerTeachinTool = StructuredTool.from_function(
    func=_get_teachin,
    name="career_teachin",
    description="获取中南大学就业信息网站的宣讲会信息。支持按校区筛选（岳麓山校区、天心校区、杏林校区、潇湘校区）。返回宣讲会列表，包括公司名称、宣讲地点和宣讲时间。",
    args_schema=TeachinInput,
)

CareerCampusRecruitTool = StructuredTool.from_function(
    func=_get_campus_recruit,
    name="career_campus_recruit",
    description="获取中南大学就业信息网站的校园招聘信息。支持关键词搜索。返回招聘信息列表，包括招聘公告，工作城市和发布时间。",
    args_schema=CampusRecruitInput,
)

CareerCampusInternTool = StructuredTool.from_function(
    func=_get_campus_intern,
    name="career_campus_intern",
    description="获取中南大学就业信息网站的实习信息。支持关键词搜索。返回实习信息列表，包括实习公告、工作城市和发布时间。",
    args_schema=CampusInternInput,
)

CareerJobfairTool = StructuredTool.from_function(
    func=_get_jobfair,
    name="career_jobfair",
    description="获取中南大学就业信息网站的招聘会信息。返回招聘会列表，包括招聘会名称、举办城市、举办地址、招聘会类型和举办时间。",
    args_schema=JobfairInput,
)

CAREER_TOOLS = [
    CareerTeachinTool,
    CareerCampusRecruitTool,
    CareerCampusInternTool,
    CareerJobfairTool,
]
