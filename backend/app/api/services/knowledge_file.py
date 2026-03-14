"""
Knowledge File Service - CRUD operations for knowledge files
"""
import uuid
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from app.database.models.knowledge_file import KnowledgeFile, FileStatus
from app.database.session import engine


class KnowledgeFileService:
    """Knowledge file CRUD service"""

    @staticmethod
    def create_knowledge_file(
        file_name: str,
        knowledge_id: str,
        user_id: str,
        oss_url: str,
        file_size: int = 0,
    ) -> KnowledgeFile:
        """Create a new knowledge file record"""
        file_id = uuid.uuid4().hex
        knowledge_file = KnowledgeFile(
            id=file_id,
            file_name=file_name,
            knowledge_id=knowledge_id,
            user_id=user_id,
            oss_url=oss_url,
            file_size=file_size,
            status=FileStatus.PROCESS,
        )
        with Session(engine) as session:
            session.add(knowledge_file)
            session.commit()
            session.refresh(knowledge_file)
        return knowledge_file

    @staticmethod
    def get_knowledge_file(file_id: str) -> Optional[KnowledgeFile]:
        """Get knowledge file by ID"""
        with Session(engine) as session:
            statement = select(KnowledgeFile).where(KnowledgeFile.id == file_id)
            return session.exec(statement).first()

    @staticmethod
    def list_knowledge_files(knowledge_id: str) -> List[KnowledgeFile]:
        """List all files in a knowledge base"""
        with Session(engine) as session:
            statement = select(KnowledgeFile).where(KnowledgeFile.knowledge_id == knowledge_id)
            return list(session.exec(statement).all())

    @staticmethod
    def update_file_status(file_id: str, status: str) -> bool:
        """Update file processing status"""
        with Session(engine) as session:
            statement = select(KnowledgeFile).where(KnowledgeFile.id == file_id)
            knowledge_file = session.exec(statement).first()
            if knowledge_file:
                knowledge_file.status = status
                knowledge_file.update_time = datetime.now()
                session.commit()
                return True
            return False

    @staticmethod
    def delete_knowledge_file(file_id: str) -> bool:
        """Delete a knowledge file"""
        with Session(engine) as session:
            statement = select(KnowledgeFile).where(KnowledgeFile.id == file_id)
            knowledge_file = session.exec(statement).first()
            if knowledge_file:
                session.delete(knowledge_file)
                session.commit()
                return True
            return False
