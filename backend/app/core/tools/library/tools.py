"""
LangChain Tools - 图书馆查询
"""
import logging
from typing import List
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool
from app.core.context import ToolContext
from .service import get_library_service
from .models import LibraryBookSearchResult, LibraryBookItemCopiesResult

logger = logging.getLogger(__name__)


# ============ Tool Input Models ============

class LibrarySearchInput(BaseModel):
    """图书馆搜索输入"""
    keywords: str = Field(..., description="搜索关键词，建议使用简短领域关键词（3字以内）")
    page: int = Field(default=1, description="页码，默认第1页")
    rows: int = Field(default=10, description="每页数量，默认10条")


class LibraryGetBookLocationInput(BaseModel):
    """图书位置查询输入"""
    record_id: int = Field(..., description="图书记录ID（来自搜索结果中的 record_id）")


# ============ Tool Functions ============

def _format_search_result(result: LibraryBookSearchResult) -> str:
    """格式化搜索结果"""
    if result.total == 0:
        return "未找到相关图书"

    lines = [f"共找到 {result.total} 条结果：\n"]

    for i, book in enumerate(result.items, 1):
        lines.append(f"--- 第 {i} 条 ---")
        lines.append(f"📚 书名: {book.title}")
        if book.author:
            lines.append(f"👤 作者: {book.author}")
        if book.publisher:
            lines.append(f"🏢 出版社: {book.publisher}")
        if book.publish_year:
            lines.append(f"📅 出版年: {book.publish_year}")
        if book.isbns:
            lines.append(f"📖 ISBN: {', '.join(book.isbns)}")
        if book.call_no:
            lines.append(f"🔖 索书号: {', '.join(book.call_no)}")
        lines.append(f"📊 馆藏: {book.physical_count} 册 / 在架: {book.on_shelf_count} 册")
        lines.append(f"🔑 Record ID: {book.record_id}")
        lines.append("")

    return "\n".join(lines)


def _search_library(keywords: str, page: int = 1, rows: int = 10) -> str:
    """
    搜索中南大学图书馆馆藏图书

    Args:
        keywords: 搜索关键词
        page: 页码
        rows: 每页数量

    Returns:
        str: 格式化后的搜索结果
    """
    try:
        service = get_library_service()
        result = service.search(keywords, page, rows)
        return _format_search_result(result)
    except Exception as e:
        logger.error(f"Library search failed: {e}")
        return f"搜索失败: {str(e)}"


def _format_copies_result(result: LibraryBookItemCopiesResult) -> str:
    """格式化复本位置结果"""
    if result.total == 0:
        return "未找到复本信息"

    lines = [f"共 {result.total} 个复本：\n"]

    for i, copy in enumerate(result.items, 1):
        lines.append(f"--- 复本 {i} ---")
        lines.append(f"📍 馆: {copy.lib_name or '未知'}")
        lines.append(f"📍 位置: {copy.cur_location_name or copy.location_name or '未知'}")
        lines.append(f"🔖 索书号: {copy.call_no}")
        if copy.barcode:
            lines.append(f"🏷️ 条码号: {copy.barcode}")
        if copy.shelf_no:
            lines.append(f"📦 架位号: {copy.shelf_no}")
        status = "✅ 在架" if copy.process_type == "在架" else "❌ 已借出"
        lines.append(f"📌 状态: {status}")
        if copy.in_date:
            lines.append(f"📅 入藏日期: {copy.in_date}")
        lines.append("")

    return "\n".join(lines)


def _get_book_location(record_id: int) -> str:
    """
    查询图书的馆藏位置信息

    Args:
        record_id: 图书记录ID（来自搜索结果）

    Returns:
        str: 格式化后的复本位置信息
    """
    try:
        service = get_library_service()
        result = service.get_book_copies(record_id)
        return _format_copies_result(result)
    except Exception as e:
        logger.error(f"Library get copies failed: {e}")
        return f"查询失败: {str(e)}"


# ============ LangChain Tools ============

library_search = StructuredTool.from_function(
    func=_search_library,
    name="library_search",
    description="搜索中南大学图书馆馆藏。根据关键词搜索图书，返回图书列表及其 record_id。可用于查找特定主题的图书。",
    args_schema=LibrarySearchInput,
)

library_get_book_location = StructuredTool.from_function(
    func=_get_book_location,
    name="library_get_book_location",
    description="查询图书的馆藏位置信息。根据搜索结果中的 record_id 查询该书的所有复本所在位置、可借状态等。",
    args_schema=LibraryGetBookLocationInput,
)


# 工具列表
LIBRARY_TOOLS = [
    library_search,
    library_get_book_location,
]


# ============ Factory Function ============


def create_library_tools(ctx: ToolContext) -> List[BaseTool]:
    """
    创建图书馆工具（不需要登录）

    Library 工具是公开的，所有用户都可以使用
    """

    def _search_library(keywords: str, page: int = 1, rows: int = 10) -> str:
        """搜索图书馆馆藏"""
        try:
            service = get_library_service()
            result = service.search(keywords, page, rows)
            return _format_search_result(result)
        except Exception as e:
            logger.error(f"Library search failed: {e}")
            return f"搜索失败: {str(e)}"

    def _get_book_location(record_id: int) -> str:
        """查询图书位置"""
        try:
            service = get_library_service()
            result = service.get_book_copies(record_id)
            return _format_copies_result(result)
        except Exception as e:
            logger.error(f"Library get copies failed: {e}")
            return f"查询失败: {str(e)}"

    return [
        StructuredTool.from_function(
            func=_search_library,
            name="library_search",
            description="搜索中南大学图书馆馆藏。根据关键词搜索图书，返回图书列表及其 record_id。可用于查找特定主题的图书。"
        ),
        StructuredTool.from_function(
            func=_get_book_location,
            name="library_get_book_location",
            description="查询图书的馆藏位置信息。根据搜索结果中的 record_id 查询该书的所有复本所在位置、可借状态等。"
        ),
    ]
