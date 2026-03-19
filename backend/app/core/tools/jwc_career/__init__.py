"""
JWC Career module for fetching career center information from career.csu.edu.cn.

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
    JwcTeachinTool,
    JwcCampusRecruitTool,
    JwcCampusInternTool,
    JwcJobfairTool,
    JWC_CAREER_TOOLS,
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
    "JwcTeachinTool",
    "JwcCampusRecruitTool",
    "JwcCampusInternTool",
    "JwcJobfairTool",
    "JWC_CAREER_TOOLS",
]
