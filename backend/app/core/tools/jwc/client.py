"""
教务系统业务客户端 - 从参考代码 jwc_client.py 移植
"""
import logging
from dataclasses import dataclass
from typing import List

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
                term=cells[1].get_text(strip=True),       # 初修学期
                course_name=cells[3].get_text(strip=True),  # 课程
                score=cells[6].get_text(strip=True),        # 成绩
                credit=cells[7].get_text(strip=True),       # 学分
                attribute=cells[8].get_text(strip=True),    # 课程属性
                nature=cells[9].get_text(strip=True),       # 课程性质
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

        # 直接解析 table#dataList，不需要选择学期
        rows = soup.select("table#dataList tr")

        for row in rows[1:]:  # 跳过表头
            cells = row.find_all("td")
            if len(cells) >= 4:
                # 表格结构: 学期/类型, 计算学分, 专业排名, 平均分
                ranks.append(RankEntry(
                    term=cells[0].get_text(strip=True),        # 学期/类型
                    total_score=cells[1].get_text(strip=True),  # 计算学分
                    class_rank=cells[2].get_text(strip=True),  # 专业排名
                    average_score=cells[3].get_text(strip=True), # 平均分
                ))

        logger.info(f"查询到 {len(ranks)} 条排名记录")
        return ranks

    def get_class_schedule(self, term: str, week: str = "0") -> tuple[List[ClassEntry], str]:
        """查询课表

        Returns:
            (课表列表, 学期开始日期)
        """
        url = URLS["class"]
        data = {"xnxq01id": term, "zc": week if week != "0" else ""}

        resp = self._session.post(url, data=data)
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        classes = []

        # 使用 table#kbtable 第一个表格
        kbtable = soup.select("table#kbtable")
        if not kbtable:
            logger.warning("未找到课表表格 kbtable")
            return classes, ""

        main_table = kbtable[0]
        rows = main_table.find_all("tr")

        for row in rows:
            # 获取节次信息（每行第一个 th）
            th_cells = row.find_all("th")
            time_in_day = th_cells[0].get_text(strip=True).replace("\xa0", "") if th_cells else ""

            # 遍历每行的 td（每列代表一个星期）
            td_cells = row.find_all("td")
            for col_idx, cell in enumerate(td_cells):
                time_in_week = str(col_idx + 1)  # 星期 1-7

                # 查找课程块：优先 kbcontent，否则 kbcontent1
                visible_blocks = cell.find_all("div", class_="kbcontent")
                blocks = visible_blocks if visible_blocks else cell.find_all("div", class_="kbcontent1")

                for block in blocks:
                    # 获取课程名：去掉 font 和 br 标签后的文本
                    block_copy = BeautifulSoup(str(block), "html.parser")
                    for tag in block_copy.find_all(["font", "br"]):
                        tag.decompose()
                    course_name = block_copy.get_text(strip=True)

                    # 通过 title 属性获取教师、周次、教室
                    fonts = block.find_all("font")
                    teacher = ""
                    weeks = ""
                    place = ""

                    for font in fonts:
                        title = font.get("title", "")
                        if "老师" in title:
                            teacher = font.get_text(strip=True)
                        elif "周次" in title:
                            weeks = font.get_text(strip=True)
                        elif "教室" in title:
                            place = font.get_text(strip=True)

                    # 如果 title 没有匹配，尝试按顺序获取
                    if not teacher and fonts:
                        teacher = fonts[0].get_text(strip=True)
                    if not weeks and len(fonts) > 1:
                        weeks = fonts[1].get_text(strip=True)
                    if not place and len(fonts) > 2:
                        place = fonts[2].get_text(strip=True)

                    if course_name or teacher or weeks or place:
                        classes.append(ClassEntry(
                            course_name=course_name,
                            teacher=teacher,
                            weeks=weeks,
                            place=place,
                            day_of_week=time_in_week,
                            time_of_day=time_in_day,
                        ))

        # 从第二个表格获取学期开始日期
        start_week_day = ""
        if len(kbtable) > 1:
            info_td = kbtable[1].find("td")
            if info_td:
                info_text = info_td.get_text(strip=True)
                import re
                match = re.search(r"第1周\xa0(.*?)日", info_text)
                if match:
                    start_week_day = match.group(1)

        logger.info(f"查询到 {len(classes)} 条课表记录, start_week_day={start_week_day}")
        return classes, start_week_day

    def get_level_exams(self) -> List[LevelExamEntry]:
        """查询等级考试成绩"""
        url = URLS["level_exam"]
        resp = self._session.get(url)
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        exams = []

        for row in soup.select("table#dataList tr"):
            cells = row.find_all("td")
            if len(cells) < 9:
                continue

            exams.append(LevelExamEntry(
                course=cells[1].get_text(strip=True),
                written_score=cells[2].get_text(strip=True),
                computer_score=cells[3].get_text(strip=True),
                total_score=cells[4].get_text(strip=True),
                written_level=cells[5].get_text(strip=True),
                computer_level=cells[6].get_text(strip=True),
                total_level=cells[7].get_text(strip=True),
                exam_date=cells[8].get_text(strip=True),
            ))

        logger.info(f"查询到 {len(exams)} 条等级考试记录")
        return exams
