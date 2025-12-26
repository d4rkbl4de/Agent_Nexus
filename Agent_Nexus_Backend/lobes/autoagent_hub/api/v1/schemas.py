from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class TaskStatus(str, Enum):
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskCreateRequest(BaseModel):
    agent_id: str
    goal: str
    context: Dict[str, Any] = Field(default_factory=dict)
    pre_approved: bool = False
    priority: int = Field(default=1, ge=1, le=5)
    
    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "agent_id": "orchestrator-prime",
                "goal": "Audit cloud infrastructure and suggest cost optimizations",
                "context": {"cloud_provider": "aws", "region": "us-east-1"},
                "pre_approved": False,
                "priority": 2
            }
        }
    )

class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class AgentRegistryResponse(BaseModel):
    agent_id: str
    name: str
    version: str
    capabilities: List[str]
    status: str
    last_active: str
    config_schema: Dict[str, Any]

class PlanStepSchema(BaseModel):
    step_id: str
    tool_name: str
    description: str
    requires_approval: bool
    status: str

class OrchestrationPlanResponse(BaseModel):
    plan_id: str
    task_id: str
    steps: List[PlanStepSchema]
    estimated_tokens: Optional[int] = None
    cost_estimate: Optional[float] = None

class StepApprovalRequest(BaseModel):
    approved: bool
    reason: Optional[str] = None
    modified_args: Optional[Dict[str, Any]] = None

class HubErrorDetail(BaseModel):
    code: str
    message: str
    target: Optional[str] = None

class HubErrorResponse(BaseModel):
    category: str
    trace_id: str
    error: HubErrorDetail