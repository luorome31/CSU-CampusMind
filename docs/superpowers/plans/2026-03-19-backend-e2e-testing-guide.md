# CampusMind Backend E2E Testing Guide

**Purpose:** End-to-end testing guide for authentication, streaming chat requests, and all tool calling flows.

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
│  │  │  (creates ctx) │    │  (ReAct loop)   │    │  (graph)   │  │  │
│  │  └─────────────────┘    └────────┬────────┘    └────────────┘  │  │
│  │                                │                              │  │
│  │  ┌─────────────────────────────▼──────────────────────────────┐ │  │
│  │  │              Tools (structured by subsystem)               │ │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐     │ │  │
│  │  │  │ career/ │ │ library/│ │  jwc/   │ │    oa/    │     │ │  │
│  │  │  │  (4)   │ │  (2)    │ │  (4)    │ │    (1)    │     │ │  │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └───────────┘     │ │  │
│  │  │  ┌────────────────────────────────────────────────┐    │ │  │
│  │  │  │  rag_search (shared)                           │    │ │  │
│  │  │  └────────────────────────────────────────────────┘    │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication Flow

### 2.1 Login

**Endpoint:** `POST /api/v1/auth/login`

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "YOUR_STUDENT_ID", "password": "YOUR_PASSWORD"}'
```

**Success Response (200):**
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

### 2.2 Authenticated Requests

All subsequent requests include:

```
Authorization: Bearer <token>
```

### 2.3 Logout

**Endpoint:** `POST /api/v1/auth/logout`

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"user_id": "2020123456"}'
```

---

## 3. Streaming Completion API

### 3.1 Endpoint

**Endpoint:** `POST /api/v1/completion/stream`

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "查询通知",
    "knowledge_ids": [],
    "user_id": "2020123456",
    "enable_rag": false
  }'
```

### 3.2 SSE Response Format

**Event Types:**

| Type | Description |
|------|-------------|
| `event` with `status: START` | Tool execution begins |
| `event` with `status: END` | Tool execution completed |
| `event` with `status: ERROR` | Tool execution failed |
| `response_chunk` | LLM token stream |

**Example SSE Stream:**
```
data: {"type": "event", "timestamp": 1710816000.123, "data": {"title": "开始分析用户问题", "status": "START", "message": "正在分析需要使用的工具..."}}

data: {"type": "event", "timestamp": 1710816000.456, "data": {"title": "开始分析用户问题", "status": "END", "message": "将调用工具: oa_notification_list"}}

data: {"type": "event", "timestamp": 1710816000.789, "data": {"title": "执行工具: oa_notification_list", "status": "START", "message": "参数: {\"pageNo\": 1, \"pageSize\": 20}"}}

data: {"type": "event", "timestamp": 1710816001.234, "data": {"title": "执行工具: oa_notification_list", "status": "END", "message": "执行完成"}}

data: {"type": "response_chunk", "timestamp": 1710816001.456, "data": {"chunk": "根据", "accumulated": "根据"}}

data: {"type": "response_chunk", "timestamp": 1710816001.567, "data": {"chunk": "查询结果，", "accumulated": "根据查询结果，"}}
```

---

## 4. Tool Catalog

### 4.1 Tool Availability by Auth State

| Tool | Anonymous | Authenticated |
|------|-----------|---------------|
| **rag_search** | ✅ | ✅ |
| **career_teachin** | ✅ | ✅ |
| **career_campus_recruit** | ✅ | ✅ |
| **career_campus_intern** | ✅ | ✅ |
| **career_jobfair** | ✅ | ✅ |
| **library_search** | ✅ | ✅ |
| **library_get_book_location** | ✅ | ✅ |
| **jwc_grade** | ❌ | ✅ |
| **jwc_schedule** | ❌ | ✅ |
| **jwc_rank** | ❌ | ✅ |
| **jwc_level_exam** | ❌ | ✅ |
| **oa_notification_list** | ❌ | ✅ |

**Total: 12 tools**
- Public (no auth): 7 tools
- Requires auth: 5 tools

---

### 4.2 Public Tools (No Authentication Required)

#### 4.2.1 RAG Tool

**Name:** `rag_search`

**Description:** Search knowledge bases to retrieve relevant context.

**Input Schema:**
```json
{
  "query": "string",        // Required - The search query
  "knowledge_ids": ["string"], // Required - List of knowledge base IDs
  "top_k": 5,               // Optional - Number of results (default: 5)
  "min_score": 0.0          // Optional - Minimum relevance score
}
```

**Example Call:**
```json
{
  "query": "如何申请休学",
  "knowledge_ids": ["kb-uuid-123"],
  "top_k": 3
}
```

**Expected Response Format:**
```
=== 相关上下文 ===
[Retrieved context content here]
=== 来源 ===
1. policy.pdf (相关度: 0.92)
2. handbook.pdf (相关度: 0.85)
```

---

#### 4.2.2 Career Tools

**Name:** `career_teachin`

**Description:** Get campus recruitment 宣讲会 information.

**Input Schema:**
```json
{
  "zone": "岳麓山校区"  // Optional - Filter by campus (岳麓山校区/天心校区/杏林校区/潇湘校区), empty = all
}
```

**Example Call:**
```json
{"zone": "岳麓山校区"}
```

**Example Call (no filter):**
```json
{}
```

---

**Name:** `career_campus_recruit`

**Description:** Get 校园招聘 information.

**Input Schema:**
```json
{
  "keyword": "软件开发"  // Optional - Search keyword, empty = all
}
```

---

**Name:** `career_campus_intern`

**Description:** Get 实习岗位 information.

**Input Schema:**
```json
{
  "keyword": "算法"  // Optional - Search keyword, empty = all
}
```

---

**Name:** `career_jobfair`

**Description:** Get 招聘会 information.

**Input Schema:**
```json
{}  // No parameters required
```

---

#### 4.2.3 Library Tools

**Name:** `library_search`

**Description:** Search library catalog.

**Input Schema:**
```json
{
  "keywords": "string",  // Required - Search keywords (建议3字以内)
  "page": 1,            // Optional - Page number (default: 1)
  "rows": 10             // Optional - Results per page (default: 10)
}
```

**Example Call:**
```json
{"keywords": "Python", "page": 1, "rows": 5}
```

**Expected Response Format:**
```
共找到 42 条结果：

