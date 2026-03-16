"""教务系统业务访问 - 使用已保存的 Cookie

高内聚低耦合设计：
- 每个业务函数独立，只做一件事
- Cookie 加载与业务逻辑分离
- 统一的错误处理和数据解析
"""
import json
import logging
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============ 常量定义 ============
JWC_BASE_URL = "http://csujwc.its.csu.edu.cn/jsxsd"

# 业务接口 URL
URLS = {
    "grade": f"{JWC_BASE_URL}/kscj/yscjcx_list",           # 成绩查询
    "rank": f"{JWC_BASE_URL}/kscj/zybm_cx",               # 专业排名
    "class": f"{JWC_BASE_URL}/xskb/xskb_list.do",         # 课表
    "level_exam": f"{JWC_BASE_URL}/kscj/djkscj_list",    # 等级考试
    "student_info": f"{JWC_BASE_URL}/grxx/xsxx",          # 学生信息
    "student_plan": f"{JWC_BASE_URL}/pyfa/pyfa_query",    # 培养计划
    "minor_reg": f"{JWC_BASE_URL}/fxgl/fxbmxx",           # 辅修报名
    "minor_pay": f"{JWC_BASE_URL}/fxgl/fxxkjf_query",    # 辅修缴费
}


# ============ 数据模型 ============
@dataclass
class Grade:
    """成绩"""
    term: str           # 学期
    course_name: str    # 课程名称
    score: str         # 成绩
    credit: str        # 学分
    attribute: str     # 课程属性
    nature: str        # 课程性质


@dataclass
class RankEntry:
    """排名"""
    term: str           # 学期
    total_score: str    # 总分
    class_rank: str    # 班级排名
    average_score: str # 平均分


@dataclass
class ClassEntry:
    """课表条目"""
    course_name: str    # 课程名
    teacher: str       # 教师
    weeks: str         # 周次
    place: str         # 地点
    day_of_week: str   # 星期几
    time_of_day: str   # 第几节


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


# ============ Cookie 加载 ============
class CookieLoader:
    """Cookie 加载器 - 从文件加载已保存的 Cookie"""

    def __init__(self, storage_path: str = "./cache_test_sessions.json"):
        self._storage_path = storage_path

    def load(self, user_id: str, subsystem: str = "jwc") -> Optional[requests.Session]:
        """从文件加载 Cookie"""
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if user_id not in data or subsystem not in data[user_id]:
                logger.warning(f"No saved session for {user_id}:{subsystem}")
                return None

            session_data = data[user_id][subsystem]
            cookies_dict = session_data.get("cookies", {})

            # 创建 Session 并恢复 Cookie
            session = requests.Session()
            for name, cookie_info in cookies_dict.items():
                session.cookies.set(
                    name,
                    cookie_info.get("value"),  # value
                    domain=cookie_info.get("domain"),
                    path=cookie_info.get("path", "/"),
                )

            logger.info(f"Cookies loaded for {user_id}:{subsystem}")
            return session

        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return None


# ============ 业务逻辑 - 高内聚 ============
class JwcClient:
    """教务系统客户端 - 高内聚，每个方法只做一件事"""

    def __init__(self, session: requests.Session):
        self._session = session

    def get_grades(self, term: str = "") -> list[Grade]:
        """
        查询成绩

        Args:
            term: 学期，如 "2024-2025-1"，空则查全部

        Returns:
            成绩列表
        """
        url = URLS["grade"]
        data = {"xnxq01id": term} if term else {}
        # for cookie in self._session.cookies:
        #    print(f"名称: {cookie.name}, 值: {cookie.value}, 域: {cookie.domain}, 路径: {cookie.path}, 过期: {cookie.expires}")
        
        # self._session.cookies.set("SF_cookie_350", "25110820", domain='csujwc.its.csu.edu.cn')
        # self._session.cookies.set('JSESSIONID', 'CF6A79CFB09710A0691F47BC59E05FE1', domain='csujwc.its.csu.edu.cn')
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

    def get_rank(self) -> list[RankEntry]:
        """
        查询专业排名

        Returns:
            排名列表
        """
        url = URLS["rank"]
        resp = self._session.get(url)
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        ranks = []

        # 解析学期选项
        for option in soup.select("select[name='xqfw'] option"):
            term = option.get_text(strip=True)
            if not term:
                continue

            # 查询该学期的排名
            form = {"xqfw": term}
            rank_resp = self._session.post(url, data=form)
            rank_html = rank_resp.text

            rank_soup = BeautifulSoup(rank_html, "html.parser")
            rows = rank_soup.select("table#table1 tr")

            for row in rows[1:]:  # 跳过表头
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

    def get_class_schedule(self, term: str, week: str = "0") -> list[ClassEntry]:
        """
        查询课表

        Args:
            term: 学期，如 "2024-2025-1"
            week: 周次，"0" 为全部周

        Returns:
            课表列表
        """
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

    def get_level_exams(self) -> list[LevelExamEntry]:
        """
        查询等级考试成绩

        Returns:
            等级考试列表
        """
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


