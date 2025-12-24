from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import UUID
from pydantic import BaseModel

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime

class AgentStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"

class AgentState(BaseSchema):
    app_id: str
    status: AgentStatus = AgentStatus.IDLE
    last_activity: datetime

class CommonSchema(TimestampSchema):
    id: UUID
    app_id: str
    user_id: str

# Models needed by CRUD
class MeetingBase(BaseSchema):
    title: str
    start_time: datetime
    end_time: datetime
    raw_transcript: str

class MeetingInDB(MeetingBase, CommonSchema):
    pass
