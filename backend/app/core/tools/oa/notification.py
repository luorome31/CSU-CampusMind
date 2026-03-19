# backend/app/core/tools/oa/notification.py
"""
OANotificationList tool - 校内通知查询工具
"""
import logging
from typing import Optional

import requests
from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool

from app.core.context import ToolContext
from .departments import DepartmentEnum, build_params

logger = logging.getLogger(__name__)


def _format_notification_results(result: dict) -> str:
    """Format notification API response into readable text."""
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
            return _format_notification_results(resp.json())

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
                    return _format_notification_results(resp.json())
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