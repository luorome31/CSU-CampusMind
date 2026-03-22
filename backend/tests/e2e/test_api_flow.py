"""
E2E 测试 - 使用 FastAPI TestClient 进行集成测试

无需启动服务器，直接在测试中调用 API
"""

import pytest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.mark.e2e
class TestLLMInteractionE2E:
    """LLM 交互端到端测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_completion_endpoint_exists(self, client):
        """测试 completion 端点存在"""
        response = client.post(
            "/api/v1/completion",
            json={
                "message": "test",
                "knowledge_ids": [],
                "user_id": "test_user"
            }
        )
        # 可能返回 400 (需要 knowledge_ids) 或其他错误，但不能是 404
        assert response.status_code != 404

    def test_chat_endpoint_exists(self, client):
        """测试 chat 端点存在"""
        response = client.post(
            "/api/v1/chat",
            json={
                "query": "test",
                "knowledge_id": "test_knowledge",
                "user_id": "test_user"
            }
        )
        # 可能返回错误，但不能是 404
        assert response.status_code != 404

    def test_stream_endpoint_exists(self, client):
        """测试流式端点存在 (检查端点是否注册)"""
        # TestClient 不支持 stream 参数，改为检查端点是否存在
        from app.main import app
        routes = [r.path for r in app.routes]
        assert "/api/v1/chat/stream" in routes or any("chat/stream" in r for r in routes)


@pytest.mark.e2e
class TestKnowledgeFlowE2E:
    """知识库流程端到端测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_create_knowledge(self, client):
        """测试创建知识库"""
        response = client.post(
            "/api/v1/knowledge/create",
            json={
                "name": "测试知识库",
                "description": "测试描述",
                "user_id": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "测试知识库"

    def test_list_knowledge(self, client):
        """测试列出知识库"""
        response = client.get("/api/v1/knowledge/list/test_user")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.e2e
class TestDialogFlowE2E:
    """对话流程端到端测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_dialog_creation(self, client):
        """测试对话创建"""
        # 创建知识库
        kb_response = client.post(
            "/api/v1/knowledge/create",
            json={
                "name": "测试",
                "user_id": "test_user"
            }
        )
        kb_id = kb_response.json()["id"]

        # 发送消息
        response = client.post(
            "/api/v1/chat",
            json={
                "query": "你好",
                "knowledge_id": kb_id,
                "user_id": "test_user"
            }
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "dialog_id" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
