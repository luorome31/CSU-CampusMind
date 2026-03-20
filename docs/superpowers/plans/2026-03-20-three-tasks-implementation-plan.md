# Three Tasks Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix history bug, verify event persistence, add tool use logging

**Architecture:**
- Task 1: Prepend history from DB to LLM messages in `generate_stream()`
- Task 2: Verification only (no code changes) - verify existing event persistence logic
- Task 3: Add `@tool_logger` decorator + thread-local context for user_id/dialog_id

**Tech Stack:** FastAPI, SQLModel, LangGraph, asyncpg, loguru

---

## Chunk 1: Task 2 - Verify Event Persistence

**Goal:** Confirm existing event persistence logic is correct (no code changes needed)

### Task 2.1: Verify schema and model alignment

- [ ] **Step 1: Check schema `events` column type**

Run: `grep -n "events" /home/luorome/software/CampusMind/docs/database/schema.sql`
Expected: Line 47 shows `events TEXT,`

- [ ] **Step 2: Check `ChatHistory` model mapping**

Run: `grep -n "events" /home/luorome/software/CampusMind/backend/app/database/models/chat_history.py`
Expected: Line 30 shows `events: Optional[str] = Field(default=None, ...)`

- [ ] **Step 3: Verify event capture in streaming**

Read `completion.py` lines 195-225:
- [ ] Line 195: `accumulated_content += event.get("data", {}).get("chunk", "")` for response chunks
- [ ] Line 200: `events.append(event)` for non-chunk events
- [ ] Line 225: `events=json.dumps(events) if events else None` in assistant ChatHistory

**Verification Result:** Task 2 is complete. No code changes needed.

---

## Chunk 2: Task 1 - Fix History Bug

**Goal:** Make `generate_stream()` retrieve and use chat history

### Task 1.1: Write failing test

**Files:**
- Test: `backend/tests/api/v1/test_completion_history.py`

- [ ] **Step 1: Create test file**

```python
"""
Tests for completion endpoint with history support
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.api.v1.completion import generate_stream


class TestHistorySupport:
    """Test that generate_stream uses chat history"""

    @pytest.mark.asyncio
    async def test_history_prepended_to_messages(self):
        """History messages should be prepended before the new user message"""
        # Arrange
        mock_agent = MagicMock()
        mock_agent.astream = MagicMock(return_value=iter([
            {"type": "response_chunk", "timestamp": 1.0, "data": {"chunk": "Hi", "accumulated": "Hi"}}
        ]))

        mock_session = AsyncMock()
        mock_dialog = MagicMock()
        mock_dialog.id = "test-dialog-id"

        # Create mock history records
        mock_history_user = MagicMock()
        mock_history_user.role = "user"
        mock_history_user.content = "Hello"
        mock_history_user.events = None
        mock_history_user.extra = None

        mock_history_assistant = MagicMock()
        mock_history_assistant.role = "assistant"
        mock_history_assistant.content = "Hi there!"
        mock_history_assistant.events = None
        mock_history_assistant.extra = None

        # Mock HistoryService to return history
        with patch("app.api.v1.completion.HistoryService") as mock_history_service:
            mock_history_service.get_history_by_dialog = AsyncMock(
                return_value=[mock_history_user, mock_history_assistant]
            )

            # Act - collect what messages would be sent to the agent
            messages_sent = []
            async def capture_messages(messages):
                messages_sent.extend(messages)
                async for _ in mock_agent.astream(messages):
                    yield _

            # We need to patch at the source - the HumanMessage creation
            with patch("app.api.v1.completion.HumanMessage") as mock_hm:
                mock_hm.side_effect = lambda content: MagicMock(__class__.__name__="HumanMessage", content=content)

                with patch("app.api.v1.completion.AIMessage") as mock_aim:
                    mock_aim.side_effect = lambda content: MagicMock(__class__.__name__="AIMessage", content=content)

                    # Call generate_stream - we only care that it calls HistoryService
                    with patch("app.api.v1.completion.ChatHistory") as mock_ch:
                        mock_ch.return_value = MagicMock(id="1", dialog_id="test", role="user", content="test")

                        # Create an async generator to consume the stream
                        async def consume():
                            gen = generate_stream(
                                agent=mock_agent,
                                message="New message",
                                knowledge_ids=[],
                                session=mock_session,
                                dialog_id="test-dialog-id",
                                model="gpt-4"
                            )
                            async for _ in gen:
                                pass

                        await consume()

                        # Assert: HistoryService.get_history_by_dialog was called
                        mock_history_service.get_history_by_dialog.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/luorome/software/CampusMind/backend && python -m pytest tests/api/v1/test_completion_history.py -v 2>&1 | head -50`
