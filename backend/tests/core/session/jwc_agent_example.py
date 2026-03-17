"""
Example: How to integrate JWC Tools in React Agent

This module demonstrates how to use JWC (Jiaowu/Academic Affairs System) tools
with the React Agent for querying student academic information.
"""
from langchain_openai import ChatOpenAI
from app.core.session.factory import get_session_manager
from app.core.tools.jwc import JWC_TOOLS, set_session_manager


def create_jwc_agent():
    """
    Create a React Agent with JWC Tools integrated.

    This function shows how to:
    1. Get SessionManager from the factory
    2. Set it to the JWC tools module
    3. Create a ReactAgent with JWC tools

    Returns:
        ReactAgent: Configured agent with JWC tools
    """
    # Get SessionManager from factory
    session_manager = get_session_manager()

    # Set to tools module (required for JWC tools to work)
    set_session_manager(session_manager)

    # Create LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    # Create Agent with JWC Tools
    from app.core.agents.react_agent import ReactAgent

    system_prompt = """你是一个智能助手，可以帮助用户查询教务系统信息。

可用工具:
- jwc_grade: 查询成绩
- jwc_schedule: 查询课表
- jwc_rank: 查询专业排名
- jwc_level_exam: 查询等级考试成绩
- jwc_set_password: 设置密码（首次使用前必须调用）"""

    agent = ReactAgent(
        model=llm,
        system_prompt=system_prompt,
        tools=JWC_TOOLS  # Pass JWC Tools
    )

    return agent


async def run_jwc_agent_example():
    """
    Example: Run the JWC agent to handle user queries.

    This demonstrates a typical usage pattern where:
    1. First set password for a user (required before first use)
    2. Then query academic information
    """
    from langchain_core.messages import HumanMessage

    # Create agent
    agent = create_jwc_agent()

    # Example 1: Set password for a user (required before first use)
    print("=== Example 1: Setting password ===")
    messages = [
        HumanMessage(content="请帮我设置密码，我的学号是 123456，密码是 mypassword123")
    ]

    async for output in agent.astream(messages):
        if output["type"] == "response_chunk":
            print(output["data"]["chunk"], end="")
        elif output["type"] == "event":
            print(f"\n[Event] {output['data']['title']}: {output['data']['message']}")

    print("\n")

    # Example 2: Query grades
    print("=== Example 2: Query grades ===")
    messages = [
        HumanMessage(content="请帮我查询 2024-2025-1 学期的成绩")
    ]

    async for output in agent.astream(messages):
        if output["type"] == "response_chunk":
            print(output["data"]["chunk"], end="")
        elif output["type"] == "event":
            print(f"\n[Event] {output['data']['title']}: {output['data']['message']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_jwc_agent_example())
