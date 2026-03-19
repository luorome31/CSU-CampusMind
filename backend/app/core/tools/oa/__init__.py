# backend/app/core/tools/oa/__init__.py
"""
OA 工具模块 - 校内通知查询
"""
from typing import List

from app.core.context import ToolContext
from app.core.tools.oa.notification import OANotificationListTool, OANotificationListInput


def create_oa_tools(ctx: ToolContext) -> List:
    """
    创建校内通知工具

    始终可用，但需要用户已登录（认证检查在工具内部进行）
    """
    return [OANotificationListTool]


__all__ = [
    "create_oa_tools",
    "OANotificationListTool",
    "OANotificationListInput",
]