# CSU OANetwork Notification Tool - Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate CSU OANetwork (校内办公网) notification API as a LangGraph tool for authenticated users to search campus notifications.

**Architecture:** Three new components: `OASessionProvider` (session management), `departments.py` + `notification.py` (tool), integrated into `AgentFactory` and `UnifiedSessionManager`.

**Tech Stack:** Python `requests`, Pydantic, LangChain StructuredTool, `uv` for dependency management.

---

## Chunk 1: OASessionProvider

**Files:**
- Create: `backend/app/core/session/providers/oa.py`
- Modify: `backend/app/core/session/providers/__init__.py`
- Modify: `backend/app/core/session/manager.py`
- Test: `backend/tests/app/core/session/providers/test_oa.py`

---

### Step 1: Add OASessionProvider

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/app/core/session/providers/test_oa.py
import pytest
from unittest.mock import MagicMock, patch

class TestOASessionProvider:
    def test_subsystem_name_is_oa(self):
        from app.core.session.providers.oa import OASessionProvider
        assert OASessionProvider.subsystem_name == "oa"

    def test_fetch_session_returns_session_with_sub_session(self):
        """Test 3-step sub-session activation flow"""
        from app.core.session.providers.oa import OASessionProvider

        provider = OASessionProvider()

        mock_session = MagicMock()
        mock_session.cookies.get.return_value = "mock_sub_session_s"

        with patch('app.core.session.providers.oa.cas_login.create_session') as mock_create_session:
            mock_create_session.return_value = mock_session

            # Step 1: oa.csu.edu.cn/con/ returns Set-Cookie with sub-session
            mock_session.get.return_value = MagicMock(
                status_code=200,
                headers={"Set-Cookie": "JSESSIONID=sub_session_s; Path=/"},
                cookies={"JSESSIONID": "sub_session_s"}
            )

            result = provider.fetch_session(castgc="test_castgc")

            assert result == mock_session
            # Verify JSESSIONID was set from step 1
            mock_session.cookies.set.assert_any_call(
                "JSESSIONID", "sub_session_s", domain="oa.csu.edu.cn", path="/"
            )

    def test_fetch_session_uses_provided_castgc(self):
        """CASTGC should be attached when accessing CAS login URL"""
        from app.core.session.providers.oa import OASessionProvider

        provider = OASessionProvider()
        mock_session = MagicMock()

        with patch('app.core.session.providers.oa.cas_login.create_session') as mock_create_session:
            mock_create_session.return_value = mock_session
            mock_session.get.return_value = MagicMock(
                status_code=200, cookies={"JSESSIONID": "s"}
            )

            provider.fetch_session(castgc="my_castgc_value")

            # CASTGC cookie should be set
            mock_session.cookies.set.assert_called()
            calls = mock_session.cookies.set.call_args_list
            castgc_call = [c for c in calls if c.kwargs.get('name') == 'CASTGC']
            assert len(castgc_call) == 1
            assert castgc_call[0].kwargs.get('value') == 'my_castgc_value'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv pytest tests/app/core/session/providers/test_oa.py -v`
Expected: FAIL — OASessionProvider not found

- [ ] **Step 3: Write OASessionProvider**

```python
# backend/app/core/session/providers/oa.py
"""
OASessionProvider - 中南大学校内办公网 Session Provider

认证流程（使用预存在的 CASTGC）:
1. 访问 https://oa.csu.edu.cn/con/ 获取子会话 S（从 Set-Cookie 提取 JSESSIONID）
2. 携带 CASTGC 访问 CAS 认证接口，自动重定向激活子会话 S
3. 子会话 S 激活后，可访问 https://oa.csu.edu.cn/con/xnbg/contentList 等接口
"""
import logging
from urllib.parse import urljoin

import requests

from app.core.session.providers.base import SubsystemSessionProvider
from app.core.session import cas_login

logger = logging.getLogger(__name__)


