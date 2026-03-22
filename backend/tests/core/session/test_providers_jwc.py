# backend/tests/core/session/test_providers_jwc.py
from unittest.mock import Mock, patch, MagicMock
from app.core.session.providers.jwc import JWCSessionProvider


class TestJWCSessionProvider:
    """测试 JWCSessionProvider"""

    def test_provider_registered(self):
        """JWC Provider 已自动注册"""
        from app.core.session.providers.base import SubsystemSessionProvider
        assert "jwc" in SubsystemSessionProvider._registry

    def test_fetch_session_sets_castgc(self):
        """fetch_session 应设置 CASTGC cookie"""
        with patch("app.core.session.providers.jwc.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.cookies.set = Mock()
            mock_session.get = Mock()
            mock_session.headers = {}
            mock_create.return_value = mock_session

            provider = JWCSessionProvider()
            provider.fetch_session("test_castgc_value")

            mock_session.cookies.set.assert_called_once_with(
                "CASTGC", "test_castgc_value", domain="ca.csu.edu.cn"
            )

    def test_fetch_session_returns_session(self):
        """fetch_session 应返回 session 对象"""
        with patch("app.core.session.providers.jwc.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.get = Mock(return_value=MagicMock(
                headers={"Location": ""},
                url="http://csujwc.its.csu.edu.cn/"
            ))
            mock_session.cookies.set = Mock()
            mock_create.return_value = mock_session

            provider = JWCSessionProvider()
            result = provider.fetch_session("test_castgc")

            assert result == mock_session
