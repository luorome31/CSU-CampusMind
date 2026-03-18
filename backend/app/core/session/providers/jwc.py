# backend/app/core/session/providers/jwc.py
import logging
import requests
from urllib.parse import urljoin

from app.core.session.providers.base import SubsystemSessionProvider
from app.core.session import cas_login

logger = logging.getLogger(__name__)


class JWCSessionProvider(SubsystemSessionProvider, subsystem_name="jwc"):
    """
    教务系统 Session Provider

    流程:
    1. 创建新 session，设置 CASTGC cookie
    2. 访问 CAS login URL with service，触发重定向到 JWC
    3. 跟随重定向，获取 JWC 的 JSESSIONID
    """

    SERVICE_URL = "http://csujwc.its.csu.edu.cn/sso.jsp"
    CAS_LOGIN_URL = "https://ca.csu.edu.cn/authserver/login"

    def fetch_session(self, castgc: str) -> requests.Session:
        session = cas_login.create_session()

        # 1. 注入 CASTGC cookie
        session.cookies.set("CASTGC", castgc, domain="ca.csu.edu.cn")

        # 2. 访问 CAS 登录 URL with service，触发重定向到 JWC
        login_url = f"{self.CAS_LOGIN_URL}?service={requests.utils.quote(self.SERVICE_URL)}"
        logger.info(f"JWC: Using CASTGC to access {login_url}")

        resp = session.get(login_url, allow_redirects=False)

        # 3. 跟随重定向到 JWC，获取 JSESSIONID
        redirect_url = resp.headers.get("Location", "")
        if redirect_url:
            if not redirect_url.startswith("http"):
                redirect_url = urljoin(login_url, redirect_url)
            resp = session.get(redirect_url, allow_redirects=True)
            logger.info(f"JWC: Subsystem final URL: {resp.url}")

        return session
