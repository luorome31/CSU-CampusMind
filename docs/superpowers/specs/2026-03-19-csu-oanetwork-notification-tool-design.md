# CSU OANetwork Notification Tool Integration Design

**Date:** 2026-03-19
**Status:** Approved

---

## 1. Overview

Integrate the CSU OANetwork (校内办公网) notification API as a LangGraph tool, enabling authenticated users to search and browse campus notifications through the Campus Assistant agent.

---

## 2. Component Architecture

```
backend/app/
├── core/
│   ├── session/
│   │   └── providers/
│   │       └── oa.py              # OASessionProvider (new)
│   └── tools/
│       └── oa/
│           ├── __init__.py        # create_oa_tools() factory
│           ├── notification.py    # OANotificationList tool (single)
│           └── departments.py      # DepartmentEnum + build_params()
```

### OASessionProvider (`providers/oa.py`)

- Extends `SubsystemSessionProvider` with `subsystem_name = "oa"`
- Implements `fetch_session(castgc: str)` with 3-step sub-session activation:
  1. `GET https://oa.csu.edu.cn/con/` → extract sub-session S from cookies
  2. `GET https://ca.csu.edu.cn/authserver/login?service=...` (with CASTGC) → follow redirect
  3. Final redirect URL with S → activates sub-session
- Stores sub-session S in memory; auto-refreshes on 3xx detection

### departments.py

- `DepartmentEnum` — Python `Literal` type with all 80+ departments from the fixed department list
- `build_params(qssj, jssj, qcbmmc, wjbt, qwss, hid_odby)` — constructs SQL WHERE clause, base64-encodes it, returns JSON string

### OANotificationList Tool (`notification.py`)

- Single tool exposing notification search via `OANotificationListInput`
- `qcbmmc` constrained to `DepartmentEnum` to prevent LLM hallucinations
- `tableName` hardcoded internally as `"ZNDX_ZHBG_GGTZ"` (not exposed to LLM)
- Uses `ToolContext.get_subsystem_session("oa")` to obtain authenticated session

---

## 3. Authentication Flow

```
User logs in via /auth/login
        ↓
CAS Server returns CASTGC → cached in UnifiedSessionManager
        ↓
Agent calls OANotificationList(...)
        ↓
ToolContext.get_subsystem_session("oa")
        ↓
OASessionProvider checks: sub-session S valid?
        ├─ Yes → use S directly
        └─ No → 3-step activation:
                1. GET https://oa.csu.edu.cn/con/ → extract S
                2. GET CAS login URL (with CASTGC) → follow redirect
                3. GET final URL with S → activate sub-session
        ↓
POST https://oa.csu.edu.cn/con/xnbg/contentList
```

CASTGC is pre-existing from the user's `/auth/login` session — OASessionProvider does NOT re-authenticate with username/password.

---

## 4. Tool Schema

### OANotificationListInput

```python
class DepartmentEnum(str, Enum):
    SCHOOL_OFFICE = "学校办公室"
    PERSONNEL_DIVISION = "人事处"
    UNDERGRADUATE_COLLEGE = "本科生院"
    # ... (full list of 80+ departments)

class OANotificationListInput(BaseModel):
    qssj: Optional[str] = Field(
        default=None,
        description="起始时间，格式 YYYY-MM-DD"
    )
    jssj: Optional[str] = Field(
        default=None,
        description="结束时间，格式 YYYY-MM-DD"
    )
    qcbmmc: Optional[DepartmentEnum] = Field(
        default=None,
        description="起草部门"
    )
    wjbt: Optional[str] = Field(
        default=None,
        description="文件标题关键词（模糊匹配）"
    )
    qwss: Optional[str] = Field(
        default=None,
        description="全文搜索关键词"
    )
    pageNo: int = Field(default=1, description="页码，从1开始")
    pageSize: int = Field(default=20, description="每页条数，建议不超过50")
```

### Internal Payload Construction

```python
# Not exposed to LLM - hardcoded inside tool function
params_str = build_params(
    qssj=input.qssj or "",
    jssj=input.jssj or "",
    qcbmmc=input.qcbmmc.value if input.qcbmmc else "",
    wjbt=input.wjbt or "",
    qwss=input.qwss or ""
)

# tableName hardcoded internally
payload = {
    "params": params_str,  # contains tableName="ZNDX_ZHBG_GGTZ"
    "pageSize": input.pageSize,
    "pageNo": input.pageNo
}
```

---

## 5. API Endpoint

- **URL:** `https://oa.csu.edu.cn/con/xnbg/contentList`
- **Method:** POST
- **Content-Type:** `application/x-www-form-urlencoded`

### Response Schema

```json
{
  "data": [
    {
      "JLNM": "string",
      "QCZHXM": "string",
      "FWZ": "string",
      "QCSJ": "YYYY-MM-DD",
      "WJBT": "string",
      "YWMS": "string",
      "DJSJP": "string",
      "LLCS": "number",
      "QCBMMC": "string",
      "PXBM": "number",
      "FWH": "string",
      "WN": "number",
      "FWN": "YYYY",
      "YWMC": "string",
      "DJSJ": "YYYY-MM-DD"
    }
  ],
  "count": "number"
}
```

---

## 6. Error Handling

| Scenario | Response |
|----------|----------|
| CASTGC expired/missing | `"请先登录后再使用校内通知查询"` |
| Sub-session expired (3xx) | Auto-re-authenticate via `fetch_session()` |
| Network error | `"查询校内通知失败，请稍后重试"` |
| Invalid params | `"搜索参数无效: {detail}"` |
| Empty results | `"未找到符合条件的通知"` |

---

## 7. Integration with AgentFactory

`create_oa_tools(ctx: ToolContext)` will be added to `AgentFactory.create_agent()`, appended to the tools list unconditionally (like career tools) — authentication check is handled inside the tool via `ctx.is_authenticated`.

---

## 8. Testing Strategy

- Unit test `OASessionProvider.fetch_session()` with mocked HTTP responses (3xx redirect sequence)
- Unit test `build_params()` for all parameter combinations and base64 encoding
- Unit test `OANotificationList` tool output schema validation
- Integration test with real OA endpoint (requires test credentials)
