"""
Search Model - For retrieval results
"""
from typing import Optional
from pydantic import BaseModel


class SearchModel(BaseModel):
    """Search result model"""
    content: str = ""
    chunk_id: str = ""
    file_id: str = ""
    file_name: str = ""
    knowledge_id: str = ""
    update_time: str = ""
    summary: str = ""
    score: float = 0.0
