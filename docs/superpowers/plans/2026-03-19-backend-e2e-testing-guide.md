# CampusMind Backend E2E Testing Guide

**Purpose:** End-to-end testing guide for authentication, streaming chat requests, and tool calling flow.

**Base URL:** `http://localhost:8000/api/v1`

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client (Frontend)                           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTP/SSE
┌───────────────────────────────▼─────────────────────────────────────┐
│                     FastAPI Backend (:8000)                         │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────────┐  │
│  │ /auth/login │───▶│ JWT Manager  │───▶│ UnifiedSessionManager  │  │
│  └─────────────┘    └──────────────┘    └──────────┬─────────────┘  │
│                                                      │               │
│  ┌──────────────────────────────────────────────────▼─────────────┐  │
│  │                   /completion/stream (SSE)                      │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌────────────┐  │  │
│  │  │  AgentFactory   │───▶│   ReactAgent    │───▶│ LangGraph  │  │  │
│  │  │  (creates ctx)  │    │  (ReAct loop)   │    │  (graph)   │  │  │
│  │  └─────────────────┘    └────────┬────────┘    └────────────┘  │  │
│  │                                │                              │  │
│  │  ┌─────────────────────────────▼──────────────────────────────┐ │  │
│  │  │              Tools (structured by subsystem)               │ │  │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐  │ │  │
│  │  │  │ career/ │  │ library/│  │  jwc/   │  │    oa/    │  │ │  │
│  │  │  └─────────┘  └─────────┘  └─────────┘  └───────────┘  │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ Tool Calls
                    ┌───────────▼───────────┐
                    │   External APIs       │
                    │  - CAS (ca.csu.edu.cn)│
                    │  - JWC (csujwc)       │
                    │  - Library (lib.csu)  │
                    │  - OA (oa.csu.edu.cn) │
                    └───────────────────────┘
```

---

## 2. Authentication Flow

### 2.1 Login Endpoint

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```json
{
  "username": "YOUR_STUDENT_ID",
  "password": "YOUR_PASSWORD"
}
```

**Response (Success 200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "2020123456",
  "expires_in": 86400
}
```

**Error Responses:**
| Status | Detail |
|--------|--------|
| 401 | 登录失败: 用户名或密码错误 |
| 401 | 登录失败: 账号可能被锁定 |
| 429 | 登录过于频繁，请等待 XX 秒后再试 |

### 2.2 Authentication Header

All subsequent requests requiring authentication must include:

```
Authorization: Bearer <token>
```

### 2.3 Logout Endpoint

