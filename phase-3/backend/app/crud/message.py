from typing import List
from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message import MessageCreate


class MessageCRUD:
    def create(
        self,
        db: Session,
        user_id: str,
        conversation_id: int,
        message_data: MessageCreate
    ) -> Message:
        """Create a new message."""
        message = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            role=message_data.role,
            content=message_data.content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_by_conversation(
        self,
        db: Session,
        user_id: str,
        conversation_id: int
    ) -> List[Message]:
        """Get all messages for a conversation."""
        return db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        ).order_by(Message.created_at.asc()).all()


message_crud = MessageCRUD()