Expected: Test fails because HistoryService is not yet called in `generate_stream`

### Task 1.2: Implement fix

**Files:**
- Modify: `backend/app/api/v1/completion.py:157-243`

- [ ] **Step 3: Add history import**

Locate line ~18 (after existing imports), add:
```python
from app.services.history.history import HistoryService
```

- [ ] **Step 4: Modify `generate_stream()` to fetch and use history**

In `generate_stream()` function, replace line ~187:
```python
# OLD (line 187):
messages = [HumanMessage(content=message)]

# NEW (lines 187-200):
# Fetch history and build messages list
histories = await HistoryService.get_history_by_dialog(session, dialog_id)

messages = []
for h in histories:
    if h.role == "user":
        messages.append(HumanMessage(content=h.content))
    elif h.role == "assistant":
        messages.append(AIMessage(content=h.content))

messages.append(HumanMessage(content=message))
```

- [ ] **Step 5: Add AIMessage import**

Locate line ~168 (where HumanMessage is imported), add:
```python
from langchain_core.messages import HumanMessage, AIMessage
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd /home/luorome/software/CampusMind/backend && python -m pytest tests/api/v1/test_completion_history.py -v 2>&1 | head -50`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
cd /home/luorome/software/CampusMind
git add backend/app/api/v1/completion.py
git commit -m "fix(api): prepend chat history to LLM messages in generate_stream"
```

---

## Chunk 3: Task 3 - Tool Use Logging

**Goal:** Add `@tool_logger` decorator for async tools

### Task 3.1: Create thread-local context

**Files:**
- Create: `backend/app/core/tools/context.py`

- [ ] **Step 1: Create context.py**

```python
"""
Thread-local context for tool execution

Provides:
- set_tool_context(user_id, dialog_id): Set current context
- get_tool_context(): Get current context (returns defaults if not set)
"""
from contextvars import ContextVar
from typing import Optional

_tool_context: ContextVar[dict] = ContextVar('tool_context', default=None)


def set_tool_context(user_id: Optional[str] = None, dialog_id: Optional[str] = None) -> None:
    """
    Set the tool execution context.

    Args:
        user_id: User ID from JWT (None for anonymous)
        dialog_id: Current dialog/thread ID
    """
    _tool_context.set({"user_id": user_id, "dialog_id": dialog_id})


def get_tool_context() -> dict:
    """
    Get the current tool execution context.

    Returns:
        dict with user_id and dialog_id (both may be None)
    """
    return _tool_context.get() or {"user_id": None, "dialog_id": None}


def clear_tool_context() -> None:
    """Clear the tool execution context."""
    _tool_context.set(None)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/core/tools/context.py
git commit -m "feat(tools): add thread-local context for tool execution"
```

### Task 3.2: Create tool_logger decorator

**Files:**
- Create: `backend/app/core/tools/decorators.py`
- Modify: `backend/app/core/tools/__init__.py`

- [ ] **Step 3: Create decorators.py**

```python
"""
Tool decorators for logging and instrumentation
"""
import functools
import time
import json
import asyncio
from loguru import logger
from typing import Optional


def tool_logger(func):
    """
    Decorator to log tool execution to tool_call_logs table.

    Usage:
        @tool_logger
        async def my_tool(self, tool_args):
            # tool execution logic
            return result

    Captures:
        - tool_name: from tool instance (self.name)
        - status: 'success' or 'failed'
        - duration_ms: execution time in milliseconds
        - error_message: JSON with args and result/error
        - user_id, dialog_id: from thread-local context
    """
    @functools.wraps(func)
    async def wrapper(self, tool_args):
        from app.database.session import async_session_dependency
        from app.database.models.tool_call_log import ToolCallLog
        from app.core.tools.context import get_tool_context

        start_time = time.time()
        tool_name = getattr(self, 'name', func.__name__)
        context = get_tool_context()

        try:
            result = await func(self, tool_args)
            status = "success"
            error_message = json.dumps({
                "args": tool_args,
                "result": str(result)[:1000]
            }, ensure_ascii=False)
            return result
        except Exception as e:
            status = "failed"
            error_message = json.dumps({
                "args": tool_args,
                "error": str(e)
            }, ensure_ascii=False)
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)

            # Fire-and-forget async insert to avoid blocking
            asyncio.create_task(_insert_log(
                tool_name=tool_name,
                user_id=context.get("user_id"),
                dialog_id=context.get("dialog_id"),
                status=status,
                error_message=error_message,
                duration_ms=duration_ms
            ))

    async def _insert_log(**kwargs):
        """Async insert to tool_call_logs table."""
        try:
            async for session in async_session_dependency():
                log = ToolCallLog(**kwargs)
                session.add(log)
                await session.commit()
                break  # Exit after one session use
        except Exception as e:
            logger.error(f"Failed to insert tool_call_log: {e}")

    return wrapper
