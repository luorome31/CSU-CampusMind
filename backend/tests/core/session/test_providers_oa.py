# backend/tests/app/core/session/providers/test_oa.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.session.providers.oa import OASessionProvider


class TestOASessionProvider:
    """测试 OASessionProvider"""

    def test_provider_registered(self):
        """OA Provider 已自动注册"""
        from app.core.session.providers.base import SubsystemSessionProvider
        assert "oa" in SubsystemSessionProvider._registry

    def test_subsystem_name_is_oa(self):
        """subsystem_name 应为 'oa'"""
        from app.core.session.providers.base import SubsystemSessionProvider
        provider_class = SubsystemSessionProvider._registry.get("oa")
        assert provider_class is not None

    def test_fetch_session_creates_session(self):
        """fetch_session 应创建新 session"""
        with patch("app.core.session.providers.oa.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.cookies.set = Mock()
            mock_session.get = Mock(return_value=MagicMock(
                headers={},
                url="https://oa.csu.edu.cn/con/"
            ))
            mock_create.return_value = mock_session

            provider = OASessionProvider()
            provider.fetch_session("test_castgc")

            mock_create.assert_called_once()

    def test_fetch_session_sets_castgc(self):
        """fetch_session 应设置 CASTGC cookie"""
        with patch("app.core.session.providers.oa.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.cookies.set = Mock()
            mock_session.get = Mock(return_value=MagicMock(
                headers={},
                url="https://oa.csu.edu.cn/con/"
            ))
            mock_create.return_value = mock_session

            provider = OASessionProvider()
            provider.fetch_session("test_castgc_value")

            mock_session.cookies.set.assert_called_once_with(
                "CASTGC", "test_castgc_value", domain="ca.csu.edu.cn"
            )

    def test_fetch_session_first_request_to_oa(self):
        """fetch_session 第一步应请求 OA 页面获取 JSESSIONID"""
        with patch("app.core.session.providers.oa.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.cookies.set = Mock()
            mock_session.get = Mock(return_value=MagicMock(
                headers={},
                url="https://oa.csu.edu.cn/con/"
            ))
            mock_create.return_value = mock_session

            provider = OASessionProvider()
            provider.fetch_session("test_castgc")

            # Verify first call was to OA_SESSION_URL
            first_call_url = mock_session.get.call_args_list[0][0][0]
            assert "oa.csu.edu.cn/con/" in first_call_url

    def test_fetch_session_second_request_to_cas(self):
        """fetch_session 第二步应请求 CAS 登录 URL"""
        with patch("app.core.session.providers.oa.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.cookies.set = Mock()

            # First response: OA page
            # Second response: CAS redirect
            mock_session.get = Mock(side_effect=[
                MagicMock(headers={}, url="https://oa.csu.edu.cn/con/"),
                MagicMock(headers={"Location": "https://oa.csu.edu.cn/con//logincas?targetUrl=..."}, url="https://ca.csu.edu.cn/authserver/login?service=..."),
                MagicMock(headers={}, url="https://oa.csu.edu.cn/con//logincas?targetUrl=...")
            ])
            mock_create.return_value = mock_session

            provider = OASessionProvider()
            provider.fetch_session("test_castgc")

            # Verify CAS login URL was called
            cas_calls = [call for call in mock_session.get.call_args_list if "ca.csu.edu.cn" in str(call)]
            assert len(cas_calls) >= 1

    def test_fetch_session_returns_session(self):
        """fetch_session 应返回 session 对象"""
        with patch("app.core.session.providers.oa.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.cookies.set = Mock()
            mock_session.get = Mock(return_value=MagicMock(
                headers={},
                url="https://oa.csu.edu.cn/con/"
            ))
            mock_create.return_value = mock_session

            provider = OASessionProvider()
            result = provider.fetch_session("test_castgc")

            assert result == mock_session

    def test_cas_service_url_encoded(self):
        """CAS service URL 应该被正确编码"""
        provider = OASessionProvider()
        assert provider.CAS_SERVICE is not None
        assert "oa.csu.edu.cn" in provider.CAS_SERVICE
        # The service URL should be URL-encoded
        assert "%" in provider.CAS_SERVICE or "https%3A" in provider.CAS_SERVICE
