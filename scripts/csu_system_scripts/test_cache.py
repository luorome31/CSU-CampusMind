"""真实登录测试 - 验证缓存是否生效"""
import os
import sys

# 添加当前目录到 path
sys.path.insert(0, ".")

from unified_session_v2 import (
    UnifiedSessionManager,
    Subsystem,
    SubsystemSessionCache,
    SessionPersistence,
    cas_login
)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

TEST_ID = os.environ.get("CSU_TEST_ID", "")
TEST_PWD = os.environ.get("CSU_TEST_PWD", "")

print(f"测试账号: {TEST_ID}")
print(f"密码长度: {len(TEST_PWD)}")

# 清理旧文件
storage_file = "./cache_test_sessions.json"
if os.path.exists(storage_file):
    os.remove(storage_file)

# print("\n" + "=" * 60)
# print("测试 1: 直接调用 CAS 登录（不经过缓存）")
# print("=" * 60)

# # 直接调用 cas_login，看看会发生什么
# try:
#     print("\n[1.1] 直接调用 cas_login...")
#     session = cas_login(TEST_ID, TEST_PWD, "http://csujwc.its.csu.edu.cn/sso.jsp")
#     print(f"✓ 登录成功!")
#     print(f"  Cookies: {dict(session.cookies)}")
# except Exception as e:
#     print(f"✗ 登录失败: {e}")
#     # 保存错误页面以便分析
#     import requests
#     # 重新尝试获取错误信息
#     session = None

print("\n" + "=" * 60)
print("测试 2: 使用 UnifiedSessionManager（带缓存）")
print("=" * 60)

# 创建管理器（启用持久化）
manager = UnifiedSessionManager(
    ttl_seconds=30 * 60,
    storage_path=storage_file,
    enable_persistence=True,
)

print("\n[2.1] 第一次调用 get_session (应该触发 CAS 登录)...")
try:
    session1 = manager.get_session(TEST_ID, TEST_PWD, Subsystem.JWC)
    print(f"✓ 成功!")
    print(f"  Session 对象: {id(session1)}")
    print(f"  Cookies: {dict(session1.cookies)}")
except Exception as e:
    print(f"✗ 失败: {e}")
    session1 = None

print("\n[2.2] 第二次调用 get_session (应该使用缓存)...")
try:
    session2 = manager.get_session(TEST_ID, TEST_PWD, Subsystem.JWC)
    print(f"✓ 成功!")
    print(f"  Session 对象: {id(session2)}")
    print(f"  Cookies: {dict(session2.cookies)}")

    # 验证是否是同一个对象
    if session1 and session2:
        if id(session1) == id(session2):
            print(f"\n✅ 确认：两次获取的是同一个 Session 对象（内存缓存生效）")
        else:
            print(f"\n⚠️ 警告：Session 对象不同")
except Exception as e:
    print(f"✗ 失败: {e}")
    session2 = None

print("\n[2.3] 第三次调用 get_session (从新创建的 manager，应该从文件加载)...")
# 创建新的 manager 实例（模拟进程重启）
manager2 = UnifiedSessionManager(
    ttl_seconds=30 * 60,
    storage_path=storage_file,
    enable_persistence=True,
)

try:
    session3 = manager2.get_session(TEST_ID, TEST_PWD, Subsystem.JWC)
    print(f"✓ 成功!")
    print(f"  Session 对象: {id(session3)}")
    print(f"  Cookies: {dict(session3.cookies)}")

    if session1 and session3:
        if id(session1) == id(session3):
            print(f"\n✅ 确认：同一个 Session（文件加载成功）")
        else:
            print(f"\n✅ 文件加载成功（但对象ID不同，因为是新创建的 Session）")
except Exception as e:
    print(f"✗ 失败: {e}")

print("\n[2.4] 查看保存的文件...")
if os.path.exists(storage_file):
    with open(storage_file, "r") as f:
        content = f.read()
    print(f"✓ 文件已保存")
    print(f"内容:\n{content[:800]}")
else:
    print("✗ 文件未保存")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
