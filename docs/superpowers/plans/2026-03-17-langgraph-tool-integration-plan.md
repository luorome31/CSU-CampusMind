# LangGraph 工具集成实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 JWC 和 Library 工具集成到 LangGraph ReactAgent，支持用户通过 JWT 认证后使用私有工具

**Architecture:** 使用 ToolContext 封装用户身份和 session 管理，工具工厂函数利用闭包隐藏 user_id，避免大模型参数污染

**Tech Stack:** FastAPI, LangGraph, LangChain, JWT (PyJWT), Redis (可选)

---

## Chunk 1: 基础设施 - JWT 和 ToolContext

### Task 1.1: 添加 JWT 配置和 JWTManager

**Files:**
- Modify: `backend/app/config.py` - 添加 JWT 配置项
- Create: `backend/app/core/security.py` - JWT 工具类

**Steps:**

- [ ] **Step 1: 修改 config.py 添加 JWT 配置**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.config import settings; print(settings.jwt_secret_key)"` 确认模块可导入

在 Settings 类中添加:
```python
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
```

在 from_env 方法中添加:
```python
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            jwt_expire_hours=int(os.getenv("JWT_EXPIRE_HOURS", "24")),
```

- [ ] **Step 2: 创建 security.py**

Create file: `backend/app/core/security.py`

```python
"""
JWT 令牌管理模块
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt

from app.config import settings

logger = logging.getLogger(__name__)


class JWTManager:
    """JWT 令牌管理类"""

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256"
    ):
        self.secret_key = secret_key or settings.jwt_secret_key
        self.algorithm = algorithm

    def create_token(
        self,
        payload: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建 JWT token"""
        to_encode = payload.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours)

        to_encode.update({"exp": expire})

        encoded = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        return encoded

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """解码 JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token 已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT token 无效: {e}")
            return None

    def verify_token(self, token: str) -> bool:
        """验证 token 是否有效"""
        return self.decode_token(token) is not None


# 全局实例
jwt_manager = JWTManager()
```

- [ ] **Step 3: 添加 PyJWT 依赖**

Run: `cd /home/luorome/software/CampusMind/backend && uv add pyjwt`

- [ ] **Step 4: 验证模块可导入**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.security import jwt_manager; print('JWTManager imported successfully')"`

- [ ] **Step 5: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/config.py backend/app/core/security.py
git commit -m "feat(security): add JWT manager and config"
```

---

### Task 1.2: 创建 ToolContext 类

**Files:**
- Create: `backend/app/core/context.py` - ToolContext 类

**Steps:**

- [ ] **Step 1: 创建 context.py**

Create file: `backend/app/core/context.py`

```python
"""
ToolContext - 工具运行时上下文
"""
import logging
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.session.manager import UnifiedSessionManager

logger = logging.getLogger(__name__)


