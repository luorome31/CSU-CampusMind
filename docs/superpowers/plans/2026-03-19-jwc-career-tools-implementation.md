# 就业指导中心 Tool Calling 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `backend/app/core/tools/jwc_career/` 模块中实现4个无需认证的就业信息查询工具，供 LangGraph Agent 调用。

**Architecture:** 遵循 `client.py → service.py → tools.py` 模式，每个工具独立无依赖。HTTP 请求使用 requests，HTML 解析使用 BeautifulSoup4，返回 markdown 表格格式。

**Tech Stack:** Python 3.14+, requests, beautifulsoup4, langchain-core (StructuredTool), pydantic

---

## Chunk 1: 项目骨架与数据模型

**Files:**
- Create: `backend/app/core/tools/jwc_career/__init__.py`
- Create: `backend/app/core/tools/jwc_career/client.py`
- Create: `backend/app/core/tools/jwc_career/service.py`
- Create: `backend/app/core/tools/jwc_career/tools.py`
- Create: `backend/tests/core/tools/jwc_career/__init__.py`
- Modify: `backend/app/core/tools/__init__.py` (添加 jwc_career 导出)

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p backend/app/core/tools/jwc_career
mkdir -p backend/tests/core/tools/jwc_career
touch backend/app/core/tools/jwc_career/__init__.py
touch backend/tests/core/tools/jwc_career/__init__.py
```

- [ ] **Step 2: 创建 `client.py` - HTTP请求与HTML解析**

```python
"""
就业指导中心 HTTP 客户端 - 爬取 career.csu.edu.cn
"""
import logging
from dataclasses import dataclass
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ============ 常量定义 ============
BASE_URL = "http://career.csu.edu.cn"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "http://career.csu.edu.cn/",
}

TIMEOUT = 10


# ============ 数据模型 ============
@dataclass
class TeachinEntry:
    """宣讲会条目"""
    company: str
    location: str
    time: str


@dataclass
class CampusRecruitEntry:
    """校园招聘条目"""
    title: str
    city: str
    publish_time: str


@dataclass
class CampusInternEntry:
    """实习信息条目"""
    title: str
    city: str
    publish_time: str


@dataclass
class JobfairEntry:
    """招聘会条目"""
    name: str
    city: str
    address: str
    fair_type: str
    time: str


