# backend/app/core/tools/oa/__init__.py
"""
OA 工具模块 - 校内通知查询
"""
import json
import logging
from datetime import datetime
from typing import List, Optional

import requests
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.core.context import ToolContext
from app.core.tools.oa.departments import DepartmentEnum, build_params

logger = logging.getLogger(__name__)

NOTIFICATION_API_URL = "https://oa.csu.edu.cn/con/xnbg/contentList"


def _decode_json_with_bom(response: requests.Response) -> dict:
    """Decode JSON response, handling various encoding issues."""
    # Check content-encoding
    content_encoding = response.headers.get("Content-Encoding", "")
    logger.debug(f"Response Content-Encoding: {content_encoding}")

    content = response.content

    # Handle gzip compression if present
    if content_encoding.lower() == "gzip":
        import gzip
        try:
            content = gzip.decompress(content)
            logger.info("Decompressed gzip response")
        except Exception as e:
            logger.warning(f"Failed to decompress gzip: {e}")

    try:
        return response.json()
    except json.JSONDecodeError as e:
        logger.info(f"Standard JSON parsing failed: {e}, trying alternative encodings...")

        # Try different encodings
        encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"]
        for encoding in encodings:
            try:
                return json.loads(content.decode(encoding))
            except Exception:
                continue

        # If all fail, save to file for manual inspection
        debug_file = f"/tmp/oa_response_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
        with open(debug_file, "wb") as f:
            f.write(content)
        logger.error(f"Failed to parse response. Saved to {debug_file} ({len(content)} bytes)")
        raise


class OANotificationListInput(BaseModel):
    """校内通知查询输入参数"""
    qssj: Optional[str] = Field(default=None, description="起始时间，格式 YYYY-MM-DD")
    jssj: Optional[str] = Field(default=None, description="结束时间，格式 YYYY-MM-DD")
    qcbmmc: Optional[DepartmentEnum] = Field(default=None, description="起草部门")
    wjbt: Optional[str] = Field(default=None, description="文件标题关键词（模糊匹配）")
    qwss: Optional[str] = Field(default=None, description="全文搜索关键词")
    pageNo: int = Field(default=1, description="页码，从1开始")
    pageSize: int = Field(default=20, description="每页条数，建议不超过50")


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


def create_oa_tools(ctx: ToolContext) -> List:
    """
    创建校内通知工具（依赖 ToolContext，利用闭包隐藏 user_id）

    Args:
        ctx: 工具运行时上下文，包含用户身份和会话管理

    Returns:
        OA 相关工具列表
    """

    def _query_notifications(
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
            logger.warning("oa_notification_list: user not authenticated")
            return "请先登录后再使用校内通知查询"

        # 2. 获取 OA Session
        logger.info(f"oa_notification_list: attempting to get OA session for user {ctx.user_id}")
        session = ctx.get_subsystem_session("oa")
        if session is None:
            logger.error(f"oa_notification_list: get_subsystem_session('oa') returned None for user {ctx.user_id}")
            return "获取校内办公网会话失败，请稍后重试"
        logger.info(f"oa_notification_list: OA session obtained successfully")

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
                return _format_notification_results(_decode_json_with_bom(resp))

            elif resp.status_code >= 300 and resp.status_code < 400:
                redirect_url = resp.headers.get('Location', 'unknown')
                logger.warning(f"OA notification query: got redirect (status {resp.status_code}), redirect URL: {redirect_url}")
                # Force re-fetch of session
                try:
                    logger.info(f"OA notification query: attempting to re-fetch OA session")
                    session = ctx.session_manager.get_session(ctx.user_id, "oa")
                    resp = session.post(
                        NOTIFICATION_API_URL,
                        data=payload,
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        logger.info(f"OA notification query: re-fetch successful, got {len(_decode_json_with_bom(resp).get('data', []))} results")
                        return _format_notification_results(_decode_json_with_bom(resp))
                    else:
                        logger.error(f"OA notification query: re-fetch failed with status {resp.status_code}")
                except Exception as retry_err:
                    logger.error(f"OA notification query: re-fetch session exception: {retry_err}", exc_info=True)
                return "校内通知查询失败，请稍后重试"
            else:
                logger.error(f"OA notification query failed: status={resp.status_code}, response text: {resp.text[:200] if resp.text else 'empty'}")
                return "查询校内通知失败，请稍后重试"

        except requests.exceptions.Timeout as e:
            logger.error(f"OA notification query timeout: {e}")
            return "查询校内通知超时，请稍后重试"
        except requests.exceptions.ConnectionError as e:
            logger.error(f"OA notification query connection error: {e}", exc_info=True)
            return "无法连接到校内通知系统，请检查网络连接"
        except Exception as e:
            logger.error(f"OA notification query unexpected exception: {e}", exc_info=True)
            return "查询校内通知失败，请稍后重试"

    return [
        StructuredTool.from_function(
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
        ),
    ]


__all__ = [
    "create_oa_tools",
]