class OASessionProvider(SubsystemSessionProvider, subsystem_name="oa"):
    """
    校内办公网 Session Provider

    认证流程:
    1. 创建新 session，访问 https://oa.csu.edu.cn/con/ 获取子会话 JSESSIONID
    2. 设置 CASTGC cookie，访问 CAS 登录接口触发重定向
    3. 跟随重定向完成子会话激活
    """

    OA_BASE_URL = "https://oa.csu.edu.cn"
    OA_SESSION_URL = f"{OA_BASE_URL}/con/"  # 注意末尾斜杠不能少
    CAS_LOGIN_URL = "https://ca.csu.edu.cn/authserver/login"
    CAS_SERVICE = "https%3A%2F%2Foa.csu.edu.cn%2Fcon%2F%2Flogincas%3FtargetUrl%3DaHR0cHM6Ly9vYS5jc3UuZWR1LmNuL2Nvbi8v"

    def fetch_session(self, castgc: str) -> requests.Session:
        """
        获取校内办公网会话

        Args:
            castgc: CAS 登录成功后获取的 CASTGC cookie

        Returns:
            带着校内办公网有效子会话的 requests.Session
        """
        session = cas_login.create_session()

        # === Step 1: 访问 OA 首页获取子会话 JSESSIONID ===
        logger.info("OA: Step 1 - Fetching sub-session from oa.csu.edu.cn/con/")
        resp = session.get(self.OA_SESSION_URL, allow_redirects=False)

        # 提取 JSESSIONID（子会话标识）
        jsessionid = session.cookies.get("JSESSIONID", domain="oa.csu.edu.cn")
        if not jsessionid:
            # 尝试从 Set-Cookie header 解析
            set_cookie = resp.headers.get("Set-Cookie", "")
            for cookie_str in set_cookie.split(","):
                if "JSESSIONID" in cookie_str:
                    for part in cookie_str.split(";"):
                        if "JSESSIONID" in part and "=" in part:
                            jsessionid = part.split("=")[1].strip()
                            break
        logger.info(f"OA: Sub-session JSESSIONID obtained: {jsessionid}")

        # === Step 2: 携带 CASTGC 访问 CAS 认证接口 ===
        login_url = f"{self.CAS_LOGIN_URL}?service={self.CAS_SERVICE}"
        session.cookies.set("CASTGC", castgc, domain="ca.csu.edu.cn")
        logger.info(f"OA: Step 2 - Accessing CAS login with CASTGC")

        resp = session.get(login_url, allow_redirects=False)

        # === Step 3: 跟随重定向完成子会话激活 ===
        redirect_url = resp.headers.get("Location", "")
        if redirect_url:
            if not redirect_url.startswith("http"):
                redirect_url = urljoin(login_url, redirect_url)
            logger.info(f"OA: Step 3 - Following redirect to activate sub-session: {redirect_url}")
            resp = session.get(redirect_url, allow_redirects=True)
            logger.info(f"OA: Sub-session activated, final URL: {resp.url}")
        else:
            logger.warning("OA: No redirect received from CAS login")

        return session
```

- [ ] **Step 4: Register OASessionProvider in providers/__init__.py**

Modify `backend/app/core/session/providers/__init__.py`:

```python
# backend/app/core/session/providers/__init__.py
from app.core.session.providers.base import SubsystemSessionProvider
from app.core.session.providers.jwc import JWCSessionProvider
from app.core.session.providers.oa import OASessionProvider

__all__ = ["SubsystemSessionProvider", "JWCSessionProvider", "OASessionProvider"]
```

- [ ] **Step 5: Add OA subsystem to UnifiedSessionManager**

Modify `backend/app/core/session/manager.py`:

```python
# Add to Subsystem enum:
class Subsystem:
    JWC = "jwc"
    LIBRARY = "library"
    ECARD = "ecard"
    OA = "oa"  # NEW

# Add to SUBSYSTEM_SERVICE_URLS:
SUBSYSTEM_SERVICE_URLS = {
    Subsystem.JWC: "http://csujwc.its.csu.edu.cn/sso.jsp",
    Subsystem.LIBRARY: "https://lib.csu.edu.cn/system/resource/code/auth/clogin.jsp",
    Subsystem.ECARD: "https://ecard.csu.edu.cn/berserker-auth/cas/login/wisedu?targetUrl=https://ecard.csu.edu.cn/plat-pc/?name=loginTransit",
    Subsystem.OA: "https://oa.csu.edu.cn/con/",  # NEW
}

