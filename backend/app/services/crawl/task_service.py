"""
Crawl Task Service - CRUD operations for background crawl tasks
"""
import uuid
from typing import Optional
from datetime import datetime
from sqlmodel import Session, select

from app.database.models.crawl_task import CrawlTask, CrawlTaskStatus
from app.database.session import engine


class CrawlTaskService:
    """Crawl Task CRUD service"""

    @staticmethod
    def create_task(
        user_id: str,
        total_urls: int,
        knowledge_id: Optional[str] = None,
    ) -> CrawlTask:
        """Create a new crawl task record"""
        task_id = uuid.uuid4().hex
        task = CrawlTask(
            id=task_id,
            user_id=user_id,
            knowledge_id=knowledge_id,
            total_urls=total_urls,
            status=CrawlTaskStatus.PROCESSING,
        )
        with Session(engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    @staticmethod
    def get_task(task_id: str) -> Optional[CrawlTask]:
        """Get crawl task by ID"""
        with Session(engine) as session:
            statement = select(CrawlTask).where(CrawlTask.id == task_id)
            return session.exec(statement).first()

    @staticmethod
    def update_task_progress(
        task_id: str,
        success: bool,
    ) -> Optional[CrawlTask]:
        """Atomically increment completed_urls and success/fail counts"""
        with Session(engine) as session:
            statement = select(CrawlTask).where(CrawlTask.id == task_id)
            task = session.exec(statement).first()
            if not task:
                return None

            task.completed_urls += 1
            if success:
                task.success_count += 1
            else:
                task.fail_count += 1

            if task.completed_urls >= task.total_urls:
                task.status = CrawlTaskStatus.COMPLETED

            task.update_time = datetime.now()
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def mark_task_failed(task_id: str) -> Optional[CrawlTask]:
        """Explicitly mark a task as completely failed"""
        with Session(engine) as session:
            statement = select(CrawlTask).where(CrawlTask.id == task_id)
            task = session.exec(statement).first()
            if not task:
                return None

            task.status = CrawlTaskStatus.FAILED
            task.update_time = datetime.now()
            session.commit()
            session.refresh(task)
            return task