# ============ CareerClient ============
class CareerClient:
    """就业指导中心客户端"""

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(HEADERS)

    def get_teachin(self, zone: str = "") -> List[TeachinEntry]:
        """获取宣讲会信息

        Args:
            zone: 校区名称，可选值：岳麓山校区、杏林校区、天心校区、潇湘校区

        Returns:
            宣讲会列表
        """
        url = f"{BASE_URL}/teachin"
        params = {"zone": zone} if zone else {}

        resp = self._session.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        entries = []

        # 宣讲会列表在 ul.infoList.teachinList 中
        for ul in soup.select("ul.infoList.teachinList"):
            lis = ul.find_all("li")
            if len(lis) < 3:
                continue

            # li.span1: 公司名称 (第一个a标签的title)
            company_link = lis[0].find("a")
            company = company_link.get("title", "").strip() if company_link else ""

            # li.span4: 举办地点
            location = lis[1].get_text(strip=True)

            # li.span5: 举办时间
            time = lis[2].get_text(strip=True)

            entries.append(TeachinEntry(company=company, location=location, time=time))

        logger.info(f"获取到 {len(entries)} 条宣讲会信息")
        return entries

    def get_campus_recruit(self, keyword: str = "") -> List[CampusRecruitEntry]:
        """获取校园招聘信息

        Args:
            keyword: 搜索关键字

        Returns:
            校园招聘列表
        """
        url = f"{BASE_URL}/campus/index/category/1"
        params = {"keyword": keyword} if keyword else {}

        resp = self._session.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        entries = []

        # 招聘信息在 ul.infoList 中（不含 teachinList/jobfairList）
        for ul in soup.select("div.infoBox > ul.infoList"):
            # 跳过包含 teachinList 或 jobfairList 的 ul
            if "teachinList" in ul.get("class", []) or "jobfairList" in ul.get("class", []):
                continue

            lis = ul.find_all("li")
            if len(lis) < 3:
                continue

            # span7: 标题
            title_link = lis[0].find("a")
            title = title_link.get_text(strip=True) if title_link else ""

            # span1: 城市
            city = lis[1].get_text(strip=True)

            # span4: 发布时间
            publish_time = lis[2].get_text(strip=True)

            entries.append(CampusRecruitEntry(title=title, city=city, publish_time=publish_time))

        logger.info(f"获取到 {len(entries)} 条校园招聘信息")
        return entries

    def get_campus_intern(self, keyword: str = "") -> List[CampusInternEntry]:
        """获取实习岗位信息

        Args:
            keyword: 搜索关键字

        Returns:
            实习信息列表
        """
        url = f"{BASE_URL}/campus/index/category/2"
        params = {"keyword": keyword} if keyword else {}

        resp = self._session.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        entries = []

        # 实习信息在 ul.infoList 中（与招聘信息结构相同）
        for ul in soup.select("div.infoBox > ul.infoList"):
            if "teachinList" in ul.get("class", []) or "jobfairList" in ul.get("class", []):
                continue

            lis = ul.find_all("li")
            if len(lis) < 3:
                continue

            title_link = lis[0].find("a")
            title = title_link.get_text(strip=True) if title_link else ""
            city = lis[1].get_text(strip=True)
            publish_time = lis[2].get_text(strip=True)

            entries.append(CampusInternEntry(title=title, city=city, publish_time=publish_time))

        logger.info(f"获取到 {len(entries)} 条实习信息")
        return entries

    def get_jobfair(self) -> List[JobfairEntry]:
        """获取大型招聘会信息

        Returns:
            招聘会列表
        """
        url = f"{BASE_URL}/jobfair"

        resp = self._session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        entries = []

        # 招聘会在 ul.infoList.jobfairList 中
        for ul in soup.select("ul.infoList.jobfairList"):
            lis = ul.find_all("li")
            if len(lis) < 5:
                continue

            # span1: 名称
            name_link = lis[0].find("a")
            name = name_link.get("title", "").strip() if name_link else ""

            # span2: 城市
            city = lis[1].get_text(strip=True)

            # span3: 地址
            address = lis[2].get_text(strip=True)

            # span4: 类型
            fair_type = lis[3].get_text(strip=True)

            # span5: 时间
            time = lis[4].get_text(strip=True)

            entries.append(JobfairEntry(
                name=name, city=city, address=address, fair_type=fair_type, time=time
            ))

        logger.info(f"获取到 {len(entries)} 条招聘会信息")
        return entries
```

- [ ] **Step 3: 创建 `service.py` - 业务逻辑封装**

```python
"""
就业指导中心服务 - 整合 CareerClient，提供格式化输出
"""
import logging
from typing import List

from .client import (
    CareerClient,
    TeachinEntry,
    CampusRecruitEntry,
    CampusInternEntry,
    JobfairEntry,
)

logger = logging.getLogger(__name__)


