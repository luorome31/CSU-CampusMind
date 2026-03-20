import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestAuthAutoCreateUser:
    """测试 CAS 登录时自动创建用户"""

    @pytest.mark.asyncio
    async def test_ensure_user_exists_creates_new_user(self):
        """新用户登录时应创建用户记录"""
        with patch("app.api.v1.auth.async_session_dependency") as mock_session_dep:
            mock_session = AsyncMock()
            mock_session.get = AsyncMock(return_value=None)  # 用户不存在
            mock_session.commit = AsyncMock()
            mock_session_dep.return_value = mock_session

            from app.api.v1.auth import _ensure_user_exists
            await _ensure_user_exists("student123")

            # 验证用户被添加和提交
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_user_exists_skips_existing(self):
        """已存在用户不应重复创建"""
        with patch("app.api.v1.auth.async_session_dependency") as mock_session_dep:
            mock_session = AsyncMock()
            existing_user = MagicMock()
            mock_session.get = AsyncMock(return_value=existing_user)  # 用户已存在
            mock_session_dep.return_value = mock_session

            from app.api.v1.auth import _ensure_user_exists
            await _ensure_user_exists("student123")

            # 验证用户未被添加
            mock_session.add.assert_not_called()
