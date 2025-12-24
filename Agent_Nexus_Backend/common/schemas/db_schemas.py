from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, conlist

class AnalysisResult(BaseModel):
    id: UUID = Field(default_factory=UUID)
    result_data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StudyPlan(BaseModel):
    id: UUID = Field(default_factory=UUID)
    topic: str
    steps: conlist(str, min_length=1)
    status: str = "draft"

class ActionItem(BaseModel):
    id: UUID = Field(default_factory=UUID)
    description: str
    owner: str
    due_date: datetime | None = None
    is_completed: bool = False

class StudyRequest(BaseModel):
    id: UUID = Field(default_factory=UUID)
    user_query: str
    status: str = "pending"
    plan_id: UUID | None = None
