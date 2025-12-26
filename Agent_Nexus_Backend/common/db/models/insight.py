from sqlalchemy import String, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any
from common.db.base import Base

class Insight(Base):
    __tablename__ = "insights"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    meeting_id: Mapped[Optional[int]] = mapped_column(ForeignKey("meetings.id", ondelete="SET NULL"), index=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True)
    
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    source_type: Mapped[str] = mapped_column(String(50), default="meeting")
    
    tags: Mapped[Dict[str, Any]] = mapped_column(JSON, server_default='[]')
    metadata_extra: Mapped[Dict[str, Any]] = mapped_column(JSON, server_default='{}')
    
    trace_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)

    user: Mapped["User"] = relationship("User", back_populates="insights")
    meeting: Mapped[Optional["Meeting"]] = relationship("Meeting", back_populates="insights")

class ActionItem(Base):
    __tablename__ = "action_items"

    insight_id: Mapped[int] = mapped_column(ForeignKey("insights.id", ondelete="CASCADE"), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255))
    due_date: Mapped[Optional[str]] = mapped_column(String(100))
    
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    
    insight: Mapped["Insight"] = relationship("Insight")