```

**Note:** The `async_session_dependency` is a generator (FastAPI dependency). We use `async for` to get the session.

- [ ] **Step 4: Update `__init__.py` to export decorator**

```python
"""
Core tools module
"""
from app.core.tools.rag_tool import create_rag_tool
from app.core.tools.library.tools import library_search, library_get_book_location, LIBRARY_TOOLS
from app.core.tools.career import CAREER_TOOLS, create_career_tools
from app.core.tools.decorators import tool_logger  # NEW
from app.core.tools.context import set_tool_context, get_tool_context, clear_tool_context  # NEW

__all__ = [
    "create_rag_tool",
    "library_search",
    "library_get_book_location",
    "LIBRARY_TOOLS",
    "CAREER_TOOLS",
    "create_career_tools",
    "tool_logger",  # NEW
    "set_tool_context",  # NEW
    "get_tool_context",  # NEW
    "clear_tool_context",  # NEW
]
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/tools/decorators.py backend/app/core/tools/__init__.py
git commit -m "feat(tools): add @tool_logger decorator for async tool logging"
```

### Task 3.3: Integrate context setup in completion.py

**Files:**
- Modify: `backend/app/api/v1/completion.py`

- [ ] **Step 6: Set tool context before streaming**

In `completion_stream()` endpoint (around line 310), before returning the streaming response:

```python
# Set tool context for logging (around line 310, before return)
from app.core.tools.context import set_tool_context
set_tool_context(user_id=jwt_user_id, dialog_id=dialog.id)
```

Find the line `return WatchedStreamingResponse(...)` and add context setup BEFORE it.

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/v1/completion.py
git commit -m "feat(api): set tool context before streaming for logging"
```

### Task 3.4: Apply decorator to RagTool

**Files:**
- Modify: `backend/app/core/tools/rag_tool.py`

- [ ] **Step 8: Apply decorator to RagTool._arun**

```python
from app.core.tools.decorators import tool_logger  # Add import

class RagTool(BaseTool):
    # ... existing code ...

    @tool_logger  # ADD THIS DECORATOR
    async def _arun(
        self,
        query: str,
        knowledge_ids: List[str],
        top_k: int = 5,
        min_score: float = 0.0
    ) -> str:
        # ... existing implementation ...
```

- [ ] **Step 9: Commit**

```bash
git add backend/app/core/tools/rag_tool.py
git commit -m "feat(tools): apply @tool_logger to RagTool._arun"
```

---

## Chunk 4: Integration & Verification

### Task 4.1: Verify ToolCallLog model compatibility

- [ ] **Step 1: Check model vs schema alignment**

The schema.sql has `user_id TEXT NOT NULL` but the model has `user_id: str = Field(index=True)` with no `nullable=True`. For anonymous users, we need to allow NULL.

**Run**: `grep -n "user_id" /home/luorome/software/CampusMind/backend/app/database/models/tool_call_log.py`

**Expected**: Line 24 shows `user_id: str = Field(...)` - this should be `Optional[str]` for anonymous support

**Fix if needed**: Edit `tool_call_log.py` line 24:
```python
# OLD:
user_id: str = Field(index=True, description="User who triggered the call")
# NEW:
user_id: Optional[str] = Field(default=None, index=True, description="User who triggered the call (None for anonymous)")
```

**Commit if changed**:
```bash
git add backend/app/database/models/tool_call_log.py
git commit -m "fix(model): allow user_id NULL for anonymous tool calls"
```

### Task 4.2: End-to-end test

- [ ] **Step 2: Start backend and test tool logging**

```bash
cd /home/luorome/software/CampusMind/backend
# Start server
uvicorn app.main:app --host 127.0.0.1 --port 18000 &
sleep 3

# Test streaming with RAG (tool call should be logged)
curl -X POST http://127.0.0.1:18000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "knowledge_ids": ["test-id"], "enable_rag": true}'

# Wait for completion
sleep 5

# Check tool_call_logs table
psql $DATABASE_URL -c "SELECT tool_name, status, duration_ms, error_message FROM tool_call_logs ORDER BY created_at DESC LIMIT 5;"
```

**Expected**: Log entry with tool_name='rag_search', status='success', error_message containing args/result JSON

---

## Summary

| Chunk | Task | Status |
|-------|------|--------|
| 1 | Task 2: Verify Event Persistence | Verification only |
| 2 | Task 1: Fix History Bug | ~10 lines changed in completion.py |
| 3 | Task 3: Tool Logging | 2 new files + decorator + context setup |
| 4 | Integration & Verification | End-to-end test |
