"""
Career center module for fetching career information from career.csu.edu.cn.

No authentication required.
"""

from .client import (
    TeachinEntry,
    CampusRecruitEntry,
    CampusInternEntry,
    JobfairEntry,
    CareerClient,
)
from .service import CareerService
from .tools import (
    TeachinInput,
    CampusRecruitInput,
    CampusInternInput,
    JobfairInput,
    CareerTeachinTool,
    CareerCampusRecruitTool,
    CareerCampusInternTool,
    CareerJobfairTool,
    CAREER_TOOLS,
    create_career_tools,
)

__all__ = [
    # Data models
    "TeachinEntry",
    "CampusRecruitEntry",
    "CampusInternEntry",
    "JobfairEntry",
    # Client
    "CareerClient",
    # Service
    "CareerService",
    # Tools
    "TeachinInput",
    "CampusRecruitInput",
    "CampusInternInput",
    "JobfairInput",
    "CareerTeachinTool",
    "CareerCampusRecruitTool",
    "CareerCampusInternTool",
    "CareerJobfairTool",
    "CAREER_TOOLS",
    "create_career_tools",
]
