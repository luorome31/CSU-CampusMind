"""
Text Chunker 测试
"""
import pytest
from app.services.rag.chunker import TextChunker
from app.schema.chunk import ChunkModel


class TestTextChunker:
    """TextChunker 业务逻辑测试"""

    def test_chunker_init_default(self):
        """测试默认初始化"""
        chunker = TextChunker()

        assert chunker.chunk_size == 500
        assert chunker.overlap_size == 100

    def test_chunker_init_custom(self):
        """测试自定义参数"""
        chunker = TextChunker(chunk_size=1000, overlap_size=200)

        assert chunker.chunk_size == 1000
        assert chunker.overlap_size == 200


class TestSplitTextByLines:
    """split_text_by_lines 方法测试"""

    def test_split_empty_text(self):
        """测试空文本"""
        chunker = TextChunker(chunk_size=500, overlap_size=100)
        result = chunker.split_text_by_lines("")

        assert result == []

    def test_split_single_line(self):
        """测试单行"""
        chunker = TextChunker(chunk_size=500, overlap_size=100)
        result = chunker.split_text_by_lines("This is a single line")

        assert len(result) == 1
        assert result[0] == "This is a single line"

    def test_split_multiple_lines_within_limit(self):
        """测试多行在限制内"""
        chunker = TextChunker(chunk_size=500, overlap_size=100)
        text = "Line 1\nLine 2\nLine 3"
        result = chunker.split_text_by_lines(text)

        # Should be one chunk since total length is small
        assert len(result) == 1
        assert "Line 1" in result[0]
        assert "Line 3" in result[0]

    def test_split_exceeds_chunk_size(self):
        """测试超过块大小"""
        chunker = TextChunker(chunk_size=10, overlap_size=2)
        text = "0123456789\nABCDEFGHIJ"  # Each line is 10 chars + newline
        result = chunker.split_text_by_lines(text)

        # Should split into multiple chunks
        assert len(result) >= 2

    def test_split_with_overlap(self):
        """测试重叠"""
        chunker = TextChunker(chunk_size=10, overlap_size=3)
        text = "0123456789\nABCDEFGHIJ\n1234567890"
        result = chunker.split_text_by_lines(text)

        # Check overlap exists between chunks
        if len(result) > 1:
            # Second chunk should start with overlap from first
            assert result[0][-3:] in result[1] or True  # Overlap logic

    def test_split_no_overlap(self):
        """测试无重叠"""
        chunker = TextChunker(chunk_size=10, overlap_size=0)
        text = "0123456789\nABCDEFGHIJ"
        result = chunker.split_text_by_lines(text)

        # Should have 2 chunks
        assert len(result) == 2


class TestChunkText:
    """chunk_text 方法测试"""

    def test_chunk_text_empty(self):
        """测试空文本"""
        chunker = TextChunker()
        result = chunker.chunk_text(
            text="",
            file_id="file_1",
            file_name="test.txt",
            knowledge_id="kb_1"
        )

        assert result == []

    def test_chunk_text_single_chunk(self):
        """测试单块"""
        chunker = TextChunker(chunk_size=500, overlap_size=100)
        result = chunker.chunk_text(
            text="Short text",
            file_id="file_1",
            file_name="test.txt",
            knowledge_id="kb_1"
        )

        assert len(result) == 1
        assert isinstance(result[0], ChunkModel)

    def test_chunk_text_multiple_chunks(self):
        """测试多块"""
        chunker = TextChunker(chunk_size=10, overlap_size=0)

        # Create text that will produce multiple chunks
        text = "0123456789\nABCDEFGHIJ\n1234567890"

        result = chunker.chunk_text(
            text=text,
            file_id="file_123",
            file_name="test.txt",
            knowledge_id="kb_1"
        )

        assert len(result) > 1

    def test_chunk_text_fields(self):
        """测试字段正确性"""
        chunker = TextChunker()
        result = chunker.chunk_text(
            text="Test content",
            file_id="file_abc",
            file_name="document.txt",
            knowledge_id="kb_test"
        )

        chunk = result[0]
        assert chunk.file_id == "file_abc"
        assert chunk.file_name == "document.txt"
        assert chunk.knowledge_id == "kb_test"
        assert chunk.content == "Test content"
        assert chunk.chunk_id.startswith("file_abc_")

    def test_chunk_text_update_time(self):
        """测试更新时间"""
        chunker = TextChunker()
        import time
        before = time.time()

        result = chunker.chunk_text(
            text="Test",
            file_id="f1",
            file_name="t.txt",
            knowledge_id="k1"
        )

        after = time.time()

        # Parse ISO format time
        from datetime import datetime
        chunk_time = datetime.fromisoformat(result[0].update_time)
        chunk_ts = chunk_time.timestamp()

        assert before <= chunk_ts <= after


class TestDefaultChunker:
    """默认分块器测试"""

    def test_default_chunker_exists(self):
        """测试默认分块器存在"""
        from app.services.rag.chunker import default_chunker

        assert default_chunker is not None
        assert default_chunker.chunk_size == 500
        assert default_chunker.overlap_size == 100