--- 第 1 条 ---
📚 书名: Python编程从入门到实践
👤 作者: Eric Matthes
🏢 出版社: 人民邮电出版社
📅 出版年: 2019
📖 ISBN: 9787115427028
🔖 索书号: TP311.561/M389
📊 馆藏: 5 册 / 在架: 3 册
🔑 Record ID: 123456
```

---

**Name:** `library_get_book_location`

**Description:** Get book location/copies info.

**Input Schema:**
```json
{
  "record_id": 123456  // Required - Book record ID from search results
}
```

---

### 4.3 Authenticated Tools (Require Login)

#### 4.3.1 JWC (教务系统) Tools

**Error Response (not authenticated):**
```
请先登录后再查询成绩
```

---

**Name:** `jwc_grade`

**Description:** Query student grades.

**Input Schema:**
```json
{
  "term": "2024-2025-1"  // Optional - Semester, empty = all terms
}
```

**Example Call:**
```json
{"term": "2024-2025-1"}
```

**Expected Response Format:**
```
## 成绩查询结果

| 学期 | 课程名称 | 成绩 | 学分 | 课程属性 | 课程性质 |
|------|----------|------|------|----------|----------|
| 2024-2025-1 | 高等数学A(一) | 95 | 5.0 | 普通 | 必修 |
```

---

**Name:** `jwc_schedule`

**Description:** Query student class schedule.

**Input Schema:**
```json
{
  "term": "2024-2025-1",  // Required - Semester (e.g., "2024-2025-1")
  "week": "0"             // Optional - Week number, "0" = all weeks (default: "0")
}
```

**Example Call:**
```json
{"term": "2024-2025-1", "week": "1"}
```

**Expected Response Format:**
```
## 课表查询结果

| 课程名称 | 教师 | 周次 | 地点 | 星期 | 节次 |
|----------|------|------|------|------|------|
| 高等数学A(一) | 张三 | 1-16 | 教学楼A101 | 星期一 | 1-2 |

> 学期第1周开始于: 2024-09-02日
```

---

**Name:** `jwc_rank`

**Description:** Query student major ranking.

**Input Schema:**
```json
{}  // No parameters required (user_id from session)
```

---

**Name:** `jwc_level_exam`

**Description:** Query level exam results (CET-4/6, computer tests, etc.).

**Input Schema:**
```json
{}  // No parameters required (user_id from session)
```

---

#### 4.3.2 OA (校内办公网) Tools

**Error Response (not authenticated):**
```
请先登录后再使用校内通知查询
```

---

**Name:** `oa_notification_list`

**Description:** Query campus notifications (行政发文、党委发文等).

**Input Schema:**
```json
{
  "qssj": "2024-01-01",         // Optional - Start date (YYYY-MM-DD)
  "jssj": "2024-12-31",         // Optional - End date (YYYY-MM-DD)
  "qcbmmc": "学校办公室",        // Optional - Drafting department (from enum)
  "wjbt": "通知",               // Optional - Title keyword (fuzzy match)
  "qwss": "印发",               // Optional - Full-text search keyword
  "pageNo": 1,                  // Optional - Page number (default: 1)
  "pageSize": 20                // Optional - Page size (default: 20)
}
```

**Available Departments (qcbmmc):**
```
学校办公室 | 人事处 | 本科生院 | 研究生院 | 科学研究部 | 图书馆 |
党委宣传部 | 党委组织部 | 学生工作部（处）| 校团委 | 纪委办公室 |
出版社 | 继续教育学院 | 国际合作与交流处 | 档案馆（校史馆）| ...
(共85个部门)
```

**Example Call - Query school office notifications:**
```json
{
  "qcbmmc": "学校办公室",
  "pageNo": 1,
  "pageSize": 10
}
```

**Example Call - Query by date range:**
```json
{
  "qssj": "2024-03-01",
  "jssj": "2024-06-30",
  "wjbt": "放假"
}
```

**Expected Response Format:**
```
共找到 6 条通知：

