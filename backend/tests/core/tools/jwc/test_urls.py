"""
教务系统 URL 测试脚本

功能：
1. 从持久化文件加载 Session
2. 对四个教务系统 URL 发送请求
3. 保存返回的 HTML 到文件
4. 请求间隔防封

使用方式：
    cd backend
    uv run python -m tests.core.test_jwc_urls
"""
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# 确保 app 在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config import settings
from app.core.session import FileSessionPersistence
import requests


# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════

# 请求间隔（秒）
REQUEST_INTERVAL = 3

# 教务系统 URL（带默认参数）
JWC_URLS = {
    "成绩查询": {
        "url": "http://csujwc.its.csu.edu.cn/jsxsd/kscj/yscjcx_list",
        "method": "POST",
        "data": {"xnxq01id": "2024-2025-1"}  # 学期参数
    },
    "专业排名": {
        "url": "http://csujwc.its.csu.edu.cn/jsxsd/kscj/zybm_cx",
        "method": "GET",
        "data": {}
    },
    "课表查询": {
        "url": "http://csujwc.its.csu.edu.cn/jsxsd/xskb/xskb_list.do",
        "method": "POST",
        "data": {"xnxq01id": "2024-2025-1", "zc": "0"}  # 学期和周次
    },
    "等级考试": {
        "url": "http://csujwc.its.csu.edu.cn/jsxsd/kscj/djkscj_list",
        "method": "GET",
        "data": {}
    },
}

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "http://csujwc.its.csu.edu.cn/",
}


# ═══════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'


def load_session_from_file(storage_path: str) -> requests.Session:
    """从持久化文件加载 Session"""
    print(f"{Colors.CYAN}▶ 加载 Session: {storage_path}{Colors.RESET}")

    if not os.path.exists(storage_path):
        print(f"{Colors.RED}✗ Session 文件不存在: {storage_path}{Colors.RESET}")
        print(f"  请先运行一次查询成绩，让系统创建 Session")
        return None

    with open(storage_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 找到任意一个用户的 session
    user_id = None
    subsystem = None
    for uid, subs in data.items():
        user_id = uid
        for sub in subs:
            subsystem = sub
            break
        if subsystem:
            break

    if not user_id or not subsystem:
        print(f"{Colors.RED}✗ 未找到保存的 Session{Colors.RESET}")
        return None

    session_data = data[user_id][subsystem]
    cookies_dict = session_data.get("cookies", {})

    session = requests.Session()
    session.headers.update(HEADERS)

    for name, cookie_info in cookies_dict.items():
        session.cookies.set(
            name,
            cookie_info.get("value"),
            domain=cookie_info.get("domain"),
            path=cookie_info.get("path", "/"),
        )

    print(f"  {Colors.GREEN}✓{Colors.RESET} 已加载 Session: {user_id} / {subsystem}")
    print(f"  Cookies: {list(cookies_dict.keys())}")

    return session


def save_html(content: str, name: str, output_dir: Path):
    """保存 HTML 到文件"""
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"{name}.html"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  {Colors.GREEN}✓{Colors.RESET} 已保存: {filepath}")
    return filepath


def test_url(session: requests.Session, name: str, url_info: dict, output_dir: Path) -> bool:
    """测试单个 URL"""
    url = url_info["url"]
    method = url_info.get("method", "GET")
    data = url_info.get("data", {})

    print(f"\n{Colors.CYAN}▶ 测试: {name}{Colors.RESET}")
    print(f"  URL: {url}")
    print(f"  Method: {method}")
    if data:
        print(f"  Data: {data}")

    try:
        if method == "POST":
            response = session.post(url, data=data, timeout=30)
        else:
            response = session.get(url, timeout=30)

        print(f"  状态码: {response.status_code}")
        print(f"  内容长度: {len(response.text)} 字符")

        # 检查是否需要登录
        if "登录" in response.text and "用户名" in response.text:
            print(f"  {Colors.YELLOW}⚠{Colors.RESET} 可能需要重新登录（页面包含登录表单）")

        # 保存 HTML
        filepath = save_html(response.text, name, output_dir)
        return True

    except requests.RequestException as e:
        print(f"  {Colors.RED}✗ 请求失败: {e}{Colors.RESET}")
        return False


# ═══════════════════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"""
{Colors.CYAN}
╔══════════════════════════════════════════════════════════════╗
║              教务系统 URL 测试脚本                        ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)

    # 1. 检查配置
    print(f"{Colors.CYAN}▶ 检查配置{Colors.RESET}")
    print(f"  Session 文件: {settings.session_storage_path}")

    # 2. 加载 Session
    session = load_session_from_file(settings.session_storage_path)
    if not session:
        return

    # 3. 创建输出目录
    output_dir = Path("./data/jwc_debug")
    print(f"\n{Colors.CYAN}▶ 输出目录: {output_dir}{Colors.RESET}")

    # 4. 测试每个 URL
    results = {}
    for i, (name, url_info) in enumerate(JWC_URLS.items(), 1):
        print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.CYAN}# {i}/{len(JWC_URLS)}: {name}{Colors.RESET}")

        success = test_url(session, name, url_info, output_dir)
        results[name] = success

        # 请求间隔
        if i < len(JWC_URLS):
            print(f"\n{Colors.YELLOW}等待 {REQUEST_INTERVAL} 秒...{Colors.RESET}")
            time.sleep(REQUEST_INTERVAL)

    # 5. 总结
    print(f"""
{Colors.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                        测试结果                            ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)

    for name, success in results.items():
        status = f"{Colors.GREEN}✓{Colors.RESET}" if success else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} {name}")

    print(f"""
{Colors.CYAN}
请查看以下文件，手动检查内容：
{output_dir}/

{Colors.YELLOW}提示：{Colors.RESET}
- 如果 HTML 包含具体数据（如成绩、课表），说明接口可用
- 如果跳转到登录页面，说明 Session 已失效
- 如果返回错误信息，检查网络连接
    """)


if __name__ == "__main__":
    main()
