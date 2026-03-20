"""
E2E 测试：真实调用 CAS 和教务系统

⚠️ 警告：此测试会真实调用外部系统
- 需要有效的 CAS 账号
- 会执行 CAS 登录操作
- 可能触发登录频率限制（建议测试间隔 > 5 分钟）

运行方式：
    # 跳过测试
    uv run pytest tests/core/test_jwc_e2e.py -v -k "not test_e2e"

    # 运行 E2E 测试（需要配置 .env）
    uv run pytest tests/core/test_jwc_e2e.py -v -k "test_e2e"
"""
import pytest
import os
import time
from unittest.mock import MagicMock
from app.config import settings
from app.core.session import UnifiedSessionManager, FileSessionPersistence, LoginRateLimiter


# 跳过所有测试如果没有配置 CAS 凭证
# Also mark as async since get_jwc_session is now async
# Note: e2e tests require Redis for CASTGC caching
pytestmark = [
    pytest.mark.skipif(
        not settings.cas_username or not settings.cas_password,
        reason="CAS credentials not configured in .env"
    ),
    pytest.mark.asyncio
]


def pytest_runtest_setup(item):
    """Skip e2e tests if Redis is not initialized."""
    if "e2e" in item.nodeid.lower():
        try:
            from app.core.session.redis_client import get_redis
            get_redis()
        except RuntimeError:
            pytest.skip("Redis not initialized")


@pytest.fixture
def session_manager(tmp_path):
    """创建 SessionManager 实例"""
    session_path = tmp_path / "sessions.json"
    persistence = FileSessionPersistence(storage_path=str(session_path))
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # Mock persistence.load to return a coroutine that yields None
    # This allows the code to proceed to CAS login (since no stored session exists)
    async def mock_load(*args, **kwargs):
        return None
    manager._persistence.load = mock_load

    # Mock persistence._redis for CASTGC operations
    # Create a mock Redis that stores data in memory
    castgc_store = {}
    mock_redis = MagicMock()

    async def mock_redis_get(key):
        return castgc_store.get(key)

    async def mock_redis_setex(key, ttl, value):
        castgc_store[key] = value

    async def mock_redis_delete(key):
        castgc_store.pop(key, None)

    mock_redis.get = mock_redis_get
    mock_redis.setex = mock_redis_setex
    mock_redis.delete = mock_redis_delete
    manager._persistence._redis = mock_redis

    return manager


class TestJwcE2E:
    """教务系统 E2E 测试"""

    async def test_e2e_get_jwc_session(self, session_manager):
        """测试获取教务系统 Session"""
        print(f"\n尝试使用账号 {settings.cas_username} 登录教务系统...")

        # 首次调用会执行 CAS 登录
        session = await session_manager.get_jwc_session(settings.cas_username)

        assert session is not None
        assert len(session.cookies) > 0

        print(f"✓ 登录成功，Cookies: {dict(session.cookies)}")

    async def test_e2e_cache_session(self, session_manager):
        """测试 Session 缓存"""
        print(f"\n测试 Session 缓存...")

        # 第一次获取
        session1 = await session_manager.get_jwc_session(settings.cas_username)

        # 第二次获取应该从缓存
        session2 = await session_manager.get_jwc_session(settings.cas_username)

        # 应该是同一个 Session 对象
        assert session1 is session2

        print("✓ Session 缓存正常")

    async def test_e2e_query_grades(self, session_manager):
        """测试查询成绩（真实网络请求）"""
        print(f"\n尝试查询成绩...")

        from app.core.tools.jwc import JwcService

        service = JwcService(session_manager)

        try:
            # 尝试查询成绩（不指定学期，查全部）
            grades = await service.get_grades(settings.cas_username, "")

            if grades:
                print(f"✓ 查询到 {len(grades)} 条成绩记录")
                for g in grades[:3]:  # 只打印前3条
                    print(f"  {g.term} | {g.course_name} | {g.score}分")
            else:
                print("⚠ 未查询到成绩记录（可能暂无数据）")

        except Exception as e:
            if "Cookie 已失效" in str(e):
                print(f"⚠ Session 失效，需要重新登录: {e}")
                # 清除缓存重试
                await session_manager.invalidate_session(settings.cas_username)
                pytest.skip("Session 失效，跳过测试")
            else:
                raise


class TestJwcSessionPersistenceE2E:
    """Session 持久化 E2E 测试"""

    async def test_e2e_persistence(self, tmp_path):
        """测试 Session 持久化"""
        print(f"\n测试 Session 持久化...")

        session_path = tmp_path / "sessions_e2e.json"

        # 第一次：登录并保存
        persistence1 = FileSessionPersistence(storage_path=str(session_path))
        rate_limiter = LoginRateLimiter()
        manager1 = UnifiedSessionManager(
            persistence=persistence1,
            rate_limiter=rate_limiter,
            ttl_seconds=60
        )

        session1 = await manager1.get_jwc_session(settings.cas_username)
        print(f"✓ 第一次登录成功")

        # 第二次：从文件加载
        persistence2 = FileSessionPersistence(storage_path=str(session_path))
        manager2 = UnifiedSessionManager(
            persistence=persistence2,
            rate_limiter=LoginRateLimiter(),
            ttl_seconds=60
        )

        # 不需要再次登录
        session2 = await manager2.get_jwc_session(settings.cas_username)
        print(f"✓ 第二次从文件加载成功")

        # 验证是同一个 Session
        cookies1 = dict(session1.cookies)
        cookies2 = dict(session2.cookies)

        assert cookies1.get("JSESSIONID") == cookies2.get("JSESSIONID")
        print(f"✓ Session 一致")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║           教务系统 E2E 测试                              ║
╠══════════════════════════════════════════════════════════╣
║  ⚠️  警告：此测试会真实调用 CAS 和教务系统               ║
║                                                          ║
║  运行前请确保：                                          ║
║  1. 已在 .env 中配置 CAS_USERNAME 和 CAS_PASSWORD        ║
║  2. 网络可以访问 csujwc.its.csu.edu.cn                   ║
║  3. 测试间隔 > 5 分钟（避免登录频率限制）                ║
╚══════════════════════════════════════════════════════════╝
    """)

    pytest.main([__file__, "-v", "-s"])
