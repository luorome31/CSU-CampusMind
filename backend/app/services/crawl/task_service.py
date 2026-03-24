"""
Crawl Task Service - CRUD operations for background crawl tasks
"""
import uuid
import json
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
        url: Optional[str] = None,
        error: Optional[str] = None,
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
                # Record failed URL details
                if url:
                    failed_list = json.loads(task.failed_urls_json) if task.failed_urls_json else []
                    failed_list.append({
                        "url": url,
                        "error": error or "Unknown error",
                        "timestamp": datetime.now().isoformat()
                    })
                    task.failed_urls_json = json.dumps(failed_list)

            if task.completed_urls >= task.total_urls:
                # Set terminal status based on results
                if task.success_count == 0:
                    task.status = CrawlTaskStatus.FAILED
                elif task.fail_count == 0:
                    task.status = CrawlTaskStatus.COMPLETED
                else:
                    # Partial success - keep as completed but with failures
                    task.status = CrawlTaskStatus.COMPLETED

            task.update_time = datetime.now()
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def list_tasks(user_id: str) -> list[CrawlTask]:
        """List all crawl tasks for a specific user"""
        with Session(engine) as session:
            statement = select(CrawlTask).where(CrawlTask.user_id == user_id).order_by(CrawlTask.create_time.desc())
            return list(session.exec(statement).all())


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

    @staticmethod
    def delete_task(task_id: str) -> bool:
        """Delete a crawl task by ID (does not cascade to KnowledgeFile records)"""
        with Session(engine) as session:
            statement = select(CrawlTask).where(CrawlTask.id == task_id)
            task = session.exec(statement).first()
            if not task:
                return False

            session.delete(task)
            session.commit()
            return True