1. 【学校办公室】关于印发《中南大学学术期刊管理办法》的通知
   文号：- | 发文字：中大经字 | 起草时间：2026-02-10 | 浏览次数：500

2. 【学校办公室】关于印发修订后的《中南大学校务会议议事规则》的通知
   文号：- | 发文字：中大党字 | 起草时间：2026-01-19 | 浏览次数：970
```

---

## 5. E2E Test Scenarios

### 5.1 Test Environment Setup

```bash
# Start backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Required env vars
export OPENAI_API_KEY=sk-xxx
export JWT_SECRET_KEY=test-secret
```

### 5.2 Test 1: Anonymous Basic Chat

**Goal:** Verify anonymous users can chat with public tools.

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "查找Python相关的图书",
    "user_id": "anonymous",
    "enable_rag": false
  }'
```

**Expected:**
- `library_search` tool called
- Returns book list

### 5.3 Test 2: Anonymous Career Tools

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "查看最近的宣讲会信息",
    "user_id": "anonymous",
    "enable_rag": false
  }'
```

**Expected:**
- `career_teachin` tool called

### 5.4 Test 3: Authenticated Full Flow

**Step 1: Login**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "YOUR_ID", "password": "YOUR_PWD"}' | jq -r '.token')
echo "Token: $TOKEN"
```

**Step 2: Query Grades**
```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "查询我这学期的成绩",
    "user_id": "YOUR_ID",
    "enable_rag": false
  }'
```

**Expected SSE:**
```
# Tool analysis
data: {"type": "event", "data": {"title": "开始分析用户问题", "status": "START"}}
data: {"type": "event", "data": {"title": "开始分析用户问题", "status": "END", "message": "将调用工具: jwc_grade"}}

# Tool execution
data: {"type": "event", "data": {"title": "执行工具: jwc_grade", "status": "START", "message": "参数: {\"term\": \"\"}"}}
data: {"type": "event", "data": {"title": "执行工具: jwc_grade", "status": "END", "message": "执行完成"}}

# Response
data: {"type": "response_chunk", "data": {"chunk": "您", "accumulated": "您"}}
data: {"type": "response_chunk", "data": {"chunk": "的成绩", "accumulated": "您的成绩"}}
```

### 5.5 Test 4: Multi-Tool Call

**Goal:** LLM calls multiple tools in sequence.

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "帮我查一下教务处的通知，然后看看我上学期的成绩",
    "user_id": "YOUR_ID",
    "enable_rag": false
  }'
```

**Expected:**
1. `oa_notification_list` called (qcbmmc="教务处")
2. `jwc_grade` called (term="2024-2025-1")
3. LLM synthesizes both results

### 5.6 Test 5: RAG + Tool Combination

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "在知识库中搜索休学申请流程，然后查一下我的课表",
    "knowledge_ids": ["kb-uuid-xxx"],
    "user_id": "YOUR_ID",
    "enable_rag": true
  }'
```

**Expected:**
1. `rag_search` called with knowledge_ids
2. `jwc_schedule` called
3. LLM uses both context

### 5.7 Test 6: OA Notification with Multiple Filters

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "查询人事处2024年所有包含"职称"的通知",
    "user_id": "YOUR_ID",
    "enable_rag": false
  }'
```

**Expected:**
- `oa_notification_list` called with:
  - qcbmmc="人事处"
  - qssj="2024-01-01"
  - jssj="2024-12-31"
  - wjbt="职称"

### 5.8 Test 7: Tool Error Handling

**Test when JWC session expired:**
```bash
# Simulate by calling tool after CASTGC expired
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "查询我的成绩",
    "user_id": "YOUR_ID",
    "enable_rag": false
  }'
```

**Expected:**
- Tool returns: "教务系统会话已过期，请重新登录"
- Or automatic re-fetch succeeds

### 5.9 Test 8: Library Search + Location

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "搜索《设计模式》这本书，然后告诉我有没有在架的",
    "user_id": "anonymous",
    "enable_rag": false
  }'
```

