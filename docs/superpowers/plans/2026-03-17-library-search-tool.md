# 图书馆搜索工具 - 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将中南大学图书馆检索接口封装为两个 LangChain Tools（library_search 和 library_get_book_location）

**Architecture:** 参考 jwc tools 的模式，在 `backend/app/core/tools/library/` 目录下创建 service.py 和 tools.py，使用 Pydantic 定义输入输出模型，使用 requests 调用图书馆 API

**Tech Stack:** Python 3.11+, LangChain, Pydantic, requests, uv

---

## Chunk 1: 创建数据模型和服务层

### Task 1: 创建 library 模块目录和数据模型

**Files:**
- Create: `backend/app/core/tools/library/__init__.py`
- Create: `backend/app/core/tools/library/models.py`
- Modify: `backend/app/core/tools/__init__.py`

- [ ] **Step 1: 创建 `backend/app/core/tools/library/__init__.py`**

```python
"""
Library tools module - 中南大学图书馆查询
"""
from app.core.tools.library.tools import (
    library_search,
    library_get_book_location,
    LIBRARY_TOOLS,
)

__all__ = [
    "library_search",
    "library_get_book_location",
    "LIBRARY_TOOLS",
]
```

- [ ] **Step 2: 创建 `backend/app/core/tools/library/models.py`**

```python
"""
数据模型 - 图书馆搜索
"""
from typing import Optional
from pydantic import BaseModel, Field


class LibraryBookItem(BaseModel):
    """图书基本信息"""
    record_id: int = Field(..., description="记录ID，用于查询复本位置")
    title: str = Field(..., description="书名")
    author: Optional[str] = Field(None, description="作者")
    publisher: Optional[str] = Field(None, description="出版社")
    isbns: list[str] = Field(default_factory=list, description="ISBN 数组")
    publish_year: Optional[str] = Field(None, description="出版年")
    call_no: list[str] = Field(default_factory=list, description="索书号数组")
    doc_name: Optional[str] = Field(None, description="文献类型")
    physical_count: int = Field(0, description="馆藏册数")
    on_shelf_count: int = Field(0, description="在架册数")
    language: Optional[str] = Field(None, description="语言代码")
    country: Optional[str] = Field(None, description="国家代码")
    subjects: Optional[str] = Field(None, description="主题词")
    abstract: Optional[str] = Field(None, description="摘要")


class LibraryBookSearchResult(BaseModel):
    """图书搜索结果"""
    total: int = Field(..., description="搜索结果总数")
    items: list[LibraryBookItem] = Field(default_factory=list, description="图书列表")


class LibraryBookItemCopy(BaseModel):
    """单本复本信息"""
    item_id: int = Field(..., description="复本ID")
    call_no: str = Field(..., description="索书号,用于索引书架上书本的位置")
    barcode: Optional[str] = Field(None, description="条码号")
    lib_code: Optional[str] = Field(None, description="馆代码")
    lib_name: Optional[str] = Field(None, description="馆名称")
    location_id: Optional[int] = Field(None, description="位置ID")
    location_name: Optional[str] = Field(None, description="位置名称")
    cur_location_id: Optional[int] = Field(None, description="当前所在位置ID")
    cur_location_name: Optional[str] = Field(None, description="当前所在位置名称")
    vol: Optional[str] = Field(None, description="卷册信息")
    in_date: Optional[str] = Field(None, description="入藏日期")
    process_type: Optional[str] = Field(None, description="处理类型/借阅状态")
    item_policy_name: Optional[str] = Field(None, description="流通规则名称")
    shelf_no: Optional[str] = Field(None, description="架位号")


class LibraryBookItemCopiesResult(BaseModel):
    """复本列表结果"""
    total: int = Field(..., description="总数")
    items: list[LibraryBookItemCopy] = Field(default_factory=list, description="复本列表")
```

- [ ] **Step 3: 运行测试验证语法正确**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.tools.library.models import LibraryBookSearchResult; print('OK')"`
Expected: 输出 "OK"

