"""
数据库迁移脚本：为 dialog 表添加 title 列。

用途：Dialog 模型新增了 title 字段（用于存储对话会话标题），
本脚本负责执行数据库 schema 变更（ALTER TABLE）。

支持 SQLite 和 PostgreSQL。运行前请确保后端服务已停止。

使用方式：
    # 直接运行（脚本内已正确设置 PYTHONPATH）
    python /home/luorome/software/CampusMind/scripts/add_dialog_title_column.py
"""

import sys
import os

# Add the backend/ directory to the python path (project root / backend)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import inspect, text
from app.database.session import engine


def add_dialog_title_column():
    """
    数据库迁移函数：为 dialog 表添加 'title' 列。
    若列已存在则跳过（幂等操作）。
    """
    print(f"Connecting to database: {engine.url}")

    try:
        inspector = inspect(engine)
        columns = [c["name"] for c in inspector.get_columns("dialog")]

        if "title" not in columns:
            print("Adding 'title' column to 'dialog' table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE dialog ADD COLUMN title VARCHAR"))
                conn.commit()
            print("Successfully added 'title' column.")
        else:
            print("'title' column already exists.")

    except Exception as e:
        print(f"Migration failed: {e}")
        if "postgresql" in str(engine.url):
            print("\nSuggest running manual SQL on PostgreSQL:")
            print("ALTER TABLE dialog ADD COLUMN title VARCHAR;")
        sys.exit(1)


if __name__ == "__main__":
    add_dialog_title_column()
