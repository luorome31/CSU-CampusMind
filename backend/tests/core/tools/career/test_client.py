"""
CareerClient unit tests
"""
import pytest
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
