# LangGraph 工具集成设计文档

**日期**: 2026-03-17
**主题**: JWC、Library 工具与 LangGraph Agent 最佳实践集成
**目标**: 将新增的 JWC 和 Library 工具集成到现有的 ReactAgent，并支持用户认证

---

## 1. 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                        │
│                                                                  │
│  POST /auth/login          → 验证账号 → 调用 CAS → 返回 JWT     │
│  GET /completion/stream   → 解析 JWT → 注入 user_id → Agent    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ToolContext (运行时)                          │
│                                                                  │
│  class ToolContext:                                             │
│      user_id: str           # 从 JWT 解码得到                   │
│      session_manager: UnifiedSessionManager  # 子系统会话管理   │
│      subsystem_sessions: dict  # 缓存各子系统 session          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Tool Factory (工具工厂)                        │
│                                                                  │
│  def create_jwc_tools(ctx: ToolContext) -> List[BaseTool]      │
│  def create_library_tools(ctx: ToolContext) -> List[BaseTool] │
│  def create_rag_tools(ctx: ToolContext) -> List[BaseTool]     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ReactAgent (LangGraph)                        │
│                                                                  │
│  登录用户: JWC + Library + RAG tools                           │
│  未登录:   Library + RAG tools                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 核心组件

### 2.1 ToolContext 类

```python
class ToolContext:
    """工具运行时上下文，包含用户身份和会话管理"""

    def __init__(
        self,
        user_id: Optional[str] = None,
        session_manager: Optional[UnifiedSessionManager] = None
    ):
        self.user_id = user_id
        self.session_manager = session_manager
        self._subsystem_cache: Dict[str, Any] = {}

    @property
    def is_authenticated(self) -> bool:
        """用户是否已登录"""
        return self.user_id is not None and self.session_manager is not None

    def get_subsystem_session(self, subsystem: str) -> Optional[Dict]:
        """获取子系统 session，必要时自动登录"""
        if not self.is_authenticated:
            return None

        # 先检查缓存
        if subsystem in self._subsystem_cache:
            return self._subsystem_cache[subsystem]

        # 从 session_manager 获取
        session = self.session_manager.get(self.user_id, subsystem)

        # 如果失效，尝试重新登录
        if session and session.is_expired():
            session = self.session_manager.refresh(self.user_id, subsystem)

        if session:
            self._subsystem_cache[subsystem] = session

        return session
```

### 2.2 工具工厂函数（关键：闭包隐藏 user_id）

#### JWC 工具

```python
def create_jwc_tools(ctx: ToolContext) -> List[BaseTool]:
    """创建 JWC 工具（依赖 ToolContext，利用闭包隐藏 user_id）"""

    def _get_grades(term: str = "") -> str:
        """查询教务处成绩。参数：term（学期，如 '2023-2024-1'）"""
        if not ctx.is_authenticated:
            return "请先登录后再查询成绩"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        service = JwcService(session)
        grades = service.get_grades(ctx.user_id, term)
        return _format_grades(grades)

    def _get_schedule(term: str, week: str = "0") -> str:
        """查询课表"""
        if not ctx.is_authenticated:
            return "请先登录后再查询课表"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        service = JwcService(session)
        classes, start_week_day = service.get_schedule(ctx.user_id, term, week)
        return _format_schedule(classes)

    def _get_rank() -> str:
        """查询专业排名"""
        if not ctx.is_authenticated:
            return "请先登录后再查询排名"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        service = JwcService(session)
        ranks = service.get_rank(ctx.user_id)
        return _format_ranks(ranks)

    def _get_level_exams() -> str:
        """查询等级考试成绩"""
        if not ctx.is_authenticated:
            return "请先登录后再查询等级考试成绩"

        session = ctx.get_subsystem_session("jwc")
        if not session:
            return "教务系统会话已过期，请重新登录"

        service = JwcService(session)
        exams = service.get_level_exams(ctx.user_id)
        return _format_level_exams(exams)

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
```

