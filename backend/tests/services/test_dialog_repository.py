"""
DialogRepository Tests - Authorization and anonymous dialog support
"""
import pytest
import os
import tempfile
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.repositories.dialog_repository import (
    DialogRepository,
    ForbiddenError,
)


@pytest.fixture(scope="function")
async def test_engine():
    """Create async test engine with SQLite"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_url = f"sqlite+aiosqlite:///{path}"
    engine = create_async_engine(db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()
    os.unlink(path)


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Create async session"""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


class TestDialogRepositoryAnonymous:
    """Tests for anonymous dialog support"""

    @pytest.mark.asyncio
    async def test_create_anonymous_dialog(self, test_session):
        """Anonymous user can create a new dialog"""
        dialog, created = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="anon-thread-001",
            jwt_user_id=None,
            agent_id="test_agent"
        )
        assert created is True
        assert dialog.user_id is None
        assert dialog.id == "anon-thread-001"
        await test_session.commit()

    @pytest.mark.asyncio
    async def test_anonymous_can_access_own_dialog(self, test_session):
        """Anonymous user can continue their own dialog"""
        # Create first
        await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="anon-thread-001",
            jwt_user_id=None
        )
        await test_session.commit()

        # Access again
        dialog, created = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="anon-thread-001",
            jwt_user_id=None
        )
        assert created is False
        assert dialog.user_id is None
        assert dialog.id == "anon-thread-001"

    @pytest.mark.asyncio
    async def test_anonymous_cannot_access_logged_in_dialog(self, test_session):
        """Anonymous cannot access a dialog owned by a logged-in user"""
        # Create dialog owned by user_1
        await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="user-thread-001",
            jwt_user_id="user_1"
        )
        await test_session.commit()

        # Anonymous tries to access it
        with pytest.raises(ForbiddenError):
            await DialogRepository.get_or_create_dialog(
                session=test_session,
                dialog_id="user-thread-001",
                jwt_user_id=None
            )


class TestDialogRepositoryAuth:
    """Tests for authenticated user authorization"""

    @pytest.mark.asyncio
    async def test_user_can_access_own_dialog(self, test_session):
        """Logged-in user can access their own dialog"""
        dialog, created = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="user-thread-001",
            jwt_user_id="user_1"
        )
        assert created is True
        assert dialog.user_id == "user_1"
        await test_session.commit()

        # Access again
        dialog2, created2 = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="user-thread-001",
            jwt_user_id="user_1"
        )
        assert created2 is False
        assert dialog2.user_id == "user_1"

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_user_dialog(self, test_session):
        """IDOR prevention: user cannot access another user's dialog"""
        # user_1 creates dialog
        await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="cross-user-thread",
            jwt_user_id="user_1"
        )
        await test_session.commit()

        # user_2 tries to access user_1's dialog
        with pytest.raises(ForbiddenError):
            await DialogRepository.get_or_create_dialog(
                session=test_session,
                dialog_id="cross-user-thread",
                jwt_user_id="user_2"
            )

    @pytest.mark.asyncio
    async def test_user_can_create_dialog_with_provided_id(self, test_session):
        """User can create dialog with specific ID (thread_id from frontend)"""
        dialog, created = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="custom-thread-uuid",
            jwt_user_id="user_1"
        )
        assert created is True
        assert dialog.id == "custom-thread-uuid"
        assert dialog.user_id == "user_1"

    @pytest.mark.asyncio
    async def test_list_user_dialogs_only_returns_own(self, test_session):
        """list_user_dialogs only returns dialogs for that specific user"""
        # Create dialogs for different users
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="d1", jwt_user_id="user_1"
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="d2", jwt_user_id="user_1"
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="d3", jwt_user_id="user_2"
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="d4", jwt_user_id=None  # anonymous
        )
        await test_session.commit()

        # List for user_1
        dialogs = await DialogRepository.list_user_dialogs(
            session=test_session, user_id="user_1"
        )
        assert len(dialogs) == 2
        assert all(d.user_id == "user_1" for d in dialogs)

    @pytest.mark.asyncio
    async def test_list_anonymous_dialogs(self, test_session):
        """list_anonymous_dialogs only returns NULL user_id dialogs"""
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="a1", jwt_user_id=None
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="a2", jwt_user_id=None
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="u1", jwt_user_id="user_1"
        )
        await test_session.commit()

        dialogs = await DialogRepository.list_anonymous_dialogs(
            session=test_session
        )
        assert len(dialogs) == 2
        assert all(d.user_id is None for d in dialogs)