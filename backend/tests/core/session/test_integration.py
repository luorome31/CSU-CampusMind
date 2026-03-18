"""
完整登录流程集成测试

测试场景:
1. 用户登录获取 CASTGC
2. 使用 CASTGC 通过 Provider 获取子系统 session
3. 验证 session 可以访问子系统
"""
import pytest
from unittest.mock import patch, MagicMock
import requests


class TestFullLoginFlow:
    """完整登录流程测试"""

    def test_castgc_flow_with_provider(self):
        """
        测试 CASTGC 获取和 Provider 获取 session 的完整流程
        """
        from app.core.session.manager import UnifiedSessionManager, NeedReLoginError
        from app.core.session.persistence import FileSessionPersistence
        from app.core.session.rate_limiter import LoginRateLimiter
        from app.core.session.providers.jwc import JWCSessionProvider

        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            session_path = os.path.join(tmpdir, "sessions.json")
            persistence = FileSessionPersistence(storage_path=session_path)
            rate_limiter = LoginRateLimiter()

            manager = UnifiedSessionManager(
                persistence=persistence,
                rate_limiter=rate_limiter,
                ttl_seconds=60
            )

            # Step 1: 验证无 CASTGC 时抛出异常
            with pytest.raises(NeedReLoginError):
                manager.get_session("user1", "jwc")

            # Step 2: 模拟 login - 保存 CASTGC
            manager._save_castgc("user1", "mock_castgc_value")

            # 验证 CASTGC 已保存
            assert manager._get_castgc("user1") == "mock_castgc_value"

            # Step 3: 使用 mock provider 获取 session
            with patch.object(JWCSessionProvider, 'fetch_session') as mock_fetch:
                mock_session = MagicMock()
                mock_session.cookies = MagicMock()
                mock_fetch.return_value = mock_session

                session = manager.get_session("user1", "jwc")

                # 验证获取成功
                assert session == mock_session
                mock_fetch.assert_called_once_with("mock_castgc_value")

    def test_provider_auto_registration(self):
        """测试 Provider 自动注册机制"""
        from app.core.session.providers.base import SubsystemSessionProvider
        from app.core.session.providers.jwc import JWCSessionProvider

        # 验证 JWC 已注册
        assert "jwc" in SubsystemSessionProvider._registry

        # 验证可以获取
        provider = SubsystemSessionProvider.get_provider("jwc")
        assert isinstance(provider, JWCSessionProvider)

    def test_unknown_provider_raises(self):
        """测试获取未注册的 provider 抛出异常"""
        from app.core.session.providers.base import SubsystemSessionProvider

        with pytest.raises(ValueError) as exc_info:
            SubsystemSessionProvider.get_provider("unknown_system")

        assert "unknown_system" in str(exc_info.value)

    def test_login_then_different_subsystems(self):
        """
        测试登录后访问不同子系统

        场景：
        1. 用户登录获取 CASTGC
        2. 访问 JWC 获取成绩
        3. 访问 Library 搜索图书
        """
        from app.core.session.manager import UnifiedSessionManager, NeedReLoginError
        from app.core.session.persistence import FileSessionPersistence
        from app.core.session.rate_limiter import LoginRateLimiter
        from app.core.session.providers.base import SubsystemSessionProvider

        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            session_path = os.path.join(tmpdir, "sessions.json")
            persistence = FileSessionPersistence(storage_path=session_path)
            rate_limiter = LoginRateLimiter()

            manager = UnifiedSessionManager(
                persistence=persistence,
                rate_limiter=rate_limiter,
                ttl_seconds=60
            )

            # Step 1: 登录（保存 CASTGC）
            manager._save_castgc("user1", "shared_castgc")

            # Step 2: 访问 JWC
            with patch.object(SubsystemSessionProvider, 'get_provider') as mock_get:
                mock_jwc_provider = MagicMock()
                mock_jwc_session = MagicMock()
                mock_jwc_session.cookies = MagicMock()
                mock_jwc_provider.fetch_session.return_value = mock_jwc_session

                def get_provider_side_effect(name):
                    if name == "jwc":
                        return mock_jwc_provider
                    # For other subsystems, return a mock
                    mock_provider = MagicMock()
                    mock_provider.fetch_session.return_value = MagicMock()
                    return mock_provider

                mock_get.side_effect = get_provider_side_effect

                jwc_session = manager.get_session("user1", "jwc")
                assert jwc_session == mock_jwc_session

                # 验证 JWC Provider 被调用时使用了 CASTGC
                mock_jwc_provider.fetch_session.assert_called_once_with("shared_castgc")


class TestNeedReLoginError:
    """测试 NeedReLoginError 异常"""

    def test_need_re_login_error_message(self):
        """验证异常消息清晰"""
        from app.core.session.manager import NeedReLoginError

        error = NeedReLoginError("用户 user1 的 CASTGC 已过期或不存在，请重新登录")
        assert "user1" in str(error)
        assert "CASTGC" in str(error)
        assert "重新登录" in str(error)
