# CampusMind E2E 测试指南

## 快速开始

### 环境要求

```bash
cd /home/luorome/software/CampusMind/backend

# 确保 .env 配置正确
CAS_USERNAME="your_student_id"
CAS_PASSWORD="your_password"
OPENAI_MODEL=MiniMax-M2.5
```

### 启动测试

```bash
# 方式1: 直接运行（需要先启动后端）
uv run uvicorn app.main:app --reload --port 8000 &
sleep 3
uv run pytest tests/e2e/ -m public_tools -v

# 方式2: tmux 分屏（推荐）
tmux new-session -d -s CampusMind_Test -c /home/luorome/software/CampusMind/backend
tmux split-window -h -t CampusMind_Test
tmux send-keys -t CampusMind_Test:0.0 'uv run uvicorn app.main:app --reload --port 8000' Enter
sleep 3
tmux send-keys -t CampusMind_Test:0.1 'cd /home/luorome/software/CampusMind/backend && uv run pytest tests/e2e/ -m public_tools -v' Enter
tmux attach -t CampusMind_Test
```

---

## 测试结构

```
tests/e2e/
├── conftest.py                      # Fixtures 和配置
├── test_auth.py                     # 认证测试
├── test_streaming_completion.py     # 流式 API 测试
├── test_public_tools.py             # 公开工具测试
├── test_authenticated_tools.py      # 认证工具测试
├── test_multi_tool_calls.py         # 多工具测试
└── README.md                        # 英文使用指南
```

### Fixtures (conftest.py)

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `http_session` | session | HTTP 会话复用 |
| `authenticated_token` | function | 从 .env 获取 JWT Token |
| `auth_headers` | function | Authorization 请求头 |
| `base_url` | session | API 基础 URL |
| `test_credentials` | session | CAS 凭据 |

### SSE 解析辅助

```python
from tests.e2e.conftest import parse_sse_stream, StreamingResponse

# 发送流式请求
response = http_session.post(
    f"{API_V1}/completion/stream",
    json={"message": "查询", "knowledge_ids": [], "user_id": "test", "enable_rag": False},
    headers={"Accept": "text/event-stream"},
    stream=True,
    timeout=120
)

# 解析 SSE 流
result = parse_sse_stream(response)

# 验证结果
assert result.success
assert "library_search" in result.get_tool_names_called()
```

---

## 测试命令

```bash
# 按标记运行
uv run pytest tests/e2e/ -m public_tools -v        # 公开工具
uv run pytest tests/e2e/ -m auth_required -v      # 需要认证
uv run pytest tests/e2e/ -m auth_tools -v         # 认证工具
uv run pytest tests/e2e/ -m e2e -v                # 所有 E2E

# 运行特定测试
uv run pytest tests/e2e/test_public_tools.py::TestPublicToolsViaCompletion::test_library_search_called_for_book_query -v

# 详细输出
uv run pytest tests/e2e/ -m public_tools -v -s
```

---

## 测试用例

### public_tools (10 tests)

| 用例 | 说明 |
|------|------|
| `test_library_search_called_for_book_query` | 图书搜索工具调用 |
| `test_career_teachin_called_for_recruitment_event_query` | 宣讲会工具调用 |
| `test_career_campus_recruit_called_for_job_query` | 校园招聘工具调用 |
| `test_career_campus_intern_called_for_internship_query` | 实习岗位工具调用 |
| `test_career_jobfair_called_for_job_fair_query` | 招聘会工具调用 |
| `test_anonymous_user_can_access_all_public_tools` | 匿名用户多工具访问 |
| `test_library_search_returns_results` | 搜索返回结果 |
| `test_teachin_with_zone_filter` | 按校区筛选 |
| `test_campus_recruit_with_keyword` | 关键词搜索 |
| `test_campus_intern_with_keyword` | 实习关键词搜索 |

### auth_required (测试认证)

| 用例 | 说明 |
|------|------|
| `test_login_with_valid_credentials_succeeds` | 有效凭据登录 |
| `test_login_with_invalid_credentials_fails` | 无效凭据拒绝 |
| `test_login_rate_limiting` | 频率限制 |
| `test_logout_with_valid_token_succeeds` | 登出 |
| `test_logout_without_token_fails` | 无 Token 拒绝 |

### auth_tools (测试 JWC/OA 工具)

| 用例 | 说明 |
|------|------|
| `test_authenticated_user_can_query_grades` | 查询成绩 (jwc_grade) |
| `test_authenticated_user_can_query_schedule` | 查询课表 (jwc_schedule) |
| `test_authenticated_user_can_query_rank` | 查询排名 (jwc_rank) |
| `test_authenticated_user_can_query_level_exam` | 查询等级考试成绩 |
| `test_authenticated_user_can_query_notifications` | 查询通知 (oa_notification_list) |

### multi_tool (多工具场景)

| 用例 | 说明 |
|------|------|
| `test_multiple_public_tools_in_sequence` | 多公开工具顺序 |
| `test_multiple_authenticated_tools_in_sequence` | 多认证工具顺序 |
| `test_rag_combined_with_authenticated_tool` | RAG + 认证工具 |
| `test_complex_multi_step_query` | 复杂多步骤 |
| `test_tool_call_order_verification` | 工具调用顺序 |

---

## 常见问题

### 401 Unauthorized

**原因**: `HTTPBearer` 的 `auto_error=True` 导致无 Token 时直接返回 401

**修复**: `app/api/dependencies.py` 第 11 行
```python
security = HTTPBearer(auto_error=False)
```

### 模型不匹配

**原因**: 默认 `gpt-3.5-turbo` 在 MiniMax API 不可用

**修复**: 使用 `.env` 中的 `OPENAI_MODEL`
```python
# app/api/v1/completion.py
model: str = Field(default=settings.openai_model, ...)

# app/core/agents/factory.py
if model_name is None:
    model_name = settings.openai_model
```

### tmux 不显示日志

**原因**: loguru 默认输出到 stderr

**修复**: `app/main.py`
```python
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

---

## pytest.ini 配置

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    auth_required: Tests requiring authentication
    public_tools: Public tools tests (no auth)
    auth_tools: Authenticated tools tests
```

---

## 调试技巧

### 查看后端日志
```bash
tmux capture-pane -t CampusMind_Test:0.0 -p | tail -30
```

### SSE 事件解析
```python
for event in result.events:
    print(f"{event.type}: {event.data}")
```

### 提取工具调用
```python
tool_names = result.get_tool_names_called()
# ['library_search', 'career_teachin', ...]
```

### 提取工具参数
```python
for event in result.events:
    if event.type == "event" and event.data.get("status") == "START":
        title = event.data.get("title", "")
        message = event.data.get("message", "")
```

---

## 相关文档

- [测试进度](./e2e-test-progress.md) - 测试用例执行状态
- [问题排查日志](./e2e-debug-log.md) - 已解决问题记录

## 参考

- [pytest 文档](https://docs.pytest.org/)
- [requests 流式请求](https://docs.python-requests.org/)
- [SSE 规范](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
