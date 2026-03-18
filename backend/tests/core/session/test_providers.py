# backend/tests/core/session/test_providers.py
import pytest
from unittest.mock import Mock, MagicMock
from app.core.session.providers.base import SubsystemSessionProvider


class TestSubsystemSessionProvider:
    """测试 SubsystemSessionProvider 基类"""

    def test_registry_starts_empty(self):
        """注册表初始为空"""
        # 创建一个临时子类验证注册机制
        class DummyProvider(SubsystemSessionProvider, subsystem_name="dummy"):
            def fetch_session(self, castgc):
                return Mock()

        assert "dummy" in SubsystemSessionProvider._registry
        provider = SubsystemSessionProvider.get_provider("dummy")
        assert isinstance(provider, DummyProvider)

    def test_get_unknown_provider_raises(self):
        """获取未注册的 provider 抛出异常"""
        with pytest.raises(ValueError) as exc_info:
            SubsystemSessionProvider.get_provider("unknown")
        assert "unknown" in str(exc_info.value)

    def test_list_registered_providers(self):
        """列出已注册的 providers"""
        class AnotherProvider(SubsystemSessionProvider, subsystem_name="another"):
            def fetch_session(self, castgc):
                return Mock()

        providers = SubsystemSessionProvider.list_registered_providers()
        assert "dummy" in providers
        assert "another" in providers
