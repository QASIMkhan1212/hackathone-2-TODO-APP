from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationCRUD:
    def create(self, db: Session, user_id: str) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def get(self, db: Session, user_id: str, conversation_id: int) -> Optional[Conversation]:
        """Get a conversation by ID for a specific user."""
        return db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

    def get_all(self, db: Session, user_id: str) -> List[Conversation]:
        """Get all conversations for a user."""
        return db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).all()

    def delete(self, db: Session, user_id: str, conversation_id: int) -> Optional[Conversation]:
        """Delete a conversation."""
        conversation = self.get(db, user_id, conversation_id)
        if not conversation:
            return None

        db.delete(conversation)
        db.commit()
        return conversation


conversation_crud = ConversationCRUD()