**Expected:**
1. `library_search` called
2. `library_get_book_location` called with record_id
3. LLM reports availability

---

## 6. Tool Parameter Reference

### 6.1 All Tools Summary Table

| Tool Name | Required Params | Optional Params | Auth |
|-----------|-----------------|----------------|------|
| `rag_search` | query, knowledge_ids | top_k, min_score | No |
| `career_teachin` | - | zone | No |
| `career_campus_recruit` | - | keyword | No |
| `career_campus_intern` | - | keyword | No |
| `career_jobfair` | - | - | No |
| `library_search` | keywords | page, rows | No |
| `library_get_book_location` | record_id | - | No |
| `jwc_grade` | - | term | Yes |
| `jwc_schedule` | term | week | Yes |
| `jwc_rank` | - | - | Yes |
| `jwc_level_exam` | - | - | Yes |
| `oa_notification_list` | - | qssj, jssj, qcbmmc, wjbt, qwss, pageNo, pageSize | Yes |

### 6.2 Semester Format Reference

JWC tools use semester format: `YYYY-YYYY-N`
- `2024-2025-1` = 2024-2025学年 第1学期 (秋季)
- `2024-2025-2` = 2024-2025学年 第2学期 (春季)
- `2023-2024-1` = 2023-2024学年 第1学期

### 6.3 Campus Zone Values

For `career_teachin`:
- `岳麓山校区`
- `天心校区`
- `杏林校区`
- `潇湘校区`
- `""` (empty = all campuses)

### 6.4 OA Department Values (Partial)

For `oa_notification_list` qcbmmc:
```
学校办公室 | 人事处 | 本科生院 | 研究生院 | 科学研究部
党委宣传部 | 党委组织部 | 党委统战部 | 党委巡视办 | 纪委办公室
学生工作部（处）| 保卫部（处）| 校工会 | 校团委
图书馆 | 档案馆（校史馆）| 信息与网络中心 | 出版社
国际教育学院 | 继续教育学院 | 体育教研部
(共85个部门，参见完整列表)
```

---

## 7. Mock Testing Reference

### 7.1 Mock Tool Functions

```python
from unittest.mock import patch, MagicMock

# Mock JWC Service
def test_jwc_tool():
    mock_service = MagicMock()
    mock_service.get_grades.return_value = [
        Grade(term="2024-2025-1", course_name="高数", score="95", ...)
    ]

    with patch('app.core.tools.jwc.service.JwcService') as MockJwc:
        MockJwc.return_value = mock_service
        # Call tool function directly
        result = _get_grades(user_id="2020123456", term="")
        assert "高等数学" in result

# Mock OA Session Provider
def test_oa_tool():
    mock_session = MagicMock()
    mock_session.post.return_value.json.return_value = {
        "data": [{"JLNM": "test", "WJBT": "测试通知", ...}],
        "count": 1
    }

    with patch('app.core.session.manager.UnifiedSessionManager.get_session') as mock:
        mock.return_value = mock_session
        # Call notification tool
        result = oa_notification_tool.invoke({
            "qcbmmc": "学校办公室"
        }, ctx)
        assert "测试通知" in result
```

### 7.2 Mock Streaming Response

```python
import asyncio
from unittest.mock import AsyncMock

async def test_streaming():
    agent = ReactAgent(model=mock_llm, tools=[mock_tool])
    messages = [HumanMessage(content="查询成绩")]

    chunks = []
    async for event in agent.astream(messages):
        chunks.append(event)

    # Verify streaming
    assert any(c["type"] == "response_chunk" for c in chunks)
    assert any("tool" in str(c) for c in chunks)
```

---

## 8. Troubleshooting

### Issue: Anonymous user gets auth-required tool

**Symptom:** LLM tries to call `jwc_grade` for anonymous user

**Cause:** System prompt doesn't properly filter tools

**Fix:** Verify `ctx.is_authenticated` is False for anonymous, and tools are filtered in AgentFactory

### Issue: Tool returns empty result

**Symptom:** Tool executes but returns empty

**Check:**
- External API may be down (JWC/OA/Library)
- Session expired
- Wrong parameters

### Issue: Streaming hangs

**Check:**
- LLM API key valid
- Network to OpenAI accessible
- Tool not blocking on external call

---

## 9. Related Documentation

- [Design Spec](./2026-03-19-csu-oanetwork-notification-tool-design.md)
- [Implementation Plan](./2026-03-19-csu-oanetwork-notification-tool-plan.md)
- [Integration Summary](./2026-03-19-csu-oanetwork-integration-summary.md)
- [Subsystem Integration Guide](../subsystem-integration-guide.md)
