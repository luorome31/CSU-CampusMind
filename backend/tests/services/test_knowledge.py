"""
Knowledge Service 测试 - 使用内存 SQLite 进行集成测试
"""
import pytest
import os
import tempfile
from sqlmodel import SQLModel, create_engine
from unittest.mock import patch


# 创建临时数据库
@pytest.fixture(scope="function")
def test_db():
    """创建临时测试数据库"""
    # 使用临时文件
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # 创建内存引擎并连接到临时文件
    engine = create_engine(f"sqlite:///{path}", echo=False)

    # 创建表
    SQLModel.metadata.create_all(engine)

    yield engine

    # 清理
    os.unlink(path)


class TestKnowledgeServiceIntegration:
    """KnowledgeService 集成测试 - 使用真实数据库"""

    def test_create_and_get_knowledge(self, test_db):
        """测试创建和获取知识库"""
        from app.services.knowledge.knowledge import KnowledgeService

        # 使用测试数据库引擎
        with patch('app.services.knowledge.knowledge.engine', test_db):
            # 创建
            kb = KnowledgeService.create_knowledge(
                name="Test KB",
                user_id="user_1",
                description="Test description"
            )

            assert kb.id.startswith("t_")
            assert kb.name == "Test KB"

            # 获取
            retrieved = KnowledgeService.get_knowledge(kb.id)
            assert retrieved is not None
            assert retrieved.name == "Test KB"

    def test_list_knowledge_by_user(self, test_db):
        """测试列出用户知识库"""
        from app.services.knowledge.knowledge import KnowledgeService

        with patch('app.services.knowledge.knowledge.engine', test_db):
            # 创建两个知识库
            _ = KnowledgeService.create_knowledge(name="KB1", user_id="user_1")
            _ = KnowledgeService.create_knowledge(name="KB2", user_id="user_1")
            _ = KnowledgeService.create_knowledge(name="KB3", user_id="user_2")

            # 列出 user_1 的知识库
            user1_kbs = KnowledgeService.list_knowledge_by_user("user_1")
            assert len(user1_kbs) == 2

            # 列出 user_2 的知识库
            user2_kbs = KnowledgeService.list_knowledge_by_user("user_2")
            assert len(user2_kbs) == 1

    def test_delete_knowledge(self, test_db):
        """测试删除知识库"""
        from app.services.knowledge.knowledge import KnowledgeService

        with patch('app.services.knowledge.knowledge.engine', test_db):
            # 创建
            kb = KnowledgeService.create_knowledge(name="To Delete", user_id="user_1")

            # 删除
            result = KnowledgeService.delete_knowledge(kb.id)
            assert result is True

            # 验证删除
            retrieved = KnowledgeService.get_knowledge(kb.id)
            assert retrieved is None

    def test_delete_nonexistent_knowledge(self, test_db):
        """测试删除不存在的知识库"""
        from app.services.knowledge.knowledge import KnowledgeService

        with patch('app.services.knowledge.knowledge.engine', test_db):
            result = KnowledgeService.delete_knowledge("nonexistent")
            assert result is False
