# E2E 测试问题排查与修复日志

> 最后更新: 2026-03-19

---

## 问题 #001: HTTPBearer 导致 401 Unauthorized

**发现日期**: 2026-03-19
**测试类别**: public_tools
**严重程度**: 🔴 高

### 症状

所有公开工具测试请求返回 `401 Unauthorized`：
```
AssertionError: Request failed: HTTP 401: {"detail":"Not authenticated"}
```

### 排查过程

1. **检查后端日志**
   ```bash
   curl -s http://localhost:8000/health  # 正常返回
   ```

2. **检查认证端点**
   ```bash
   # 直接调用 login 端点 - 正常
   # 说明认证本身没问题
   ```

3. **检查 dependencies.py**
   ```python
   # app/api/dependencies.py
   security = HTTPBearer()  # auto_error=True (默认)
   ```

4. **定位根因**
   - `HTTPBearer()` 默认 `auto_error=True`
   - 当请求没有 `Authorization` 头时，直接返回 401
   - 永远不会执行到 `get_optional_user` 函数

### 修复方案

```python
# app/api/dependencies.py 第 11 行
security = HTTPBearer(auto_error=False)
```

### 验证

```bash
# 修复后测试
curl -s -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"test","knowledge_ids":[],"user_id":"test","enable_rag":false}'

# 不再返回 401，返回 200
```

### 相关文件

- `app/api/dependencies.py`

---

## 问题 #002: 模型名称不匹配

**发现日期**: 2026-03-19
**测试类别**: public_tools
**严重程度**: 🔴 高

### 症状

Agent 执行返回错误：
```
ERROR: Agent Execution Error: invalid params, unknown model 'gpt-3.5-turbo' (2013)
```

### 排查过程

1. **检查 .env 配置**
   ```bash
   grep OPENAI_MODEL .env
   # OPENAI_MODEL=MiniMax-M2.5
   ```

2. **检查代码**
   ```python
   # app/api/v1/completion.py
   model: str = Field(default="gpt-3.5-turbo", ...)

   # app/core/agents/factory.py
   model_name: str = "gpt-3.5-turbo"  # 硬编码默认值
   ```

3. **定位根因**
   - 请求中 `model` 字段使用硬编码的 `gpt-3.5-turbo`
   - MiniMax API 不支持该模型名
   - `.env` 中配置的 `MiniMax-M2.5` 未被使用

### 修复方案

```python
# app/api/v1/completion.py
from app.config import settings

# 第 73 行
model: str = Field(default=settings.openai_model, description="LLM model to use")

# 第 86 行
def get_llm(model_name: str = None) -> ChatOpenAI:
    if model_name is None:
        model_name = settings.openai_model
```

```python
# app/core/agents/factory.py

# 第 106 行
model_name: str = None

# 第 119 行
if model_name is None:
    model_name = settings.openai_model
```

### 验证

```bash
# 修复后，后端日志显示
INFO | Tool library_search executed. Args: {'keywords': 'Python'}, Result: 共找到 3155 条结果
```

### 相关文件

- `app/api/v1/completion.py`
- `app/core/agents/factory.py`

---

## 问题 #003: loguru 日志不显示

**发现日期**: 2026-03-19
**测试类别**: tmux 分屏调试
**严重程度**: 🟡 中

### 症状

在 tmux 分屏中，后端 pane 显示空白或只有 uvicorn 启动信息，看不到应用日志。

### 排查过程

1. **检查 tmux 配置**
   ```bash
   tmux capture-pane -t CampusMind_Test:0.0 -p
   # 只显示:
   # INFO: Will watch for changes in these directories
   # INFO: Uvicorn running on http://127.0.0.1:8000
   ```

2. **检查 loguru 配置**
   ```python
   # app/main.py
   from loguru import logger
   # 只导入了，没有配置
   ```

3. **定位根因**
   - loguru 默认输出到 `stderr`
   - uvicorn `--reload` 模式可能不正确处理 stderr
   - 需要显式配置输出到 `stdout`

