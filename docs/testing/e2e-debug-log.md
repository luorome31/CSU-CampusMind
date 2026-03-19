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
