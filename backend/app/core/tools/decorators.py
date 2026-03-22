"""
Tool decorators for logging and instrumentation
"""
import functools
import time
import json
import asyncio
from loguru import logger
from app.database.session import async_session_dependency
from app.database.models import ToolCallLog


def tool_logger(func):
    """
    Decorator to log tool execution to tool_call_logs table.

    Captures: tool_name, status, duration_ms, error_message (JSON with args/results)
    """
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        from app.core.tools.context import get_tool_context

        start_time = time.time()
        tool_name = getattr(self, 'name', func.__name__)
        context = get_tool_context()

        try:
            result = await func(self, *args, **kwargs)
            status = "success"
            error_message = json.dumps({
                "args": kwargs if kwargs else args,
                "result": str(result)[:1000]
            }, ensure_ascii=False)
            return result
        except Exception as e:
            status = "failed"
            error_message = json.dumps({
                "args": kwargs if kwargs else args,
                "error": str(e)
            }, ensure_ascii=False)
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
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
                break
        except Exception as e:
            logger.error(f"Failed to insert tool_call_log: {e}")

    return wrapper