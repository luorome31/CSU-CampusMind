# backend/app/core/session/providers/oa.py
import logging
import requests
from urllib.parse import urljoin

from app.core.session.providers.base import SubsystemSessionProvider
from app.core.session import cas_login

logger = logging.getLogger(__name__)


class OASessionProvider(SubsystemSessionProvider, subsystem_name="oa"):
    """
    校内办公网 (OA) Session Provider

    流程:
    1. GET https://oa.csu.edu.cn/con/ → 提取 JSESSIONID (sub-session S) 从 cookies
    2. 设置 CASTGC cookie，GET https://ca.csu.edu.cn/authserver/login?service=... → 跟随重定向
    3. 跟随最终重定向以激活 sub-session S
    """

    OA_BASE_URL = "https://oa.csu.edu.cn"
    OA_SESSION_URL = "https://oa.csu.edu.cn/con/"
    CAS_LOGIN_URL = "https://ca.csu.edu.cn/authserver/login"
    CAS_SERVICE = "https%3A%2F%2Foa.csu.edu.cn%2Fcon%2F%2Flogincas%3FtargetUrl%3DaHR0cHM6Ly9vYS5jc3UuZWR1LmNuL2Nvbi8v"

    def fetch_session(self, castgc: str) -> requests.Session:
        session = cas_login.create_session()

        # Step 1: 访问 OA 页面获取 JSESSIONID (sub-session S)
        logger.info(f"OA: Fetching JSESSIONID from {self.OA_SESSION_URL}")
        resp = session.get(self.OA_SESSION_URL, allow_redirects=True)
        logger.info(f"OA: After step 1, cookies: {list(session.cookies.keys())}")

        # Step 2: 设置 CASTGC cookie，访问 CAS 登录 URL with service
        session.cookies.set("CASTGC", castgc, domain="ca.csu.edu.cn")
        login_url = f"{self.CAS_LOGIN_URL}?service={self.CAS_SERVICE}"
        logger.info(f"OA: Using CASTGC to access CAS: {login_url}")

        resp = session.get(login_url, allow_redirects=False)
        redirect_url = resp.headers.get("Location", "")

        # Step 3: 跟随重定向到 OA，激活 sub-session S
        if redirect_url:
            if not redirect_url.startswith("http"):
                redirect_url = urljoin(login_url, redirect_url)
            logger.info(f"OA: Following redirect to: {redirect_url}")
            resp = session.get(redirect_url, allow_redirects=True)
            logger.info(f"OA: Subsystem final URL: {resp.url}")

        logger.info(f"OA: Final cookies: {list(session.cookies.keys())}")
        return session
