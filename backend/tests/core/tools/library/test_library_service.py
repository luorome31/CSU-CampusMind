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
