from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator
import uuid

class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    ANALYST = "analyst"
    EXECUTOR = "executor"
    REFLECTOR = "reflector"

class AgentRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = Field(..., min_length=3, max_length=1000)
    role: AgentRole
    context: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("goal")
    @classmethod
    def goal_must_not_be_empty_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Goal cannot be empty whitespace")
        return v

class AgentResponse(BaseModel):
    request_id: str
    success: bool
    output: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    source: str
    payload: Dict[str, Any]