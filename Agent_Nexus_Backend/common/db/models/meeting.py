from sqlalchemy import String, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Dict, Any
from common.db.base import Base

class Meeting(Base):
    __tablename__ = "meetings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_transcript: Mapped[Optional[str]] = mapped_column(Text)
    processed_summary: Mapped[Optional[str]] = mapped_column(Text)
    
    source_url: Mapped[Optional[str]] = mapped_column(String(1024))
    meeting_platform: Mapped[str] = mapped_column(String(50), default="unknown")
    
    recording_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, server_default='{}')
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    
    trace_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)

    user: Mapped["User"] = relationship("User", back_populates="meetings")
    insights: Mapped[List["Insight"]] = relationship("Insight", back_populates="meeting", cascade="all, delete-orphan")

class MeetingChunk(Base):
    __tablename__ = "meeting_chunks"

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"), index=True, nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    speaker_label: Mapped[Optional[str]] = mapped_column(String(100))
    start_time: Mapped[Optional[float]]
    end_time: Mapped[Optional[float]]
    
    embedding_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)

    meeting: Mapped["Meeting"] = relationship("Meeting")