"""
E2E 测试：包含大模型调用的端到端测试

测试完整流程：
1. React Agent + JWC Tools
2. 用户输入查询请求
3. Agent 决定调用 Tool
4. Tool 执行教务系统查询
5. 返回结果给 Agent
6. Agent 生成最终回复

运行方式：
    uv run python -m tests.core.test_jwc_agent_e2e

注意事项：
- 需要在 .env 中配置 CAS_USERNAME 和 CAS_PASSWORD
- 需要配置 OPENAI_API_KEY（或其他 LLM）
"""
import os
import sys
import asyncio
from datetime import datetime

# 确保 app 在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config import settings
from app.core.session import UnifiedSessionManager, FileSessionPersistence, LoginRateLimiter
from app.core.tools.jwc import JWC_TOOLS, set_session_manager
from app.core.agents.react_agent import ReactAgent


# ═══════════════════════════════════════════════════════════════
# 日志配置
# ═══════════════════════════════════════════════════════════════

class Colors:
    """ANSI 颜色码"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'


def log_step(title: str, content: str = ""):
    """打印步骤日志"""
    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.CYAN}▶ {title}{Colors.RESET}")
    if content:
        print(f"{Colors.GRAY}{content}{Colors.RESET}")


def log_info(msg: str):
    """打印信息"""
    print(f"  {Colors.BLUE}ℹ{Colors.RESET} {msg}")


def log_success(msg: str):
    """打印成功"""
    print(f"  {Colors.GREEN}✓{Colors.RESET} {msg}")


def log_warning(msg: str):
    """打印警告"""
    print(f"  {Colors.YELLOW}⚠{Colors.RESET} {msg}")


def log_error(msg: str):
    """打印错误"""
    print(f"  {Colors.RED}✗{Colors.RESET} {msg}")


def log_tool(name: str, args: str, result: str):
    """打印工具调用"""
    print(f"\n{Colors.MAGENTA}🔧 Tool: {name}{Colors.RESET}")
    print(f"  {Colors.GRAY}参数: {args}{Colors.RESET}")
    print(f"  {Colors.GRAY}结果: {result[:200]}...{Colors.RESET}")


def log_model(message: str, is_user: bool = True):
    """打印模型消息"""
    role = "👤 User" if is_user else "🤖 Assistant"
    color = Colors.YELLOW if is_user else Colors.GREEN
    print(f"\n{color}{role}:{Colors.RESET}")
    print(f"  {message[:500]}{'...' if len(message) > 500 else ''}")


# ═══════════════════════════════════════════════════════════════
# 测试用例
# ═══════════════════════════════════════════════════════════════

def check_environment():
    """检查环境配置"""
    log_step("检查环境配置")

    errors = []

    if not settings.cas_username:
        errors.append("CAS_USERNAME 未配置")
    else:
        log_info(f"CAS_USERNAME: {settings.cas_username}")

    if not settings.cas_password:
        errors.append("CAS_PASSWORD 未配置")
    else:
        log_info(f"CAS_PASSWORD: {'*' * len(settings.cas_password)}")

    if not settings.openai_api_key:
        errors.append("OPENAI_API_KEY 未配置")
    else:
        log_info(f"OPENAI_API_KEY: {settings.openai_api_key[:10]}...")

    if errors:
        for e in errors:
            log_error(e)
        log_warning("请在 .env 文件中配置必要的环境变量")
        return False

    log_success("环境检查通过")
    return True


def init_session_manager():
    """初始化 SessionManager"""
    log_step("初始化 SessionManager")

    persistence = FileSessionPersistence(
        storage_path=settings.session_storage_path
    )

    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=settings.session_ttl_seconds,
    )

    # 设置到 JWC Tools
    set_session_manager(manager)

    log_success("SessionManager 初始化完成")
    return manager


def create_agent():
    """创建 React Agent"""
    log_step("创建 React Agent")

    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        log_error("请安装 langchain-openai: uv add langchain-openai")
        return None

    # 创建 LLM
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0.7,
    )

    system_prompt = f"""你是一个智能助手，可以帮助用户查询教务系统信息。

用户信息（已配置）：
- 学号：{settings.cas_username}
- 学期格式：如 '2024-2025-1'

可用工具：
- jwc_grade: 查询学生成绩（参数：user_id, term）
- jwc_schedule: 查询学生课表（参数：user_id, term, week）
- jwc_rank: 查询专业排名（参数：user_id）
- jwc_level_exam: 查询等级考试成绩（参数：user_id）

重要说明：
- user_id 已经配置为 {settings.cas_username}，调用工具时直接使用该值
- term 参数可选，不填则查询所有学期
- 当用户询问成绩、课表、排名、考试等信息时，直接调用相应工具获取数据
- 回答时请用中文。
- 如果查询结果为空，告知用户可能的原因（如该学期无成绩）"""

    agent = ReactAgent(
        model=llm,
        system_prompt=system_prompt,
        tools=JWC_TOOLS
    )

    log_success(f"Agent 创建完成，工具数量: {len(JWC_TOOLS)}")
    for tool in JWC_TOOLS:
        log_info(f"  - {tool.name}")

    return agent


async def run_query(agent: ReactAgent, query: str):
    """运行查询"""
    log_step(f"执行查询: {query}")
    log_model(query, is_user=True)

    try:
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content=query)]
        full_response = ""

        print(f"\n{Colors.CYAN}▶ Agent 响应:{Colors.RESET}")

        async for output in agent.astream(messages):
            output_type = output.get("type")

            if output_type == "event":
                data = output.get("data", {})
                status = data.get("status", "")
                title = data.get("title", "")
                message = data.get("message", "")

                if status == "START":
                    print(f"  {Colors.BLUE}→{Colors.RESET} {title}: {message}")
                elif status == "END":
                    print(f"  {Colors.GREEN}✓{Colors.RESET} {title}: {message}")
                elif status == "ERROR":
                    print(f"  {Colors.RED}✗{Colors.RESET} {title}: {message}")

            elif output_type == "response_chunk":
                chunk = output.get("data", {}).get("chunk", "")
                if chunk:
                    print(chunk, end="", flush=True)
                    full_response += chunk

        print(f"\n")
        log_success("查询完成")

        return full_response

    except Exception as e:
        log_error(f"查询失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_flow():
    """测试流程"""
    print(f"""
{Colors.CYAN}
╔══════════════════════════════════════════════════════════════╗
║         教务系统 Agent E2E 测试                          ║
║         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)

    # 1. 检查环境
    if not check_environment():
        return

    # 2. 初始化 SessionManager
    manager = init_session_manager()

    # 3. 创建 Agent
    agent = create_agent()
    if not agent:
        return

    # 4. 测试用例
    test_cases = [
        "查询我的成绩",
        # "查询我的课表",
        # "查询我的专业排名",
    ]

    for i, query in enumerate(test_cases, 1):
        print(f"\n{Colors.MAGENTA}{'#' * 60}")
        print(f"# 测试用例 {i}/{len(test_cases)}")
        print(f"{'#' * 60}{Colors.RESET}")

        await run_query(agent, query)

        # 测试间隔，避免频繁调用
        if i < len(test_cases):
            log_info("等待 2 秒...")
            import time
            time.sleep(2)

    log_step("测试完成")
    print(f"""
{Colors.GREEN}
╔══════════════════════════════════════════════════════════════╗
║                      测试结束                                ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)


def main():
    """主函数"""
    asyncio.run(test_flow())


if __name__ == "__main__":
    main()
