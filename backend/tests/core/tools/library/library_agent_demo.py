"""
Library Agent Demo - 演示 Agent 调用图书馆工具

这个脚本演示了如何创建一个使用 LangGraph 的 Agent 来调用图书馆搜索工具。
"""
import json
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from app.config import settings
from app.core.tools.library import library_search, library_get_book_location, LIBRARY_TOOLS


def create_library_agent(model: str = None):
    """
    创建图书馆 Agent

    Args:
        model: 使用的模型名称，默认使用 settings 中的配置

    Returns:
        LangGraph Agent
    """
    # 使用 settings 中的配置
    api_key = settings.openai_api_key
    if not api_key:
        print("警告: 未设置 OPENAI_API_KEY，将使用模拟模式")
        return None

    model_name = model or settings.openai_model
    base_url = settings.openai_base_url

    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url
    )
    agent = create_react_agent(llm, tools=LIBRARY_TOOLS)
    return agent


def demo_tools():
    """演示工具定义"""
    print("=" * 60)
    print("图书馆工具演示")
    print("=" * 60)

    # 显示工具信息
    print("\n[1] 可用工具:")
    for i, tool in enumerate(LIBRARY_TOOLS, 1):
        print(f"\n--- 工具 {i}: {tool.name} ---")
        print(f"描述: {tool.description}")

        # 显示输入 schema
        if hasattr(tool, "args_schema") and tool.args_schema:
            schema = tool.args_schema.model_json_schema()
            print(f"输入参数:")
            props = schema.get("properties", {})
            for name, info in props.items():
                required = name in schema.get("required", [])
                desc = info.get("description", "")
                print(f"  - {name}{' (必填)' if required else ''}: {desc}")

    # 直接调用工具演示
    print("\n" + "=" * 60)
    print("[2] 直接调用工具演示")
    print("=" * 60)

    # 调用搜索工具
    print("\n--- 搜索: 'Vue' ---")
    result = library_search.invoke({"keywords": "Vue", "page": 1, "rows": 3})
    print(result[:800])

    # 提取 record_id
    print("\n--- 提取 record_id 并查询位置 ---")
    print("从搜索结果中提取 record_id=794724")
    result2 = library_get_book_location.invoke({"record_id": 794724})
    print(result2[:500])


def demo_agent_flow():
    """演示 Agent 流程（需要 API Key）"""
    print("\n" + "=" * 60)
    print("[3] Agent 流程演示（需要 OpenAI API Key）")
    print("=" * 60)

    agent = create_library_agent()
    if agent is None:
        print("跳过: 需要设置 OPENAI_API_KEY")
        return

    # 场景 1: 搜索图书
    print("\n--- 用户查询: '搜索 Vue 相关的图书' ---")
    result = agent.invoke({"messages": [("human", "搜索 Vue 相关的图书，返回前 3 本")]})

    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"\n调用工具: {tc['name']}")
                print(f"参数: {json.dumps(tc['args'], ensure_ascii=False)}")

        if hasattr(msg, "type") and msg.type == "tool":
            print(f"\n工具返回: {msg.content[:200]}...")

    print(f"\n最终回答: {result['messages'][-1].content[:300]}...")

    # 场景 2: 查询位置
    print("\n--- 用户查询: '查找第一本书的位置' ---")
    # 注意: 实际使用中 Agent 会记住上下文
    result2 = agent.invoke({
        "messages": [("human", "使用 record_id=794724 查询这本书在哪个图书馆")]
    })

    print(f"\n最终回答: {result2['messages'][-1].content}")


def main():
    """主函数"""
    # 演示工具
    demo_tools()

    # 演示 Agent（需要 API Key）
    demo_agent_flow()

    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
    print("\n使用说明:")
    print("1. 设置 OPENAI_API_KEY 环境变量")
    print("2. 运行: PYTHONPATH=. uv run python scripts/library_agent_demo.py")


if __name__ == "__main__":
    main()
