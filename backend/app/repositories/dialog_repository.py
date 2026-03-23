"""
Dialog Repository - Centralized dialog access with authorization.

Handles:
- Anonymous dialog creation (user_id=NULL)
- Authenticated dialog access (user_id must match JWT)
- IDOR prevention (cannot access another user's dialog)
"""
from datetime import datetime
from typing import Optional, Tuple
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.dialog import Dialog


class DialogRepositoryError(Exception):
    """Base exception for dialog repository errors."""
    pass


class ForbiddenError(DialogRepositoryError):
    """Raised when user attempts to access a dialog they don't own."""
    pass


class DialogRepository:
    """Repository for dialog operations with built-in authorization."""

    @staticmethod
    async def get_or_create_dialog(
        session: AsyncSession,
        dialog_id: str,
        jwt_user_id: Optional[str],
        agent_id: Optional[str] = None,
    ) -> Tuple[Dialog, bool]:
        """
        Get existing dialog with authorization check, or create new.

        Authorization rules:
        - Anonymous (jwt_user_id=None): can only access dialogs with user_id=NULL
        - Logged-in: can only access dialogs where user_id matches jwt_user_id

        Args:
            session: Database session
            dialog_id: Dialog ID (UUID, provided by frontend as thread_id)
            jwt_user_id: User ID from JWT token (None if anonymous)
            agent_id: Optional agent ID for new dialogs

        Returns:
            Tuple of (dialog, created_new)

        Raises:
            ForbiddenError: user attempts to access another user's dialog
        """
        statement = select(Dialog).where(Dialog.id == dialog_id)
        result = await session.execute(statement)
        existing = result.scalar_one_or_none()

        if existing is not None:
            # Dialog exists — check authorization
            if not DialogRepository._authorize_access(existing, jwt_user_id):
                raise ForbiddenError("Access denied to this dialog")
            # Update timestamp and return existing
            existing.updated_at = datetime.now()
            await session.commit()
            return existing, False

        # Dialog doesn't exist — create new
        new_dialog = Dialog(
            id=dialog_id,
            user_id=jwt_user_id,  # None for anonymous, actual ID for logged-in
            agent_id=agent_id,
            updated_at=datetime.now()
        )
        session.add(new_dialog)
        await session.commit()
        await session.refresh(new_dialog)
        return new_dialog, True

    @staticmethod
    def _authorize_access(dialog: Dialog, jwt_user_id: Optional[str]) -> bool:
        """
        Check if user is authorized to access a dialog.

        Rules:
        - Anonymous (jwt_user_id=None): can only access dialogs where user_id IS NULL
        - Logged-in: can only access dialogs where user_id matches jwt_user_id
        """
        if jwt_user_id is None:
            return dialog.user_id is None
        else:
            return dialog.user_id == jwt_user_id

    @staticmethod
    async def get_dialog_if_authorized(
        session: AsyncSession,
        dialog_id: str,
        jwt_user_id: Optional[str],
    ) -> Optional[Dialog]:
        """
        Get dialog only if user is authorized.

        Returns None if dialog doesn't exist or user is not authorized.
        Does NOT raise ForbiddenError — returns None silently.
        """
        statement = select(Dialog).where(Dialog.id == dialog_id)
        result = await session.execute(statement)
        dialog = result.scalar_one_or_none()

        if dialog is None:
            return None

        if not DialogRepository._authorize_access(dialog, jwt_user_id):
            return None

        return dialog

    @staticmethod
    async def list_user_dialogs(
        session: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> list[Dialog]:
        """List all dialogs for a logged-in user."""
        statement = (
            select(Dialog)
            .where(Dialog.user_id == user_id)
            .order_by(Dialog.updated_at.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def delete_dialog(
        session: AsyncSession,
        dialog_id: str,
        jwt_user_id: Optional[str]
    ) -> bool:
        """Delete a dialog if user is authorized."""
        dialog = await DialogRepository.get_dialog_if_authorized(session, dialog_id, jwt_user_id)
        if dialog:
            # Delete associated chat history first
            from app.database.models.chat_history import ChatHistory
            history_stmt = select(ChatHistory).where(ChatHistory.dialog_id == dialog_id)
            history_result = await session.execute(history_stmt)
            for msg in history_result.scalars().all():
                await session.delete(msg)
            
            await session.delete(dialog)
            await session.commit()
            return True
        return False

    @staticmethod
    async def get_dialog_history(
        session: AsyncSession,
        dialog_id: str,
        jwt_user_id: Optional[str]
    ) -> list:
        """Get full message history for a dialog if user is authorized."""
        dialog = await DialogRepository.get_dialog_if_authorized(session, dialog_id, jwt_user_id)
        if not dialog:
            return []
        
        from app.database.models.chat_history import ChatHistory
        statement = (
            select(ChatHistory)
            .where(ChatHistory.dialog_id == dialog_id)
            .order_by(ChatHistory.created_at.asc())
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def update_dialog_title(
        session: AsyncSession,
        dialog_id: str,
        title: str,
        jwt_user_id: Optional[str]
    ) -> Optional[Dialog]:
        """Update dialog title if user is authorized."""
        dialog = await DialogRepository.get_dialog_if_authorized(session, dialog_id, jwt_user_id)
        if dialog:
            dialog.title = title
            dialog.updated_at = datetime.now()
            await session.commit()
            await session.refresh(dialog)
            return dialog
        return None

    @staticmethod
    async def list_anonymous_dialogs(
        session: AsyncSession,
        limit: int = 50
    ) -> list[Dialog]:
        """List all anonymous dialogs (user_id IS NULL)."""
        statement = (
            select(Dialog)
            .where(Dialog.user_id.is_(None))
            .order_by(Dialog.updated_at.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())