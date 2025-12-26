from sqlalchemy import String, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Dict, Any
from common.db.base import Base

class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    tier: Mapped[str] = mapped_column(String(50), default="free")
    api_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, server_default='{}')
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, server_default='{}')
    
    last_login: Mapped[Optional[str]] = mapped_column(String(100))
    trace_context: Mapped[Optional[str]] = mapped_column(String(255))

    meetings: Mapped[List["Meeting"]] = relationship(
        "Meeting", back_populates="user", cascade="all, delete-orphan"
    )
    insights: Mapped[List["Insight"]] = relationship(
        "Insight", back_populates="user", cascade="all, delete-orphan"
    )
    chats: Mapped[List["Chat"]] = relationship(
        "Chat", back_populates="user", cascade="all, delete-orphan"
    )
    study_sessions: Mapped[List["StudySession"]] = relationship(
        "StudySession", back_populates="user", cascade="all, delete-orphan"
    )