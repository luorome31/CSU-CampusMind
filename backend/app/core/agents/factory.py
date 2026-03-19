"""
Agent 工厂 - 根据用户登录状态创建不同的 Agent
"""
import logging
from typing import Optional, List

from langchain_openai import ChatOpenAI

from app.config import settings
from app.core.context import ToolContext
from app.core.session.manager import UnifiedSessionManager
from app.core.agents.react_agent import ReactAgent
from app.core.tools.jwc import create_jwc_tools
from app.core.tools.oa import create_oa_tools  # NEW
from app.core.tools.library import create_library_tools
from app.core.tools.career import create_career_tools
from app.core.tools.rag_tool import create_rag_tool

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Agent 工厂，根据用户登录状态创建不同的 Agent

    设计原则：
    - 登录用户：JWC + Library + Career + RAG tools
    - 未登录用户：Library + Career + RAG tools
    """

    def __init__(self, session_manager: UnifiedSessionManager):
        self.session_manager = session_manager

    def _get_llm(self, model_name: str = "gpt-3.5-turbo") -> ChatOpenAI:
        """获取 LLM 实例"""
        api_key = settings.openai_api_key or settings.embedding_api_key

        if not api_key:
            raise ValueError("No LLM API key configured")

        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=settings.openai_base_url,
            streaming=True
        )

    def _build_system_prompt(
        self,
        ctx: ToolContext,
        knowledge_ids: Optional[List[str]] = None
    ) -> str:
        """构建 system prompt"""
        base_prompt = """你是一个智能校园助手，可以帮助用户解答问题和查询信息。

请根据用户的问题，使用合适的工具来获取信息并回答。
如果你不确定某些信息，请如实告知用户。"""

        if knowledge_ids:
            base_prompt += f"""

当前可用的知识库 ID 列表: {knowledge_ids}
当用户询问需要查找知识库的问题时，使用 rag_search 工具搜索。"""

        if ctx.is_authenticated:
            base_prompt += f"""

用户已登录（学号: {ctx.user_id}），你可以访问以下个人信息：
- jwc_grade: 查询成绩
- jwc_schedule: 查询课表
- jwc_rank: 查询专业排名
- jwc_level_exam: 查询等级考试成绩
- oa_notification_list: 查询校内通知（需登录）

你还可以使用以下公开工具：
- library_search: 搜索图书馆馆藏
- library_get_book_location: 查询图书位置
- rag_search: 搜索知识库
- career_teachin: 查询宣讲会信息
- career_campus_recruit: 查询校园招聘信息
- career_campus_intern: 查询实习岗位信息
- career_jobfair: 查询招聘会信息

重要：这些工具不需要你接收 user_id 参数，系统会自动处理用户身份。"""
        else:
            base_prompt += """
当前为游客模式，你可以使用以下公开工具：
- library_search: 搜索图书馆馆藏
- library_get_book_location: 查询图书位置
- rag_search: 搜索知识库
- career_teachin: 查询宣讲会信息
- career_campus_recruit: 查询校园招聘信息
- career_campus_intern: 查询实习岗位信息
- career_jobfair: 查询招聘会信息

如果需要访问个人成绩、课表等信息，请提示用户先登录。"""

        return base_prompt

    def create_agent(
        self,
        user_id: Optional[str] = None,
        knowledge_ids: Optional[List[str]] = None,
        model_name: str = "gpt-3.5-turbo"
    ) -> ReactAgent:
        """
        创建 Agent

        Args:
            user_id: 用户 ID（从 JWT 解码得到），None 表示未登录
            knowledge_ids: 知识库 ID 列表
            model_name: LLM 模型名称

        Returns:
            ReactAgent 实例
        """
        # 创建上下文
        ctx = ToolContext(
            user_id=user_id,
            session_manager=self.session_manager if user_id else None
        )

        # 收集工具
        tools = []

        # 图书馆工具（始终可用）
        tools.extend(create_library_tools(ctx))

        # Career 工具（始终可用，无需认证）
        tools.extend(create_career_tools(ctx))

        # RAG 工具（始终可用）
        if knowledge_ids:
            for kid in knowledge_ids:
                tools.append(create_rag_tool(knowledge_ids=[kid]))

        # OA 工具（需要登录，认证检查在工具内部）
        if ctx.is_authenticated:
            tools.extend(create_oa_tools(ctx))  # NEW

        # JWC 工具（需要登录）
        if ctx.is_authenticated:
            tools.extend(create_jwc_tools(ctx))
            logger.info(f"Creating agent for authenticated user: {user_id}")
        else:
            logger.info("Creating agent for anonymous user")

        # 构建 system prompt
        system_prompt = self._build_system_prompt(ctx, knowledge_ids)

        # 创建 Agent
        return ReactAgent(
            model=self._get_llm(model_name),
            system_prompt=system_prompt,
            tools=tools
        )


# 全局工厂实例（需要通过 initialize_factory 初始化）
_agent_factory: Optional[AgentFactory] = None


def get_agent_factory() -> AgentFactory:
    """获取全局 AgentFactory 实例"""
    if _agent_factory is None:
        raise RuntimeError("AgentFactory not initialized. Call initialize_agent_factory() first.")
    return _agent_factory


def initialize_agent_factory(session_manager: UnifiedSessionManager):
    """初始化全局 AgentFactory"""
    global _agent_factory
    _agent_factory = AgentFactory(session_manager)
    logger.info("AgentFactory initialized")
