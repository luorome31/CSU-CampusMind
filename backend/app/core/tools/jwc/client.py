"""
教务系统业务客户端 - 从参考代码 jwc_client.py 移植
"""
import logging
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ============ 常量定义 ============
JWC_BASE_URL = "http://csujwc.its.csu.edu.cn/jsxsd"

URLS = {
    "grade": f"{JWC_BASE_URL}/kscj/yscjcx_list",
    "rank": f"{JWC_BASE_URL}/kscj/zybm_cx",
    "class": f"{JWC_BASE_URL}/xskb/xskb_list.do",
    "level_exam": f"{JWC_BASE_URL}/kscj/djkscj_list",
    "student_info": f"{JWC_BASE_URL}/grxx/xsxx",
    "student_plan": f"{JWC_BASE_URL}/pyfa/pyfa_query",
}


# ============ 数据模型 ============
@dataclass
class Grade:
    """成绩"""
    term: str
    course_name: str
    score: str
    credit: str
    attribute: str
    nature: str


@dataclass
class RankEntry:
    """排名"""
    term: str
    total_score: str
    class_rank: str
    average_score: str


@dataclass
class ClassEntry:
    """课表条目"""
    course_name: str
    teacher: str
    weeks: str
    place: str
    day_of_week: str
    time_of_day: str


@dataclass
class LevelExamEntry:
    """等级考试"""
    course: str
    written_score: str
    computer_score: str
    total_score: str
    written_level: str
    computer_level: str
    total_level: str
    exam_date: str


# ============ JwcClient ============
class JwcClient:
    """教务系统客户端"""

    def __init__(self, session: requests.Session):
        self._session = session

    def get_grades(self, term: str = "") -> List[Grade]:
        """查询成绩"""
        url = URLS["grade"]
        data = {"xnxq01id": term} if term else {}

        resp = self._session.post(url, data=data)
        html = resp.text

        if "学生个人考试成绩" not in html:
            raise Exception("成绩查询失败，可能 Cookie 已失效")

        soup = BeautifulSoup(html, "html.parser")
        grades = []

        for row in soup.select("table#dataList tr"):
            cells = row.find_all("td")
            if len(cells) < 9:
                continue

            grades.append(Grade(
                term=cells[3].get_text(strip=True),
                course_name=cells[4].get_text(strip=True),
                score=cells[5].get_text(strip=True),
                credit=cells[6].get_text(strip=True),
                attribute=cells[7].get_text(strip=True),
                nature=cells[8].get_text(strip=True),
            ))

        logger.info(f"查询到 {len(grades)} 条成绩记录")
        return grades

    def get_rank(self) -> List[RankEntry]:
        """查询专业排名"""
        url = URLS["rank"]
        resp = self._session.get(url)
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        ranks = []

        for option in soup.select("select[name='xqfw'] option"):
            term = option.get_text(strip=True)
            if not term:
                continue

            form = {"xqfw": term}
            rank_resp = self._session.post(url, data=form)
            rank_html = rank_resp.text

            rank_soup = BeautifulSoup(rank_html, "html.parser")
            rows = rank_soup.select("table#table1 tr")

            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 4:
                    ranks.append(RankEntry(
                        term=term,
                        total_score=cells[1].get_text(strip=True),
                        class_rank=cells[2].get_text(strip=True),
                        average_score=cells[3].get_text(strip=True),
                    ))

        logger.info(f"查询到 {len(ranks)} 条排名记录")
        return ranks

    def get_class_schedule(self, term: str, week: str = "0") -> List[ClassEntry]:
        """查询课表"""
        url = URLS["class"]
        data = {"xnxq01id": term, "zc": week}

        resp = self._session.post(url, data=data)
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        classes = []

        for row in soup.select("table#table1 tr"):
            cells = row.find_all("td")
            if len(cells) < 6:
                continue

            classes.append(ClassEntry(
                course_name=cells[1].get_text(strip=True),
                teacher=cells[2].get_text(strip=True),
                weeks=cells[3].get_text(strip=True),
                place=cells[4].get_text(strip=True),
                day_of_week=cells[5].get_text(strip=True),
                time_of_day=cells[6].get_text(strip=True),
            ))

        logger.info(f"查询到 {len(classes)} 条课表记录")
        return classes

    def get_level_exams(self) -> List[LevelExamEntry]:
        """查询等级考试成绩"""
        url = URLS["level_exam"]
        resp = self._session.get(url)
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        exams = []

        for row in soup.select("table#dataList tr"):
            cells = row.find_all("td")
            if len(cells) < 8:
                continue

            exams.append(LevelExamEntry(
                course=cells[0].get_text(strip=True),
                written_score=cells[1].get_text(strip=True),
                computer_score=cells[2].get_text(strip=True),
                total_score=cells[3].get_text(strip=True),
                written_level=cells[4].get_text(strip=True),
                computer_level=cells[5].get_text(strip=True),
                total_level=cells[6].get_text(strip=True),
                exam_date=cells[7].get_text(strip=True),
            ))

        logger.info(f"查询到 {len(exams)} 条等级考试记录")
        return exams