class ToolContext:
    """
    工具运行时上下文，包含用户身份和会话管理

    用于在 Agent 创建时注入用户身份信息，
    工具函数通过闭包访问 ctx 中的 user_id，
    避免 user_id 暴露给大模型
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        session_manager: Optional["UnifiedSessionManager"] = None
    ):
        self.user_id = user_id
        self.session_manager = session_manager
        self._subsystem_cache: Dict[str, Any] = {}

    @property
    def is_authenticated(self) -> bool:
        """用户是否已登录"""
        return self.user_id is not None and self.session_manager is not None

    def get_subsystem_session(self, subsystem: str) -> Optional[Dict[str, Any]]:
        """
        获取子系统 session，必要时自动登录

        注意：当前版本 UnifiedSessionManager.get_session 会自动处理登录
        """
        if not self.is_authenticated:
            logger.warning(f"User not authenticated, cannot get subsystem session for {subsystem}")
            return None

        try:
            # 从 session_manager 获取 session
            session = self.session_manager.get_session(self.user_id, subsystem)
            return session
        except Exception as e:
            logger.error(f"Failed to get subsystem session for {subsystem}: {e}")
            return None


# 导出
__all__ = ["ToolContext"]
```

- [ ] **Step 2: 验证模块可导入**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.context import ToolContext; print('ToolContext imported successfully')"`

- [ ] **Step 3: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/core/context.py
git commit -m "feat(context): add ToolContext class"
```

---

## Chunk 2: 工具工厂函数改造

### Task 2.1: 改造 JWC 工具为工厂函数

**Files:**
- Modify: `backend/app/core/tools/jwc/tools.py` - 改为工厂函数
- Create: `backend/tests/core/tools/jwc/test_tool_factory.py` - 单元测试

**Steps:**

- [ ] **Step 1: 阅读现有 tools.py**

Run: `cat /home/luorome/software/CampusMind/backend/app/core/tools/jwc/tools.py` 确认现有实现

- [ ] **Step 2: 备份并重写 tools.py**

Modify: `backend/app/core/tools/jwc/tools.py`

保留原有函数用于兼容，添加新的工厂函数:

```python
"""
LangChain Tools 封装 - 教务系统查询
改造为工厂函数模式，利用闭包隐藏 user_id
"""
import logging
from typing import Optional, List

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from app.core.context import ToolContext
from app.core.session.manager import UnifiedSessionManager
from .service import JwcService

logger = logging.getLogger(__name__)


# ============ Tool Input Models ============

class GradeInput(BaseModel):
    term: str = Field(default="", description="学期，如 '2024-2025-1'，为空则查询全部")


class ScheduleInput(BaseModel):
    term: str = Field(..., description="学期，如 '2024-2025-1'")
    week: str = Field(default="0", description="周次，'0' 为全部周")


# ============ 格式化函数 ============

def _format_grades(grades: list) -> str:
    """格式化成绩为字符串"""
    if not grades:
        return "未查询到成绩记录"

    lines = ["## 成绩查询结果\n"]
    lines.append(f"| 学期 | 课程名称 | 成绩 | 学分 |")
    lines.append(f"|------|----------|------|------|")

    for g in grades:
        lines.append(f"| {g.term} | {g.course_name} | {g.score} | {g.credit} |")

    return "\n".join(lines)


def _format_schedule(classes: list) -> str:
    """格式化课表为字符串"""
    if not classes:
        return "未查询到课表记录"

    lines = ["## 课表查询结果\n"]
    lines.append(f"| 课程名称 | 教师 | 周次 | 地点 | 星期 | 节次 |")
    lines.append(f"|----------|------|------|------|------|------|")

    for c in classes:
        lines.append(f"| {c.course_name} | {c.teacher} | {c.weeks} | {c.place} | {c.day_of_week} | {c.time_of_day} |")

    return "\n".join(lines)


def _format_ranks(ranks: list) -> str:
    """格式化排名为字符串"""
    if not ranks:
        return "未查询到排名记录"

    lines = ["## 专业排名结果\n"]
    lines.append(f"| 学期 | 总分 | 班级排名 | 平均分 |")
    lines.append(f"|------|------|----------|--------|")

    for r in ranks:
        lines.append(f"| {r.term} | {r.total_score} | {r.class_rank} | {r.average_score} |")

    return "\n".join(lines)


def _format_level_exams(exams: list) -> str:
    """格式化等级考试为字符串"""
    if not exams:
        return "未查询到等级考试记录"

    lines = ["## 等级考试成绩\n"]
    lines.append(f"| 科目 | 总分 | 等级 | 考试日期 |")
    lines.append(f"|------|------|------|----------|")

    for e in exams:
        lines.append(f"| {e.course} | {e.total_score} | {e.total_level} | {e.exam_date} |")

    return "\n".join(lines)


# ============ 工具工厂函数 ============

def create_jwc_tools(ctx: ToolContext) -> List[BaseTool]:
    """
    创建 JWC 工具（依赖 ToolContext，利用闭包隐藏 user_id）

    关键设计：
    - user_id 完全隐藏在闭包中，大模型看不到
    - 工具签名只包含业务参数（term, week 等）
    - 内部进行认证检查，返回友好提示
    """

    def _get_grades(term: str = "") -> str:
        """查询教务处成绩"""
        if not ctx.is_authenticated:
            return "请先登录后再查询成绩"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        try:
            service = JwcService(session)
            grades = service.get_grades(ctx.user_id, term)
            return _format_grades(grades)
        except Exception as e:
            logger.error(f"成绩查询失败: {e}")
            return f"成绩查询失败: {str(e)}"

    def _get_schedule(term: str, week: str = "0") -> str:
        """查询课表"""
        if not ctx.is_authenticated:
            return "请先登录后再查询课表"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        try:
            service = JwcService(session)
            classes, _ = service.get_schedule(ctx.user_id, term, week)
            return _format_schedule(classes)
        except Exception as e:
            logger.error(f"课表查询失败: {e}")
            return f"课表查询失败: {str(e)}"

    def _get_rank() -> str:
        """查询专业排名"""
        if not ctx.is_authenticated:
            return "请先登录后再查询排名"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        try:
            service = JwcService(session)
            ranks = service.get_rank(ctx.user_id)
            return _format_ranks(ranks)
        except Exception as e:
            logger.error(f"排名查询失败: {e}")
            return f"排名查询失败: {str(e)}"

    def _get_level_exams() -> str:
        """查询等级考试成绩"""
        if not ctx.is_authenticated:
            return "请先登录后再查询等级考试成绩"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        try:
            service = JwcService(session)
            exams = service.get_level_exams(ctx.user_id)
            return _format_level_exams(exams)
        except Exception as e:
            logger.error(f"等级考试查询失败: {e}")
            return f"等级考试查询失败: {str(e)}"

    return [
        StructuredTool.from_function(
            func=_get_grades,
            name="jwc_grade",
            description="查询学生的考试成绩。参数：term（学期，如 '2023-2024-1'），不传则查询所有学期成绩。"
        ),
        StructuredTool.from_function(
            func=_get_schedule,
            name="jwc_schedule",
            description="查询学生的课表。参数：term（学期，必填），week（周次，默认 0 查全部）。"
        ),
        StructuredTool.from_function(
            func=_get_rank,
            name="jwc_rank",
            description="查询学生的专业排名。不需要参数。"
        ),
        StructuredTool.from_function(
            func=_get_level_exams,
            name="jwc_level_exam",
            description="查询学生的等级考试成绩（如英语四六级、计算机等级考试等）。不需要参数。"
        ),
    ]


# ============ 兼容旧接口 ============

# 保留原有实现用于兼容
# ... (原有代码保持不变)
```

- [ ] **Step 3: 更新 __init__.py 导出工厂函数**

Modify: `backend/app/core/tools/jwc/__init__.py`

```python
from app.core.tools.jwc.tools import create_jwc_tools, JWC_TOOLS

__all__ = [
    "create_jwc_tools",
    "JWC_TOOLS",  # 保留旧接口
]
```

- [ ] **Step 4: 验证导入**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.tools.jwc import create_jwc_tools; print('JWC tools factory imported')"`

- [ ] **Step 5: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/core/tools/jwc/
git commit -m "feat(jwc): convert tools to factory function with closure for user_id"
```

---

### Task 2.2: 改造 Library 工具为工厂函数

**Files:**
- Modify: `backend/app/core/tools/library/tools.py` - 改为工厂函数

**Steps:**

- [ ] **Step 1: 阅读现有 tools.py**

Run: `cat /home/luorome/software/CampusMind/backend/app/core/tools/library/tools.py`

- [ ] **Step 2: 修改 library tools.py**

Modify: `backend/app/core/tools/library/tools.py`

添加工厂函数（图书馆工具不需要登录）:

```python
# 在文件末尾添加:

def create_library_tools(ctx: ToolContext) -> List[BaseTool]:
    """
    创建图书馆工具（不需要登录）

    Library 工具是公开的，所有用户都可以使用
    """

    def _search_library(keywords: str, page: int = 1, rows: int = 10) -> str:
        """搜索图书馆馆藏"""
        try:
            service = get_library_service()
            result = service.search(keywords, page, rows)
            return _format_search_result(result)
        except Exception as e:
            logger.error(f"Library search failed: {e}")
            return f"搜索失败: {str(e)}"

    def _get_book_location(record_id: int) -> str:
        """查询图书位置"""
        try:
            service = get_library_service()
            result = service.get_book_copies(record_id)
            return _format_copies_result(result)
        except Exception as e:
            logger.error(f"Library get copies failed: {e}")
            return f"查询失败: {str(e)}"

    return [
        StructuredTool.from_function(
            func=_search_library,
            name="library_search",
            description="搜索中南大学图书馆馆藏。根据关键词搜索图书，返回图书列表及其 record_id。可用于查找特定主题的图书。"
        ),
        StructuredTool.from_function(
            func=_get_book_location,
            name="library_get_book_location",
            description="查询图书的馆藏位置信息。根据搜索结果中的 record_id 查询该书的所有复本所在位置、可借状态等。"
        ),
    ]
```

- [ ] **Step 3: 添加导入**

在文件开头添加:
```python
from app.core.context import ToolContext
from langchain_core.tools import BaseTool
from typing import List
```

- [ ] **Step 4: 更新 __init__.py**

Modify: `backend/app/core/tools/library/__init__.py`

```python
from app.core.tools.library.tools import create_library_tools, library_search, library_get_book_location, LIBRARY_TOOLS

__all__ = [
    "create_library_tools",
    "library_search",
    "library_get_book_location",
    "LIBRARY_TOOLS",
]
```

- [ ] **Step 5: 验证导入**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.tools.library import create_library_tools; print('Library tools factory imported')"`

- [ ] **Step 6: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/core/tools/library/
git commit -m "feat(library): convert tools to factory function"
```

---

## Chunk 3: AgentFactory 创建

### Task 3.1: 创建 AgentFactory

**Files:**
- Create: `backend/app/core/agents/factory.py` - AgentFactory 类

**Steps:**

- [ ] **Step 1: 创建 factory.py**

Create file: `backend/app/core/agents/factory.py`

```python
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
from app.core.tools.library import create_library_tools
from app.core.tools.rag_tool import create_rag_tool

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Agent 工厂，根据用户登录状态创建不同的 Agent

    设计原则：
    - 登录用户：JWC + Library + RAG tools
    - 未登录用户：Library + RAG tools
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

重要：这些工具不需要你接收 user_id 参数，系统会自动处理用户身份。"""
        else:
            base_prompt += """

当前为游客模式，你可以使用以下公开工具：
- library_search: 搜索图书馆馆藏
- library_get_book_location: 查询图书位置
- rag_search: 搜索知识库

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

        # RAG 工具（始终可用）
        if knowledge_ids:
            for kid in knowledge_ids:
                tools.append(create_rag_tool(knowledge_ids=[kid]))

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
```

- [ ] **Step 2: 更新 agents/__init__.py**

Modify: `backend/app/core/agents/__init__.py`

```python
from app.core.agents.react_agent import ReactAgent
from app.core.agents.factory import AgentFactory, get_agent_factory, initialize_agent_factory

__all__ = [
    "ReactAgent",
    "AgentFactory",
    "get_agent_factory",
    "initialize_agent_factory",
]
```

- [ ] **Step 3: 验证导入**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.agents.factory import AgentFactory; print('AgentFactory imported')"`

- [ ] **Step 4: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/core/agents/factory.py backend/app/core/agents/__init__.py
git commit -m "feat(agents): add AgentFactory for creating agents with context"
```

---

## Chunk 4: API 层 - 认证依赖和登录接口

### Task 4.1: 创建认证依赖注入

**Files:**
- Create: `backend/app/api/dependencies.py` - 认证依赖

**Steps:**

- [ ] **Step 1: 创建 dependencies.py**

Create file: `backend/app/api/dependencies.py`

```python
"""
API 依赖注入
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import jwt_manager

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    从 JWT 获取当前用户信息（必需认证）

    如果 token 无效或过期，返回 401 错误
    """
    token = credentials.credentials
    payload = jwt_manager.decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    可选的用户认证

    有 token 则解析，无 token 则返回 None
    适用于公开接口但支持登录用户获取更多功能
    """
    if credentials is None:
        return None

    token = credentials.credentials
    return jwt_manager.decode_token(token)