class CareerService:
    """就业指导中心服务入口"""

    def __init__(self):
        self._client = CareerClient()

    def get_teachin(self, zone: str = "") -> str:
        """查询宣讲会并格式化为 markdown"""
        try:
            entries = self._client.get_teachin(zone)
            return self._format_teachin(entries)
        except Exception as e:
            logger.error(f"宣讲会查询失败: {e}")
            return "宣讲会查询失败，请稍后重试"

    def get_campus_recruit(self, keyword: str = "") -> str:
        """查询校园招聘并格式化为 markdown"""
        try:
            entries = self._client.get_campus_recruit(keyword)
            return self._format_campus_recruit(entries)
        except Exception as e:
            logger.error(f"校园招聘查询失败: {e}")
            return "校园招聘查询失败，请稍后重试"

    def get_campus_intern(self, keyword: str = "") -> str:
        """查询实习信息并格式化为 markdown"""
        try:
            entries = self._client.get_campus_intern(keyword)
            return self._format_campus_intern(entries)
        except Exception as e:
            logger.error(f"实习信息查询失败: {e}")
            return "实习信息查询失败，请稍后重试"

    def get_jobfair(self) -> str:
        """查询招聘会并格式化为 markdown"""
        try:
            entries = self._client.get_jobfair()
            return self._format_jobfair(entries)
        except Exception as e:
            logger.error(f"招聘会查询失败: {e}")
            return "招聘会查询失败，请稍后重试"

    def _format_teachin(self, entries: List[TeachinEntry]) -> str:
        if not entries:
            return "宣讲会查询结果为空"
        lines = ["## 宣讲会查询结果\n"]
        lines.append("| 名称 | 举办地点 | 举办时间 |")
        lines.append("|------|----------|----------|")
        for e in entries:
            lines.append(f"| {e.company} | {e.location} | {e.time} |")
        return "\n".join(lines)

    def _format_campus_recruit(self, entries: List[CampusRecruitEntry]) -> str:
        if not entries:
            return "校园招聘查询结果为空"
        lines = ["## 校园招聘信息\n"]
        lines.append("| 招聘公告 | 工作城市 | 发布时间 |")
        lines.append("|----------|----------|----------|")
        for e in entries:
            lines.append(f"| {e.title} | {e.city} | {e.publish_time} |")
        return "\n".join(lines)

    def _format_campus_intern(self, entries: List[CampusInternEntry]) -> str:
        if not entries:
            return "实习信息查询结果为空"
        lines = ["## 实习岗位信息\n"]
        lines.append("| 实习公告 | 工作城市 | 发布时间 |")
        lines.append("|----------|----------|----------|")
        for e in entries:
            lines.append(f"| {e.title} | {e.city} | {e.publish_time} |")
        return "\n".join(lines)

    def _format_jobfair(self, entries: List[JobfairEntry]) -> str:
        if not entries:
            return "招聘会查询结果为空"
        lines = ["## 大型招聘会信息\n"]
        lines.append("| 招聘会名称 | 举办城市 | 举办地址 | 类型 | 举办时间 |")
        lines.append("|------------|----------|----------|------|----------|")
        for e in entries:
            lines.append(f"| {e.name} | {e.city} | {e.address} | {e.fair_type} | {e.time} |")
        return "\n".join(lines)
```

- [ ] **Step 4: 创建 `tools.py` - LangChain StructuredTool 定义**

```python
"""
就业指导中心 LangChain Tools
"""
import logging
from typing import List

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from .service import CareerService

logger = logging.getLogger(__name__)


# ============ Tool Input Models ============
class TeachinInput(BaseModel):
    zone: str = Field(
        default="",
        description="校区名称，可选值：岳麓山校区、杏林校区、天心校区、潇湘校区，空值查询全部"
    )


class CampusRecruitInput(BaseModel):
    keyword: str = Field(default="", description="搜索关键字")


class CampusInternInput(BaseModel):
    keyword: str = Field(default="", description="搜索关键字")


class JobfairInput(BaseModel):
    pass  # 无参数


# ============ Tool Functions ============
def _get_service() -> CareerService:
    return CareerService()


def _get_teachin(zone: str = "") -> str:
    """查询宣讲会信息"""
    service = _get_service()
    return service.get_teachin(zone)


def _get_campus_recruit(keyword: str = "") -> str:
    """查询校园招聘信息"""
    service = _get_service()
    return service.get_campus_recruit(keyword)


def _get_campus_intern(keyword: str = "") -> str:
    """查询实习岗位信息"""
    service = _get_service()
    return service.get_campus_intern(keyword)


def _get_jobfair() -> str:
    """查询大型招聘会信息"""
    service = _get_service()
    return service.get_jobfair()


# ============ LangChain Tools ============
JwcTeachinTool = StructuredTool.from_function(
    func=_get_teachin,
    name="jwc_teachin",
    description="查询中南大学就业信息网站的宣讲会信息。可按校区筛选（岳麓山校区、杏林校区、天心校区、潇湘校区）。"
    "适用于：查询企业宣讲会时间地点、筛选特定校区宣讲会。",
    args_schema=TeachinInput,
)

JwcCampusRecruitTool = StructuredTool.from_function(
    func=_get_campus_recruit,
    name="jwc_campus_recruit",
    description="查询中南大学就业信息网站的校园招聘信息。支持关键字搜索。"
    "适用于：查询校园招聘公告、搜索特定企业或岗位的招聘信息。",
    args_schema=CampusRecruitInput,
)