#### Library 工具（不需要登录）

```python
def create_library_tools(ctx: ToolContext) -> List[BaseTool]:
    """创建图书馆工具（不需要登录）"""

    def _search_library(keywords: str, page: int = 1, rows: int = 10) -> str:
        """搜索图书馆馆藏"""
        service = get_library_service()
        result = service.search(keywords, page, rows)
        return _format_search_result(result)

    def _get_book_location(record_id: int) -> str:
        """查询图书位置"""
        service = get_library_service()
        result = service.get_book_copies(record_id)
        return _format_copies_result(result)

    return [
        StructuredTool.from_function(
            func=_search_library,
            name="library_search",
            description="搜索中南大学图书馆馆藏。根据关键词搜索图书，返回图书列表及其 record_id。"
        ),
        StructuredTool.from_function(
            func=_get_book_location,
            name="library_get_book_location",
            description="查询图书的馆藏位置信息。根据搜索结果中的 record_id 查询该书的所有复本所在位置。"
        ),
    ]
```

### 2.3 AgentFactory

```python
class AgentFactory:
    """Agent 工厂，根据用户登录状态创建不同的 Agent"""

    def __init__(self, session_manager: UnifiedSessionManager):
        self.session_manager = session_manager

    def create_agent(
        self,
        user_id: Optional[str] = None,
        knowledge_ids: List[str] = None,
        model_name: str = "gpt-3.5-turbo"
    ) -> ReactAgent:

        # 创建上下文
        ctx = ToolContext(
            user_id=user_id,
            session_manager=self.session_manager if user_id else None
        )

        # 根据登录状态选择工具
        tools = []

        # 图书馆工具（始终可用）
        tools.extend(create_library_tools(ctx))

        # RAG 工具（始终可用）
        if knowledge_ids:
            tools.extend(create_rag_tools(ctx, knowledge_ids))

        # JWC 工具（需要登录）
        if ctx.is_authenticated:
            tools.extend(create_jwc_tools(ctx))

        # 创建 Agent
        system_prompt = self._build_system_prompt(ctx, knowledge_ids)

        return ReactAgent(
            model=get_llm(model_name),
            system_prompt=system_prompt,
            tools=tools
        )
```

---

## 3. Session 存储接口（预留 Redis）

```python
class SessionStorage(ABC):
    """Session 存储抽象接口"""

    @abstractmethod
    def get(self, user_id: str, subsystem: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def set(self, user_id: str, subsystem: str, session: Dict[str, Any], ttl: int = 3600):
        pass

    @abstractmethod
    def delete(self, user_id: str, subsystem: str = None):
        pass

    @abstractmethod
    def exists(self, user_id: str, subsystem: str) -> bool:
        pass


class RedisSessionStorage(SessionStorage):
    """Redis 存储实现（预留）"""

    def __init__(self, redis_url: str):
        import redis
        self.redis = redis.from_url(redis_url)

    def _key(self, user_id: str, subsystem: str) -> str:
        return f"session:{user_id}:{subsystem}"

    def get(self, user_id: str, subsystem: str) -> Optional[Dict]:
        import json
        data = self.redis.get(self._key(user_id, subsystem))
        return json.loads(data) if data else None

    def set(self, user_id: str, subsystem: str, session: Dict, ttl: int = 3600):
        import json
        self.redis.setex(self._key(user_id, subsystem), ttl, json.dumps(session))

    def delete(self, user_id: str, subsystem: str = None):
        if subsystem:
            self.redis.delete(self._key(user_id, subsystem))
        else:
            pattern = f"session:{user_id}:*"
            for key in self.redis.scan_iter(pattern):
                self.redis.delete(key)

    def exists(self, user_id: str, subsystem: str) -> bool:
        return self.redis.exists(self._key(user_id, subsystem)) > 0
```

---

## 4. JWT 实现

```python
class JWTManager:
    """JWT 令牌管理"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, payload: Dict[str, Any], expires_delta: timedelta = None) -> str:
        to_encode = payload.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def verify_token(self, token: str) -> bool:
        return self.decode_token(token) is not None
```