```

- [ ] **Step 2: 验证导入**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.api.dependencies import get_current_user, get_optional_user; print('Dependencies imported')"`

- [ ] **Step 3: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/api/dependencies.py
git commit -m "feat(auth): add JWT authentication dependencies"
```

---

### Task 4.2: 创建登录接口

**Files:**
- Create: `backend/app/api/v1/auth.py` - 登录/登出接口

**Steps:**

- [ ] **Step 1: 创建 auth.py**

Create file: `backend/app/api/v1/auth.py`

```python
"""
认证 API - 登录/登出接口
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from app.config import settings
from app.core.security import jwt_manager
from app.core.session.manager import UnifiedSessionManager
from app.core.session.factory import get_session_manager
from app.core.session.rate_limiter import LoginRateLimiter
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])


# ============ Request/Response Models ============

class LoginRequest(BaseModel):
    """登录请求"""
    username: str  # 学号
    password: str
    subsystem: str = "jwc"  # 默认教务系统


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user_id: str
    expires_in: int  # 秒


class LogoutRequest(BaseModel):
    """登出请求"""
    user_id: str


class RefreshRequest(BaseModel):
    """刷新 token 请求"""
    pass


# ============ 速率限制器 ============

_rate_limiter = LoginRateLimiter()


# ============ API Endpoints ============

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录接口

    流程：
    1. 检查登录频率
    2. 调用 CAS 登录获取子系统 session
    3. 存储 subsystem session
    4. 生成 JWT 返回
    """
    # 1. 登录频率检查
    try:
        _rate_limiter.check(request.username)
    except Exception as e:
        logger.warning(f"Login rate limit exceeded for {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录过于频繁，请稍后再试: {str(e)}"
        )

    # 2. 获取 session manager
    session_manager = get_session_manager()

    # 3. 调用 CAS 登录
    try:
        from app.core.session import cas_login
        from app.core.session.manager import SUBSYSTEM_SERVICE_URLS

        service_url = SUBSYSTEM_SERVICE_URLS.get(request.subsystem)
        if not service_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"未知的子系统: {request.subsystem}"
            )

        session = cas_login.cas_login(
            request.username,
            request.password,
            service_url,
            _rate_limiter
        )
    except Exception as e:
        logger.error(f"CAS login failed for {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"登录失败: {str(e)}"
        )

    # 4. 存储 subsystem session
    try:
        session_manager._cache.set(request.username, request.subsystem, session)
        session_manager._persistence.save(
            request.username,
            request.subsystem,
            session,
            settings.session_ttl_seconds
        )
    except Exception as e:
        logger.error(f"Failed to save session for {request.username}: {e}")
        # 不阻塞登录成功，只是警告

    # 5. 生成 JWT
    token = jwt_manager.create_token({"user_id": request.username})

    logger.info(f"User {request.username} logged in successfully")

    return LoginResponse(
        token=token,
        user_id=request.username,
        expires_in=settings.jwt_expire_hours * 3600
    )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    用户登出接口

    清除用户的 subsystem session
    """
    # 验证权限：只能登出自己的账号
    if current_user.get("user_id") != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作"
        )

    # 清除 session
    session_manager = get_session_manager()
    session_manager.invalidate_session(request.user_id)

    logger.info(f"User {request.user_id} logged out")

    return {"message": "登出成功"}


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    刷新 JWT token
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录"
        )

    user_id = current_user["user_id"]
    new_token = jwt_manager.create_token({"user_id": user_id})

    return LoginResponse(
        token=new_token,
        user_id=user_id,
        expires_in=settings.jwt_expire_hours * 3600
    )
```

- [ ] **Step 2: 注册路由**

Modify: `backend/app/api/v1/index.py` 添加:

```python
from app.api.v1 import auth

router.include_router(auth.router)
```

- [ ] **Step 3: 验证导入**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.api.v1.auth import router; print('Auth router imported')"`

- [ ] **Step 4: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/api/v1/auth.py backend/app/api/v1/index.py
git commit -m "feat(auth): add login/logout/refresh API endpoints"
```

---

### Task 4.3: 修改 completion 接口集成认证

**Files:**
- Modify: `backend/app/api/v1/completion.py` - 集成认证依赖

**Steps:**

- [ ] **Step 1: 阅读现有 completion.py**

确认现有实现需要修改的部分

- [ ] **Step 2: 修改 completion.py**

在文件开头添加导入:
```python
from app.api.dependencies import get_optional_user
from app.core.agents.factory import get_agent_factory, initialize_agent_factory
from app.core.session.factory import get_session_manager
```

修改 `completion_stream` 函数签名:
```python
@router.post("/completion/stream")
async def completion_stream(
    request: CompletionRequest,
    current_user: Optional[dict] = Depends(get_optional_user)  # 改为可选认证
):
    # current_user 可能为 None（未登录）或 {user_id: "xxx"}（已登录）
    user_id = current_user.get("user_id") if current_user else None

    # 初始化 AgentFactory（如果是首次）
    try:
        agent_factory = get_agent_factory()
    except RuntimeError:
        # 首次初始化
        initialize_agent_factory(get_session_manager())
        agent_factory = get_agent_factory()

    # 创建 Agent（根据 user_id 自动选择工具）
    agent = agent_factory.create_agent(
        user_id=user_id,
        knowledge_ids=request.knowledge_ids,
        model_name=request.model
    )

    # ... 其余代码保持不变
```

- [ ] **Step 3: 验证语法**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.api.v1.completion import router; print('Completion router OK')"`

- [ ] **Step 4: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/api/v1/completion.py
git commit -m "feat(completion): integrate JWT authentication with optional user"
```

---

## Chunk 5: 集成测试

### Task 5.1: 创建集成测试

**Files:**
- Create: `backend/tests/core/test_agent_integration.py` - 集成测试

**Steps:**

- [ ] **Step 1: 创建集成测试**

Create file: `backend/tests/core/test_agent_integration.py`

```python
"""
集成测试：Agent + Tools + Auth

