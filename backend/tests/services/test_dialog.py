"""
Dialog Service 测试 - 使用真正的异步集成测试
"""
import pytest
import os
import tempfile
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel


@pytest.fixture(scope="function")
async def test_engine():
    """创建异步测试引擎"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # 使用 aiosqlite
    db_url = f"sqlite+aiosqlite:///{path}"
    engine = create_async_engine(db_url, echo=False)

    # 创建表
    from app.database.models.dialog import Dialog
    from app.database.models.chat_history import ChatHistory
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # 清理
    await engine.dispose()
    os.unlink(path)


@pytest.fixture(scope="function")
async def test_session_maker(test_engine):
    """创建 session maker"""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


class TestDialogServiceAsync:
    """DialogService 异步集成测试"""

    @pytest.mark.asyncio(scope="function")
    async def test_create_dialog(self, test_engine):
        """测试创建对话框"""
        from app.services.dialog.dialog import DialogService

        async_session_maker = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_maker() as session:
            dialog = await DialogService.create_dialog(
                session=session,
                user_id="user_1",
                agent_id="agent_1"
            )

            assert dialog.user_id == "user_1"
            assert dialog.agent_id == "agent_1"
            await session.commit()

    @pytest.mark.asyncio(scope="function")
    async def test_get_dialog(self, test_engine):
        """测试获取对话框"""
        from app.services.dialog.dialog import DialogService

        async_session_maker = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_maker() as session:
            # 创建
            dialog = await DialogService.create_dialog(
                session=session,
                user_id="user_1"
            )
            await session.commit()

            # 获取
            retrieved = await DialogService.get_dialog(session, dialog.id)
            assert retrieved is not None
            assert retrieved.user_id == "user_1"

    @pytest.mark.asyncio(scope="function")
    async def test_list_user_dialogs(self, test_engine):
        """测试列出用户对话框"""
        from app.services.dialog.dialog import DialogService

        async_session_maker = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_maker() as session:
            # 创建多个对话框
            await DialogService.create_dialog(session=session, user_id="user_1")
            await DialogService.create_dialog(session=session, user_id="user_1")
            await DialogService.create_dialog(session=session, user_id="user_2")
            await session.commit()

            # 列出 user_1 的对话框
            dialogs = await DialogService.list_user_dialogs(session, "user_1")
            assert len(dialogs) == 2

    @pytest.mark.asyncio(scope="function")
    async def test_update_dialog_time(self, test_engine):
        """测试更新对话框时间"""
        from app.services.dialog.dialog import DialogService

        async_session_maker = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_maker() as session:
            # 创建
            dialog = await DialogService.create_dialog(session, user_id="user_1")
            await session.commit()

            # 更新
            await DialogService.update_dialog_time(session, dialog.id)

            # 验证
            updated = await DialogService.get_dialog(session, dialog.id)
            assert updated.updated_at is not None
