# backend/app/core/tools/oa/notification.py
"""
OANotificationList tool - 校内通知查询工具

NOTE: This module is deprecated. Import from app.core.tools.oa instead.
"""
from app.core.tools.oa import (
    OANotificationListInput,
    create_oa_tools,
)

# Re-export for backwards compatibility
__all__ = [
    "create_oa_tools",
    "OANotificationListInput",
]
