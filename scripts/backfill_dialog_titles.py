"""
数据回填脚本：为没有标题的 dialog 记录补充 title 字段。

用途：新对话功能上线后，历史 dialog 记录没有 title，本脚本根据首条
用户消息内容生成前 25 字符作为标题（与 completion.py 的即时标题逻辑一致）。

运行前提：已完成数据库迁移（add_dialog_title_column.py）。

使用方式：
    # 直接运行（脚本内已正确设置 PYTHONPATH）
    python /home/luorome/software/CampusMind/scripts/backfill_dialog_titles.py
"""

import asyncio
import re
import sys
import os

# Add the backend/ directory to the python path (project root / backend)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlmodel import select, Session
from app.database.session import engine
from app.database.models.dialog import Dialog
from app.database.models.chat_history import ChatHistory


async def backfill_titles():
    """
    Backfill titles for dialogs that don't have one.
    It uses the content of the first message in the dialog.
    """
    print("Starting title backfill...")
    count = 0

    with Session(engine) as session:
        # 1. Find all dialogs without a title
        statement = select(Dialog).where((Dialog.title == None) | (Dialog.title == ""))
        dialogs = session.exec(statement).all()

        print(f"Found {len(dialogs)} dialogs needing backfill.")

        for dialog in dialogs:
            # 2. Find the first user message for this dialog
            msg_statement = (
                select(ChatHistory)
                .where(ChatHistory.dialog_id == dialog.id)
                .where(ChatHistory.role == "user")
                .order_by(ChatHistory.created_at.asc())
                .limit(1)
            )
            first_msg = session.exec(msg_statement).first()

            if first_msg:
                # Strip thinking tags and angle brackets like completion.py does
                content = re.sub(r'<think>.*?</think>', '', first_msg.content, flags=re.DOTALL | re.IGNORECASE).strip()
                content = re.sub(r'<.*?>', '', content).strip()
                new_title = content[:25]
                if len(content) > 25:
                    new_title += "..."

                dialog.title = new_title
                session.add(dialog)
                count += 1
                print(f"Updated Dialog {dialog.id}: {new_title}")
            else:
                # If no messages, set a placeholder
                dialog.title = "新对话"
                session.add(dialog)
                count += 1
                print(f"Updated empty Dialog {dialog.id}: 新对话")

        session.commit()

    print(f"Finished. Successfully updated {count} dialogs.")


if __name__ == "__main__":
    asyncio.run(backfill_titles())