### 修复方案

```python
# app/main.py
import sys
from loguru import logger

logger.configure(
    handlers=[{
        "sink": sys.stdout,
        "level": "INFO",
        "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {message}",
    }]
)
```

### 验证

```bash
# 修复后，tmux 后端 pane 显示
2026-03-19 18:04:08.983 | INFO | app.core.agents.react_agent | Tool library_search executed...
```

### 相关文件

- `app/main.py`

---

## 问题 #004: pytest-timeout 不存在

**发现日期**: 2026-03-19
**测试类别**: 命令行参数
**严重程度**: 🟢 低

### 症状

运行 `pytest --timeout=120` 报错：
```
pytest: error: unrecognized arguments: --timeout=120
```

### 排查过程

1. **检查 pytest.ini**
   ```ini
   addopts = -v --strict-markers
   # 没有 --timeout 参数
   ```

2. **检查已安装包**
   ```bash
   uv pip list | grep timeout
   # 没有安装 pytest-timeout
   ```

### 修复方案

不需要修复。pytest 默认会对每个测试设置合理的超时（通常是 2 分钟）。如需明确超时，可安装 `pytest-timeout` 包。

### 相关文件

- `pytest.ini`

---

## 问题 #005: get_current_user 在 credentials 为 None 时返回 500

**发现日期**: 2026-03-19
**测试类别**: auth_required
**严重程度**: 🔴 高

### 症状

`test_logout_without_token_fails` 测试失败：
```
AssertionError: Expected 401 for unauthenticated logout, got 500
```

### 排查过程

1. **检查后端日志**
   - 没有详细的错误堆栈信息
   - 只有测试发送的请求日志

2. **检查 logout 端点代码**
   ```python
   # app/api/v1/auth.py 第 106-110 行
   @router.post("/logout")
   async def logout(
       request: LogoutRequest,
       current_user: dict = Depends(get_current_user)
   ):
   ```

3. **检查 get_current_user 实现**
   ```python
   # app/api/dependencies.py 第 14-22 行
   async def get_current_user(
       credentials: HTTPAuthorizationCredentials = Depends(security)
   ) -> dict:
       token = credentials.credentials  # ← 这里是问题！
   ```

4. **定位根因**
   - `HTTPBearer(auto_error=False)` 使得没有 Authorization 头时 `credentials` 为 `None`
   - `get_current_user` 直接访问 `credentials.credentials`
   - `None.credentials` 抛出 `AttributeError` → 500 Internal Server Error

### 修复方案

```python
# app/api/dependencies.py
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    # ... 其余代码不变
```

### 验证

```bash
# 修复后测试
curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test"}'

# 返回 401 Unauthorized
```

### 相关文件

- `app/api/dependencies.py`

---

## 问题 #006: CAS 账号被锁定

**发现日期**: 2026-03-19
**测试类别**: auth_required
**严重程度**: 🔴 高

### 症状

登录测试返回 401 错误：
```
AssertionError: Expected 200, got 401: {"detail":"登录失败: 账号可能被锁定"}
```

### 排查过程

1. **检查错误信息**
   - 错误提示"账号可能被锁定"
   - 这是 CAS 系统的安全机制

2. **定位根因**
   - 多次登录尝试导致账号被锁定
   - 需要等待一段时间（通常是几分钟到几十分钟）自动解锁
   - 或联系管理员手动解锁

### 解决方案

1. **等待自动解锁**（推荐）
   - CAS 账号通常会在几分钟到几十分钟后自动解锁
   - 稍后再运行测试

2. **使用备用账号**
   - 如果有备用测试账号，更新 `.env` 文件

3. **联系管理员**
   - 如果急需解锁，联系 CAS 系统管理员

### 相关文件

- `backend/.env` (CAS_USERNAME, CAS_PASSWORD)

---

