"""
CAS 登录逻辑 - 参考 unified_session_v2.py 实现
"""
import secrets
import base64
import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES

logger = logging.getLogger(__name__)

# 常量定义
CAS_BASE_URL = "https://ca.csu.edu.cn"
CAS_LOGIN_URL = f"{CAS_BASE_URL}/authserver/login"
AES_CHARSET = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# 子系统 CAS service URL
SUBSYSTEM_SERVICE_URLS = {
    "jwc": "http://csujwc.its.csu.edu.cn/sso.jsp",
    "library": "https://lib.csu.edu.cn/system/resource/code/auth/clogin.jsp",
    "ecard": "https://ecard.csu.edu.cn/berserker-auth/cas/login/wisedu?targetUrl=https://ecard.csu.edu.cn/plat-pc/?name=loginTransit",
}


def random_string(length: int) -> str:
    return "".join(secrets.choice(AES_CHARSET) for _ in range(length))


def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    padding = block_size - (len(data) % block_size)
    return data + bytes([padding] * padding)


def encrypt_password(password: str, salt: str) -> str:
    prefix = random_string(64)
    iv = random_string(16)
    plain = pkcs7_pad((prefix + password).encode("utf-8"), 16)
    cipher = AES.new(salt.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    encrypted = cipher.encrypt(plain)
    return base64.b64encode(encrypted).decode("utf-8")


def create_session() -> requests.Session:
    """创建带默认请求头的 Session"""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


class CASLoginError(Exception):
    """CAS 登录错误"""
    pass


class AccountLockedError(Exception):
    """账号被锁定错误"""
    pass


def cas_login(
    username: str,
    password: str,
    service_url: str,
    rate_limiter=None
) -> requests.Session:
    """
    CAS 统一认证登录

    流程:
    1. 访问 CAS 登录页面获取表单字段 (lt, execution, salt 等)
    2. 提交登录表单，成功后获取 CASTGC cookie
    3. 使用 CASTGC cookie 访问子系统服务 URL，获取子系统 session

    返回的 session 包含:
    - CASTGC: CAS 认证 cookie (用于后续刷新子系统 session)
    - 子系统的 JSESSIONID: 子系统 session (如 JWC 的 JSESSIONID)
    """
    if rate_limiter:
        if not rate_limiter.can_login(username):
            wait_time = rate_limiter.get_wait_time(username)
            raise AccountLockedError(f"登录过于频繁，请等待 {wait_time:.0f} 秒后再试")
        rate_limiter.record_login(username)

    session = create_session()

    try:
        # ========== Step 1: 获取登录表单 ==========
        login_url = f"{CAS_LOGIN_URL}?service={requests.utils.quote(service_url)}"
        logger.info(f"Step 1: Fetching login page: {login_url}")

        resp = session.get(login_url, allow_redirects=False)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        lt = soup.find("input", {"name": "lt"})["value"]
        execution = soup.find("input", {"name": "execution"})["value"]
        event_id = soup.find("input", {"name": "_eventId"})["value"]
        dllt = soup.find("input", {"name": "dllt"})["value"]
        salt = soup.find("input", {"id": "pwdEncryptSalt"})["value"]

        if not salt or not execution:
            raise CASLoginError("Failed to parse login page")

        # ========== Step 2: 提交登录表单，获取 CASTGC ==========
        encrypted_pwd = encrypt_password(password, salt)

        form_data = {
            "username": username,
            "password": encrypted_pwd,
            "passwordText": "",
            "lt": lt,
            "execution": execution,
            "_eventId": event_id,
            "cllt": "userNameLogin",
            "dllt": dllt,
        }

        logger.info(f"Step 2: Submitting login form for user: {username}")
        resp = session.post(login_url, data=form_data, allow_redirects=False)

        # 检查是否登录成功
        if resp.status_code == 401 or "账号" in resp.text or "锁定" in resp.text:
            raise AccountLockedError("账号可能被锁定")

        # 检查 CASTGC cookie 是否存在
        cookies = {c.name: c.value for c in session.cookies}
        castgc = cookies.get("CASTGC")

        if not castgc:
            if "密码" in resp.text or "错误" in resp.text:
                raise CASLoginError("用户名或密码错误")
            raise CASLoginError(f"登录失败: 未获取到 CASTGC cookie, 当前 cookies: {list(cookies.keys())}")

        logger.info(f"CASTGC cookie obtained: {castgc[:30]}...")

        # ========== Step 3: 使用 CASTGC 访问子系统，获取子系统 session ==========
        # 再次访问 CAS 登录 URL，这次会携带 CASTGC，自动重定向到子系统并设置子系统的 session
        logger.info(f"Step 3: Accessing subsystem with CASTGC: {service_url}")

        subsystem_session_resp = session.get(login_url, allow_redirects=False)

        # 如果有重定向，跟随重定向
        redirect_url = subsystem_session_resp.headers.get("Location", "")
        if redirect_url:
            logger.info(f"Following redirect to subsystem: {redirect_url}")
            if not redirect_url.startswith("http"):
                redirect_url = urljoin(login_url, redirect_url)

            # 跟随重定向，这次允许自动重定向以获取子系统的 cookie
            subsystem_session_resp = session.get(redirect_url, allow_redirects=True)
            logger.info(f"Subsystem final URL: {subsystem_session_resp.url}")

        # 记录日志中的 cookies
        final_cookies = {c.name: c.value for c in session.cookies}
        logger.info(f"Cookies after subsystem access: {list(final_cookies.keys())}")

        # 验证是否获取到了子系统 session (通常是 JSESSIONID)
        subsystem_jsessionid = final_cookies.get("JSESSIONID")
        if subsystem_jsessionid:
            logger.info(f"Subsystem JSESSIONID obtained: {subsystem_jsessionid[:20]}...")

        return session

    except AccountLockedError:
        raise
    except requests.RequestException as e:
        raise CASLoginError(f"网络请求失败: {e}")


def cas_login_only_castgc(username: str, password: str, rate_limiter=None) -> str:
    """
    仅获取 CASTGC，不访问任何子系统

    这是简化版的登录，只用于获取 CASTGC cookie。
    后续使用 CASTGC 通过 SubsystemSessionProvider 获取各子系统的 session。

    Returns:
        CASTGC cookie 值

    Raises:
        AccountLockedError: 账号被锁定
        CASLoginError: 登录失败
    """
    if rate_limiter:
        if not rate_limiter.can_login(username):
            wait_time = rate_limiter.get_wait_time(username)
            raise AccountLockedError(f"登录过于频繁，请等待 {wait_time:.0f} 秒后再试")
        rate_limiter.record_login(username)

    session = create_session()

    try:
        login_url = CAS_LOGIN_URL  # no service param — CAS server sets CASTGC on bare authserver/login

        # Step 1: 获取登录表单
        resp = session.get(login_url, allow_redirects=False)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        lt = soup.find("input", {"name": "lt"})["value"]
        execution = soup.find("input", {"name": "execution"})["value"]
        event_id = soup.find("input", {"name": "_eventId"})["value"]
        dllt = soup.find("input", {"name": "dllt"})["value"]
        salt = soup.find("input", {"id": "pwdEncryptSalt"})["value"]

        if not salt or not execution:
            raise CASLoginError("Failed to parse login page")

        # Step 2: 提交登录表单，获取 CASTGC
        encrypted_pwd = encrypt_password(password, salt)

        form_data = {
            "username": username,
            "password": encrypted_pwd,
            "passwordText": "",
            "lt": lt,
            "execution": execution,
            "_eventId": event_id,
            "cllt": "userNameLogin",
            "dllt": dllt,
        }

        resp = session.post(login_url, data=form_data, allow_redirects=False)

        # 检查是否登录成功
        if resp.status_code == 401 or "账号" in resp.text or "锁定" in resp.text:
            raise AccountLockedError("账号可能被锁定")

        cookies = {c.name: c.value for c in session.cookies}
        castgc = cookies.get("CASTGC")

        if not castgc:
            if "密码" in resp.text or "错误" in resp.text:
                raise CASLoginError("用户名或密码错误")
            raise CASLoginError(f"登录失败: 未获取到 CASTGC")

        logger.info(f"CASTGC obtained: {castgc[:30]}...")
        return castgc

    except AccountLockedError:
        raise
    except requests.RequestException as e:
        raise CASLoginError(f"网络请求失败: {e}")
