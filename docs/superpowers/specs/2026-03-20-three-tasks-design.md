# Three Tasks Design: History Bug Fix, Event Persistence Verification, Tool Use Logging

**Date**: 2026-03-20
**Status**: Approved
**Type**: Bug Fix + Feature Addition

## Overview

Three related tasks for the CampusMind chat backend:
1. Fix: Conversation interface not correctly using History
2. Verify: LLM-returned `event` field persistence to database
3. Add: Tool Use logging to database

## Task 1: Fix History Bug

### Problem
`generate_stream()` in `completion.py` does not fetch or use chat history when building messages for the LLM. Each request starts with a fresh context.

### Solution
**File**: `backend/app/api/v1/completion.py`

**Location**: `generate_stream()` function, before building `messages` list (line ~187)

**Implementation**:
1. Call `HistoryService.get_history_by_dialog(session, dialog_id)` to retrieve existing history
2. Convert each `ChatHistory` record to LangChain `HumanMessage` or `AIMessage` based on `role` field
3. Prepend to the messages list before adding the new `HumanMessage`

**Code Flow**:
```python
# Fetch history
histories = await HistoryService.get_history_by_dialog(session, dialog_id)

# Build messages from history
messages = []
for h in histories:
    if h.role == "user":
        messages.append(HumanMessage(content=h.content))
    elif h.role == "assistant":
        messages.append(AIMessage(content=h.content))

# Add current message
messages.append(HumanMessage(content=message))
```

**Files Modified**:
- `backend/app/api/v1/completion.py`

---

## Task 2: Verify Event Persistence

### Problem
Verify that LLM-returned `event` field is correctly persisted to database.

### Current State (Line 225 in completion.py)
```python
events=json.dumps(events) if events else None
```

### Verification Checklist
- [ ] `chat_history.events` column is `TEXT` type (schema.sql line 47) — can store JSON
- [ ] `ChatHistory` model correctly maps `events` field
- [ ] Events are captured during streaming (line 200: `events.append(event)`)
- [ ] Events are saved on assistant message (line 225)

### Conclusion
**No code changes needed.** The persistence logic is already correct. This task is complete upon verification.

---

## Task 3: Tool Use Logging

### Problem
Tool executions are not logged to `tool_call_logs` table, making debugging difficult.

### Solution
Create a `@tool_logger` decorator for tool functions.

**New File**: `backend/app/core/tools/decorators.py`

**Decorator Logic**:
```python
import functools
import time
import json
from loguru import logger

def tool_logger(func):
    """
    Decorator to log tool execution to tool_call_logs table.

    Captures: tool_name, status, duration_ms, error_message (JSON with args/results)
    """
    @functools.wraps(func)
    async def wrapper(tool_self, tool_args):
        from app.database.session import async_session_dependency
        from app.database.models.tool_call_log import ToolCallLog
        from app.core.tools.context import get_tool_context  # Thread-local context

        start_time = time.time()
        tool_name = getattr(tool_self, 'name', func.__name__)

        try:
            result = await func(tool_self, tool_args)
            status = "success"
            error_message = json.dumps({
                "args": tool_args,
                "result": str(result)[:1000]  # Truncate for safety
            }, ensure_ascii=False)
            return result
        except Exception as e:
            status = "error"
            error_message = json.dumps({
                "args": tool_args,
                "error": str(e)
            }, ensure_ascii=False)
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            context = get_tool_context()

            # Fire-and-forget async insert
            asyncio.create_task(_insert_log(
                tool_name=tool_name,
                user_id=context.user_id,
                dialog_id=context.dialog_id,
                status=status,
                error_message=error_message,
                duration_ms=duration_ms
            ))

    async def _insert_log(**kwargs):
        """Async insert to avoid blocking streaming."""
        try:
            session = async_session_dependency()
            log = ToolCallLog(**kwargs)
            session.add(log)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to insert tool_call_log: {e}")

    return wrapper
```

**Thread-Local Context** (new file: `backend/app/core/tools/context.py`):
```python
from contextvars import ContextVar

_tool_context: ContextVar[dict] = ContextVar('tool_context', default=None)

def set_tool_context(user_id=None, dialog_id=None):
    _tool_context.set({"user_id": user_id, "dialog_id": dialog_id})

def get_tool_context():
    return _tool_context.get() or {"user_id": None, "dialog_id": None}
```

**Context Setup** in `completion.py`:
Before calling `generate_stream()`, set context:
```python
context = get_tool_context()  # Will need to pass user_id, dialog_id
```

**Files Created**:
- `backend/app/core/tools/decorators.py` — decorator implementation
- `backend/app/core/tools/context.py` — thread-local context

**Files Modified**:
- `backend/app/core/tools/__init__.py` — export decorator

---

## Coupling Analysis

| | Task 1 | Task 2 | Task 3 |
|---|---|---|---|
| **Task 1** | — | Low | Low |
| **Task 2** | Low | — | Low |
| **Task 3** | Low | Low | — |

**Independence**: All three tasks are largely independent. They touch different code paths and can be developed/tested separately.

**Shared Components**:
- `HistoryService` (used by Task 1)
- `tool_call_logs` table (used by Task 3)
- `ChatHistory.events` column (verified by Task 2)

---

## Implementation Order

1. **Task 2 (Verify)**: No code changes — just verify existing logic
2. **Task 1 (History Fix)**: Minimal change, straightforward
3. **Task 3 (Tool Logging)**: New files + decorator pattern

---

## Testing

**Task 1**: Call `/completion/stream` with existing `dialog_id` — verify LLM sees history.

**Task 2**: Query `chat_history` table after a streaming response — verify `events` column is populated.

**Task 3**: Call a tool, query `tool_call_logs` — verify log entry with correct `error_message` JSON.