测试场景：
1. 未登录用户只能使用 Library 和 RAG 工具
2. 登录用户可以使用 JWC + Library + RAG 工具
3. JWT token 解析正确
4. ToolContext 正确传递 user_id
"""
import pytest
from unittest.mock import Mock, MagicMock

from app.core.context import ToolContext
from app.core.agents.factory import AgentFactory
from app.core.tools.jwc import create_jwc_tools
from app.core.tools.library import create_library_tools


class TestToolContext:
    """测试 ToolContext"""

    def test_unauthenticated_context(self):
        """未登录上下文"""
        ctx = ToolContext()
        assert not ctx.is_authenticated
        assert ctx.user_id is None
        assert ctx.get_subsystem_session("jwc") is None

    def test_authenticated_context(self):
        """已登录上下文"""
        mock_manager = Mock()
        mock_session = Mock()
        mock_manager.get_session.return_value = mock_session

        ctx = ToolContext(user_id="123456", session_manager=mock_manager)
        assert ctx.is_authenticated
        assert ctx.user_id == "123456"

        session = ctx.get_subsystem_session("jwc")
        mock_manager.get_session.assert_called_once_with("123456", "jwc")
        assert session == mock_session


class TestJwcToolsFactory:
    """测试 JWC 工具工厂"""

    def test_tools_hide_user_id(self):
        """工具函数签名不包含 user_id"""
        mock_manager = Mock()
        ctx = ToolContext(user_id="123456", session_manager=mock_manager)

        tools = create_jwc_tools(ctx)

        # 检查工具名称
        tool_names = [t.name for t in tools]
        assert "jwc_grade" in tool_names
        assert "jwc_schedule" in tool_names
        assert "jwc_rank" in tool_names
        assert "jwc_level_exam" in tool_names

        # 检查参数签名 - 不应该包含 user_id
        grade_tool = next(t for t in tools if t.name == "jwc_grade")
        params = grade_tool.args_schema.model_fields
        assert "user_id" not in params
        assert "term" in params

    def test_unauthenticated_returns_message(self):
        """未登录时返回提示消息"""
        ctx = ToolContext()  # 未认证
        tools = create_jwc_tools(ctx)

        grade_tool = next(t for t in tools if t.name == "jwc_grade")
        result = grade_tool.func(term="")

        assert "请先登录" in result


class TestLibraryToolsFactory:
    """测试 Library 工具工厂"""

    def test_tools_available_without_auth(self):
        """图书馆工具无需认证"""
        ctx = ToolContext()  # 未认证
        tools = create_library_tools(ctx)

        tool_names = [t.name for t in tools]
        assert "library_search" in tool_names
        assert "library_get_book_location" in tool_names


class TestAgentFactory:
    """测试 AgentFactory"""

    def test_create_agent_for_anonymous(self):
        """为匿名用户创建 Agent"""
        mock_manager = Mock()
        factory = AgentFactory(mock_manager)

        agent = factory.create_agent(
            user_id=None,
            knowledge_ids=[]
        )

        # 检查 system prompt 包含游客模式
        assert "游客模式" in agent.system_prompt

    def test_create_agent_for_authenticated(self):
        """为登录用户创建 Agent"""
        mock_manager = Mock()
        factory = AgentFactory(mock_manager)

        agent = factory.create_agent(
            user_id="123456",
            knowledge_ids=[]
        )

        # 检查 system prompt 包含用户信息
        assert "123456" in agent.system_prompt
        assert "已登录" in agent.system_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

- [ ] **Step 2: 运行测试**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/core/test_agent_integration.py -v`

- [ ] **Step 3: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/tests/core/test_agent_integration.py
git commit -m "test: add integration tests for agent factory"
```

---

## 完成

实现计划已完成。每个 chunk 都是自包含的，可以独立实现和测试。

**计划保存路径**: `docs/superpowers/plans/2026-03-17-langgraph-tool-integration-plan.md`

Ready to execute?