# Add helper method to UnifiedSessionManager:
def get_oa_session(self, user_id: str) -> requests.Session:
    """获取校内办公网 Session"""
    return self.get_session(user_id, Subsystem.OA)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && uv pytest tests/app/core/session/providers/test_oa.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/core/session/providers/oa.py backend/app/core/session/providers/__init__.py backend/app/core/session/manager.py backend/tests/app/core/session/providers/test_oa.py
git commit -m "feat(session): add OASessionProvider for CSU OANetwork"
```

---

## Chunk 2: OANotificationList Tool (departments.py + notification.py)

**Files:**
- Create: `backend/app/core/tools/oa/departments.py`
- Create: `backend/app/core/tools/oa/notification.py`
- Create: `backend/app/core/tools/oa/__init__.py`
- Test: `backend/tests/app/core/tools/oa/test_notification.py`

---

### Step 1: Write build_params test

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/app/core/tools/oa/test_notification.py
import pytest
import base64
import json


class TestBuildParams:
    def test_build_params_with_all_fields(self):
        from app.core.tools.oa.departments import build_params
        result = build_params(
            qssj="2024-03-12",
            jssj="2024-12-31",
            qcbmmc="学校办公室",
            wjbt="通知",
            qwss="印发",
            hid_odby="DJSJP DESC"
        )
        # Result is a JSON string containing tableName and base64-encoded tjnr
        parsed = json.loads(result)
        assert parsed["tableName"] == "ZNDX_ZHBG_GGTZ"
        assert parsed["pxzd"] == "DJSJP DESC"
        # tjnr should be base64 of the SQL condition
        tjnr = parsed["tjnr"]
        decoded = base64.b64decode(tjnr).decode("utf-8")
        assert "DJSJP >= to_date('2024-03-12" in decoded
        assert "DJSJP <= to_date('2024-12-31" in decoded
        assert "QCBMMC like '%学校办公室%'" in decoded
        assert "WJBT LIKE '%通知%'" in decoded
        assert "QWSS LIKE '%印发%'" in decoded

    def test_build_params_empty_fields(self):
        from app.core.tools.oa.departments import build_params
        result = build_params()
        parsed = json.loads(result)
        assert parsed["tableName"] == "ZNDX_ZHBG_GGTZ"
        assert parsed["tjnr"] == ""  # empty string when no conditions
        assert parsed["pxzd"] == ""

    def test_build_params_partial_fields(self):
        from app.core.tools.oa.departments import build_params
        result = build_params(wjbt="放假")
        parsed = json.loads(result)
        decoded = base64.b64decode(parsed["tjnr"]).decode("utf-8")
        assert "WJBT LIKE '%放假%'" in decoded
        # Should NOT contain other conditions
        assert "QCBMMC" not in decoded
        assert "QWSS" not in decoded


class TestDepartmentEnum:
    def test_department_enum_has_school_office(self):
        from app.core.tools.oa.departments import DepartmentEnum
        assert hasattr(DepartmentEnum, "SCHOOL_OFFICE")
        assert DepartmentEnum.SCHOOL_OFFICE.value == "学校办公室"

    def test_department_enum_has_personnel_division(self):
        from app.core.tools.oa.departments import DepartmentEnum
        assert hasattr(DepartmentEnum, "PERSONNEL_DIVISION")
        assert DepartmentEnum.PERSONNEL_DIVISION.value == "人事处"

    def test_department_enum_all_values_are_strings(self):
        from app.core.tools.oa.departments import DepartmentEnum
        for member in DepartmentEnum:
            assert isinstance(member.value, str)
            assert len(member.value) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv pytest tests/app/core/tools/oa/test_notification.py::TestBuildParams -v`
Expected: FAIL — modules not found

- [ ] **Step 3: Write departments.py**

