import uuid
from typing import Any, Dict, List, Optional, Union
from pydantic import Field
from common.schemas.base import BaseNexusModel, TraceableMixin, TimestampMixin

class LobeContext(BaseNexusModel, TraceableMixin):
    lobe_id: str
    session_id: str
    user_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    active_agent_id: Optional[str] = None

class AgentHandover(BaseNexusModel, TraceableMixin):
    source_lobe: str
    target_lobe: str
    payload: Dict[str, Any]
    priority: int = Field(default=1, ge=1, le=5)
    context_snapshot: Optional[Dict[str, Any]] = None

class MemoryFragment(BaseNexusModel):
    fragment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    memory_type: str = Field(..., pattern="^(semantic|episodic|procedural)$")
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ToolDefinition(BaseNexusModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    strict_mode: bool = True

class ToolExecutionCall(BaseNexusModel, TraceableMixin):
    tool_name: str
    arguments: Dict[str, Any]
    caller_id: str

class ToolExecutionResult(BaseNexusModel, TraceableMixin):
    tool_name: str
    output: Union[str, Dict[str, Any]]
    is_error: bool = False
    execution_time_ms: float

class TaskRequirement(BaseNexusModel):
    required_capability: str
    min_trust_score: float = 0.8
    policy_overrides: Optional[List[str]] = None