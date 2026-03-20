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
    """Set the tool execution context."""
    _tool_context.set({"user_id": user_id, "dialog_id": dialog_id})


def get_tool_context() -> dict:
    """Get the current tool execution context."""
    return _tool_context.get() or {"user_id": None, "dialog_id": None}


def clear_tool_context() -> None:
    """Clear the tool execution context."""
    _tool_context.set(None)