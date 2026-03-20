"""
Dialog Service - Service for dialog operations
"""
from datetime import datetime
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.dialog import Dialog


class DialogService:
    """Service for dialog operations"""

    @staticmethod
    async def create_dialog(
        session: AsyncSession,
        user_id: Optional[str],
        agent_id: Optional[str] = None,
        dialog_id: Optional[str] = None
    ) -> Dialog:
        """
        Create a new dialog

        Args:
            session: Database session
            user_id: User ID
            agent_id: Agent ID
            dialog_id: Optional dialog ID (if not provided, will generate UUID)

        Returns:
            Dialog instance
        """
        import uuid
        if not dialog_id:
            dialog_id = str(uuid.uuid4())

        dialog = Dialog(
            id=dialog_id,
            user_id=user_id,
            agent_id=agent_id,
            updated_at=datetime.now()
        )
        session.add(dialog)
        await session.commit()
        await session.refresh(dialog)
        return dialog

    @staticmethod
    async def get_dialog(session: AsyncSession, dialog_id: str) -> Optional[Dialog]:
        """Get dialog by ID"""
        statement = select(Dialog).where(Dialog.id == dialog_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_dialog_time(session: AsyncSession, dialog_id: str):
        """Update dialog's last update time"""
        dialog = await DialogService.get_dialog(session, dialog_id)
        if dialog:
            dialog.updated_at = datetime.now()
            await session.commit()

    @staticmethod
    async def list_user_dialogs(
        session: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> list[Dialog]:
        """List user's dialogs

        Note: This only works for logged-in users. Anonymous dialogs have no
        user_id to filter by, so they cannot be retrieved via this method.
        """
        statement = (
            select(Dialog)
            .where(Dialog.user_id == user_id)
            .order_by(Dialog.updated_at.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
