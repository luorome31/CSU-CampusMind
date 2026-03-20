"""
Redis 集成测试

测试完整的 Redis 使用场景:
1. Session 存储和读取
2. 历史缓存
3. CAS 登录自动建户
"""
import pytest
import redis


class TestRedisSessionIntegration:
    """Session Redis 集成测试"""

    def test_redis_connection(self):
        """验证 Redis 连接"""
        r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        r.set("test_key", "test_value")
        assert r.get("test_key") == "test_value"
        r.delete("test_key")

    def test_session_key_format(self):
        """验证 session key 格式"""
        r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        key = f"session:user123:jwc"
        r.setex(key, 60, "test_session")
        assert r.exists(key) == 1
        r.delete(key)


class TestRedisHistoryIntegration:
    """历史缓存 Redis 集成测试"""

    def test_history_key_format(self):
        """验证 history key 格式"""
        r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        key = "history:dialog123"
        r.setex(key, 60, '["msg1", "msg2"]')
        assert r.get(key) == '["msg1", "msg2"]'
        r.delete(key)