## 问题 #007: oa_notification_list 缺少 ctx 参数

**发现日期**: 2026-03-19
**测试类别**: auth_tools
**严重程度**: 🔴 高

### 症状

工具调用报错：
```
ERROR: oa_notification_list Error: _query_notifications() missing 1 required positional argument: 'ctx'
```

### 排查过程

1. **检查错误信息**
   - `_query_notifications()` 缺少 `ctx` 参数

2. **检查工具定义**
   ```python
   # app/core/tools/oa/__init__.py (修复前)
   def create_oa_tools(ctx: ToolContext) -> List:
       return [OANotificationListTool]  # ctx 未被使用！

   # app/core/tools/oa/notification.py
   OANotificationListTool = StructuredTool.from_function(
       func=_query_notifications,  # _query_notifications 有 ctx 参数
       ...
   )
   ```

3. **定位根因**
   - `_query_notifications` 是顶层函数，有 `ctx` 参数
   - 但 `create_oa_tools` 直接返回工具实例，没有通过闭包捕获 `ctx`
   - LangChain 的 `StructuredTool.from_function()` 不会自动注入 `ctx`

### 修复方案

参照 `jwc/tools.py` 的正确模式，使用内部函数闭包捕获 `ctx`：

```python
# app/core/tools/oa/__init__.py
def create_oa_tools(ctx: ToolContext) -> List:
    def _query_notifications(
        qssj: Optional[str] = None,
        ...
    ) -> str:
        # ctx 通过闭包被捕获
        if not ctx.is_authenticated:
            return "请先登录后再使用校内通知查询"
        session = ctx.get_subsystem_session("oa")
        ...

    return [
        StructuredTool.from_function(
            func=_query_notifications,  # 使用内部函数
            name="oa_notification_list",
            ...
        ),
    ]
```

### 验证

```bash
# 修复后，工具调用不再报错
uv run pytest tests/e2e/test_authenticated_tools.py::TestOaTools -v
# 全部 PASSED
```

### 相关文件

- `app/core/tools/oa/__init__.py`
- `app/core/tools/oa/notification.py`
- `app/core/tools/jwc/tools.py` (参考)

---

## 问题 #008: OA 通知查询 JSON 解析失败 (UTF-8 BOM)

**发现日期**: 2026-03-19
**测试类别**: multi_tool
**严重程度**: 🟡 中

### 症状

OA 通知查询返回错误：
```
JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)
```

### 排查过程

1. **检查响应内容**
   - OA 系统返回的响应包含 UTF-8 BOM
   - `resp.json()` 无法直接解析

2. **添加调试日志**
   - 将失败的响应内容保存到文件
   - 确认是 BOM 问题

### 修复方案

```python
# app/core/tools/oa/__init__.py
def _decode_json_with_bom(response: requests.Response) -> dict:
    """Decode JSON response, handling various encoding issues."""
    try:
        return response.json()
    except json.JSONDecodeError as e:
        logger.info(f"Standard JSON parsing failed: {e}, trying alternative encodings...")
        encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"]
        for encoding in encodings:
            try:
                return json.loads(response.content.decode(encoding))
            except Exception:
                continue
        raise
```

### 验证

```bash
# 修复后测试
uv run pytest tests/e2e/test_multi_tool_calls.py -v
# test_oas_notification_with_multiple_filters PASSED
# test_rapid_sequential_requests PASSED
```

### 相关文件

- `app/core/tools/oa/__init__.py`

---

## 问题模板

复制以下模板记录新问题：

---

## 问题 #XXX: [简短描述]

**发现日期**: YYYY-MM-DD
**测试类别**: xxx
**严重程度**: 🔴🟡🟢

### 症状

描述具体错误现象。

### 排查过程

1. 步骤1
2. 步骤2
3. 步骤3

### 修复方案

```python
# 相关代码
```

### 验证

```bash
# 验证命令和结果
```

### 相关文件

- `file1.py`
- `file2.py`
