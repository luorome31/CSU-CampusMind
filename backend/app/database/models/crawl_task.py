"""
Crawl Task Model - SQLModel for tracking batch crawl background tasks
"""
from datetime import datetime
import json
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import computed_field


class CrawlTaskStatus:
    """Crawl task status constants"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CrawlTask(SQLModel, table=True):
    """Crawl task table - stores the progress and status of batch crawling jobs"""
    __tablename__ = "crawl_task"

    id: str = Field(default=None, primary_key=True, description="Task ID")
    knowledge_id: Optional[str] = Field(default=None, description="Optional associated knowledge base ID")
    user_id: str = Field(index=True, description="User who initiated the task")
    total_urls: int = Field(default=0, description="Total number of URLs to crawl")
    completed_urls: int = Field(default=0, description="Number of completed URLs (both success and fail)")
    success_count: int = Field(default=0, description="Number of successfully crawled URLs")
    fail_count: int = Field(default=0, description="Number of failed URLs")
    status: str = Field(default=CrawlTaskStatus.PROCESSING, description="Status: processing/completed/failed")
    failed_urls_json: str = Field(
        default="[]",
        description="JSON string of failed URLs with error details: [{url, error, timestamp}]"
    )
    create_time: datetime = Field(default_factory=datetime.now, description="Task creation time")
    update_time: datetime = Field(default_factory=datetime.now, description="Task last update time")

    @computed_field
    @property
    def failed_urls(self) -> list:
        """Parse failed_urls_json to list - computed field for Pydantic serialization"""
        try:
            return json.loads(self.failed_urls_json) if self.failed_urls_json else []
        except (json.JSONDecodeError, TypeError):
            return []