**Endpoint:** `POST /api/v1/auth/logout`

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "user_id": "2020123456"
}
```

**Response (200):**
```json
{
  "message": "登出成功"
}
```

### 2.4 Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Headers:** `Authorization: Bearer <token>`

**Response:** Same as login response with new token.

---

## 3. Streaming Completion API

### 3.1 Main Streaming Endpoint

**Endpoint:** `POST /api/v1/completion/stream`

**Headers:**
```
Authorization: Bearer <token>  (optional - enables more tools)
Content-Type: application/json
```

**Request:**
```json
{
  "message": "查询学校办公室最近的通知",
  "knowledge_ids": ["kb-uuid-1"],
  "user_id": "2020123456",
  "dialog_id": null,
  "enable_rag": true,
  "top_k": 5,
  "min_score": 0.0,
  "model": "gpt-3.5-turbo"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ | User's message/query |
| `knowledge_ids` | string[] | if enable_rag=true | Knowledge base UUIDs for RAG |
| `user_id` | string | ✅ | User identifier |
| `dialog_id` | string/null | ❌ | For conversation history |
| `enable_rag` | boolean | ❌ | Enable RAG retrieval (default: true) |
| `top_k` | int | ❌ | Context chunks (default: 5) |
| `min_score` | float | ❌ | Minimum similarity score |
| `model` | string | ❌ | LLM model name |

### 3.2 SSE Response Format

The endpoint returns **Server-Sent Events (SSE)** with `Content-Type: text/event-stream`.

#### Event Types

**1. Tool Execution Start**
```
event: tool_start
data: {"type": "event", "timestamp": 1710816000.123, "data": {"title": "执行工具: oa_notification_list", "status": "START", "message": "参数: {...}"}}
```

**2. Tool Execution End**
```
event: tool_end
data: {"type": "event", "timestamp": 1710816001.456, "data": {"title": "执行工具: oa_notification_list", "status": "END", "message": "执行完成"}}
```

**3. Tool Execution Error**
```
event: tool_error
data: {"type": "event", "timestamp": 1710816001.789, "data": {"title": "执行工具: oa_notification_list", "status": "ERROR", "message": "执行工具 oa_notification_list 失败: ..."}}
```

**4. Model Response Chunk**
```
event: response_chunk
data: {"type": "response_chunk", "timestamp": 1710816002.012, "data": {"chunk": "根据查询结果，", "accumulated": "根据查询结果，学校办公室最近发布了以下通知："}}
```

#### Response Headers

```
Content-Type: text/event-stream
X-Dialog-ID: <dialog_uuid>
```

---

## 4. Tool Calling Flow

### 4.1 Available Tools by Auth State

| Tool | Anonymous | Authenticated |
|------|-----------|---------------|
| `rag_search` | ✅ | ✅ |
| `career_teachin` | ✅ | ✅ |
| `career_campus_recruit` | ✅ | ✅ |
| `career_campus_intern` | ✅ | ✅ |
| `career_jobfair` | ✅ | ✅ |
| `library_search` | ✅ | ✅ |
| `library_get_book_location` | ✅ | ✅ |
| `jwc_grade` | ❌ | ✅ |
| `jwc_schedule` | ❌ | ✅ |
| `jwc_rank` | ❌ | ✅ |
| `jwc_level_exam` | ❌ | ✅ |
| `oa_notification_list` | ❌ | ✅ |

### 4.2 Tool Execution Sequence

```
1. User sends message
2. LLM analyzes → decides to call tool(s)
3. Agent sends "START" event with tool name + parameters
4. Tool executes (may call external APIs like JWC/OA)
5. Agent sends "END" event
6. LLM receives tool result → generates response
7. Response chunks stream to client via SSE
8. If more tools needed → repeat from step 2
9. Final response → conversation ends
```

### 4.3 ToolResult Format

Tool results are returned as strings (success) or error messages:

**Success:**
```
共找到 6 条通知：
1. 【学校办公室】关于印发《中南大学校务会议议事规则》的通知
   文号：- | 发文字：中大党字 | 起草时间：2026-01-19 | 浏览次数：970
...
```

**Error:**
```
请先登录后再使用校内通知查询
```

---

## 5. E2E Test Scenarios

### 5.1 Test Setup

```bash
# Start backend server
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Or with environment variables
OPENAI_API_KEY=sk-xxx JWT_SECRET_KEY=test-secret uv run uvicorn app.main:app --reload
```

### 5.2 Test 1: Anonymous User Chat

**Goal:** Verify anonymous users can chat without authentication.

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "user_id": "anonymous",
    "enable_rag": false
  }'
```

**Expected:**
- SSE stream returns with model response
- No tool calls (direct response)

### 5.3 Test 2: Full Authenticated Flow

**Step 1: Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "YOUR_ID", "password": "YOUR_PASSWORD"}'
```

**Step 2: Save token from response, then:**
```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "查询学校办公室最近的通知",
    "user_id": "YOUR_ID",
    "enable_rag": false
  }'
```

**Expected SSE Sequence:**
```
# 1. Tool analysis start
data: {"type": "event", "data": {"title": "开始分析用户问题", "status": "START", "message": "正在分析需要使用的工具..."}}

# 2. Tool selected
data: {"type": "event", "data": {"title": "开始分析用户问题", "status": "END", "message": "将调用工具: oa_notification_list"}}

# 3. Tool execution start
data: {"type": "event", "data": {"title": "执行工具: oa_notification_list", "status": "START", "message": "参数: {\"pageNo\": 1, \"pageSize\": 20, ...}"}}

# 4. Tool execution end
data: {"type": "event", "data": {"title": "执行工具: oa_notification_list", "status": "END", "message": "执行完成"}}

# 5. Response chunks
data: {"type": "response_chunk", "data": {"chunk": "根据", "accumulated": "根据"}}
data: {"type": "response_chunk", "data": {"chunk": "查询结果，", "accumulated": "根据查询结果，"}}
...
```

### 5.4 Test 3: OA Notification Tool (Newly Integrated)

**Login first, then:**
```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "查询人事处2024年的所有通知",
    "user_id": "YOUR_ID",
    "enable_rag": false
  }'
```

**Expected:**
- `oa_notification_list` tool is called
- Tool internally calls `build_params(qssj="2024-01-01", jssj="2024-12-31", qcbmmc="人事处", ...)`
- Results formatted and returned to LLM

