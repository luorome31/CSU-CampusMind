"""
Knowledge File Service 测试 - 使用内存 SQLite 进行集成测试
"""
import pytest
import os
import tempfile
from sqlmodel import SQLModel, create_engine


@pytest.fixture(scope="function")
def test_db():
    """创建临时测试数据库"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    engine = create_engine(f"sqlite:///{path}", echo=False)

    # 创建表
    SQLModel.metadata.create_all(engine)

    yield engine

    os.unlink(path)


class TestKnowledgeFileServiceIntegration:
    """KnowledgeFileService 集成测试"""

    def test_create_and_get_file(self, test_db):
        """测试创建和获取文件"""
        from app.services.knowledge_file.knowledge_file import KnowledgeFileService

        with patch('app.services.knowledge_file.knowledge_file.engine', test_db):
            # 创建
            kf = KnowledgeFileService.create_knowledge_file(
                file_name="test.txt",
                knowledge_id="kb_1",
                user_id="user_1",
                oss_url="https://oss.example.com/test.txt",
                object_name="user_1/kb_1/test.txt",
                file_size=1024
            )

            assert kf.file_name == "test.txt"

            # 获取
            retrieved = KnowledgeFileService.get_knowledge_file(kf.id)
            assert retrieved is not None
            assert retrieved.file_name == "test.txt"

    def test_list_knowledge_files(self, test_db):
        """测试列出知识文件"""
        from app.services.knowledge_file.knowledge_file import KnowledgeFileService

        with patch('app.services.knowledge_file.knowledge_file.engine', test_db):
            # 创建多个文件
            _ = KnowledgeFileService.create_knowledge_file(
                file_name="file1.txt", knowledge_id="kb_1", user_id="user_1",
                oss_url="http://test.com/1", object_name="user_1/kb_1/file1.txt"
            )
            _ = KnowledgeFileService.create_knowledge_file(
                file_name="file2.txt", knowledge_id="kb_1", user_id="user_1",
                oss_url="http://test.com/2", object_name="user_1/kb_1/file2.txt"
            )
            _ = KnowledgeFileService.create_knowledge_file(
                file_name="file3.txt", knowledge_id="kb_2", user_id="user_1",
                oss_url="http://test.com/3", object_name="user_1/kb_2/file3.txt"
            )

            # 列出 kb_1 的文件
            files = KnowledgeFileService.list_knowledge_files("kb_1")
            assert len(files) == 2

    def test_update_file_status(self, test_db):
        """测试更新文件状态"""
        from app.services.knowledge_file.knowledge_file import KnowledgeFileService

        with patch('app.services.knowledge_file.knowledge_file.engine', test_db):
            # 创建
            kf = KnowledgeFileService.create_knowledge_file(
                file_name="test.txt", 
                knowledge_id="kb_1", 
                user_id="user_1",
                oss_url="http://test.com/test", 
                object_name="user_1/kb_1/test.txt"
            )

            # 更新状态
            result = KnowledgeFileService.update_file_status(kf.id, "success")
            assert result is True

            # 验证
            updated = KnowledgeFileService.get_knowledge_file(kf.id)
            assert updated.status == "success"

    def test_delete_file(self, test_db):
        """测试删除文件"""
        from app.services.knowledge_file.knowledge_file import KnowledgeFileService

        with patch('app.services.knowledge_file.knowledge_file.engine', test_db):
            kf = KnowledgeFileService.create_knowledge_file(
                file_name="test.txt", 
                knowledge_id="kb_1", 
                user_id="user_1",
                oss_url="http://test.com/test", 
                object_name="user_1/kb_1/test.txt"
            )

            result = KnowledgeFileService.delete_knowledge_file(kf.id)
            assert result is True

            retrieved = KnowledgeFileService.get_knowledge_file(kf.id)
            assert retrieved is None


# Helper for patching
from unittest.mock import patch