- [ ] **Step 4: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/core/tools/library/ backend/app/core/tools/__init__.py
git commit -m "feat(library): add library models"
```

---

### Task 2: 创建 LibraryService 封装 API 调用

**Files:**
- Create: `backend/app/core/tools/library/service.py`

- [ ] **Step 1: 创建 `backend/app/core/tools/library/service.py`**

```python
"""
Library Service - 封装图书馆 API 调用
"""
import json
import logging
import requests
from typing import Optional
from .models import (
    LibraryBookSearchResult,
    LibraryBookItem,
    LibraryBookItemCopiesResult,
    LibraryBookItemCopy,
)

logger = logging.getLogger(__name__)

# API 配置
SEARCH_URL = "https://opac.lib.csu.edu.cn/find/unify/advancedSearch"
LOCATION_URL = "https://opac.lib.csu.edu.cn/find/physical/groupitems"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "sec-ch-ua-platform": "\"Linux\"",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "mappingPath": "",
    "groupCode": "800388",
    "sec-ch-ua-mobile": "?0",
    "x-lang": "CHI",
    "Content-Type": "application/json;charset=UTF-8",
    "content-language": "zh_CN",
    "Origin": "https://opac.lib.csu.edu.cn",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://opac.lib.csu.edu.cn/",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}


