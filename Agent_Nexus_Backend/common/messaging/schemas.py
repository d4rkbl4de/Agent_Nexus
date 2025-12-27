from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator

class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class EventType(str, Enum):
    AGENT_INVOKED = "agent.invoked"
    AGENT_THOUGHT = "agent.thought"
    TOOL_CALL = "tool.call"
    TOOL_RESPONSE = "tool.response"
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    MEMORY_COMMITTED = "memory.committed"
    POLICY_VIOLATION = "policy.violation"
    ERROR_ESCALATION = "error.escalation"
    SYSTEM_SIGNAL = "system.signal"

class AgentThoughtPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    thought: str
    internal_monologue: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    tokens_used: int = 0

class ToolCallPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str

class ToolResponsePayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    call_id: str
    output: Any
    is_error: bool = False
    execution_time_ms: float = 0.0

class TaskEventPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    task_id: str
    worker_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    retry_count: int = 0

class PolicyEventPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    policy_id: str
    rule_violated: str
    severity: str
    action_taken: str
    block_execution: bool = True

class MessageSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex}")
    trace_id: str = Field(..., min_length=1)
    agent_id: Optional[str] = None
    event_type: EventType
    priority: MessagePriority = MessagePriority.NORMAL
    payload: Union[
        AgentThoughtPayload, 
        ToolCallPayload, 
        ToolResponsePayload, 
        TaskEventPayload, 
        PolicyEventPayload, 
        Dict[str, Any]
    ]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("trace_id")
    @classmethod
    def validate_trace_context(cls, v: str) -> str:
        if not v:
            raise ValueError("Rule 20 Violation: Trace context is mandatory for all messages.")
        return v

class BusEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    version: str = "1.0"
    source_lobe: str = Field(..., pattern="^(InsightMate|StudyFlow|ChatBuddy|AutoAgent_Hub|CORE)$")
    target_lobe: str = "*"
    message: MessageSchema
    hmac_signature: Optional[str] = None