"""
Business logic service for career center information with markdown formatting.
"""

import logging

from .client import CareerClient, TeachinEntry, CampusRecruitEntry, CampusInternEntry, JobfairEntry

logger = logging.getLogger(__name__)


class CareerService:
    """Service for career center information."""

    def __init__(self):
        self.client = CareerClient()

    def get_teachin(self, zone: str = "") -> str:
        """
        Get 宣讲会 list as markdown table.

        Args:
            zone: Filter by campus zone

        Returns:
            Markdown formatted table or error message
        """
        try:
            entries = self.client.get_teachin(zone)
            return self._format_teachin(entries)
        except Exception as e:
            logger.error(f"Teachin query failed: {e}")
            return "宣讲会查询失败，请稍后重试"

    def get_campus_recruit(self, keyword: str = "") -> str:
        """
        Get 校园招聘 list as markdown table.

        Args:
            keyword: Filter by keyword in title

        Returns:
            Markdown formatted table or error message
        """
        try:
            entries = self.client.get_campus_recruit(keyword)
            return self._format_campus_recruit(entries)
        except Exception as e:
            logger.error(f"Campus recruit query failed: {e}")
            return "校园招聘查询失败，请稍后重试"

    def get_campus_intern(self, keyword: str = "") -> str:
        """
        Get 实习 list as markdown table.

        Args:
            keyword: Filter by keyword in title

        Returns:
            Markdown formatted table or error message
        """
        try:
            entries = self.client.get_campus_intern(keyword)
            return self._format_campus_intern(entries)
        except Exception as e:
            logger.error(f"Campus intern query failed: {e}")
            return "实习信息查询失败，请稍后重试"

    def get_jobfair(self) -> str:
        """
        Get 招聘会 list as markdown table.

        Returns:
            Markdown formatted table or error message
        """
        try:
            entries = self.client.get_jobfair()
            return self._format_jobfair(entries)
        except Exception as e:
            logger.error(f"Jobfair query failed: {e}")
            return "招聘会查询失败，请稍后重试"

    def _format_teachin(self, entries: list[TeachinEntry]) -> str:
        """Format teachin entries as markdown table."""
        if not entries:
            return "宣讲会查询结果为空"

        header = "| 公司名称 | 宣讲地点 | 宣讲时间 |\n|---|---|---|"
        rows = []
        for e in entries:
            rows.append(f"| {e.company} | {e.location} | {e.time} |")
        return header + "\n" + "\n".join(rows)

    def _format_campus_recruit(self, entries: list[CampusRecruitEntry]) -> str:
        """Format campus recruit entries as markdown table."""
        if not entries:
            return "校园招聘查询结果为空"

        header = "| 招聘公告 | 工作城市 | 发布时间 |\n|---|---|---|"
        rows = []
        for e in entries:
            rows.append(f"| {e.title} | {e.city} | {e.publish_time} |")
        return header + "\n" + "\n".join(rows)

    def _format_campus_intern(self, entries: list[CampusInternEntry]) -> str:
        """Format campus intern entries as markdown table."""
        if not entries:
            return "实习信息查询结果为空"

        header = "| 实习公告 | 工作城市 | 发布时间 |\n|---|---|---|"
        rows = []
        for e in entries:
            rows.append(f"| {e.title} | {e.city} | {e.publish_time} |")
        return header + "\n" + "\n".join(rows)

    def _format_jobfair(self, entries: list[JobfairEntry]) -> str:
        """Format jobfair entries as markdown table."""
        if not entries:
            return "招聘会查询结果为空"

        header = "| 招聘会名称 | 举办城市 | 举办地址 | 招聘会类型 | 举办时间 |\n|---|---|---|---|---|"
        rows = []
        for e in entries:
            rows.append(f"| {e.name} | {e.city} | {e.address} | {e.fair_type} | {e.time} |")
        return header + "\n" + "\n".join(rows)