class LibraryService:
    """图书馆服务"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def search(self, keywords: str, page: int = 1, rows: int = 10) -> LibraryBookSearchResult:
        """
        搜索图书馆馆藏

        Args:
            keywords: 搜索关键词
            page: 页码
            rows: 每页数量

        Returns:
            LibraryBookSearchResult: 搜索结果
        """
        payload = {
            "docCode": [None],
            "litCode": [],
            "matchMode": "2",
            "resourceType": [],
            "subject": [],
            "discode1": [],
            "publisher": [],
            "libCode": [],
            "locationId": [],
            "eCollectionIds": [],
            "neweCollectionIds": [],
            "curLocationId": [],
            "campusId": [],
            "kindNo": [],
            "collectionName": [],
            "author": [],
            "langCode": [],
            "countryCode": [],
            "publishBegin": None,
            "publishEnd": None,
            "coreInclude": [],
            "ddType": [],
            "verifyStatus": [],
            "group": [],
            "sortField": "relevance",
            "sortClause": None,
            "page": page,
            "rows": rows,
            "onlyOnShelf": None,
            "searchItems": [
                {
                    "oper": None,
                    "searchField": "keyWord",
                    "matchMode": "2",
                    "searchFieldContent": keywords
                }
            ],
            "searchFieldContent": "",
            "searchField": "keyWord",
            "searchFieldList": None,
            "isOpen": False
        }

        try:
            response = self.session.post(SEARCH_URL, data=json.dumps(payload), timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                logger.warning(f"Search failed: {data.get('message')}")
                return LibraryBookSearchResult(total=0, items=[])

            search_result = data.get("data", {})
            total = search_result.get("numFound", 0)
            items = []

            for item in search_result.get("searchResult", []):
                items.append(LibraryBookItem(
                    record_id=item.get("recordId", 0),
                    title=item.get("title", ""),
                    author=item.get("author"),
                    publisher=item.get("publisher"),
                    isbns=item.get("isbns", []),
                    publish_year=item.get("publishYear"),
                    call_no=item.get("callNo", []),
                    doc_name=item.get("docName"),
                    physical_count=item.get("physicalCount", 0),
                    on_shelf_count=item.get("onShelfCountI", 0),
                    language=item.get("langCode"),
                    country=item.get("countryCode"),
                    subjects=item.get("subjectWord"),
                    abstract=item.get("adstract"),
                ))

            return LibraryBookSearchResult(total=total, items=items)

        except Exception as e:
            logger.error(f"Library search error: {e}")
            return LibraryBookSearchResult(total=0, items=[])

    def get_book_copies(self, record_id: int) -> LibraryBookItemCopiesResult:
        """
        获取图书复本位置信息

        Args:
            record_id: 图书记录ID

        Returns:
            LibraryBookItemCopiesResult: 复本列表
        """
        payload = {
            "page": 1,
            "rows": 50,
            "entrance": None,
            "recordId": str(record_id),
            "isUnify": True,
            "sortType": 0,
            "callNo": ""
        }

        try:
            response = self.session.post(LOCATION_URL, data=json.dumps(payload), timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                logger.warning(f"Get copies failed: {data.get('message')}")
                return LibraryBookItemCopiesResult(total=0, items=[])

            copies_data = data.get("data", {})
            total = copies_data.get("totalCount", 0)
            items = []

            for item in copies_data.get("list", []):
                items.append(LibraryBookItemCopy(
                    item_id=item.get("itemId", 0),
                    call_no=item.get("callNo", ""),
                    barcode=item.get("barcode"),
                    lib_code=item.get("libCode"),
                    lib_name=item.get("libName"),
                    location_id=item.get("locationId"),
                    location_name=item.get("locationName"),
                    cur_location_id=item.get("curLocationId"),
                    cur_location_name=item.get("curLocationName"),
                    vol=item.get("vol"),
                    in_date=item.get("inDate"),
                    process_type=item.get("processType"),
                    item_policy_name=item.get("itemPolicyName"),
                    shelf_no=item.get("shelfNo"),
                ))

            return LibraryBookItemCopiesResult(total=total, items=items)

        except Exception as e:
            logger.error(f"Library get copies error: {e}")
            return LibraryBookItemCopiesResult(total=0, items=[])


# 全局服务实例
_library_service: Optional[LibraryService] = None


def get_library_service() -> LibraryService:
    """获取全局 LibraryService 实例"""
    global _library_service
    if _library_service is None:
        _library_service = LibraryService()
    return _library_service
```

- [ ] **Step 2: 运行测试验证语法正确**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.tools.library.service import LibraryService; print('OK')"`
Expected: 输出 "OK"

- [ ] **Step 3: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/core/tools/library/service.py
git commit -m "feat(library): add library service"
```

---

## Chunk 2: 创建 LangChain Tools

### Task 3: 创建 library tools.py

**Files:**
- Create: `backend/app/core/tools/library/tools.py`

- [ ] **Step 1: 创建 `backend/app/core/tools/library/tools.py`**

```python
"""
LangChain Tools - 图书馆查询
"""
import logging
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from .service import LibraryService, get_library_service
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
```

- [ ] **Step 2: 运行测试验证语法正确**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.tools.library.tools import LIBRARY_TOOLS; print(f'Loaded {len(LIBRARY_TOOLS)} tools')"`
Expected: 输出 "Loaded 2 tools"

- [ ] **Step 3: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/core/tools/library/tools.py
git commit -m "feat(library): add library langchain tools"
```

---

## Chunk 3: 集成和测试

### Task 4: 更新 __init__.py 导出

**Files:**
- Modify: `backend/app/core/tools/__init__.py`

- [ ] **Step 1: 更新 `backend/app/core/tools/__init__.py`**

```python
"""
Core tools module
"""
from app.core.tools.rag_tool import create_rag_tool
from app.core.tools.library.tools import library_search, library_get_book_location, LIBRARY_TOOLS

__all__ = [
    "create_rag_tool",
    "library_search",
    "library_get_book_location",
    "LIBRARY_TOOLS",
]
```

- [ ] **Step 2: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/core/tools/__init__.py
git commit -m "feat(library): export library tools"
```

---

### Task 5: 创建单元测试

**Files:**
- Create: `backend/tests/core/tools/library/__init__.py`
- Create: `backend/tests/core/tools/library/test_library_service.py`

- [ ] **Step 1: 创建测试目录和 __init__.py**

```bash
mkdir -p backend/tests/core/tools/library
touch backend/tests/core/tools/library/__init__.py
```

- [ ] **Step 2: 创建 `backend/tests/core/tools/library/test_library_service.py`**

```python
"""
Library Service Tests
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.tools.library.models import (
    LibraryBookItem,
    LibraryBookSearchResult,
    LibraryBookItemCopy,
    LibraryBookItemCopiesResult,
)
from app.core.tools.library.service import LibraryService


class TestLibraryModels:
    """测试数据模型"""

    def test_library_book_item(self):
        item = LibraryBookItem(
            record_id=794724,
            title="Vue.js实战",
            author="梁灏编著",
            publisher="清华大学出版社",
            isbns=["978-7-302-48492-9"],
            publish_year="2017",
            call_no=["TP392.092.2/LH"],
            doc_name="图书",
            physical_count=3,
            on_shelf_count=3,
            language="chi",
            country="CN",
        )
        assert item.record_id == 794724
        assert item.title == "Vue.js实战"
        assert item.on_shelf_count == 3

    def test_library_book_search_result(self):
        items = [
            LibraryBookItem(
                record_id=1,
                title="Test Book",
                physical_count=2,
                on_shelf_count=1,
            )
        ]
        result = LibraryBookSearchResult(total=1, items=items)
        assert result.total == 1
        assert len(result.items) == 1

    def test_library_book_item_copy(self):
        copy = LibraryBookItemCopy(
            item_id=2831014,
            call_no="TP392.092.2/LH",
            barcode="101134599",
            lib_name="中南大学",
            location_name="天心校区馆-铁道书库",
            process_type="在架",
            shelf_no="21架B面2列3层",
        )
        assert copy.item_id == 2831014
        assert copy.process_type == "在架"


