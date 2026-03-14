"""
Knowledge Service - CRUD operations for knowledge base
"""
import uuid
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from app.database.models.knowledge import KnowledgeBase
from app.database.session import engine


class KnowledgeService:
    """Knowledge base CRUD service"""

    @staticmethod
    def create_knowledge(
        name: str,
        user_id: str,
        description: str = ""
    ) -> KnowledgeBase:
        """Create a new knowledge base"""
        knowledge_id = f"t_{uuid.uuid4().hex[:16]}"
        knowledge = KnowledgeBase(
            id=knowledge_id,
            name=name,
            description=description,
            user_id=user_id,
        )
        with Session(engine) as session:
            session.add(knowledge)
            session.commit()
            session.refresh(knowledge)
        return knowledge

    @staticmethod
    def get_knowledge(knowledge_id: str) -> Optional[KnowledgeBase]:
        """Get knowledge base by ID"""
        with Session(engine) as session:
            statement = select(KnowledgeBase).where(KnowledgeBase.id == knowledge_id)
            return session.exec(statement).first()

    @staticmethod
    def list_knowledge_by_user(user_id: str) -> List[KnowledgeBase]:
        """List all knowledge bases for a user"""
        with Session(engine) as session:
            statement = select(KnowledgeBase).where(KnowledgeBase.user_id == user_id)
            return list(session.exec(statement).all())

    @staticmethod
    def delete_knowledge(knowledge_id: str) -> bool:
        """Delete a knowledge base"""
        with Session(engine) as session:
            statement = select(KnowledgeBase).where(KnowledgeBase.id == knowledge_id)
            knowledge = session.exec(statement).first()
            if knowledge:
                session.delete(knowledge)
                session.commit()
                return True
            return False