```python
# backend/app/core/tools/oa/departments.py
"""
部门枚举和查询参数构造

基于中南大学校内办公网前端 JavaScript 代码逆向工程
"""
import base64
import json
from enum import Enum
from typing import Literal


# === Department Enum ===
# All 80+ departments from the fixed department list
_DEPARTMENT_VALUES = [
    "中共中南大学委员会",
    "中南大学",
    "学校办公室",
    "纪委办公室",
    "党委巡视办",
    "党委组织部",
    "党委宣传部",
    "党委统战部",
    "学生工作部（处）",
    "保卫部（处）",
    "机关及直附属单位党委",
    "校工会",
    "校团委",
    "党委教师工作部",
    "人事处",
    "监察处",
    "计划财务处",
    "本科生院",
    "科学研究部",
    "人文社会科学处",
    "研究生院",
    "发展规划与学科建设处",
    "国内合作处",
    "国际合作与交流处",
    "医院管理处",
    "资产与实验室管理处",
    "房产管理处",
    "审计处",
    "后勤保障部",
    "基建处",
    "离退休工作处",
    "采购与招标管理中心",
    "湘雅医学院",
    "实验动物学部",
    "铁道校区管委会",
    "人文学院",
    "外国语学院",
    "马克思主义学院",
    "公共管理学院",
    "材料科学与工程学院",
    "粉末冶金研究院",
    "冶金与环境学院",
    "地球科学与信息物理学院",
    "体育教研部",
    "信息与网络中心",
    "图书馆",
    "档案馆（校史馆）",
    "继续教育学院",
    "教育发展与校友事务办公室",
    "高等研究中心",
    "出版社",
    "校医院",
    "资产经营有限公司",
    "国际教育学院",
    "第二附属中学",
    "第一附属小学",
    "第二附属小学",
    "其他单位",
    ""双一流"建设办公室",
    "创新创业指导中心",
    "创新与创业教育办公室",
    "党校",
    "档案馆",
    "档案馆 (校史馆)",
    "发展与联络办公室（教育基金会、校友总会）",
    "国际合作与交流处、学校保密办公室",
    "后勤管理处",
    "后勤集团",
    "基础医学院",
    "计划财务处、信息与网络中心",
    "科学研究部、人文社科处",
    "普教管理服务中心",
    "人事处  计划财务处",
    "图书馆      学工部",
    "文学与新闻传播学院",
    "校办产业管理办公室",
    "校级奖励金委员会",
    "信息安全与大数据研究院",
    "信息科学与工程学院",
    "学生工作部",
    "研究生工作部（处）",
    "研究生院、国际合作与交流处",
    "职工医院",
    "资产管理处",
]

# Generate safe Python identifier for each department
def _to_identifier(name: str) -> str:
    return name.replace("（", "_").replace("）", "").replace("(", "_").replace(")", "").replace(" ", "_").replace(",", "_").replace("'", "").replace(""", "").replace(""", "")


class DepartmentEnum(str, Enum):
    """起草部门枚举，严格限制 LLM 可选的部门范围"""
    _ignore_ = ["name"]
    for _dept in _DEPARTMENT_VALUES:
        _id = _to_identifier(_dept)
        locals()[_id] = _dept


# === Query Parameter Builder ===

def build_params(
    qssj: str = "",
    jssj: str = "",
    qcbmmc: str = "",
    wjbt: str = "",
    qwss: str = "",
    hid_odby: str = "",
) -> str:
    """
    构造校内通知查询的 params 参数（JSON 字符串）

    Args:
        qssj: 起始时间 YYYY-MM-DD
        jssj: 结束时间 YYYY-MM-DD
        qcbmmc: 起草部门名称（模糊匹配）
        wjbt: 文件标题关键词（模糊匹配）
        qwss: 全文搜索关键词
        hid_odby: 排序字段，如 "DJSJP DESC"

    Returns:
        JSON 字符串，可直接作为 params 表单参数使用
    """
    # 1. 拼接高级搜索条件
    gjssCXTJ = ""
    if qssj:
        gjssCXTJ += f" and DJSJP >= to_date('{qssj} 00:00:00','yyyy-mm-dd hh24:mi:ss') "
    if jssj:
        gjssCXTJ += f" and DJSJP <= to_date('{jssj} 23:59:59','yyyy-mm-dd hh24:mi:ss')"
    if qcbmmc:
        gjssCXTJ += f" and QCBMMC like '%{qcbmmc}%' "
    if wjbt:
        gjssCXTJ += f" and WJBT LIKE '%{wjbt}%'  "
    if qwss:
        gjssCXTJ += f" and QWSS LIKE '%{qwss}%' "

    # 2. Base64 编码
    tjnr_encoded = base64.b64encode(gjssCXTJ.encode("utf-8")).decode("utf-8")

    # 3. 构造参数字典（tableName 硬编码，不暴露给 LLM）
    params_dict = {
        "tableName": "ZNDX_ZHBG_GGTZ",  # 校内通知固定表名
        "tjnr": tjnr_encoded,
        "pxzd": hid_odby,
    }

    # 4. 转换为紧凑 JSON 字符串
    return json.dumps(params_dict, separators=(",", ":"), ensure_ascii=False)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && uv pytest tests/app/core/tools/oa/test_notification.py::TestBuildParams -v`
