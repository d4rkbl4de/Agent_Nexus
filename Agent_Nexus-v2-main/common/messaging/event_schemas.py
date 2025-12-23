from pydantic import BaseModel, Field
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime


class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskEvent(BaseEvent):
    task_name: str
    payload: Dict[str, Any]


class AgentEvent(BaseEvent):
    event_type: str
    data: Dict[str, Any]
