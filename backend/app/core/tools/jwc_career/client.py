"""
HTTP client for career.csu.edu.cn with BeautifulSoup HTML parsing.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


BASE_URL = "http://career.csu.edu.cn"


@dataclass
class TeachinEntry:
    """宣讲会 entry."""
    company: str
    location: str
    time: str


@dataclass
class CampusRecruitEntry:
    """校园招聘 entry."""
    title: str
    city: str
    publish_time: str


@dataclass
class CampusInternEntry:
    """实习 entry."""
    title: str
    city: str
    publish_time: str


@dataclass
class JobfairEntry:
    """招聘会 entry."""
    name: str
    city: str
    address: str
    fair_type: str
    time: str


class CareerClient:
    """Client for career.csu.edu.cn career center information."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "http://career.csu.edu.cn/",
        })

    def _fetch(self, path: str, params: Optional[dict] = None) -> BeautifulSoup:
        """Fetch and parse HTML from career.csu.edu.cn."""
        url = f"{BASE_URL}{path}"
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def get_teachin(self, zone: str = "") -> list[TeachinEntry]:
        """
        Fetch 宣讲会 list.

        Args:
            zone: Filter by campus zone (e.g., "岳麓山校区", "天心校区", "杏林校区", "潇湘校区")

        Returns:
            List of TeachinEntry
        """
        logger.info(f"Fetching teachin, zone={zone}")
        params = {}
        if zone:
            params["zone"] = zone

        soup = self._fetch("/teachin", params=params)
        entries = []

        for ul in soup.select("ul.infoList.teachinList"):
            company_li = ul.select_one("li.span1")
            location_li = ul.select_one("li.span4")
            time_li = ul.select_one("li.span5")

            if company_li and location_li and time_li:
                a_tag = company_li.select_one("a")
                company = a_tag.get("title", a_tag.get_text(strip=True)) if a_tag else company_li.get_text(strip=True)
                entries.append(TeachinEntry(
                    company=company,
                    location=location_li.get_text(strip=True),
                    time=time_li.get_text(strip=True),
                ))

        logger.info(f"Fetched {len(entries)} teachin entries")
        return entries

    def get_campus_recruit(self, keyword: str = "") -> list[CampusRecruitEntry]:
        """
        Fetch 校园招聘 list.

        Args:
            keyword: Filter by keyword in title

        Returns:
            List of CampusRecruitEntry
        """
        logger.info(f"Fetching campus recruit, keyword={keyword}")
        params = {}
        if keyword:
            params["keyword"] = keyword

        soup = self._fetch("/campus/index/category/1", params=params)
        entries = []

        for ul in soup.select("div.infoBox > ul.infoList"):
            title_li = ul.select_one("li.span7")
            city_li = ul.select_one("li.span1")
            time_li = ul.select_one("li.span4")

            if title_li and city_li and time_li:
                entries.append(CampusRecruitEntry(
                    title=title_li.get_text(strip=True),
                    city=city_li.get_text(strip=True),
                    publish_time=time_li.get_text(strip=True),
                ))

        logger.info(f"Fetched {len(entries)} campus recruit entries")
        return entries

    def get_campus_intern(self, keyword: str = "") -> list[CampusInternEntry]:
        """
        Fetch 实习 list.

        Args:
            keyword: Filter by keyword in title

        Returns:
            List of CampusInternEntry
        """
        logger.info(f"Fetching campus intern, keyword={keyword}")
        params = {}
        if keyword:
            params["keyword"] = keyword

        soup = self._fetch("/campus/index/category/2", params=params)
        entries = []

        for ul in soup.select("div.infoBox > ul.infoList"):
            title_li = ul.select_one("li.span7")
            city_li = ul.select_one("li.span1")
            time_li = ul.select_one("li.span4")

            if title_li and city_li and time_li:
                entries.append(CampusInternEntry(
                    title=title_li.get_text(strip=True),
                    city=city_li.get_text(strip=True),
                    publish_time=time_li.get_text(strip=True),
                ))

        logger.info(f"Fetched {len(entries)} campus intern entries")
        return entries

    def get_jobfair(self) -> list[JobfairEntry]:
        """
        Fetch 招聘会 list.

        Returns:
            List of JobfairEntry
        """
        logger.info("Fetching jobfair")
        soup = self._fetch("/jobfair")
        entries = []

        for ul in soup.select("ul.infoList.jobfairList"):
            name_li = ul.select_one("li.span1")
            city_li = ul.select_one("li.span2")
            address_li = ul.select_one("li.span3")
            type_li = ul.select_one("li.span4")
            time_li = ul.select_one("li.span5")

            if name_li and city_li and address_li and type_li and time_li:
                entries.append(JobfairEntry(
                    name=name_li.get_text(strip=True),
                    city=city_li.get_text(strip=True),
                    address=address_li.get_text(strip=True),
                    fair_type=type_li.get_text(strip=True),
                    time=time_li.get_text(strip=True),
                ))

        logger.info(f"Fetched {len(entries)} jobfair entries")
        return entries