Expected: PASS

- [ ] **Step 5: Write notification.py**

```python
# backend/app/core/tools/oa/notification.py
"""
OANotificationList tool - 校内通知查询工具
"""
import logging
from typing import List, Optional
from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool, BaseTool

from app.core.context import ToolContext
from .departments import DepartmentEnum, build_params

logger = logging.getLogger(__name__)


# === Input Schema ===

class OANotificationListInput(BaseModel):
    """校内通知查询输入参数"""
    qssj: Optional[str] = Field(
        default=None,
        description="起始时间，格式 YYYY-MM-DD"
    )
    jssj: Optional[str] = Field(
        default=None,
        description="结束时间，格式 YYYY-MM-DD"
    )
    qcbmmc: Optional[DepartmentEnum] = Field(
        default=None,
        description="起草部门"
    )
    wjbt: Optional[str] = Field(
        default=None,
        description="文件标题关键词（模糊匹配）"
    )
    qwss: Optional[str] = Field(
        default=None,
        description="全文搜索关键词"
    )
    pageNo: int = Field(default=1, description="页码，从1开始")
    pageSize: int = Field(default=20, description="每页条数，建议不超过50")


# === Tool Function ===

NOTIFICATION_API_URL = "https://oa.csu.edu.cn/con/xnbg/contentList"


def _query_notifications(
    ctx: ToolContext,
    qssj: Optional[str] = None,
    jssj: Optional[str] = None,
    qcbmmc: Optional[str] = None,
    wjbt: Optional[str] = None,
    qwss: Optional[str] = None,
    pageNo: int = 1,
    pageSize: int = 20,
) -> str:
    """
    查询中南大学校内通知

    支持按时间范围、部门、标题关键词、全文搜索筛选通知。
    """
    # 1. 认证检查
    if not ctx.is_authenticated:
        return "请先登录后再使用校内通知查询"

    # 2. 获取 OA Session
    session = ctx.get_subsystem_session("oa")
    if session is None:
        return "获取校内办公网会话失败，请稍后重试"

    # 3. 构造查询参数
    params_str = build_params(
        qssj=qssj or "",
        jssj=jssj or "",
        qcbmmc=qcbmmc or "",
        wjbt=wjbt or "",
        qwss=qwss or "",
    )

    # 4. 发送请求
    payload = {
        "params": params_str,
        "pageSize": str(pageSize),
        "pageNo": str(pageNo),
    }

    try:
        resp = session.post(
            NOTIFICATION_API_URL,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )

        if resp.status_code == 200:
            result = resp.json()
            count = result.get("count", 0)
            data = result.get("data", [])

            if count == 0:
                return "未找到符合条件的通知"

            # 格式化返回结果
            lines = [f"共找到 {count} 条通知：\n"]
            for i, item in enumerate(data, 1):
                lines.append(
                    f"{i}. 【{item.get('QCBMMC', '未知部门')}】{item.get('WJBT', '无标题')}\n"
                    f"   文号：{item.get('FWH', '-')} | 发文字：{item.get('FWZ', '-')} | "
                    f"起草时间：{item.get('DJSJ', '-')} | "
                    f"浏览次数：{item.get('LLCS', 0)}\n"
                )
            return "".join(lines)

        elif resp.status_code >= 300 and resp.status_code < 400:
            logger.warning(f"OA session expired (status {resp.status_code}), redirect: {resp.headers.get('Location')}")
            # Force re-fetch of session
            try:
                session = ctx.session_manager.get_session(ctx.user_id, "oa")
                resp = session.post(
                    NOTIFICATION_API_URL,
                    data=payload,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    count = result.get("count", 0)
                    data = result.get("data", [])
                    if count == 0:
                        return "未找到符合条件的通知"
                    lines = [f"共找到 {count} 条通知：\n"]
                    for i, item in enumerate(data, 1):
                        lines.append(
                            f"{i}. 【{item.get('QCBMMC', '未知部门')}】{item.get('WJBT', '无标题')}\n"
                            f"   文号：{item.get('FWH', '-')} | 发文字：{item.get('FWZ', '-')} | "
                            f"起草时间：{item.get('DJSJ', '-')} | "
                            f"浏览次数：{item.get('LLCS', 0)}\n"
                        )
                    return "".join(lines)
            except Exception:
                pass
            return "校内通知查询失败，请稍后重试"
        else:
            logger.error(f"OA notification query failed: status={resp.status_code}")
            return "查询校内通知失败，请稍后重试"

    except Exception as e:
        logger.error(f"OA notification query exception: {e}")
        return "查询校内通知失败，请稍后重试"


# === Tool Definition ===

OANotificationListTool = StructuredTool.from_function(
    func=_query_notifications,
    name="oa_notification_list",
    description="""查询中南大学校内通知（行政发文、党委发文等）。

支持多条件组合搜索：
- 按时间范围筛选（起始时间和结束时间）
- 按起草部门筛选（从预设部门列表中选择）
- 按文件标题关键词模糊搜索
- 按全文内容关键词搜索

返回通知列表，包括标题、发文类型、起草部门、文号、浏览次数等信息。

使用示例：
- "查询学校办公室最近的通知" → 不需要时间参数
- "查询2024年3月到6月的教务通知" → 设置 qssj=2024-03-01, jssj=2024-06-30
- "搜索标题包含'放假'的通知" → 设置 wjbt=放假
- "搜索内容涉及'论文'的通知" → 设置 qwss=论文
""",
    args_schema=OANotificationListInput,
)
```

