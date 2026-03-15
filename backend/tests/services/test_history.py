"""
History Service 测试 - 使用真正的异步集成测试
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

    db_url = f"sqlite+aiosqlite:///{path}"
    engine = create_async_engine(db_url, echo=False)

    # 创建表 - 需要同时创建 Dialog 因为有外键关系
    from app.database.models.dialog import Dialog
    from app.database.models.chat_history import ChatHistory
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # 清理
    await engine.dispose()
    os.unlink(path)


class TestHistoryServiceAsync:
    """HistoryService 异步集成测试"""

    @pytest.mark.asyncio(scope="function")
    async def test_save_chat_history(self, test_engine):
        """测试保存聊天历史"""
        from app.services.history.history import HistoryService
        from app.services.dialog.dialog import DialogService

        async_session_maker = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_maker() as session:
            # 先创建 dialog
            dialog = await DialogService.create_dialog(session, user_id="user_1")
            await session.commit()

            # 保存历史
            history = await HistoryService.save_chat_history(
                session=session,
                role="user",
                content="Hello",
                dialog_id=dialog.id
            )

            assert history.role == "user"
            assert history.content == "Hello"
            await session.commit()

    @pytest.mark.asyncio(scope="function")
    async def test_get_history_by_dialog(self, test_engine):
        """测试获取对话框历史"""
        from app.services.history.history import HistoryService
        from app.services.dialog.dialog import DialogService

        async_session_maker = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_maker() as session:
            # 创建 dialog
            dialog = await DialogService.create_dialog(session, user_id="user_1")
            await session.commit()

            # 保存多条历史
            await HistoryService.save_chat_history(session, role="user", content="Hello", dialog_id=dialog.id)
            await HistoryService.save_chat_history(session, role="assistant", content="Hi!", dialog_id=dialog.id)
            await session.commit()

            # 获取历史
            histories = await HistoryService.get_history_by_dialog(session, dialog.id)
            assert len(histories) == 2

    @pytest.mark.asyncio(scope="function")
    async def test_delete_dialog_history(self, test_engine):
        """测试删除对话框历史"""
        from app.services.history.history import HistoryService
        from app.services.dialog.dialog import DialogService

        async_session_maker = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_maker() as session:
            # 创建 dialog
            dialog = await DialogService.create_dialog(session, user_id="user_1")
            await session.commit()

            # 保存历史
            await HistoryService.save_chat_history(session, role="user", content="Hello", dialog_id=dialog.id)
            await session.commit()

            # 删除
            await HistoryService.delete_dialog_history(session, dialog.id)

            # 验证
            histories = await HistoryService.get_history_by_dialog(session, dialog.id)
            assert len(histories) == 0

    @pytest.mark.asyncio(scope="function")
    async def test_get_history_with_limit(self, test_engine):
        """测试获取历史限制数量"""
        from app.services.history.history import HistoryService
        from app.services.dialog.dialog import DialogService

        async_session_maker = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_maker() as session:
            dialog = await DialogService.create_dialog(session, user_id="user_1")
            await session.commit()

            # 保存 5 条历史
            for i in range(5):
                await HistoryService.save_chat_history(
                    session, role="user", content=f"Message {i}", dialog_id=dialog.id
                )
            await session.commit()

            # 只获取 3 条
            histories = await HistoryService.get_history_by_dialog(session, dialog.id, limit=3)
            assert len(histories) == 3