---

## 5. API 接口设计

### 5.1 认证接口

```python
# api/v1/auth.py
class LoginRequest(BaseModel):
    username: str
    password: str
    subsystem: str = "jwc"

class LoginResponse(BaseModel):
    token: str
    user_id: str
    expires_in: int


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录 - 调用 CAS 获取子系统 session"""

    # 1. 登录频率检查
    rate_limiter.check(request.username)

    # 2. 调用 CAS 登录
    session = await cas_login(request.username, request.password, request.subsystem)

    # 3. 存储 subsystem session
    session_manager.store(request.username, request.subsystem, session)

    # 4. 生成 JWT
    token = jwt_manager.create_token({"user_id": request.username})

    return LoginResponse(token=token, user_id=request.username, expires_in=86400)


@router.post("/auth/logout")
async def logout(request: LogoutRequest, current_user: Dict = Depends(get_current_user)):
    """用户登出"""
    session_manager.delete(request.user_id)
    return {"message": "登出成功"}
```

### 5.2 认证依赖注入

```python
# api/dependencies.py
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[Dict]:
    """从 JWT 获取当前用户信息"""
    token = credentials.credentials
    return jwt_manager.decode_token(token)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """可选的用户认证"""
    if credentials is None:
        return None
    return get_current_user(credentials)
```

### 5.3 流式对话接口

```python
# api/v1/completion.py
@router.post("/completion/stream")
async def completion_stream(
    request: CompletionRequest,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    user_id = current_user.get("user_id") if current_user else None

    agent = agent_factory.create_agent(
        user_id=user_id,
        knowledge_ids=request.knowledge_ids,
        model_name=request.model
    )

    return StreamingResponse(agent.astream(messages))
```

---

## 6. System Prompt 模板

```python
def _build_system_prompt(self, ctx: ToolContext, knowledge_ids: List[str] = None) -> str:
    base_prompt = """你是一个智能校园助手，可以帮助用户解答问题和查询信息。"""

    if knowledge_ids:
        base_prompt += f"\n当前可用的知识库 ID 列表: {knowledge_ids}"

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
```

---

## 7. 文件变更清单

| 操作 | 文件路径 | 说明 |
|------|----------|------|
| 新增 | `core/security.py` | JWT 工具类 |
| 新增 | `core/context.py` | ToolContext 类 |
| 新增 | `core/session/storage.py` | 存储抽象接口 + Redis 实现 |
| 新增 | `api/v1/auth.py` | 登录/登出接口 |
| 新增 | `api/dependencies.py` | 认证依赖注入 |
| 修改 | `core/tools/jwc/tools.py` | 改为工厂函数，闭包隐藏 user_id |
| 修改 | `core/tools/library/tools.py` | 改为工厂函数 |
| 修改 | `core/tools/__init__.py` | 导出工厂函数 |
| 修改 | `core/agents/factory.py` | 新增 AgentFactory |
| 修改 | `api/v1/completion.py` | 集成认证依赖 |
| 修改 | `config.py` | 添加 JWT 配置 |

---

## 8. 实现顺序

### Phase 1: 基础设施
1.1 JWT 工具类 (core/security.py)
1.2 ToolContext 类 (core/context.py)
1.3 Session 存储接口 + Redis 实现 (core/session/storage.py)

### Phase 2: 工具改造
2.1 改造 JWC 工具为工厂函数
2.2 改造 Library 工具为工厂函数
2.3 改造 RAG 工具为工厂函数

### Phase 3: Agent 集成
3.1 创建 AgentFactory
3.2 改造 ReactAgent 支持 ToolContext

### Phase 4: API 层
4.1 认证依赖注入 (api/dependencies.py)
4.2 登录接口 (api/v1/auth.py)
4.3 修改 completion 接口

### Phase 5: 配置与测试
5.1 添加配置项 + 集成测试
