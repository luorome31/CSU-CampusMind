"""
Knowledge File Service - CRUD operations for knowledge files
"""
import uuid
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from app.database.models.knowledge_file import KnowledgeFile, FileStatus
from app.database.session import engine
from app.services.storage.client import storage_client


class KnowledgeFileService:
    """Knowledge file CRUD service"""

    @staticmethod
    def create_knowledge_file(
        file_name: str,
        knowledge_id: str,
        user_id: str,
        oss_url: str,
        object_name: str,
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
            object_name=object_name,
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
    def list_knowledge_files(
        knowledge_id: str, 
        status: Optional[str] = None
    ) -> List[KnowledgeFile]:
        """List files in a knowledge base with optional status filtering"""
        with Session(engine) as session:
            statement = select(KnowledgeFile).where(KnowledgeFile.knowledge_id == knowledge_id)
            if status:
                statement = statement.where(KnowledgeFile.status == status)
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
        """Delete a knowledge file (DB record and OSS content)"""
        with Session(engine) as session:
            statement = select(KnowledgeFile).where(KnowledgeFile.id == file_id)
            knowledge_file = session.exec(statement).first()
            if knowledge_file:
                # Cleanup OSS
                try:
                    storage_client.delete_content(knowledge_file.object_name)
                except Exception:
                    pass # Don't block DB deletion if OSS fails
                
                session.delete(knowledge_file)
                session.commit()
                return True
            return False

    @staticmethod
    def list_all_pending_files(user_id: str) -> List[KnowledgeFile]:
        """List all files requiring manual verification across all KBs for a user"""
        with Session(engine) as session:
            statement = select(KnowledgeFile).where(
                KnowledgeFile.user_id == user_id,
                KnowledgeFile.status == FileStatus.PENDING_VERIFY
            ).order_by(KnowledgeFile.create_time.desc())
            return list(session.exec(statement).all())

    @staticmethod
    def count_knowledge_files(knowledge_id: str) -> int:
        """Count files in a knowledge base"""
        with Session(engine) as session:
            statement = select(KnowledgeFile).where(KnowledgeFile.knowledge_id == knowledge_id)
            return len(list(session.exec(statement).all()))
