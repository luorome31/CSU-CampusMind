import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from app.core.session.redis_persistence import RedisSessionPersistence


class TestRedisSessionPersistence:
    """测试 RedisSessionPersistence"""

    @pytest.fixture
    def mock_redis(self):
        with patch("app.core.session.redis_persistence.redis") as mock:
            yield mock

    def test_key_format(self, mock_redis):
        """验证 key 格式"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis
        key = impl._key("user123", "jwc")
        assert key == "session:user123:jwc"

    def test_save_serializes_cookies(self, mock_redis):
        """save 应正确序列化 cookies"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis

        mock_cookie = MagicMock()
        mock_cookie.name = "CASTGC"
        mock_cookie.value = "abc123"
        mock_cookie.domain = "ca.csu.edu.cn"
        mock_cookie.path = "/"
        mock_cookie.secure = True

        mock_session = MagicMock()
        mock_session.cookies = [mock_cookie]

        impl.save("user123", "jwc", mock_session, 1800)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "session:user123:jwc"
        assert call_args[0][1] == 1800

    def test_load_returns_session(self, mock_redis):
        """load 应返回重建的 session"""
        with patch("app.core.session.redis_persistence.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
            impl._redis = mock_redis

            import json
            mock_redis.get.return_value = json.dumps({
                "cookies": {"CASTGC": {"value": "abc123", "domain": "ca.csu.edu.cn"}},
                "saved_at": 1234567890.0
            })

            result = impl.load("user123", "jwc")

            assert result is not None
            mock_session.cookies.set.assert_called_once_with("CASTGC", "abc123", domain="ca.csu.edu.cn", path="/", secure=False)

    def test_load_returns_none_when_missing(self, mock_redis):
        """key 不存在时返回 None"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis
        mock_redis.get.return_value = None

        result = impl.load("user123", "jwc")

        assert result is None

    def test_invalidate_deletes_key(self, mock_redis):
        """invalidate 应删除指定 key"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis

        impl.invalidate("user123", "jwc")

        mock_redis.delete.assert_called_once_with("session:user123:jwc")

    def test_invalidate_all_deletes_user_keys(self, mock_redis):
        """subsystem=None 时删除用户所有 session keys"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis
        mock_redis.keys.return_value = ["session:user123:jwc", "session:user123:library"]

        impl.invalidate("user123")

        mock_redis.keys.assert_called_once_with("session:user123:*")
        mock_redis.delete.assert_called_once()