class TestLibraryService:
    """测试 LibraryService """

    @patch("app.core.tools.library.service.requests.Session")
    def test_search_success(self, mock_session_class):
        """测试搜索成功"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "numFound": 1,
                "searchResult": [
                    {
                        "recordId": 794724,
                        "title": "Vue.js实战",
                        "author": "梁灏编著",
                        "publisher": "清华大学出版社",
                        "isbns": ["978-7-302-48492-9"],
                        "publishYear": "2017",
                        "callNo": ["TP392.092.2/LH"],
                        "docName": "图书",
                        "physicalCount": 3,
                        "onShelfCountI": 3,
                        "langCode": "chi",
                        "countryCode": "CN",
                    }
                ]
            }
        }
        mock_session.post.return_value = mock_response

        service = LibraryService()
        result = service.search("Vue")

        assert result.total == 1
        assert result.items[0].title == "Vue.js实战"

    @patch("app.core.tools.library.service.requests.Session")
    def test_search_empty(self, mock_session_class):
        """测试搜索无结果"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "numFound": 0,
                "searchResult": []
            }
        }
        mock_session.post.return_value = mock_response

        service = LibraryService()
        result = service.search("xyznonexist")

        assert result.total == 0
        assert len(result.items) == 0


class TestToolFunctions:
    """测试 Tool 函数格式化"""

    def test_format_search_result_empty(self):
        from app.core.tools.library.tools import _format_search_result

        result = LibraryBookSearchResult(total=0, items=[])
        output = _format_search_result(result)
        assert "未找到" in output

    def test_format_search_result_with_items(self):
        from app.core.tools.library.tools import _format_search_result

        items = [
            LibraryBookItem(
                record_id=794724,
                title="Vue.js实战",
                author="梁灏",
                publisher="清华大学出版社",
                isbns=["978-7-302-48492-9"],
                publish_year="2017",
                call_no=["TP392.092.2/LH"],
                physical_count=3,
                on_shelf_count=3,
            )
        ]
        result = LibraryBookSearchResult(total=1, items=items)
        output = _format_search_result(result)

        assert "Vue.js实战" in output
        assert "梁灏" in output
        assert "794724" in output

    def test_format_copies_result(self):
        from app.core.tools.library.tools import _format_copies_result

        items = [
            LibraryBookItemCopy(
                item_id=2831014,
                call_no="TP392.092.2/LH",
                barcode="101134599",
                lib_name="中南大学",
                location_name="天心校区馆-铁道书库",
                cur_location_name="天心校区馆-铁道书库",
                process_type="在架",
                shelf_no="21架B面2列3层",
            )
        ]
        result = LibraryBookItemCopiesResult(total=1, items=items)
        output = _format_copies_result(result)

        assert "中南大学" in output
        assert "在架" in output
        assert "21架" in output
```

- [ ] **Step 2: 运行测试**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/core/tools/library/ -v`
Expected: 所有测试通过

- [ ] **Step 3: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/tests/core/tools/library/
git commit -m "test(library): add library service tests"
```

---

### Task 6: 最终验证

**Files:**
- None (验证步骤)

- [ ] **Step 1: 验证所有工具可以导入**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.tools import library_search, library_get_book_location, LIBRARY_TOOLS; print('Tools:', [t.name for t in LIBRARY_TOOLS])"`
Expected: 输出 `Tools: ['library_search', 'library_get_book_location']`

- [ ] **Step 2: 运行所有测试**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/core/tools/library/ -v --tb=short`
Expected: 所有测试通过

- [ ] **Step 3: 最终 commit**

```bash
cd /home/luorome/software/CampusMind
git status
git add -A
git commit -m "feat(library): complete library search tools implementation"
```
