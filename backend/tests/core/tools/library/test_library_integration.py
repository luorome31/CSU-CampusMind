"""
Library Tools Integration Tests - Real API Tests

这些测试会调用真实的中南大学图书馆 API。
使用标记来区分：@pytest.mark.integration
"""
import pytest
from app.core.tools.library.service import LibraryService
from app.core.tools.library.tools import _search_library, _get_book_location


class TestLibrarySearchIntegration:
    """集成测试：图书馆搜索"""

    @pytest.mark.integration
    def test_search_vue_books(self):
        """测试搜索 Vue 相关的图书"""
        service = LibraryService()
        result = service.search("Vue", page=1, rows=5)

        # 验证返回结构
        assert result.total > 0, "应该找到 Vue 相关的图书"
        assert len(result.items) > 0, "应该返回图书列表"

        # 验证第一条结果的字段
        first_book = result.items[0]
        assert first_book.record_id > 0, "应该有有效的 record_id"
        assert first_book.title, "应该有书名"
        assert first_book.physical_count >= 0, "应该有馆藏数量"

        print(f"\n=== 搜索 'Vue' 结果 ===")
        print(f"总数: {result.total}")
        print(f"第一条: {first_book.title}")
        print(f"Record ID: {first_book.record_id}")

    @pytest.mark.integration
    def test_search_with_special_chars(self):
        """测试搜索特殊字符 - 图书馆使用模糊匹配"""
        service = LibraryService()
        # 图书馆 API 使用模糊匹配，特殊字符可能返回大量结果或空结果
        result = service.search("!!!@@@###", page=1, rows=5)

        # API 行为不确定，可能是 0 也可能不是 0
        # 只验证返回结构正确
        assert isinstance(result.total, int), "total 应该是整数"
        assert isinstance(result.items, list), "items 应该是列表"

    @pytest.mark.integration
    def test_search_python_books(self):
        """测试搜索 Python 相关的图书"""
        service = LibraryService()
        result = service.search("Python", page=1, rows=3)

        assert result.total > 0, "应该找到 Python 相关的图书"
        assert len(result.items) <= 3, "应该最多返回 3 条"

        print(f"\n=== 搜索 'Python' 结果 ===")
        print(f"总数: {result.total}")
        for i, book in enumerate(result.items[:3], 1):
            print(f"{i}. {book.title} - {book.author}")


class TestLibraryGetBookCopiesIntegration:
    """集成测试：获取图书复本位置"""

    @pytest.mark.integration
    def test_get_book_copies_by_record_id(self):
        """测试根据 record_id 获取复本位置"""
        # 先搜索获取一个有效的 record_id
        service = LibraryService()
        search_result = service.search("Vue", page=1, rows=1)

        assert search_result.total > 0, "搜索应该返回结果"

        record_id = search_result.items[0].record_id
        book_title = search_result.items[0].title

        # 查询复本位置
        copies_result = service.get_book_copies(record_id)

        # 验证返回结构
        assert copies_result.total > 0, f"《{book_title}》应该有复本"

        first_copy = copies_result.items[0]
        assert first_copy.item_id > 0, "应该有有效的 item_id"
        assert first_copy.call_no, "应该有索书号"
        assert first_copy.lib_name, "应该有馆名称"

        print(f"\n=== 《{book_title}》复本信息 ===")
        print(f"Record ID: {record_id}")
        print(f"复本总数: {copies_result.total}")
        print(f"第一个复本:")
        print(f"  - 馆: {first_copy.lib_name}")
        print(f"  - 位置: {first_copy.cur_location_name or first_copy.location_name}")
        print(f"  - 索书号: {first_copy.call_no}")
        print(f"  - 状态: {first_copy.process_type}")

    @pytest.mark.integration
    def test_get_copies_with_invalid_id(self):
        """测试使用无效的 record_id"""
        service = LibraryService()
        result = service.get_book_copies(999999999)

        # 无效 ID 应该返回空结果
        assert result.total == 0, "无效 ID 应该返回 0 复本"


class TestLibraryToolsIntegration:
    """集成测试：LangChain Tools 函数"""

    @pytest.mark.integration
    def test_library_search_tool(self):
        """测试 library_search tool 函数"""
        result = _search_library("Java", page=1, rows=3)

        # 验证返回的是格式化字符串
        assert "共找到" in result, "结果应该包含总数"
        assert "Record ID:" in result, "结果应该包含 record_id"

        print(f"\n=== library_search 工具测试 ===")
        print(result[:500])  # 打印前 500 字符

    @pytest.mark.integration
    def test_library_get_location_tool(self):
        """测试 library_get_book_location tool 函数"""
        # 先搜索获取 record_id
        service = LibraryService()
        search_result = service.search("数据结构", page=1, rows=1)
        if search_result.total == 0:
            pytest.skip("未找到测试数据")

        record_id = search_result.items[0].record_id

        # 使用 tool 获取位置
        result = _get_book_location(record_id)

        # 验证返回的是格式化字符串
        assert "复本" in result or "未找到" in result, "结果应该包含复本信息"

        print(f"\n=== library_get_book_location 工具测试 ===")
        print(result[:500])


class TestLibrarySearchEndToEnd:
    """端到端测试：完整的搜索和查询流程"""

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_full_search_flow(self):
        """测试完整的搜索流程"""
        # 1. 搜索图书
        service = LibraryService()
        search_result = service.search("机器学习", page=1, rows=5)

        assert search_result.total > 0, "应该找到图书"

        # 2. 获取第一本书的复本位置
        first_book = search_result.items[0]
        copies_result = service.get_book_copies(first_book.record_id)

        # 3. 验证数据完整性
        assert first_book.title, "书名不应为空"
        assert first_book.record_id > 0, "record_id 应为正数"

        if copies_result.total > 0:
            assert copies_result.items[0].call_no, "索书号不应为空"

        print(f"\n=== 端到端测试: 搜索 '机器学习' ===")
        print(f"找到 {search_result.total} 本书")
        print(f"第一本: {first_book.title}")
        print(f"作者: {first_book.author}")
        print(f"馆藏: {first_book.physical_count} 册 / 在架: {first_book.on_shelf_count} 册")
        print(f"复本数量: {copies_result.total}")
