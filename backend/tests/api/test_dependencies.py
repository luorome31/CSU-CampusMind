"""
TDD 测试: Auth Dependencies

这些测试验证 API 认证依赖注入功能
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.api.dependencies import get_current_user, get_optional_user


class TestGetCurrentUser:
    """测试必需认证的依赖"""

    @pytest.mark.asyncio
    async def test_decode_valid_token(self):
        """有效 token 应返回用户信息"""
        # 模拟 JWT 解码结果
        with patch("app.api.dependencies.jwt_manager") as mock_jwt:
            mock_jwt.decode_token.return_value = {"user_id": "123456"}

            # 模拟 FastAPI 依赖
            mock_credentials = Mock()
            mock_credentials.credentials = "valid-token"

            # 调用依赖
            result = await get_current_user(mock_credentials)

            assert result == {"user_id": "123456"}
            mock_jwt.decode_token.assert_called_once_with("valid-token")

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        """无效 token 应抛出 401 错误"""
        with patch("app.api.dependencies.jwt_manager") as mock_jwt:
            mock_jwt.decode_token.return_value = None

            mock_credentials = Mock()
            mock_credentials.credentials = "invalid-token"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self):
        """过期 token 应抛出 401 错误"""
        with patch("app.api.dependencies.jwt_manager") as mock_jwt:
            mock_jwt.decode_token.return_value = None  # 过期返回 None

            mock_credentials = Mock()
            mock_credentials.credentials = "expired-token"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == 401
            assert "重新登录" in exc_info.value.detail


class TestGetOptionalUser:
    """测试可选认证的依赖"""

    @pytest.mark.asyncio
    async def test_with_valid_token(self):
        """有效 token 应返回用户信息"""
        with patch("app.api.dependencies.jwt_manager") as mock_jwt:
            mock_jwt.decode_token.return_value = {"user_id": "123456"}

            mock_credentials = Mock()
            mock_credentials.credentials = "valid-token"

            result = await get_optional_user(mock_credentials)

            assert result == {"user_id": "123456"}

    @pytest.mark.asyncio
    async def test_without_credentials(self):
        """无 credentials 应返回 None"""
        result = await get_optional_user(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_token_returns_none(self):
        """无效 token 应返回 None（不抛出异常）"""
        with patch("app.api.dependencies.jwt_manager") as mock_jwt:
            mock_jwt.decode_token.return_value = None

            mock_credentials = Mock()
            mock_credentials.credentials = "invalid-token"

            result = await get_optional_user(mock_credentials)

            assert result is None


class TestSecurityScheme:
    """测试安全方案配置"""

    def test_bearer_auth_required_for_current_user(self):
        """get_current_user 需要 Bearer token"""
        # 验证 HTTPBearer 被正确使用
        from app.api.dependencies import security
        from fastapi.security import HTTPBearer

        assert isinstance(security, HTTPBearer)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