- [ ] **Step 6: Write __init__.py**

```python
# backend/app/core/tools/oa/__init__.py
from typing import List

from app.core.context import ToolContext
from .notification import OANotificationListTool, OANotificationListInput


def create_oa_tools(ctx: ToolContext) -> List:
    """
    创建校内通知工具

    始终可用，但需要用户已登录（认证检查在工具内部进行）
    """
    return [OANotificationListTool]
```

- [ ] **Step 7: Run notification tests**

Run: `cd backend && uv pytest tests/app/core/tools/oa/test_notification.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add backend/app/core/tools/oa/departments.py backend/app/core/tools/oa/notification.py backend/app/core/tools/oa/__init__.py backend/tests/app/core/tools/oa/test_notification.py
git commit -m "feat(oa): add OANotificationList tool for CSU campus notifications"
```

---

## Chunk 3: Integration (AgentFactory)

**Files:**
- Modify: `backend/app/core/agents/factory.py`

---

- [ ] **Step 1: Import create_oa_tools in factory.py**

Add to imports in `backend/app/core/agents/factory.py`:

```python
from app.core.tools.oa import create_oa_tools  # NEW
```

- [ ] **Step 2: Add oa tools to create_agent method**

In the `create_agent` method of `AgentFactory`, after the JWC tools block:

```python
# OA 工具（需要登录，认证检查在工具内部）
if ctx.is_authenticated:
    tools.extend(create_oa_tools(ctx))  # NEW
```

Also update the system prompt (in `_build_system_prompt`) to add:
```
- oa_notification_list: 查询校内通知（需登录）
```

Add it under the JWC tools section in the authenticated prompt.

- [ ] **Step 3: Verify AgentFactory works**

Run: `cd backend && uv python -c "from app.core.agents.factory import AgentFactory; print('OK')"`
Expected: No import errors

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/agents/factory.py
git commit -m "feat(agent): integrate OANotificationList tool into AgentFactory"
```

