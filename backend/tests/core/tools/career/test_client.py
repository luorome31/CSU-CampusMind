"""
CareerClient unit tests
"""
import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from app.core.tools.career.client import (
    CareerClient,
    TeachinEntry,
    CampusRecruitEntry,
    CampusInternEntry,
    JobfairEntry,
)


@pytest.fixture
def client():
    return CareerClient()


class TestTeachinEntry:
    """Test TeachinEntry structure."""

    def test_teachin_entry_creation(self):
        entry = TeachinEntry(company="Test Company", location="Test Location", time="Test Time")
        assert entry.company == "Test Company"
        assert entry.location == "Test Location"
        assert entry.time == "Test Time"


class TestCampusRecruitEntry:
    """Test CampusRecruitEntry structure."""

    def test_campus_recruit_entry_creation(self):
        entry = CampusRecruitEntry(title="Test Title", city="Test City", publish_time="2024-01-01")
        assert entry.title == "Test Title"
        assert entry.city == "Test City"
        assert entry.publish_time == "2024-01-01"


class TestCampusInternEntry:
    """Test CampusInternEntry structure."""

    def test_campus_intern_entry_creation(self):
        entry = CampusInternEntry(title="Test Title", city="Test City", publish_time="2024-01-01")
        assert entry.title == "Test Title"
        assert entry.city == "Test City"
        assert entry.publish_time == "2024-01-01"


class TestJobfairEntry:
    """Test JobfairEntry structure."""

    def test_jobfair_entry_creation(self):
        entry = JobfairEntry(
            name="Test Name",
            city="Test City",
            address="Test Address",
            fair_type="Test Type",
            time="Test Time",
        )
        assert entry.name == "Test Name"
        assert entry.city == "Test City"
        assert entry.address == "Test Address"
        assert entry.fair_type == "Test Type"
        assert entry.time == "Test Time"


class TestParseTeachin:
    """Test parsing of teachin HTML."""

    def test_parse_teachin_html(self, client):
        """Test parsing teachin HTML from local file."""
        html_path = Path(__file__).parent.parent.parent.parent.parent.parent / "docs/development_doc/宣讲会信息.txt"
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            start = content.find("<!DOCTYPE")
            if start != -1:
                content = content[start:]

        soup = BeautifulSoup(content, "html.parser")
        entries = []

        for ul in soup.select("ul.infoList.teachinList"):
            company_li = ul.select_one("li.span1")
            location_li = ul.select_one("li.span4")
            time_li = ul.select_one("li.span5")

            if company_li and location_li and time_li:
                a_tag = company_li.select_one("a")
                company = (
                    a_tag.get("title", a_tag.get_text(strip=True))
                    if a_tag
                    else company_li.get_text(strip=True)
                )
                entries.append(
                    TeachinEntry(
                        company=company,
                        location=location_li.get_text(strip=True),
                        time=time_li.get_text(strip=True),
                    )
                )

        assert len(entries) > 0
        assert "贝斯（无锡）信息系统有限公司" in entries[0].company
        assert "2026-03-19" in entries[0].time


class TestParseCampusRecruit:
    """Test parsing of campus recruit HTML."""

    def test_parse_campus_recruit_html(self, client):
        """Test parsing campus recruit HTML from local file."""
        html_path = Path(__file__).parent.parent.parent.parent.parent.parent / "docs/development_doc/公司招聘信息.txt"
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            start = content.find("<!DOCTYPE")
            if start != -1:
                content = content[start:]

        soup = BeautifulSoup(content, "html.parser")
        entries = []

        for ul in soup.select("div.infoBox > ul.infoList"):
            title_li = ul.select_one("li.span7")
            city_li = ul.select_one("li.span1")
            time_li = ul.select_one("li.span4")

            if title_li and city_li and time_li:
                entries.append(
                    CampusRecruitEntry(
                        title=title_li.get_text(strip=True),
                        city=city_li.get_text(strip=True),
                        publish_time=time_li.get_text(strip=True),
                    )
                )

        assert len(entries) > 0
        assert "有色金属类招聘信息汇总" in entries[0].title
        assert "2026-03-17" in entries[0].publish_time


class TestParseCampusIntern:
    """Test parsing of campus intern HTML."""

    def test_parse_campus_intern_html(self, client):
        """Test parsing campus intern HTML from local file."""
        html_path = Path(__file__).parent.parent.parent.parent.parent.parent / "docs/development_doc/公司实习信息.txt"
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            start = content.find("<!DOCTYPE")
            if start != -1:
                content = content[start:]

        soup = BeautifulSoup(content, "html.parser")
        entries = []

        for ul in soup.select("div.infoBox > ul.infoList"):
            title_li = ul.select_one("li.span7")
            city_li = ul.select_one("li.span1")
            time_li = ul.select_one("li.span4")

            if title_li and city_li and time_li:
                entries.append(
                    CampusInternEntry(
                        title=title_li.get_text(strip=True),
                        city=city_li.get_text(strip=True),
                        publish_time=time_li.get_text(strip=True),
                    )
                )

        assert len(entries) > 0
        assert "淘天有限公司" in entries[0].title
        assert "2026-03-18" in entries[0].publish_time


class TestParseJobfair:
    """Test parsing of jobfair HTML."""

    def test_parse_jobfair_html(self, client):
        """Test parsing jobfair HTML from local file."""
        html_path = Path(__file__).parent.parent.parent.parent.parent.parent / "docs/development_doc/招聘会信息.txt"
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            start = content.find("<!DOCTYPE")
            if start != -1:
                content = content[start:]

        soup = BeautifulSoup(content, "html.parser")
        entries = []

        for ul in soup.select("ul.infoList.jobfairList"):
            name_li = ul.select_one("li.span1")
            city_li = ul.select_one("li.span2")
            address_li = ul.select_one("li.span3")
            type_li = ul.select_one("li.span4")
            time_li = ul.select_one("li.span5")

            if name_li and city_li and address_li and type_li and time_li:
                entries.append(
                    JobfairEntry(
                        name=name_li.get_text(strip=True),
                        city=city_li.get_text(strip=True),
                        address=address_li.get_text(strip=True),
                        fair_type=type_li.get_text(strip=True),
                        time=time_li.get_text(strip=True),
                    )
                )

        assert len(entries) > 0
        assert "中南大学2026届春季第二场大型综合双选会" in entries[0].name
        assert "2026-04-19" in entries[0].time
