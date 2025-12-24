from fastapi import APIRouter, status
from pydantic import BaseModel
from ..tasks import process_chat_message

router = APIRouter()

class ChatMessage(BaseModel):
    user_id: str
    message: str

@router.post("/message", status_code=status.HTTP_202_ACCEPTED)
async def submit_chat_message(chat_data: ChatMessage):
    process_chat_message.send(
        user_id=chat_data.user_id,
        message=chat_data.message
    )
    
    return {
        "status": "Task Queued",
        "user_id": chat_data.user_id,
        "message": "Chat message queued for asynchronous agent response."
    }

@router.get("/health")
async def get_health():
    return {"status": "ok", "service": "ChatBuddy+ API"}