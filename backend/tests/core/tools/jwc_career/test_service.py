"""
CareerService unit tests
"""
import pytest

from app.core.tools.jwc_career.service import CareerService
from app.core.tools.jwc_career.client import (
    TeachinEntry,
    CampusRecruitEntry,
    CampusInternEntry,
    JobfairEntry,
)


@pytest.fixture
def service():
    return CareerService()


class TestFormatTeachin:
    """Test teachin markdown formatting."""

    def test_format_teachin_with_data(self, service):
        entries = [
            TeachinEntry(company="Test Company", location="Test Location", time="2026-03-19 14:00"),
        ]
        result = service._format_teachin(entries)
        assert "| 公司名称 | 宣讲地点 | 宣讲时间 |" in result
        assert "| Test Company | Test Location | 2026-03-19 14:00 |" in result

    def test_format_teachin_empty(self, service):
        result = service._format_teachin([])
        assert result == "宣讲会查询结果为空"


class TestFormatCampusRecruit:
    """Test campus recruit markdown formatting."""

    def test_format_campus_recruit_with_data(self, service):
        entries = [
            CampusRecruitEntry(title="Test Title", city="Test City", publish_time="2026-03-17"),
        ]
        result = service._format_campus_recruit(entries)
        assert "| 招聘公告 | 工作城市 | 发布时间 |" in result
        assert "| Test Title | Test City | 2026-03-17 |" in result

    def test_format_campus_recruit_empty(self, service):
        result = service._format_campus_recruit([])
        assert result == "校园招聘查询结果为空"


class TestFormatCampusIntern:
    """Test campus intern markdown formatting."""

    def test_format_campus_intern_with_data(self, service):
        entries = [
            CampusInternEntry(title="Test Title", city="Test City", publish_time="2026-03-18"),
        ]
        result = service._format_campus_intern(entries)
        assert "| 实习公告 | 工作城市 | 发布时间 |" in result
        assert "| Test Title | Test City | 2026-03-18 |" in result

    def test_format_campus_intern_empty(self, service):
        result = service._format_campus_intern([])
        assert result == "实习信息查询结果为空"


class TestFormatJobfair:
    """Test jobfair markdown formatting."""

    def test_format_jobfair_with_data(self, service):
        entries = [
            JobfairEntry(
                name="Test Name",
                city="Test City",
                address="Test Address",
                fair_type="Test Type",
                time="2026-04-19",
            ),
        ]
        result = service._format_jobfair(entries)
        assert "| 招聘会名称 | 举办城市 | 举办地址 | 招聘会类型 | 举办时间 |" in result
        assert "| Test Name | Test City | Test Address | Test Type | 2026-04-19 |" in result

    def test_format_jobfair_empty(self, service):
        result = service._format_jobfair([])
        assert result == "招聘会查询结果为空"
