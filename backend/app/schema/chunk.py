"""
Chunk Model - Data model for text chunks
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ChunkModel(BaseModel):
    """Chunk data model"""
    chunk_id: str
    content: str
    file_id: str
    file_name: str
    knowledge_id: str
    update_time: str
    summary: Optional[str] = ""

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "file_id": self.file_id,
            "file_name": self.file_name,
            "knowledge_id": self.knowledge_id,
            "update_time": self.update_time,
            "summary": self.summary
        }