JwcCampusInternTool = StructuredTool.from_function(
    func=_get_campus_intern,
    name="jwc_campus_intern",
    description="查询中南大学就业信息网站的实习岗位信息。支持关键字搜索。"
    "适用于：查询实习招聘信息、搜索特定企业或岗位的实习信息。",
    args_schema=CampusInternInput,
)

JwcJobfairTool = StructuredTool.from_function(
    func=_get_jobfair,
    name="jwc_jobfair",
    description="查询中南大学就业信息网站的大型招聘会/双选会信息。"
    "适用于：查询大型招聘会时间地点、了解校级或院系举办的招聘会信息。",
    args_schema=JobfairInput,
)


# 工具列表
JWC_CAREER_TOOLS = [
    JwcTeachinTool,
    JwcCampusRecruitTool,
    JwcCampusInternTool,
    JwcJobfairTool,
]
```

- [ ] **Step 5: 创建 `__init__.py` - 模块导出**

```python
"""
就业指导中心 Tool Calling 模块

无需认证的就业信息查询工具，供 LangGraph Agent 调用。
"""
from .client import (
    CareerClient,
    TeachinEntry,
    CampusRecruitEntry,
    CampusInternEntry,
    JobfairEntry,
)
from .service import CareerService
from .tools import (
    JwcTeachinTool,
    JwcCampusRecruitTool,
    JwcCampusInternTool,
    JwcJobfairTool,
    JWC_CAREER_TOOLS,
)

__all__ = [
    "CareerClient",
    "TeachinEntry",
    "CampusRecruitEntry",
    "CampusInternEntry",
    "JobfairEntry",
    "CareerService",
    "JwcTeachinTool",
    "JwcCampusRecruitTool",
    "JwcCampusInternTool",
    "JwcJobfairTool",
    "JWC_CAREER_TOOLS",
]
```

- [ ] **Step 6: 更新 `app/core/tools/__init__.py`**

在 `__all__` 列表中添加导出：

```python
"""
Core tools module
"""
from app.core.tools.rag_tool import create_rag_tool
from app.core.tools.library.tools import library_search, library_get_book_location, LIBRARY_TOOLS
from app.core.tools.jwc_career import JWC_CAREER_TOOLS

__all__ = [
    "create_rag_tool",
    "library_search",
    "library_get_book_location",
    "LIBRARY_TOOLS",
    "JWC_CAREER_TOOLS",
]
```

- [ ] **Step 7: 提交 Chunk 1**

```bash
git add backend/app/core/tools/jwc_career/
git add backend/app/core/tools/__init__.py
git commit -m "feat(tools): add jwc_career module for career center tools

- 4 tools: jwc_teachin, jwc_campus_recruit, jwc_campus_intern, jwc_jobfair
- No authentication required
- Returns markdown table format"
```

---

## Chunk 2: 单元测试

**Files:**
- Create: `backend/tests/core/tools/jwc_career/test_client.py`
- Create: `backend/tests/core/tools/jwc_career/test_service.py`
- Create: `backend/tests/core/tools/jwc_career/test_tools.py`

- [ ] **Step 1: 创建测试文件 - `test_client.py`**

使用 HTML 示例文件进行测试：

```python
"""
CareerClient 单元测试
"""
import pytest
from pathlib import Path
from app.core.tools.jwc_career.client import (
    CareerClient,
    TeachinEntry,
    CampusRecruitEntry,
    CampusInternEntry,
    JobfairEntry,
)


@pytest.fixture
def client():
    return CareerClient()


class TestParseTeachin:
    """测试宣讲会解析"""

    def test_parse_teachin_html(self, client):
        """测试解析宣讲会HTML"""
        html_path = Path(__file__).parent.parent.parent.parent.parent.parent / \
            "docs/development_doc/宣讲会信息.txt"
        with open(html_path, "r", encoding="utf-8") as f:
            # 跳过HTTP响应头
            content = f.read()
            # 找到HTML开始位置
            start = content.find("<!DOCTYPE")
            if start != -1:
                content = content[start:]

        # 使用 BeautifulSoup 直接解析
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")

        entries = []
        for ul in soup.select("ul.infoList.teachinList"):
            lis = ul.find_all("li")
            if len(lis) < 3:
                continue
            company_link = lis[0].find("a")
            company = company_link.get("title", "").strip() if company_link else ""
            location = lis[1].get_text(strip=True)
            time = lis[2].get_text(strip=True)
            entries.append(TeachinEntry(company=company, location=location, time=time))

        assert len(entries) > 0
        assert "贝斯（无锡）信息系统有限公司" in entries[0].company
        assert "2026-03-19" in entries[0].time

    def test_teachin_entry_structure(self):
        """测试 TeachinEntry 数据结构"""
        entry = TeachinEntry(
            company="测试公司",
            location="岳麓山校区",
            time="2026-03-19 14:00"
        )
        assert entry.company == "测试公司"
        assert entry.location == "岳麓山校区"
        assert entry.time == "2026-03-19 14:00"
```

- [ ] **Step 2: 创建测试文件 - `test_service.py`**

```python
"""
CareerService 单元测试
"""
import pytest
from unittest.mock import patch, MagicMock
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
    """测试宣讲会格式化"""

    def test_format_teachin_with_data(self, service):
        """测试有数据时的格式化"""
        entries = [
            TeachinEntry(company="公司A", location="岳麓山校区", time="2026-03-19 14:00"),
            TeachinEntry(company="公司B", location="天心校区", time="2026-03-20 10:00"),
        ]
        result = service._format_teachin(entries)

        assert "## 宣讲会查询结果" in result
        assert "| 名称 | 举办地点 | 举办时间 |" in result
        assert "| 公司A | 岳麓山校区 | 2026-03-19 14:00 |" in result
        assert "| 公司B | 天心校区 | 2026-03-20 10:00 |" in result

    def test_format_teachin_empty(self, service):
        """测试无数据时的格式化"""
        result = service._format_teachin([])
        assert result == "宣讲会查询结果为空"


class TestFormatCampusRecruit:
    """测试校园招聘格式化"""

    def test_format_campus_recruit_with_data(self, service):
        entries = [
            CampusRecruitEntry(title="招聘公告A", city="长沙市", publish_time="2026-03-19"),
        ]
        result = service._format_campus_recruit(entries)

        assert "## 校园招聘信息" in result
        assert "| 招聘公告 | 工作城市 | 发布时间 |" in result

    def test_format_campus_recruit_empty(self, service):
        result = service._format_campus_recruit([])
        assert result == "校园招聘查询结果为空"


class TestFormatCampusIntern:
    """测试实习信息格式化"""

    def test_format_campus_intern_with_data(self, service):
        entries = [
            CampusInternEntry(title="实习公告A", city="北京市", publish_time="2026-03-18"),
        ]
        result = service._format_campus_intern(entries)

        assert "## 实习岗位信息" in result
        assert "| 实习公告 | 工作城市 | 发布时间 |" in result

    def test_format_campus_intern_empty(self, service):
        result = service._format_campus_intern([])
        assert result == "实习信息查询结果为空"


class TestFormatJobfair:
    """测试招聘会格式化"""

    def test_format_jobfair_with_data(self, service):
        entries = [
            JobfairEntry(
                name="大型招聘会",
                city="长沙市",
                address="中南大学",
                fair_type="校园招聘会",
                time="2026-04-19"
            )
        ]
        result = service._format_jobfair(entries)

        assert "## 大型招聘会信息" in result
        assert "| 招聘会名称 | 举办城市 | 举办地址 | 类型 | 举办时间 |" in result

    def test_format_jobfair_empty(self, service):
        result = service._format_jobfair([])
        assert result == "招聘会查询结果为空"
```

- [ ] **Step 3: 创建测试文件 - `test_tools.py`**

```python
"""
JWC Career Tools 单元测试
"""
import pytest
from unittest.mock import patch, MagicMock
from app.core.tools.jwc_career.tools import (
    JWC_CAREER_TOOLS,
    JwcTeachinTool,
    JwcCampusRecruitTool,
    JwcCampusInternTool,
    JwcJobfairTool,
)