# ============ 统一入口 ============
class JwcService:
    """
    教务系统服务 - 低耦合

    职责：
    1. 加载 Cookie
    2. 协调各业务模块
    """

    def __init__(self, storage_path: str = "./cache_test_sessions.json"):
        self._storage_path = storage_path
        self._session: Optional[requests.Session] = None
        self._client: Optional[JwcClient] = None

    def connect(self, user_id: str) -> bool:
        """
        连接教务系统（加载已保存的 Cookie）

        Args:
            user_id: 用户 ID

        Returns:
            是否连接成功
        """
        loader = CookieLoader(self._storage_path)
        self._session = loader.load(user_id, "jwc")

        if self._session:
            self._client = JwcClient(self._session)
            return True
        return False

    @property
    def grades(self) -> JwcClient:
        """成绩查询"""
        if not self._client:
            raise Exception("请先调用 connect() 连接教务系统")
        return self._client

    @property
    def rank(self) -> JwcClient:
        """排名查询"""
        if not self._client:
            raise Exception("请先调用 connect() 连接教务系统")
        return self._client

    @property
    def classes(self) -> JwcClient:
        """课表查询"""
        if not self._client:
            raise Exception("请先调用 connect() 连接教务系统")
        return self._client

    @property
    def level_exams(self) -> JwcClient:
        """等级考试查询"""
        if not self._client:
            raise Exception("请先调用 connect() 连接教务系统")
        return self._client


# ============ 使用示例 ============
def main():
    print("\n" + "=" * 60)
    print("教务系统业务访问 - 使用已保存的 Cookie")
    print("=" * 60)

    USER_ID = "8209220131"

    # 1. 连接教务系统（加载 Cookie）
    print("\n[1] 连接教务系统...")
    service = JwcService(storage_path="./cache_test_sessions.json")

    if not service.connect(USER_ID):
        print("✗ 连接失败，请先登录保存 Cookie")
        return

    print("✓ 连接成功")

    # 2. 查询成绩
    print("\n[2] 查询成绩...")
    try:
        grades = service.grades.get_grades("")
        print(f"✓ 查询到 {len(grades)} 条成绩")
        for g in grades[:3]:  # 只显示前3条
            print(f"  {g.term} | {g.course_name} | {g.score}分 | {g.credit}学分")
    except Exception as e:
        print(f"✗ 成绩查询失败: {e}")

    # 3. 查询等级考试
    print("\n[3] 查询等级考试...")
    try:
        exams = service.level_exams.get_level_exams()
        print(f"✓ 查询到 {len(exams)} 条等级考试")
        for e in exams[:3]:
            print(f"  {e.course} | 笔试:{e.written_level} | 机试:{e.computer_level}")
    except Exception as e:
        print(f"✗ 等级考试查询失败: {e}")

    # 4. 查询课表（需要指定学期）
    print("\n[4] 查询课表...")
    try:
        classes = service.classes.get_class_schedule("2024-2025-1", "1")
        print(f"✓ 查询到 {len(classes)} 条课表")
        for c in classes[:3]:
            print(f"  {c.course_name} | {c.teacher} | {c.place}")
    except Exception as e:
        print(f"✗ 课表查询失败: {e}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