### 5.5 Test 4: Multiple Tool Calls

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "帮我查一下教务处的通知，然后看看我的成绩",
    "user_id": "YOUR_ID",
    "enable_rag": false
  }'
```

**Expected:**
- First call: `oa_notification_list` with `qcbmmc="教务处"`
- Then call: `jwc_grade`
- LLM synthesizes both results

### 5.6 Test 5: Session Expiry & Re-auth

**Step 1:** Login and get token (valid 24 hours)

**Step 2:** Wait for CASTGC to expire (~2 hours for CAS session)

**Step 3:** Try to use OA tool

**Expected:**
- First attempt fails → session manager re-fetches
- If CASTGC expired → returns "请先登录后再使用校内通知查询"

### 5.7 Test 6: Rate Limiting

```bash
# Attempt login 6 times rapidly
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "test", "password": "wrong"}'
  echo ""
done
```

**Expected:**
- First 5 attempts return 401 (wrong password)
- 6th attempt returns 429 (rate limited)

---

## 6. Test Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Required for LLM calls |
| `JWT_SECRET_KEY` | `your-secret-key-change-in-production` | JWT signing key |
| `JWT_EXPIRE_HOURS` | 24 | Token expiry |
| `SESSION_TTL_SECONDS` | 1800 | Subsystem session cache TTL |
| `CAS_USERNAME` | - | CAS credentials (for testing) |
| `CAS_PASSWORD` | - | CAS credentials (for testing) |

---

## 7. Mock Testing

For unit/integration tests without real external APIs:

### 7.1 Mock OASessionProvider

```python
from unittest.mock import patch, MagicMock

def test_oa_notification_with_mocked_session():
    mock_session = MagicMock()
    mock_session.post.return_value.json.return_value = {
        "data": [{"JLNM": "test", "WJBT": "测试通知"}],
        "count": 1
    }

    with patch('app.core.session.manager.UnifiedSessionManager.get_session') as mock_get:
        mock_get.return_value = mock_session

        # Now call the tool
        result = oa_notification_tool.invoke({
            "qssj": "2024-01-01",
            "jssj": "2024-12-31",
            "pageNo": 1,
            "pageSize": 20
        }, ctx)

        assert "测试通知" in result
```

### 7.2 Mock ReactAgent Streaming

```python
import asyncio
from unittest.mock import AsyncMock, patch

async def test_agent_streaming():
    agent = ReactAgent(model=mock_llm, tools=[mock_tool])

    messages = [HumanMessage(content="查询通知")]
    chunks = []

    async for event in agent.astream(messages):
        chunks.append(event)

    assert len(chunks) > 0
    assert any(c["type"] == "response_chunk" for c in chunks)
```

---

## 8. Troubleshooting

### Issue: Streaming hangs indefinitely

**Check:**
- LLM API key is valid
- Network connectivity to OpenAI API
- Tool is not blocking on external API call

### Issue: 401 after valid login

**Check:**
- Token not sent in `Authorization: Bearer <token>` format
- Token expired (24 hours)
- JWT secret key mismatch

### Issue: Tools not available for authenticated user

**Check:**
- `ctx.is_authenticated` is True
- `session_manager` is properly initialized
- `create_xxx_tools(ctx)` is called in AgentFactory

### Issue: OA tool returns "请先登录"

**Check:**
- CAS login succeeded (CASTGC obtained)
- `OASessionProvider.fetch_session()` completed successfully
- Subsystem.OA registered in session manager

---

## 9. Database Schema (for testing history)

```sql
-- Dialogs table
CREATE TABLE dialog (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    agent_id TEXT,
    updated_at TIMESTAMP
);

-- Chat history table
CREATE TABLE chat_history (
    id TEXT PRIMARY KEY,
    dialog_id TEXT,
    role TEXT,  -- 'user' or 'assistant'
    content TEXT,
    events TEXT,  -- JSON array of tool events
    extra TEXT,   -- JSON with model, duration, etc.
    created_at TIMESTAMP
);
```

---

## 10. Related Documentation

- [Design Spec](./2026-03-19-csu-oanetwork-notification-tool-design.md)
- [Implementation Plan](./2026-03-19-csu-oanetwork-notification-tool-plan.md)
- [Integration Summary](./2026-03-19-csu-oanetwork-integration-summary.md)
- [Subsystem Integration Guide](../subsystem-integration-guide.md)