class TestToolDefinitions:
    """测试工具定义"""

    def test_tools_count(self):
        """测试工具数量"""
        assert len(JWC_CAREER_TOOLS) == 4

    def test_teachin_tool(self):
        """测试宣讲会工具"""
        assert JwcTeachinTool.name == "jwc_teachin"
        assert "宣讲会" in JwcTeachinTool.description

    def test_campus_recruit_tool(self):
        """测试校园招聘工具"""
        assert JwcCampusRecruitTool.name == "jwc_campus_recruit"
        assert "校园招聘" in JwcCampusRecruitTool.description

    def test_campus_intern_tool(self):
        """测试实习工具"""
        assert JwcCampusInternTool.name == "jwc_campus_intern"
        assert "实习" in JwcCampusInternTool.description

    def test_jobfair_tool(self):
        """测试招聘会工具"""
        assert JwcJobfairTool.name == "jwc_jobfair"
        assert "招聘会" in JwcJobfairTool.description


class TestToolExecution:
    """测试工具执行（mock）"""

    @patch("app.core.tools.jwc_career.tools._get_service")
    def test_teachin_tool_call(self, mock_get_service):
        """测试宣讲会工具调用"""
        mock_service = MagicMock()
        mock_service.get_teachin.return_value = "## 宣讲会查询结果\n| 名称 | 地点 | 时间 |"
        mock_get_service.return_value = mock_service

        result = JwcTeachinTool.invoke({"zone": ""})
        assert "宣讲会" in result

    @patch("app.core.tools.jwc_career.tools._get_service")
    def test_jobfair_tool_call(self, mock_get_service):
        """测试招聘会工具调用"""
        mock_service = MagicMock()
        mock_service.get_jobfair.return_value = "## 大型招聘会信息\n| 名称 | 城市 |"
        mock_get_service.return_value = mock_service

        result = JwcJobfairTool.invoke({})
        assert "招聘会" in result
```

- [ ] **Step 4: 运行测试验证**

```bash
cd backend
uv run pytest tests/core/tools/jwc_career/ -v
```

- [ ] **Step 5: 提交 Chunk 2**

```bash
git add backend/tests/core/tools/jwc_career/
git commit -m "test(jwc_career): add unit tests for career center tools"
```

---

## Chunk 3: 集成测试（可选，如需要）

**Files:**
- Create: `backend/tests/core/tools/jwc_career/test_integration.py`

- [ ] **Step 1: 创建集成测试（需要网络）**

```python
"""
就业指导中心集成测试

运行方式:
    uv run pytest tests/core/tools/jwc_career/test_integration.py -v -m integration

注意: 需要网络连接，会发起真实HTTP请求
"""
import pytest

pytestmark = pytest.mark.integration


class TestRealAPI:
    """真实API测试（可选）"""

    def test_teachin_real(self):
        """测试真实宣讲会接口"""
        from app.core.tools.jwc_career import CareerService
        service = CareerService()
        result = service.get_teachin()

        assert "## 宣讲会查询结果" in result or "宣讲会查询" in result

    def test_jobfair_real(self):
        """测试真实招聘会接口"""
        from app.core.tools.jwc_career import CareerService
        service = CareerService()
        result = service.get_jobfair()

        assert "## 大型招聘会信息" in result or "招聘会查询" in result
```

- [ ] **Step 2: 提交 Chunk 3**

```bash
git add backend/tests/core/tools/jwc_career/test_integration.py
git commit -m "test(jwc_career): add integration tests"
```

---

## 依赖检查

在开始实现前，确认以下依赖已安装：

```bash
cd backend
uv add requests beautifulsoup4
```

---

## 实现顺序

1. **Chunk 1**: 创建项目骨架（client.py, service.py, tools.py, __init__.py）
2. **Chunk 2**: 编写单元测试（使用本地 HTML 示例文件）
3. **Chunk 3**: 集成测试（如需要）

---

## 验证清单

- [ ] `uv run pytest tests/core/tools/jwc_career/ -v` 所有测试通过
- [ ] 4个工具可正常导入
- [ ] HTML 解析逻辑正确
- [ ] markdown 表格格式正确
- [ ] 错误处理正常（无认证相关问题）
