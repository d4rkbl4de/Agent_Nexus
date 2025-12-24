from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime


class FeedbackCreate(BaseModel):
    agent_id: str
    message_id: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeedbackRecord(FeedbackCreate):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
