from sqlalchemy import String, ForeignKey, Text, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Dict, Any
from common.db.base import Base

class StudySession(Base):
    __tablename__ = "study_sessions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    topic: Mapped[Optional[str]] = mapped_column(String(255))
    
    session_goals: Mapped[List[str]] = mapped_column(JSON, server_default='[]')
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    trace_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)

    user: Mapped["User"] = relationship("User", back_populates="study_sessions")
    materials: Mapped[List["StudyMaterial"]] = relationship("StudyMaterial", back_populates="session", cascade="all, delete-orphan")
    cards: Mapped[List["Flashcard"]] = relationship("Flashcard", back_populates="session", cascade="all, delete-orphan")

class StudyMaterial(Base):
    __tablename__ = "study_materials"

    session_id: Mapped[int] = mapped_column(ForeignKey("study_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50))
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    
    source_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, server_default='{}')
    vector_indices: Mapped[List[str]] = mapped_column(JSON, server_default='[]')

    session: Mapped["StudySession"] = relationship("StudySession", back_populates="materials")

class Flashcard(Base):
    __tablename__ = "flashcards"

    session_id: Mapped[int] = mapped_column(ForeignKey("study_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    
    difficulty_score: Mapped[float] = mapped_column(Float, default=0.5)
    last_reviewed: Mapped[Optional[str]] = mapped_column(String(100))
    repetition_count: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped["StudySession"] = relationship("StudySession", back_populates="cards")