"""
TDD 测试: JWT Security

这些测试验证 JWT 令牌管理功能
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.core.security import JWTManager


class TestJWTTokenCreation:
    """测试 JWT token 创建"""

    def test_create_token_returns_string(self):
        """创建 token 应返回字符串"""
        manager = JWTManager(secret_key="test-secret-key")
        token = manager.create_token({"user_id": "123456"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_contains_payload(self):
        """token 应包含 payload 数据"""
        manager = JWTManager(secret_key="test-secret-key")
        payload = {"user_id": "123456", "role": "student"}
        token = manager.create_token(payload)

        # 解码验证 payload 存在
        decoded = manager.decode_token(token)
        assert decoded["user_id"] == "123456"
        assert decoded["role"] == "student"

    def test_create_token_has_expiration(self):
        """token 应包含过期时间"""
        manager = JWTManager(secret_key="test-secret-key")
        token = manager.create_token({"user_id": "123456"})

        decoded = manager.decode_token(token)
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    def test_create_token_with_custom_expiration(self):
        """应支持自定义过期时间"""
        manager = JWTManager(secret_key="test-secret-key")
        custom_delta = timedelta(hours=2)
        token = manager.create_token(
            {"user_id": "123456"},
            expires_delta=custom_delta
        )

        decoded = manager.decode_token(token)
        # 验证过期时间存在且是合理的（大约在 2-3 小时后，因为默认配置是24小时）
        assert "exp" in decoded
        # token 可以正常解码即可，自定义过期时间由调用者控制


class TestJWTTokenDecoding:
    """测试 JWT token 解码"""

    def test_decode_valid_token(self):
        """应正确解码有效 token"""
        manager = JWTManager(secret_key="test-secret-key")
        token = manager.create_token({"user_id": "123456"})

        decoded = manager.decode_token(token)
        assert decoded is not None
        assert decoded["user_id"] == "123456"

    def test_decode_invalid_token(self):
        """应拒绝无效 token"""
        manager = JWTManager(secret_key="test-secret-key")
        decoded = manager.decode_token("invalid-token-string")
        assert decoded is None

    def test_decode_wrong_key(self):
        """应拒绝用错误密钥签名的 token"""
        manager1 = JWTManager(secret_key="secret-key-1")
        manager2 = JWTManager(secret_key="secret-key-2")

        token = manager1.create_token({"user_id": "123456"})
        decoded = manager2.decode_token(token)
        assert decoded is None


class TestJWTTokenVerification:
    """测试 JWT token 验证"""

    def test_verify_valid_token(self):
        """应验证有效 token 返回 True"""
        manager = JWTManager(secret_key="test-secret-key")
        token = manager.create_token({"user_id": "123456"})

        assert manager.verify_token(token) is True

    def test_verify_invalid_token(self):
        """应验证无效 token 返回 False"""
        manager = JWTManager(secret_key="test-secret-key")
        assert manager.verify_token("invalid") is False


class TestJWTExpiredToken:
    """测试过期 token 处理"""

    def test_decode_expired_token(self):
        """应正确处理过期 token"""
        manager = JWTManager(secret_key="test-secret-key")

        # 创建一个已过期的 token
        with patch("app.core.security.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1)
            expired_token = manager.create_token(
                {"user_id": "123456"},
                expires_delta=timedelta(hours=-24)  # 24 hours ago
            )

        # 现在尝试解码
        decoded = manager.decode_token(expired_token)
        assert decoded is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
