"""Session 持久化 - 保存和加载 Session"""
import os
import json
import time
import logging
import threading
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============ Session 持久化 ============
class SessionPersistence:
    """
    Session 持久化 - 保存和加载 cookies

    注意：requests.Session 对象本身无法完整序列化（包含连接池等）
    我们只持久化 cookies 和必要的元数据
    """

    def __init__(self, storage_path: str = "./session_storage.json"):
        self._storage_path = Path(storage_path)
        self._lock = threading.Lock()

    def save(self, user_id: str, subsystem: str, session: requests.Session) -> None:
        """
        保存 Session 的 cookies 到文件

        Args:
            user_id: 用户 ID
            subsystem: 子系统标识
            session: 包含 cookies 的 Session
        """
        with self._lock:
            # 读取现有数据
            data = self._load_all()

            # 提取可序列化的 cookies
            cookies_dict = {}
            for cookie in session.cookies:
                cookies_dict[cookie.name] = {
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "secure": cookie.secure,
                    "expires": cookie.expires,
                    "httpOnly": cookie.has_nonstandard_attr("HttpOnly"),
                }

            # 构建保存结构
            if user_id not in data:
                data[user_id] = {}

            data[user_id][subsystem] = {
                "cookies": cookies_dict,
                "saved_at": time.time(),
                "expires_at": time.time() + 30 * 60,  # 默认 30 分钟有效
            }

            # 写入文件
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Session saved for {user_id}:{subsystem}")

    def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        """
        从文件加载 Session

        Args:
            user_id: 用户 ID
            subsystem: 子系统标识

        Returns:
            恢复的 Session，如果不存在或过期返回 None
        """
        with self._lock:
            data = self._load_all()

            if user_id not in data or subsystem not in data[user_id]:
                logger.info(f"No saved session for {user_id}:{subsystem}")
                return None

            session_data = data[user_id][subsystem]

            # 检查是否过期
            if time.time() > session_data.get("expires_at", 0):
                logger.info(f"Saved session expired for {user_id}:{subsystem}")
                self._delete(user_id, subsystem)
                return None

            # 恢复 cookies
            session = requests.Session()
            cookies_dict = session_data.get("cookies", {})

            for name, cookie_info in cookies_dict.items():
                session.cookies.set(
                    name,
                    cookie_info["value"],
                    domain=cookie_info.get("domain"),
                    path=cookie_info.get("path", "/"),
                    secure=cookie_info.get("secure", False),
                )

            logger.info(f"Session loaded for {user_id}:{subsystem}")
            return session

    def _load_all(self) -> dict:
        """加载所有持久化数据"""
        if not self._storage_path.exists():
            return {}
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load session file: {e}")
            return {}

    def _delete(self, user_id: str, subsystem: str) -> None:
        """删除指定 session"""
        data = self._load_all()
        if user_id in data and subsystem in data[user_id]:
            del data[user_id][subsystem]
            if not data[user_id]:
                del data[user_id]
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        """使 session 失效"""
        with self._lock:
            if subsystem:
                self._delete(user_id, subsystem)
            else:
                # 删除用户所有 subsystem
                data = self._load_all()
                if user_id in data:
                    del data[user_id]
                    with open(self._storage_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False)

    def cleanup_expired(self) -> int:
        """清理所有过期的 session，返回清理数量"""
        data = self._load_all()
        now = time.time()
        cleaned = 0

        for user_id in list(data.keys()):
            for subsystem in list(data[user_id].keys()):
                if now > data[user_id][subsystem].get("expires_at", 0):
                    del data[user_id][subsystem]
                    cleaned += 1
            if not data[user_id]:
                del data[user_id]

        if cleaned > 0:
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            logger.info(f"Cleaned up {cleaned} expired sessions")

        return cleaned


# ============ 完整示例 ============
def demo_persistence():
    """演示 Session 持久化"""
    print("\n" + "=" * 60)
    print("Session 持久化演示")
    print("=" * 60)

    persistence = SessionPersistence("./test_sessions.json")

    # 1. 模拟保存 Session
    print("\n【1】模拟保存 Session:")
    session = requests.Session()
    session.cookies.set("JSESSIONID", "abc123", domain="csujwc.its.csu.edu.cn")
    session.cookies.set("user", "8209220131", domain="csujwc.its.csu.edu.cn")

    persistence.save("8209220131", "jwc", session)
    print("  → Session 已保存到文件")

    # 2. 模拟加载 Session
    print("\n【2】加载 Session:")
    loaded = persistence.load("8209220131", "jwc")
    if loaded:
        print(f"  → 加载成功，cookies: {dict(loaded.cookies)}")
    else:
        print("  → 加载失败")

    # 3. 检查过期
    print("\n【3】检查过期机制:")
    print("  → 文件中的 expires_at 是保存时间 + 30 分钟")
    print("  → 加载时会检查是否超过这个时间")
    print("  → 注意：这不代表 CAS Cookie 的真实有效期")

    # 4. 查看保存的文件
    print("\n【4】查看保存的文件:")
    if os.path.exists("./test_sessions.json"):
        with open("./test_sessions.json", "r") as f:
            print(f"  内容: {f.read()[:500]}...")

    # 5. 清理
    print("\n【5】清理:")
    persistence.cleanup_expired()
    print("  → 过期 session 已清理")

    print("\n" + "=" * 60)


# ============ Session 有效期说明 ============
def explain_duration():
    """说明 Session 有效期"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    Session 有效期说明                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. CAS Cookie (服务端控制)                                 ║
║     - 取决于 CAS 服务器设置                                  ║
║     - 通常是会话 Cookie（浏览器关闭失效）                    ║
║     - 或固定时间（如 24 小时）                              ║
║     - 无法通过代码准确获取                                   ║
║                                                              ║
║  2. 子系统 Cookie (服务端控制)                              ║
║     - 教务系统: 需要实际测试                                  ║
║     - 图书馆: 需要实际测试                                    ║
║     - 校园卡: 需要实际测试                                    ║
║                                                              ║
║  3. 本地缓存 TTL (客户端控制)                                ║
║     - 当前设置为 30 分钟                                    ║
║     - 是一个安全的默认值                                     ║
║     - 可以根据实际情况调整                                   ║
║                                                              ║
║  4. 建议策略                                                ║
║     - 缓存时间 < 实际有效期 → 浪费一些但安全                 ║
║     - 缓存时间 > 实际有效期 → 可能用到失效的 cookie         ║
║     - 建议设置 15-30 分钟作为缓存 TTL                        ║
║     - 同时在请求时检测是否失效（如 302 跳转）                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    explain_duration()
    demo_persistence()
