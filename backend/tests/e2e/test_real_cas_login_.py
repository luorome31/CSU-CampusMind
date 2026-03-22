"""
真实 CAS 登录测试脚本

用法:
    cd /home/luorome/software/CampusMind/backend
    uv run python scripts/test_real_cas_login.py

注意: 需要在 .env 中配置 CAS_USERNAME 和 CAS_PASSWORD
"""
import pytest

# Skip all tests in this file - this is a manual script, not a pytest test
pytestmark = pytest.mark.skip(reason="Manual script, not a pytest test")

import os
import sys
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()

# 添加 backend 目录到 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 获取凭证
CAS_USERNAME = os.getenv("CAS_USERNAME")
CAS_PASSWORD = os.getenv("CAS_PASSWORD")

if not CAS_USERNAME or not CAS_PASSWORD:
    print("错误: 请在 .env 中配置 CAS_USERNAME 和 CAS_PASSWORD")
    sys.exit(1)

print(f"使用账号: {CAS_USERNAME}")
print("-" * 50)


def test_cas_login_only_castgc():
    """测试 cas_login_only_castgc 函数"""
    print("\n[测试 1] 测试 cas_login_only_castgc...")
    from app.core.session import cas_login

    try:
        castgc = cas_login.cas_login_only_castgc(CAS_USERNAME, CAS_PASSWORD)
        print(f"  ✓ 成功获取 CASTGC: {castgc[:30]}...")
        return castgc
    except Exception as e:
        print(f"  ✗ 获取 CASTGC 失败: {e}")
        return None


def test_jwc_provider(castgc: str):
    """测试 JWCSessionProvider"""
    print("\n[测试 2] 测试 JWCSessionProvider...")
    from app.core.session.providers.jwc import JWCSessionProvider

    try:
        provider = JWCSessionProvider()
        session = provider.fetch_session(castgc)
        cookies = {c.name: c.value for c in session.cookies}
        print("  ✓ JWC Session 获取成功")
        print(f"    Cookies: {list(cookies.keys())}")
        return session
    except Exception as e:
        print(f"  ✗ JWC Session 获取失败: {e}")
        return None


def test_manager_login():
    """测试 UnifiedSessionManager.login()"""
    print("\n[测试 3] 测试 UnifiedSessionManager.login()...")
    from app.core.session.manager import UnifiedSessionManager
    from app.core.session.persistence import FileSessionPersistence
    from app.core.session.rate_limiter import LoginRateLimiter
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = FileSessionPersistence(storage_path=os.path.join(tmpdir, "sessions.json"))
        rate_limiter = LoginRateLimiter()
        manager = UnifiedSessionManager(persistence=persistence, rate_limiter=rate_limiter)

        try:
            manager.login(CAS_USERNAME, CAS_USERNAME, CAS_PASSWORD)
            castgc = manager._get_castgc(CAS_USERNAME)
            print("  ✓ Manager.login() 成功")
            print(f"  ✓ CASTGC 已缓存: {castgc[:30]}...")
            return manager
        except Exception as e:
            print(f"  ✗ Manager.login() 失败: {e}")
            return None


def test_get_session(manager):
    """测试通过 Provider 获取 JWC session"""
    print("\n[测试 4] 测试 get_session (通过 CASTGC 获取 JWC)...")

    try:
        session = manager.get_session(CAS_USERNAME, "jwc")
        cookies = {c.name: c.value for c in session.cookies}
        print("  ✓ get_session 成功")
        print(f"    Cookies: {list(cookies.keys())}")
        return session
    except Exception as e:
        print(f"  ✗ get_session 失败: {e}")
        return None


def test_jwt_token():
    """测试 JWT token 生成和验证"""
    print("\n[测试 5] 测试 JWT Token...")
    from app.core.security import jwt_manager

    try:
        # 创建 token
        token = jwt_manager.create_token({"user_id": CAS_USERNAME})
        print(f"  ✓ Token 创建成功: {token[:50]}...")

        # 验证 token
        payload = jwt_manager.decode_token(token)
        print("  ✓ Token 验证成功")
        print(f"    Payload: {payload}")

        # 验证 token 有效
        is_valid = jwt_manager.verify_token(token)
        print(f"  ✓ Token verify: {is_valid}")

        return token
    except Exception as e:
        print(f"  ✗ JWT 测试失败: {e}")
        return None


def main():
    print("=" * 50)
    print("CAS 登录真实环境测试")
    print("=" * 50)

    results = {}

    # 测试 1: CAS 登录获取 CASTGC
    castgc = test_cas_login_only_castgc()
    results["cas_login"] = castgc is not None

    if not castgc:
        print("\n⚠️  CAS 登录失败，后续测试跳过")
        print_summary(results)
        return 1

    # 测试 2: JWC Provider
    jwc_session = test_jwc_provider(castgc)
    results["jwc_provider"] = jwc_session is not None

    # 测试 3: Manager login
    manager = test_manager_login()
    results["manager_login"] = manager is not None

    if manager:
        # 测试 4: get_session
        session = test_get_session(manager)
        results["get_session"] = session is not None

    # 测试 5: JWT
    token = test_jwt_token()
    results["jwt"] = token is not None

    print_summary(results)
    return 0


def print_summary(results):
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
    passed = sum(results.values())
    total = len(results)
    print(f"\n通过: {passed}/{total}")
    return passed == total


if __name__ == "__main__":
    sys.exit(main())
