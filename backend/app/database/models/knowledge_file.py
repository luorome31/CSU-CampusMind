"""
Knowledge File Model - SQLModel for knowledge_file table
"""
from datetime import datetime
from sqlmodel import Field, SQLModel


class FileStatus:
    """File processing status constants"""
    SUCCESS = "success"
    PROCESS = "process"
    FAIL = "fail"
    PENDING_VERIFY = "pending_verify"
    VERIFIED = "verified"
    INDEXING = "indexing"
    INDEXED = "indexed"


class KnowledgeFile(SQLModel, table=True):
    """Knowledge file table - stores file metadata and processing status"""
    __tablename__ = "knowledge_file"

    id: str = Field(default=None, primary_key=True, description="File record ID")
    file_name: str = Field(index=True, description="File name with extension")
    knowledge_id: str = Field(index=True, description="Associated knowledge base ID")
    user_id: str = Field(index=True, description="Uploader user ID")
    status: str = Field(default=FileStatus.PROCESS, description="Processing status: success/process/fail")
    oss_url: str = Field(description="OSS/MinIO storage URL")
    object_name: str = Field(description="Stable storage key/path in bucket")
    file_size: int = Field(default=0, description="File size in bytes")
    create_time: datetime = Field(default_factory=datetime.now, description="Create time")
    update_time: datetime = Field(default_factory=datetime.now, description="Update time")

    def to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "knowledge_id": self.knowledge_id,
            "user_id": self.user_id,
            "status": self.status,
            "oss_url": self.oss_url,
            "object_name": self.object_name,
            "file_size": self.file_size,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }
