"""Chat API endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ToolCall
from app.schemas.message import MessageCreate
from app.crud.conversation import conversation_crud
from app.crud.message import message_crud
from app.agent.todo_agent import todo_agent

router = APIRouter()


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Process a chat message and return the AI response.

    - Creates a new conversation if conversation_id is not provided
    - Stores user and assistant messages in the database
    - Uses Gemini AI with function calling for task management
    """
    # Get or create conversation
    conversation_id = request.conversation_id

    if conversation_id:
        conversation = conversation_crud.get(db, user_id, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = conversation_crud.create(db, user_id)
        conversation_id = conversation.id

    # Get existing messages for context
    existing_messages = message_crud.get_by_conversation(db, user_id, conversation_id)
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in existing_messages
    ]

    # Store user message
    user_message = MessageCreate(role="user", content=request.message)
    message_crud.create(db, user_id, conversation_id, user_message)

    # Process with AI agent
    try:
        response_text, tool_calls = todo_agent.process_message(
            db=db,
            user_id=user_id,
            message=request.message,
            chat_history=chat_history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

    # Store assistant response
    assistant_message = MessageCreate(role="assistant", content=response_text)
    message_crud.create(db, user_id, conversation_id, assistant_message)

    # Format tool calls for response
    formatted_tool_calls = [
        ToolCall(
            name=tc["name"],
            arguments=tc["arguments"],
            result=tc["result"]
        )
        for tc in tool_calls
    ]

    return ChatResponse(
        conversation_id=conversation_id,
        response=response_text,
        tool_calls=formatted_tool_calls
    )
