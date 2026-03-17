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
    """CAS 统一认证登录"""
    if rate_limiter:
        if not rate_limiter.can_login(username):
            wait_time = rate_limiter.get_wait_time(username)
            raise AccountLockedError(f"登录过于频繁，请等待 {wait_time:.0f} 秒后再试")
        rate_limiter.record_login(username)

    session = create_session()

    try:
        login_url = f"{CAS_LOGIN_URL}?service={requests.utils.quote(service_url)}"
        logger.info(f"Fetching login page: {login_url}")

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

        post_url = resp.headers.get("Location", login_url)
        if not post_url.startswith("http"):
            post_url = urljoin(login_url, post_url)

        resp = session.post(post_url, data=form_data, allow_redirects=False)

        final_url = resp.headers.get("Location", "")

        if resp.status_code == 401 or "账号" in resp.text or "锁定" in resp.text:
            raise AccountLockedError("账号可能被锁定")

        if not final_url:
            raise CASLoginError("登录失败: 无重定向地址")

        target_domain = service_url.split("://")[1].split("/")[0]
        if target_domain not in final_url:
            if "密码" in resp.text:
                raise CASLoginError("用户名或密码错误")
            raise CASLoginError(f"登录失败: 重定向到未知地址 {final_url}")

        # 访问重定向地址，获取目标系统的 Cookie
        logger.info(f"Following redirect to: {final_url}")

        try:
            resp = session.get(final_url, allow_redirects=False)
            while resp.status_code in (301, 302, 303, 307, 308):
                next_url = resp.headers.get("Location")
                if next_url:
                    if not next_url.startswith("http"):
                        next_url = urljoin(resp.url, next_url)
                    resp = session.get(next_url, allow_redirects=False)
                else:
                    break
        except Exception as e:
            logger.warning(f"Redirect handling failed: {e}, trying simple approach")
            session.get(final_url, allow_redirects=True)

        # 清理可能重复的 Cookie
        cookies_to_keep = {}
        for cookie in session.cookies:
            if cookie.name == "JSESSIONID":
                cookies_to_keep[cookie.name] = cookie
            else:
                cookies_to_keep[cookie.name] = cookie

        session.cookies.clear()
        for name, cookie in cookies_to_keep.items():
            session.cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)

        logger.info(f"Cookies after redirect: {dict(session.cookies)}")
        return session

    except AccountLockedError:
        raise
    except requests.RequestException as e:
        raise CASLoginError(f"网络请求失败: {e}")
