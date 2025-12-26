from sqlalchemy import String, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any
from common.db.base import Base

class Chat(Base):
    __tablename__ = "chats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    thread_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    
    system_prompt_override: Mapped[Optional[str]] = mapped_column(Text)
    model_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, server_default='{}')
    
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_extra: Mapped[Dict[str, Any]] = mapped_column(JSON, server_default='{}')

    user: Mapped["User"] = relationship("User", back_populates="chats")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    token_count: Mapped[int] = mapped_column(default=0)
    cost_estimate: Mapped[float] = mapped_column(default=0.0)
    
    trace_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    tool_calls: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    chat: Mapped["Chat"] = relationship("Chat")