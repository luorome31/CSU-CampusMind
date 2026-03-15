"""
History Service - Service for chat history operations
"""
from datetime import datetime
from typing import Optional, Any, List
from sqlmodel import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chat_history import ChatHistory


class HistoryService:
    """Service for chat history operations"""

    @staticmethod
    async def save_chat_history(
        session: AsyncSession,
        role: str,
        content: str,
        dialog_id: str,
        file_url: Optional[str] = None,
        events: Optional[List[dict]] = None,
        metadata: Optional[dict] = None
    ) -> ChatHistory:
        """
        Save chat history

        Args:
            session: Database session
            role: Role (user/assistant/system)
            content: Message content
            dialog_id: Dialog ID
            file_url: Optional file URL
            events: Tool call events
            metadata: Performance metadata

        Returns:
            ChatHistory instance
        """
        import uuid
        history_id = str(uuid.uuid4())

        history = ChatHistory(
            id=history_id,
            dialog_id=dialog_id,
            role=role,
            content=content,
            file_url=file_url,
            events=events,
            metadata=metadata,
            created_at=datetime.now()
        )
        session.add(history)
        await session.commit()
        await session.refresh(history)
        return history

    @staticmethod
    async def get_history_by_dialog(
        session: AsyncSession,
        dialog_id: str,
        limit: int = 100
    ) -> List[ChatHistory]:
        """
        Get chat history by dialog ID

        Args:
            session: Database session
            dialog_id: Dialog ID
            limit: Maximum number of records

        Returns:
            List of ChatHistory
        """
        statement = (
            select(ChatHistory)
            .where(ChatHistory.dialog_id == dialog_id)
            .order_by(ChatHistory.created_at.asc())
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    @staticmethod
    async def delete_dialog_history(
        session: AsyncSession,
        dialog_id: str
    ):
        """Delete all history for a dialog"""
        statement = select(ChatHistory).where(ChatHistory.dialog_id == dialog_id)
        result = await session.exec(statement)
        histories = result.all()

        for history in histories:
            await session.delete(history)
        await session.commit()
