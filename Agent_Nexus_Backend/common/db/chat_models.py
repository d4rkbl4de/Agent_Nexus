from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, Integer
from sqlalchemy.orm import relationship
from common.db.base import Base
from common.db.mixins import AgenticTraceMixin

class Conversation(Base, AgenticTraceMixin):
    __tablename__ = 'conversations'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    context_windows = relationship("ContextWindow", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base, AgenticTraceMixin):
    __tablename__ = 'conversation_messages'

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey('conversations.id', ondelete="CASCADE"), index=True)
    user_id = Column(String, index=True, nullable=False)
    
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    conversation = relationship("Conversation", back_populates="messages")

class ContextWindow(Base, AgenticTraceMixin):
    __tablename__ = 'context_windows'
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey('conversations.id', ondelete="CASCADE"))
    compressed_context = Column(Text, nullable=False)
    
    token_count = Column(Integer, default=0)
    
    conversation = relationship("Conversation", back_populates="context_windows")